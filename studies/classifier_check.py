#!/usr/bin/env python3
"""
Does the choice of classifier matter? The evasion comparison repeated with three models.

    python studies/classifier_check.py --background sim --out results/classifiers/simulated.csv
    python studies/classifier_check.py --background ../data/cascades/pheme.jsonl.gz --out results/classifiers/pheme.csv

Models: the paper's random forest (150 trees), histogram gradient boosting (200 iterations)
and L2 logistic regression on standardised features (missing values imputed with the
median). All features, 5-fold CV with each campaign in one fold, as in simulation_study.py,
plus a detector trained on naive campaigns only. "sim" uses the main simulation study's
corpora (simulate_corpus); a cascade file uses the semi-synthetic procedure of
semi_synthetic.py, which adds the empirical mimic.
"""
import os

# One OpenMP thread per process, set before scikit-learn loads: gradient boosting sums
# histograms across threads, and the order of those sums (hence its scores) otherwise varies.
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse  # noqa: E402
import csv  # noqa: E402
import math  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import semi_synthetic as semi
from simulation_study import N_CAMPAIGNS, SETS, STRATEGIES, forest, metrics

from cascadekit import SimConfig, extract_all, simulate_corpus

PIS = (0.10, 0.30)
SIM_STRATEGIES = ["naive", "organic timing + structure", "full mimic + rotation", "control: embedded accounts"]
REAL_STRATEGIES = SIM_STRATEGIES[:3] + ["empirical mimic + rotation", SIM_STRATEGIES[3]]
COLS = ["background", "strategy", "pi", "seed", "model", "trained_on", "auroc", "tpr_at_1pct_fpr", "auprc"]


def matrix(rows):
    """All features, with NaN kept (each model handles it in its own way)."""
    return [[float(r[c]) for c in SETS["all"]] for r in rows]


def model(name, seed):
    if name == "random forest":
        return forest(seed, 150)
    if name == "gradient boosting":
        return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, random_state=seed)
    return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                         LogisticRegression(C=1.0, max_iter=5000))


MODELS = ["random forest", "gradient boosting", "logistic regression"]


def fit(name, seed, X, y):
    if name == "random forest":                     # the forest takes the paper's -999 sentinel
        X = [[-999.0 if math.isnan(v) else v for v in row] for row in X]
    return model(name, seed).fit(X, y)


def proba(clf, name, X):
    if name == "random forest":
        X = [[-999.0 if math.isnan(v) else v for v in row] for row in X]
    return clf.predict_proba(X)[:, 1]


def corpus_for(bg, strategy, pi, seed):
    if bg == "sim":
        return simulate_corpus(400, 400, (pi, pi), N_CAMPAIGNS, SimConfig(**STRATEGIES[strategy]), seed)
    return semi.make_corpus(strategy, pi, 400, seed)


def run_task(t):
    bg, strategy, pi, seed = t["bg"], t["strategy"], t["pi"], t["seed"]
    corpus = corpus_for(bg, strategy, pi, seed)
    y = [1 if c.label == "amplified" else 0 for c in corpus]
    groups = [f"c{c.meta['campaign']}" if y[i] else f"o{i}" for i, c in enumerate(corpus)]
    X = matrix(extract_all(corpus))
    train = corpus_for(bg, "naive", pi, seed + 10_000)
    tX, ty = matrix(extract_all(train)), [1 if c.label == "amplified" else 0 for c in train]
    out = []
    cv = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed).split(X, y, groups))
    for m in MODELS:
        p = [0.0] * len(y)
        for tr, te in cv:
            clf = fit(m, seed, [X[i] for i in tr], [y[i] for i in tr])
            for i, s in zip(te, proba(clf, m, [X[i] for i in te])):
                p[i] = float(s)
        base = {"background": t["name"], "strategy": strategy, "pi": pi, "seed": seed, "model": m}
        out.append({**base, "trained_on": "same strategy (CV)", **metrics(y, p)})
        clf = fit(m, seed, tX, ty)
        out.append({**base, "trained_on": "naive only", **metrics(y, proba(clf, m, X))})
    return out


def _init(bg, max_size):
    if bg != "sim":
        semi._init(bg, max_size)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--background", required=True, help='"sim" or a cascade file')
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", help="background name in the output (default: from --background)")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--max-size", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    a = ap.parse_args()
    name = a.name or ("simulated" if a.background == "sim" else os.path.basename(a.background).split(".")[0])
    strategies = SIM_STRATEGIES if a.background == "sim" else REAL_STRATEGIES
    tasks = [{"bg": a.background, "name": name, "strategy": s, "pi": pi, "seed": seed}
             for seed in range(a.seeds) for s in strategies for pi in PIS]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    t0 = time.time()
    print(f"{name}: {len(tasks)} tasks", flush=True)
    with open(a.out, "w", newline="") as fh, Pool(a.workers, initializer=_init,
                                                  initargs=(a.background, a.max_size)) as pool:
        w = csv.DictWriter(fh, COLS)
        w.writeheader()
        for i, rows in enumerate(pool.imap_unordered(run_task, tasks), start=1):
            w.writerows(rows)
            fh.flush()
            if i % 10 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} tasks, {time.time() - t0:.0f}s", flush=True)
    print("done ->", a.out)


if __name__ == "__main__":
    main()
