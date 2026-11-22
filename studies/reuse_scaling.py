#!/usr/bin/env python3
"""
Raw account-reuse counts against rarity-weighted overlap as the corpus grows.

    python studies/reuse_scaling.py --out results/reuse_scaling

Balanced corpora (half amplified, naive campaigns, pi = 10%) of increasing size. Each campaign
keeps 20 cascades, so only the size of the corpus changes, not the campaigns themselves.
Raw features are the 0.2.0 definitions: the mean number of other cascades each account appears
in, and the share of accounts seen in five or more other cascades.
"""
import argparse
import csv
import os
import statistics as st
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cascadekit import FEATURE_GROUPS, SimConfig, extract_all, simulate_corpus  # noqa: E402
from cascadekit.features import account_counts  # noqa: E402
from simulation_study import matrix, metrics, out_of_fold  # noqa: E402

SIZES = [400, 1000, 2000, 5000, 10000]          # total cascades, half amplified
SEEDS = range(5)
SETS = {"raw counts": ["reuse_mean", "reuse_share_5plus", "distinct_account_share"],
        "rarity-weighted overlap": FEATURE_GROUPS["reuse"]}


def raw_reuse(corpus, rows):
    cnt = account_counts(corpus)
    for c, r in zip(corpus, rows):
        others = [cnt[a] - 1 for a in {n.account for n in c.nodes[1:]}]
        r["reuse_mean"] = st.fmean(others)
        r["reuse_share_5plus"] = sum(x >= 5 for x in others) / len(others)


def run(args):
    size, seed = args
    half = size // 2
    corpus = simulate_corpus(half, half, (0.1, 0.1), half // 20, SimConfig(), seed)
    rows = extract_all(corpus)
    raw_reuse(corpus, rows)
    y = [1 if c.label == "amplified" else 0 for c in corpus]
    groups = [f"c{c.meta['campaign']}" if c.label == "amplified" else f"o{i}" for i, c in enumerate(corpus)]
    out = []
    for name, cols in SETS.items():
        p, _ = out_of_fold(matrix(rows, cols), y, groups, seed, 150)
        out.append({"n_cascades": size, "seed": seed, "features": name, **metrics(y, p)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/reuse_scaling")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tasks = sorted(((s, k) for s in SIZES for k in SEEDS), key=lambda t: -t[0])
    with Pool(a.workers) as p:
        res = [r for rs in p.imap_unordered(run, tasks) for r in rs]
    res.sort(key=lambda r: (r["features"], r["n_cascades"], r["seed"]))
    with open(os.path.join(a.out, "results.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, list(res[0]))
        w.writeheader()
        w.writerows(res)
    for name in SETS:
        print(name, " ".join(f"{s}:{st.fmean(r['auroc'] for r in res if r['features'] == name and r['n_cascades'] == s):.3f}"
                             for s in SIZES))


if __name__ == "__main__":
    main()
