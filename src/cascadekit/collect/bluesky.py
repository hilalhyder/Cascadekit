#!/usr/bin/env python3
"""
Bluesky collector (cascadekit collect-bluesky).

Streams posts, reposts, deletions and account-status changes (takedowns,
suspensions) from a Jetstream instance and writes them as hourly gzip JSONL
files. Restarts resume from the last saved cursor, so the script can run
24/7 under tmux, screen or systemd.

    pip install "cascadekit[bluesky]"
    cascadekit collect-bluesky --out data/bluesky
    cascadekit collect-bluesky --out data/bluesky --follows   # also stream follow events

Output layout:  <out>/YYYY/MM/DD/HH.jsonl.gz   plus  <out>/cursor.txt
Each line is one slim record:
    {"t":"post",   "did","rkey","ts","created","langs","reply_parent","reply_root","quote","text"}
    {"t":"repost", "did","rkey","ts","created","subject","via"}
    {"t":"follow", "did","rkey","ts","subject"}
    {"t":"del",    "did","coll","rkey","ts"}
    {"t":"acct",   "did","ts","active","status"}      # status e.g. takendown / suspended / deleted
"ts" is the Jetstream time in microseconds (server side; harder to fake than "created").
Records may repeat after a reconnect; de-duplicate on (t, did, rkey) when loading.
"""
import argparse
import asyncio
import gzip
import json
import os
import signal
import time
from datetime import datetime, timezone
from urllib.parse import urlencode

POST, REPOST, FOLLOW = "app.bsky.feed.post", "app.bsky.feed.repost", "app.bsky.graph.follow"


def quoted_uri(embed):
    """Return the URI of a quoted post, if the post embeds one."""
    if not isinstance(embed, dict):
        return None
    kind = embed.get("$type", "")
    if kind == "app.bsky.embed.record":
        return (embed.get("record") or {}).get("uri")
    if kind == "app.bsky.embed.recordWithMedia":
        return ((embed.get("record") or {}).get("record") or {}).get("uri")
    return None


def slim(ev, text_langs):
    """Turn a raw Jetstream event into a compact record, or None to skip it."""
    did, ts = ev.get("did"), ev.get("time_us")
    kind = ev.get("kind") or ev.get("type")

    # Account status changes: very useful label evidence (platform takedowns).
    if kind in ("account", "acc") or "account" in ev:
        acc = ev.get("account") or {}
        return {"t": "acct", "did": did, "ts": ts,
                "active": acc.get("active"), "status": acc.get("status")}

    if kind not in ("commit", "com"):
        return None  # identity events etc.
    c = ev.get("commit") or {}
    op = c.get("operation") or c.get("type")
    coll, rkey = c.get("collection"), c.get("rkey")

    if op in ("delete", "d"):
        return {"t": "del", "did": did, "coll": coll, "rkey": rkey, "ts": ts}
    if op not in ("create", "c"):
        return None
    rec = c.get("record") or {}

    if coll == POST:
        langs = rec.get("langs") or []
        reply = rec.get("reply") or {}
        out = {"t": "post", "did": did, "rkey": rkey, "ts": ts,
               "created": rec.get("createdAt"), "langs": langs,
               "reply_parent": (reply.get("parent") or {}).get("uri"),
               "reply_root": (reply.get("root") or {}).get("uri"),
               "quote": quoted_uri(rec.get("embed"))}
        # Keep text only for the languages you will annotate; saves a lot of disk.
        if text_langs is None or any(l.split("-")[0] in text_langs for l in langs):
            out["text"] = rec.get("text")
        return out
    if coll == REPOST:
        return {"t": "repost", "did": did, "rkey": rkey, "ts": ts,
                "created": rec.get("createdAt"),
                "subject": (rec.get("subject") or {}).get("uri"),
                # Newer clients may record which repost the user saw it through.
                # If present this gives the TRUE parent, no inference needed.
                "via": (rec.get("via") or {}).get("uri")}
    if coll == FOLLOW:
        return {"t": "follow", "did": did, "rkey": rkey, "ts": ts, "subject": rec.get("subject")}
    return None


