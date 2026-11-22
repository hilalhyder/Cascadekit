#!/usr/bin/env python3
"""
Two follow-up checks quoted in the simulation-study write-up.

    python studies/followup_checks.py > results/study/followup_checks.txt

1. Size effect: at a fixed 10% amplified share, are larger cascades easier to classify
   from structure and timing? (Explains why detection improves with organic virality.)
2. What detectors pick up under evasion: medians of key features for organic and amplified
   cascades under the mimic strategies.
"""
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sklearn.metrics import roc_auc_score  # noqa: E402

from cascadekit import SimConfig, extract_all, simulate_corpus  # noqa: E402
from simulation_study import SETS, STRATEGIES, matrix, out_of_fold  # noqa: E402


def size_effect(seeds=(0, 1, 2), pi=0.10):
    print(f"1. Size effect (naive, pi = {pi}, structure + timing features)")
    res = {"small": [], "large": []}
    for seed in seeds:
        corpus = simulate_corpus(400, 400, (pi, pi), 10, SimConfig(), seed)
        rows = extract_all(corpus)
        y = [1 if c.label == "amplified" else 0 for c in corpus]
        groups = [f"c{c.meta['campaign']}" if c.label == "amplified" else f"o{i}" for i, c in enumerate(corpus)]
        p, _ = out_of_fold(matrix(rows, SETS["structure + timing"]), y, groups, seed, 150)
        n_org = [c.meta["n_organic"] for c in corpus]
        med = st.median(n_org)
        for name, keep in (("small", lambda n: n < med), ("large", lambda n: n >= med)):
            idx = [i for i, n in enumerate(n_org) if keep(n)]
            res[name].append(roc_auc_score([y[i] for i in idx], [p[i] for i in idx]))
        print(f"   seed {seed}: median organic size {med:g}; AUROC below median {res['small'][-1]:.3f}, "
              f"at or above {res['large'][-1]:.3f}")
    print(f"   mean: below median {st.fmean(res['small']):.3f}, at or above {st.fmean(res['large']):.3f}\n")


def medians(name, feats, pi=0.30, seed=0):
    rows = extract_all(simulate_corpus(300, 300, (pi, pi), 10, SimConfig(**STRATEGIES[name]), seed))
    print(f"   {name} (pi = {pi})")
    for f in feats:
        org = [r[f] for r in rows if r["label"] == "organic" and r[f] == r[f]]
        amp = [r[f] for r in rows if r["label"] == "amplified" and r[f] == r[f]]
        print(f"      {f:24s} organic median {st.median(org):10.3f}   amplified median {st.median(amp):10.3f}")


if __name__ == "__main__":
    size_effect()
    print("2. Feature medians under evasion")
    medians("organic timing + structure", ["root_share", "mean_depth", "leaf_share", "mean_offspring",
                                           "duration_s", "reuse_overlap_max", "reuse_shared_top5"])
    medians("full mimic + rotation", ["reuse_overlap_max", "reuse_shared_top5"])
