"""Reconstruct diffusion trees from raw platform records.

Platforms rarely say whom a reshare came *through*: a Bluesky repost and a Telegram
forward both point to the original post. Each reshare's parent is therefore chosen by
the first rule that applies, and the rule is stored on the node so analyses can be
re-run per rule (sensitivity check):

  via     the record names the reshare it was seen through (exact; Bluesky, when present)
  follow  the most recent EARLIER resharer of the same item whom this account follows
          (Telegram: whose channel this channel has forwarded from before)
  item    otherwise, the item being reshared (the root, or a quote post)
"""
from __future__ import annotations

import collections
import json
import os
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

from .cascade import Cascade, Node
from .io import read_jsonl


def assign_parents(reshares: List[Tuple[str, str, float]], item_of: Dict[str, str],
                   follows_of: Callable[[str], Set[str]],
                   via_of: Optional[Dict[str, str]] = None) -> Dict[str, Tuple[str, str]]:
    """reshares: (node_id, account, ts) sorted by ts. Returns node_id -> (parent_id, rule)."""
    seen = collections.defaultdict(list)
    out = {}
    for node, acct, _ in reshares:
        item = item_of[node]
        via = via_of.get(node) if via_of else None
        if via and via in out:
            out[node] = (via, "via")
        else:
            f = follows_of(acct)
            parent = next((nid for nid, a in reversed(seen[item]) if a in f), None)
            out[node] = (parent, "follow") if parent else (item, "item")
        seen[item].append((node, acct))
    return out


# ------------------------------------------------------------------ Bluesky

def _did(uri):
    return uri.split("/")[2] if uri and uri.startswith("at://") else None


class FollowCache:
    """Follow lists from streamed follow events plus, optionally, Bluesky's public API,
    cached in SQLite so each account is fetched once."""
    API = "https://public.api.bsky.app/xrpc/app.bsky.graph.getFollows"

    def __init__(self, path: Optional[str] = None, fetch: bool = False, max_pages: int = 50,
                 pause_s: float = 0.2):
        self.db = sqlite3.connect(path or ":memory:")
        self.db.execute("CREATE TABLE IF NOT EXISTS f (did TEXT PRIMARY KEY, follows TEXT)")
        self.fetch, self.max_pages, self.pause_s = fetch, max_pages, pause_s
        self.streamed: Dict[str, Set[str]] = collections.defaultdict(set)
        self._mem: Dict[str, Set[str]] = {}

    def __call__(self, did: str) -> Set[str]:
        if did in self._mem:
            return self._mem[did]
        s = set(self.streamed.get(did, ()))
        row = self.db.execute("SELECT follows FROM f WHERE did=?", (did,)).fetchone()
        if row:
            s |= set(json.loads(row[0]))
        elif self.fetch:
            got = self._fetch(did)
            self.db.execute("INSERT OR REPLACE INTO f VALUES (?,?)", (did, json.dumps(sorted(got))))
            self.db.commit()
            s |= got
        self._mem[did] = s
        return s

    def _fetch(self, did):
        out, cursor = set(), None
        for _ in range(self.max_pages):
            q = {"actor": did, "limit": 100}
            if cursor:
                q["cursor"] = cursor
            try:
                with urllib.request.urlopen(self.API + "?" + urllib.parse.urlencode(q), timeout=30) as r:
                    data = json.load(r)
            except Exception as e:  # deleted or taken-down accounts return errors
                print(f"follows {did}: {e}", file=sys.stderr)
                break
            out |= {x["did"] for x in data.get("follows", [])}
            cursor = data.get("cursor")
            time.sleep(self.pause_s)
            if not cursor:
                break
        return out


