#!/usr/bin/env python3
"""
Build cascade files from two small public datasets, for the semi-synthetic study.

    python studies/real_data.py pheme --raw ../data/raw/pheme/all-rnr-annotated-threads --out ../data/cascades/pheme.jsonl.gz
    python studies/real_data.py higgs --raw ../data/raw/higgs/higgs-activity_time.txt.gz --out ../data/cascades/higgs.jsonl.gz

PHEME (Kochkina et al. 2018, CC BY 4.0; figshare 6392078): 6,425 Twitter conversation
threads around nine breaking-news events. A thread is a source tweet and its replies;
each reply's parent is the tweet it answers (``in_reply_to_status_id``), so the tree is
exact. These are reply trees, not retweet trees.

Higgs (De Domenico et al. 2013; SNAP): retweets about the Higgs-boson announcement,
1-7 July 2012, as (user A, user B, time) edges where A retweeted B. Tweet ids are not
released, so cascades are rebuilt at user level: a retweet of B joins the cascade B most
recently joined as a retweeter, if that was within ``--window`` hours, and otherwise
B's own cascade (B as the root). The root's time is unknown and is set to its first
retweet. This is a heuristic reconstruction, not an exact tree.

Account and node ids are replaced by salted hashes; no text is kept.
"""
import argparse
import glob
import gzip
import json
import os
import sys
from email.utils import parsedate_to_datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from cascadekit import Cascade, Node, cascades_to_jsonl  # noqa: E402


def _ts(created_at):
    return parsedate_to_datetime(created_at).timestamp()


def build_pheme(raw, min_size):
    out = []
    for sdir in sorted(glob.glob(os.path.join(raw, "*", "*", "*", "source-tweets"))):
        tdir = os.path.dirname(sdir)
        event = os.path.basename(os.path.dirname(os.path.dirname(tdir))).replace("-all-rnr-threads", "")
        kind = os.path.basename(os.path.dirname(tdir))                     # rumours / non-rumours
        src_files = glob.glob(os.path.join(sdir, "*.json"))
        if not src_files:
            continue
        with open(src_files[0], encoding="utf-8") as fh:
            src = json.load(fh)
        root = Node(str(src["id"]), str(src["user"]["id"]), _ts(src["created_at"]))
        nodes = [root]
        for f in glob.glob(os.path.join(tdir, "reactions", "*.json")):
            with open(f, encoding="utf-8") as fh:
                r = json.load(fh)
            if str(r["id"]) == root.id:
                continue
            par = r.get("in_reply_to_status_id")
            nodes.append(Node(str(r["id"]), str(r["user"]["id"]), _ts(r["created_at"]),
                              str(par) if par else root.id, "reply"))
        if len(nodes) - 1 < min_size:
            continue
        out.append(Cascade(root.id, nodes, platform="twitter-replies", label="organic",
                           meta={"dataset": "pheme", "event": event, "rumour": kind == "rumours"}))
    return out


def build_higgs(raw, min_size, window_h):
    edges = []
    with gzip.open(raw, "rt") as fh:
        for line in fh:
            a, b, t, kind = line.split()
            if kind == "RT" and a != b:
                edges.append((int(t), a, b))
    edges.sort()
    cascades = {}          # root user -> {"nodes": [...], "members": set()}
    last_join = {}         # user -> (root user, node id, time) of their latest retweet
    for k, (t, a, b) in enumerate(edges):
        lj = last_join.get(b)
        if lj and t - lj[2] <= window_h * 3600:
            root, parent = lj[0], lj[1]
        else:
            root = b
            parent = f"r{b}"
        c = cascades.setdefault(root, {"nodes": [Node(f"r{root}", root, None)], "members": {root}})
        if a in c["members"]:
            continue
        nid = f"e{k}"
        c["nodes"].append(Node(nid, a, float(t), parent, "via"))
        c["members"].add(a)
        last_join[a] = (root, nid, t)
    out = []
    for root, c in cascades.items():
        nodes = c["nodes"]
        if len(nodes) - 1 < min_size:
            continue
        nodes[0].ts = min(n.ts for n in nodes[1:])
        out.append(Cascade(f"r{root}", nodes, platform="twitter-retweets", label="organic",
                           meta={"dataset": "higgs", "reconstruction": f"user-level, {window_h} h window"}))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset", choices=["pheme", "higgs"])
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-size", type=int, default=10, help="drop cascades with fewer reshares (default 10)")
    ap.add_argument("--window", type=float, default=24.0, help="Higgs: hours a retweeter stays in a cascade")
    ap.add_argument("--salt", default="cascade-real-data")
    a = ap.parse_args()
    cs = build_pheme(a.raw, a.min_size) if a.dataset == "pheme" else build_higgs(a.raw, a.min_size, a.window)
    cs = [c.anonymised(a.salt) for c in cs]
    n = cascades_to_jsonl(cs, a.out)
    sizes = sorted(c.size for c in cs)
    print(f"{a.dataset}: {n} cascades with >= {a.min_size} reshares; size median {sizes[len(sizes)//2]}, "
          f"max {sizes[-1]}, total reshares {sum(sizes)} -> {a.out}")


if __name__ == "__main__":
    main()
