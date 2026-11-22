#!/usr/bin/env python3
"""
Telegram public-channel collector (cascadekit collect-telegram).

Crawls public channels from a seed list, records every message with its
forward header (which channel and post it was forwarded from), and
snowballs to new channels found through forwards, keeping only channels whose
text is mostly in Devanagari or Arabic script (Hindi, Urdu, Kashmiri).

Setup (once):
  1. Get api_id and api_hash at https://my.telegram.org  (use a dedicated number).
  2. pip install "cascadekit[telegram]"
  3. Put channel usernames (without @), one per line, in seeds.txt

Run:
  export TG_API_ID=12345 TG_API_HASH=abcdef...
  cascadekit collect-telegram --seeds seeds.txt --since 2026-06-01 --out data/telegram

Output:
  <out>/channels.jsonl            one line per channel crawled (id, username, title, script share)
  <out>/messages/<chan_id>.jsonl.gz
      {"chan","msg","date","views","forwards","replies","text",
       "fwd_chan","fwd_post","fwd_date","fwd_user"}
  fwd_chan/fwd_post identify the ORIGINAL post; Telegram does not say which
  intermediate channel a forward came through, so parents are inferred later.
Only public channels are read. Never join private groups.
"""
import argparse
import asyncio
import gzip
import json
import os
import random
import re
from datetime import datetime, timezone

try:  # optional dependency: pip install cascadekit[telegram]
    from telethon import TelegramClient
    from telethon.errors import (ChannelPrivateError, FloodWaitError,
                                 UsernameInvalidError, UsernameNotOccupiedError)
    from telethon.tl.types import Channel, PeerChannel, PeerUser
except ImportError:  # pragma: no cover
    TelegramClient = None

DEVANAGARI = re.compile(r"[ऀ-ॿ]")
ARABIC = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")
LETTER = re.compile(r"\w")


def indic_share(texts):
    """Fraction of letters that are Devanagari or Arabic-script."""
    s = " ".join(t for t in texts if t)
    letters = len(LETTER.findall(s))
    if letters == 0:
        return 0.0
    return (len(DEVANAGARI.findall(s)) + len(ARABIC.findall(s))) / letters


def fwd_fields(msg):
    f = msg.fwd_from
    if not f:
        return {}
    out = {"fwd_date": f.date.isoformat() if f.date else None, "fwd_post": f.channel_post}
    if isinstance(f.from_id, PeerChannel):
        out["fwd_chan"] = f.from_id.channel_id
    elif isinstance(f.from_id, PeerUser):
        out["fwd_user"] = f.from_id.user_id  # forwarded from a person; keep id only for hashing later
    return out


async def crawl_channel(client, ref, since, out_dir, min_share, probe=50):
    """Crawl one channel. Returns (channel_meta, set_of_new_channel_refs) or (None, set())."""
    try:
        ent = await client.get_entity(ref)
    except (ChannelPrivateError, UsernameInvalidError, UsernameNotOccupiedError, ValueError) as e:
        print(f"  skip {ref}: {type(e).__name__}")
        return None, set()
    if not isinstance(ent, Channel) or not ent.broadcast:
        print(f"  skip {ref}: not a broadcast channel")
        return None, set()

    # Probe language before a full crawl.
    probe_texts = [m.message async for m in client.iter_messages(ent, limit=probe)]
    share = indic_share(probe_texts)
    meta = {"id": ent.id, "username": ent.username, "title": ent.title,
            "indic_share": round(share, 3), "crawled_at": datetime.now(timezone.utc).isoformat()}
    if share < min_share:
        print(f"  skip {ent.username or ent.id}: Indic share {share:.2f}")
        meta["skipped"] = True
        return meta, set()

    found = set()
    path = os.path.join(out_dir, "messages", f"{ent.id}.jsonl.gz")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    n = 0
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        async for m in client.iter_messages(ent):
            if m.date < since:
                break
            rec = {"chan": ent.id, "msg": m.id, "date": m.date.isoformat(),
                   "views": m.views, "forwards": m.forwards,
                   "replies": m.replies.replies if m.replies else None,
                   "text": m.message}
            rec.update(fwd_fields(m))
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
            # Snowball: forwarded-from channel, if Telegram sent its entity with the message.
            fchat = getattr(m.forward, "chat", None) if m.forward else None
            if isinstance(fchat, Channel) and fchat.username:
                found.add(fchat.username)
    meta["messages"] = n
    print(f"  {ent.username or ent.id}: {n} messages, Indic share {share:.2f}, {len(found)} forward sources")
    return meta, found


async def main_async(a):
    since = datetime.fromisoformat(a.since).replace(tzinfo=timezone.utc)
    os.makedirs(a.out, exist_ok=True)
    chan_log = os.path.join(a.out, "channels.jsonl")
    done = set()
    if os.path.exists(chan_log):  # resume
        with open(chan_log) as f:
            for line in f:
                m = json.loads(line)
                done.update(x for x in (m.get("username"), str(m.get("id"))) if x)

    with open(a.seeds) as f:
        queue = [(s.strip().lstrip("@"), 0) for s in f if s.strip() and not s.startswith("#")]

    client = TelegramClient(a.session, int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"])
    await client.start()
    crawled = 0
    while queue and crawled < a.max_channels:
        ref, depth = queue.pop(0)
        if ref in done:
            continue
        done.add(ref)
        print(f"[{crawled + 1}] {ref} (depth {depth})")
        while True:
            try:
                meta, found = await crawl_channel(client, ref, since, a.out, a.min_share)
                break
            except FloodWaitError as e:
                print(f"  flood wait {e.seconds}s")
                await asyncio.sleep(e.seconds + 5)
        if meta:
            with open(chan_log, "a") as f:
                f.write(json.dumps(meta, ensure_ascii=False) + "\n")
            if not meta.get("skipped"):
                crawled += 1
                if depth < a.snowball:
                    queue.extend((u, depth + 1) for u in found if u not in done)
        await asyncio.sleep(random.uniform(2, 5))  # be polite
    await client.disconnect()
    print(f"done: {crawled} channels crawled, {len(queue)} still queued")


def main(argv=None):
    p = argparse.ArgumentParser(prog="cascadekit collect-telegram", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seeds", required=True)
    p.add_argument("--since", default="2026-01-01", help="ISO date; older messages are not fetched")
    p.add_argument("--out", default="data/telegram")
    p.add_argument("--snowball", type=int, default=2, help="how many forward-hops to follow from seeds")
    p.add_argument("--max-channels", type=int, default=500)
    p.add_argument("--min-share", type=float, default=0.3,
                   help="minimum share of Devanagari/Arabic-script letters to keep a channel")
    p.add_argument("--session", default="tg_research")
    a = p.parse_args(argv)
    if TelegramClient is None:
        raise SystemExit('Telegram support needs telethon: pip install "cascadekit[telegram]"')
    asyncio.run(main_async(a))


if __name__ == "__main__":
    main()