def build_bluesky(raw_dir: str, min_size: int = 10, fetch_follows: bool = False) -> List[Cascade]:
    """Cascades from files written by ``cascadekit collect-bluesky``.
    Reposts and quote posts both count as reshares; quote chains are followed to the
    original post, which becomes the root."""
    posts, reposts, takedowns = {}, {}, set()
    follows = FollowCache(os.path.join(raw_dir, "follows.sqlite"), fetch_follows)
    for r in read_jsonl(os.path.join(raw_dir, "**", "*.jsonl.gz")):
        t = r.get("t")
        if t == "post":
            posts[f"at://{r['did']}/app.bsky.feed.post/{r['rkey']}"] = r
        elif t == "repost" and r.get("subject"):
            reposts[f"at://{r['did']}/app.bsky.feed.repost/{r['rkey']}"] = r
        elif t == "follow" and r.get("subject"):
            follows.streamed[r["did"]].add(r["subject"])
        elif t == "acct" and r.get("status") in ("takendown", "suspended"):
            takedowns.add(r["did"])

    item_of, via_of, events = {}, {}, []
    for uri, r in reposts.items():
        item_of[uri] = r["subject"]
        if r.get("via"):
            via_of[uri] = r["via"]
        events.append((uri, r["did"], r["ts"] / 1e6))
    for uri, p in posts.items():
        if p.get("quote"):
            item_of[uri] = p["quote"]
            events.append((uri, p["did"], p["ts"] / 1e6))

    def root_of(uri):
        for _ in range(50):
            q = posts.get(uri, {}).get("quote")
            if not q:
                break
            uri = q
        return uri

    groups = collections.defaultdict(list)
    for e in events:
        groups[root_of(item_of[e[0]])].append(e)

    out = []
    for root, evs in groups.items():
        if len(evs) < min_size:
            continue
        evs.sort(key=lambda e: e[2])
        parents = assign_parents(evs, item_of, follows, via_of)
        rp = posts.get(root)
        nodes = [Node(root, _did(root), rp["ts"] / 1e6 if rp else None)]
        nodes += [Node(nid, acct, ts, *parents[nid]) for nid, acct, ts in evs]
        meta = {"root_langs": rp.get("langs") if rp else None,
                "takedown_accounts": sum(1 for n in nodes if n.account in takedowns)}
        if rp and rp.get("text"):
            meta["text"] = rp["text"]
        out.append(Cascade(root, nodes, "bluesky", rp is not None, None, meta))
    return out


# ------------------------------------------------------------------ Telegram

def _epoch(iso):
    return datetime.fromisoformat(iso).timestamp() if iso else None


def build_telegram(raw_dir: str, min_size: int = 10) -> List[Cascade]:
    """Cascades from files written by ``cascadekit collect-telegram``. The root is the
    original channel post; nodes are channel-to-channel forwards of it."""
    msgs = list(read_jsonl(os.path.join(raw_dir, "messages", "*.jsonl.gz")))
    originals = {(m["chan"], m["msg"]): m for m in msgs}
    sources = collections.defaultdict(set)
    groups = collections.defaultdict(list)
    for m in msgs:
        if m.get("fwd_chan") and m.get("fwd_post"):
            sources[str(m["chan"])].add(str(m["fwd_chan"]))
            groups[(m["fwd_chan"], m["fwd_post"])].append(m)

    out = []
    for (src, post), fw in groups.items():
        if len(fw) < min_size:
            continue
        root = f"tg:{src}/{post}"
        evs = sorted(((f"tg:{m['chan']}/{m['msg']}", str(m["chan"]), _epoch(m["date"])) for m in fw),
                     key=lambda e: e[2])
        parents = assign_parents(evs, {e[0]: root for e in evs}, lambda ch: sources.get(ch, set()))
        orig = originals.get((src, post))
        root_ts = _epoch(orig["date"]) if orig else _epoch(fw[0].get("fwd_date"))
        nodes = [Node(root, str(src), root_ts)]
        nodes += [Node(nid, acct, ts, *parents[nid]) for nid, acct, ts in evs]
        meta = {"root_views": orig.get("views") if orig else None,
                "root_forwards_total": orig.get("forwards") if orig else None}  # incl. private forwards
        if orig and orig.get("text"):
            meta["text"] = orig["text"]
        out.append(Cascade(root, nodes, "telegram", orig is not None, None, meta))
    return out