class HourlyWriter:
    def __init__(self, root):
        self.root, self.key, self.fh, self.bytes = root, None, None, 0

    def write(self, rec):
        ts = rec.get("ts") or int(time.time() * 1e6)
        d = datetime.fromtimestamp(ts / 1e6, tz=timezone.utc)
        key = d.strftime("%Y/%m/%d/%H")
        if key != self.key:
            self.close()
            path = os.path.join(self.root, key + ".jsonl.gz")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.fh, self.key = gzip.open(path, "at", encoding="utf-8"), key
        line = json.dumps(rec, ensure_ascii=False) + "\n"
        self.fh.write(line)
        self.bytes += len(line)

    def close(self):
        if self.fh:
            self.fh.close()
            self.fh = None


def load_cursor(path):
    try:
        with open(path) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def save_cursor(path, cur):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(str(cur))
    os.replace(tmp, path)


async def run(args):
    try:
        import websockets  # optional dependency
    except ImportError:
        raise SystemExit('Bluesky support needs websockets: pip install "cascadekit[bluesky]"')

    os.makedirs(args.out, exist_ok=True)
    cursor_path = os.path.join(args.out, "cursor.txt")
    writer = HourlyWriter(args.out)
    text_langs = None if args.text_langs == "all" else set(args.text_langs.split(","))
    colls = [POST, REPOST] + ([FOLLOW] if args.follows else [])
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(s, stop.set)
        except NotImplementedError:  # Windows
            pass

    counts, last_report, last_save, backoff = {}, time.time(), time.time(), 1
    cursor = load_cursor(cursor_path)

    while not stop.is_set():
        params = [("wantedCollections", c) for c in colls]
        if cursor:
            params.append(("cursor", str(cursor - 5_000_000)))  # rewind 5 s to avoid gaps
        url = args.endpoint + "?" + urlencode(params)
        try:
            async with websockets.connect(url, max_size=2**22, ping_interval=30) as ws:
                print(f"[{datetime.now():%H:%M:%S}] connected (cursor={cursor})", flush=True)
                backoff = 1
                while not stop.is_set():
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=60)
                    except asyncio.TimeoutError:
                        continue
                    ev = json.loads(raw)
                    cursor = ev.get("time_us") or cursor
                    rec = slim(ev, text_langs)
                    if rec:
                        writer.write(rec)
                        counts[rec["t"]] = counts.get(rec["t"], 0) + 1
                    now = time.time()
                    if now - last_save > 5:
                        save_cursor(cursor_path, cursor)
                        last_save = now
                    if now - last_report > args.report_every:
                        mb = writer.bytes / 1e6
                        print(f"[{datetime.now():%H:%M:%S}] {counts}  ~{mb:.1f} MB uncompressed so far", flush=True)
                        last_report = now
        except (OSError, websockets.WebSocketException) as e:
            print(f"connection error: {e!r}; retrying in {backoff}s", flush=True)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 120)

    if cursor:
        save_cursor(cursor_path, cursor)
    writer.close()
    print("stopped cleanly", counts)


def main(argv=None):
    p = argparse.ArgumentParser(prog="cascadekit collect-bluesky", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default="data/bluesky")
    p.add_argument("--endpoint", default="wss://jetstream.atproto.tools/subscribe",
                   help="Jetstream websocket URL (Bluesky also runs official instances; see its docs)")
    p.add_argument("--text-langs", default="hi,ur,ks,en",
                   help="comma-separated language codes whose post text is kept, or 'all'")
    p.add_argument("--follows", action="store_true", help="also stream follow events")
    p.add_argument("--report-every", type=int, default=300, help="seconds between progress lines")
    asyncio.run(run(p.parse_args(argv)))


if __name__ == "__main__":
    main()
