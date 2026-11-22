"""
Quickstart: simulate a labelled corpus, compute the cascade fingerprint, and measure
how well each feature group separates organic from amplified cascades.

    pip install "cascadekit[dev]"        # adds scikit-learn and matplotlib
    python examples/quickstart.py --out results/

Writes:
  results/features.csv          fingerprint of every cascade
  results/auc_by_group.csv      cross-validated AUC per feature group, per difficulty, per prefix
  results/time_depth.png        one organic and one amplified cascade, side by side
"""
import argparse
import csv
import math
import os

from cascadekit import FEATURE_GROUPS, SimConfig, extract_all, simulate_corpus, write_csv


def auc_cv(rows, cols, seed=0):
    """5-fold cross-validated ROC AUC of a random forest on the given columns."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    X = [[(0.0 if (isinstance(r[c], float) and math.isnan(r[c])) else r[c]) for c in cols] for r in rows]
    y = [1 if r["label"] == "amplified" else 0 for r in rows]
    clf = RandomForestClassifier(n_estimators=300, min_samples_leaf=2, random_state=seed, n_jobs=-1)
    cv = StratifiedKFold(5, shuffle=True, random_state=seed)
    return cross_val_score(clf, X, y, cv=cv, scoring="roc_auc").mean()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results")
    ap.add_argument("--n", type=int, default=400, help="cascades per class")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    settings = {"easy (pi 0.2-0.6)": (0.2, 0.6), "hard (pi 0.05-0.15)": (0.05, 0.15)}
    groups = dict(FEATURE_GROUPS)
    groups["structure + timing (no reuse)"] = FEATURE_GROUPS["shape"] + FEATURE_GROUPS["branching"] + FEATURE_GROUPS["timing"]
    groups["all"] = [f for g in FEATURE_GROUPS.values() for f in g]

    results = []
    for name, pr in settings.items():
        corpus = simulate_corpus(a.n, a.n, pi_range=pr, seed=a.seed)
        for k in (None, 20, 50):
            rows = extract_all(corpus, prefix_k=k)
            if name.startswith("easy") and k is None:
                write_csv(rows, os.path.join(a.out, "features.csv"))
            for g, cols in groups.items():
                auc = auc_cv(rows, cols, a.seed)
                results.append({"setting": name, "prefix": k or "full", "features": g, "auc": round(auc, 3)})
                print(f"{name:22s} prefix={str(k or 'full'):5s} {g:32s} AUC={auc:.3f}")

    with open(os.path.join(a.out, "auc_by_group.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(results[0]))
        w.writeheader()
        w.writerows(results)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from cascadekit.viz import plot_time_depth
        corpus = simulate_corpus(60, 60, pi_range=(0.3, 0.4), seed=a.seed)
        org = next(c for c in corpus if c.label == "organic" and 60 <= c.size <= 150)
        amp = next(c for c in corpus if c.label == "amplified" and 60 <= c.size <= 150)
        amp_accts = {n.account for n in amp.nodes if str(n.id).startswith("m")}
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
        plot_time_depth(org, axes[0], title=f"Organic: {org.size} reshares")
        plot_time_depth(amp, axes[1], highlight_accounts=amp_accts,
                        title=f"Amplified (pi={amp.meta['pi']:.2f}): {amp.size} reshares; red = amplifier accounts")
        fig.tight_layout()
        fig.savefig(os.path.join(a.out, "time_depth.png"), dpi=200)
        print("figure ->", os.path.join(a.out, "time_depth.png"))
    except ImportError:
        print("matplotlib not installed; skipping figure")


if __name__ == "__main__":
    main()
