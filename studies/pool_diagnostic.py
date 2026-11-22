#!/usr/bin/env python3
"""
Why is reuse AUROC not monotone in the rotation pool size (E4b)?

    python studies/pool_diagnostic.py > results/study/pool_diagnostic.txt

Full mimic + rotation at pi = 20%, the E4b setting. For each pool size, the medians of the
reuse features for organic and amplified cascades, the share of cascades whose account set
overlaps no other cascade at all, and each feature's AUROC on its own. A single-feature AUROC
below 0.5 means amplified cascades score LOWER than organic ones on that feature.
"""
import os
import statistics as st
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sklearn.metrics import roc_auc_score  # noqa: E402

from cascadekit import FEATURE_GROUPS, SimConfig, extract_all, simulate_corpus  # noqa: E402
from simulation_study import N_CAMPAIGNS, POOLS, STRATEGIES  # noqa: E402

FEATS = FEATURE_GROUPS["reuse"]
SEEDS = range(10)


def one(args):
    pool, seed = args
    cfg = SimConfig(**dict(STRATEGIES["full mimic + rotation"], pool_size=pool))
    corpus = simulate_corpus(400, 400, (0.2, 0.2), N_CAMPAIGNS, cfg, seed)
    rows = extract_all(corpus)
    out = {}
    for f in FEATS:
        org = [r[f] for r in rows if r["label"] == "organic"]
        amp = [r[f] for r in rows if r["label"] == "amplified"]
        y = [0] * len(org) + [1] * len(amp)
        out[f] = (st.median(org), st.median(amp), roc_auc_score(y, org + amp))
    org = [r for r in rows if r["label"] == "organic"]
    amp = [r for r in rows if r["label"] == "amplified"]
    out["zero"] = (sum(r["reuse_shared_max"] == 0 for r in org) / len(org),
                   sum(r["reuse_shared_max"] == 0 for r in amp) / len(amp))
    # share of each amplified cascade's distinct accounts that are campaign accounts
    out["amp_acct_share"] = st.fmean(
        len({n.account for n in c.nodes if n.id.startswith("m")}) / len({n.account for n in c.nodes[1:]})
        for c in corpus if c.label == "amplified")
    return pool, seed, out


def main():
    with Pool(min(14, os.cpu_count() or 1)) as p:
        res = p.map(one, [(pool, s) for pool in POOLS for s in SEEDS])
    print(f"Full mimic + rotation, pi = 20%, {len(SEEDS)} seeds; medians and single-feature AUROC (mean over seeds)\n")
    for pool in POOLS:
        rs = [o for q, _, o in res if q == pool]
        print(f"pool {pool:>6}")
        for f in FEATS:
            om, am, auc = (st.fmean(o[f][i] for o in rs) for i in range(3))
            print(f"   {f:24s} organic {om:7.3f}   amplified {am:7.3f}   AUROC alone {auc:.3f}")
        z_o, z_a = (st.fmean(o["zero"][i] for o in rs) for i in range(2))
        print(f"   overlaps no other cascade: organic {z_o:.1%}, amplified {z_a:.1%}")
        print(f"   campaign share of an amplified cascade's accounts: {st.fmean(o['amp_acct_share'] for o in rs):.1%}\n")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "study", "pool_diagnostic.csv")
    with open(out, "w", newline="") as fh:
        fh.write("pool_size,seed,feature,organic_median,amplified_median,auroc_alone\n")
        for pool, seed, o in res:
            for f in FEATS:
                fh.write(f"{pool},{seed},{f},{o[f][0]:.5f},{o[f][1]:.5f},{o[f][2]:.5f}\n")


if __name__ == "__main__":
    main()
