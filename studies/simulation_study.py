#!/usr/bin/env python3
"""
Simulation study: how early and how faintly can coordinated amplification be detected
from diffusion-tree structure, timing and account reuse, and what does evading
detection cost the attacker?

    pip install "cascadekit[dev]"
    python studies/simulation_study.py --out results/study            # full run
    python studies/simulation_study.py --out results/quick --quick    # 1-seed smoke run
    python studies/make_figures.py --results results/study

Experiments (column "exp" in results.csv):
  share        amplified share pi; also early views (first k reshares) for four pi values
  virality     organic mean offspring m
  strategy     five evasion strategies; detector retrained, and detector trained on naive only
  pool         account rotation: pool size per campaign under the full-mimic strategy
  start delay  how late the naive campaign starts
  base rate    share of cascades in the corpus that are amplified
  sensitivity  one organic or amplification parameter moved from its default, for three settings

Protocol: random forest (150 trees) on cascadekit features; 5-fold cross-validation in which every
cascade of a campaign stays in one fold; AUROC, recall at 1% false-positive rate and
average precision from pooled out-of-fold scores; several seeds per setting.

Outputs: results.csv, costs.csv (what each strategy costs the attacker), importances.csv.
"""
import argparse
import csv
import math
import os
import statistics
import time
from multiprocessing import Pool

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedGroupKFold

from cascadekit import FEATURE_GROUPS, FEATURES, SimConfig, __version__, extract_all, simulate_corpus

SETS = {
    "size only": ["size"],
    "shape": FEATURE_GROUPS["shape"],
    "branching": FEATURE_GROUPS["branching"],
    "timing": FEATURE_GROUPS["timing"],
    "reuse": FEATURE_GROUPS["reuse"],
    "structure + timing": FEATURE_GROUPS["shape"] + FEATURE_GROUPS["branching"] + FEATURE_GROUPS["timing"],
    "all": FEATURES,
}
MAIN_SETS = list(SETS)
LIGHT_SETS = ["structure + timing", "reuse", "all"]

STRATEGIES = {
    "naive": {},
    "random timing": {"amp_timing": "poisson"},
    "organic timing": {"amp_timing": "mimic"},
    "organic timing + structure": {"amp_timing": "mimic", "amp_attach": "mimic"},
    "full mimic + rotation": {"amp_timing": "mimic", "amp_attach": "mimic",
                              "rotate_accounts": True, "pool_size": 5000},
    # Negative control: the tree is purely organic; campaign accounts only replace some accounts.
    "control: embedded accounts": {"amp_attach": "embedded"},
}

PIS = [0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.60]
EARLY_PIS = [0.05, 0.10, 0.20, 0.40]
PREFIXES = [5, 10, 20, 50, 100]
MS = [0.5, 0.65, 0.8, 0.9, 0.95]
POOLS = [50, 150, 500, 2000, 10000]
START_DELAYS = [300, 3600, 21600]
# Sensitivity: each parameter moved below and above its default (root_mean 6, delay_sigma 1.3,
# amp_followers_mean 0.15, activity_exponent 0.7), one at a time.
SENSITIVITY = {"root_mean": [3.0, 12.0], "delay_sigma": [0.8, 1.8],
               "amp_followers_mean": [0.0, 0.5], "activity_exponent": [0.5, 0.9]}
SENS_SETTINGS = [("naive", 0.10), ("organic timing + structure", 0.10), ("full mimic + rotation", 0.30)]
N_CAMPAIGNS = 10

RESULT_COLS = ["exp", "strategy", "pi", "pi_realized", "m", "pool_size", "start_delay_s", "n_org", "n_amp",
               "view", "features", "trained_on", "seed", "auroc", "tpr_at_1pct_fpr", "auprc", "param", "value"]
COST_COLS = ["exp", "strategy", "pi", "pool_size", "seed", "amp_t90_min", "amp_first_hour_share",
             "accounts_per_campaign", "cascades_per_account", "first_hour_reshares_amplified",
             "first_hour_reshares_organic"]
IMP_COLS = ["exp", "strategy", "pi", "seed", "features", "feature", "importance"]


def matrix(rows, cols):
    return [[-999.0 if (isinstance(r[c], float) and math.isnan(r[c])) else r[c] for c in cols] for r in rows]


def forest(seed, trees):
    return RandomForestClassifier(n_estimators=trees, min_samples_leaf=2, random_state=seed, n_jobs=1)


def metrics(y, p):
    fpr, tpr, _ = roc_curve(y, p)
    return {"auroc": round(roc_auc_score(y, p), 4),
            "tpr_at_1pct_fpr": round(float(max(t for f, t in zip(fpr, tpr) if f <= 0.01)), 4),
            "auprc": round(average_precision_score(y, p), 4)}


def out_of_fold(X, y, groups, seed, trees):
    """Pooled out-of-fold scores and mean feature importances; campaigns never straddle folds."""
    p = [0.0] * len(y)
    imps = []
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    for tr, te in cv.split(X, y, groups):
        clf = forest(seed, trees).fit([X[i] for i in tr], [y[i] for i in tr])
        for i, s in zip(te, clf.predict_proba([X[i] for i in te])[:, 1]):
            p[i] = float(s)
        imps.append(clf.feature_importances_)
    return p, [float(statistics.fmean(col)) for col in zip(*imps)]


def attacker_costs(corpus):
    """What the campaign pays: how slowly its reshares land and how many accounts it burns."""
    t90, first_hour, per_campaign, acct_cascades = [], [], {}, {}
    fh_amp, fh_org = [], []
    for c in corpus:
        t0 = c.nodes[0].ts
        in_hour = sum(1 for n in c.nodes[1:] if n.ts - t0 <= 3600)
        if c.label != "amplified":
            fh_org.append(in_hour)
            continue
        fh_amp.append(in_hour)
        amp = [n for n in c.nodes if n.id.startswith("m")]
        rel = sorted(n.ts - t0 for n in amp)
        t90.append(rel[max(0, math.ceil(0.9 * len(rel)) - 1)] / 60)
        first_hour.append(sum(1 for x in rel if x <= 3600) / len(rel))
        per_campaign.setdefault(c.meta["campaign"], set()).update(n.account for n in amp)
        for a in {n.account for n in amp}:
            acct_cascades[a] = acct_cascades.get(a, 0) + 1
    return {"amp_t90_min": round(statistics.median(t90), 1),
            "amp_first_hour_share": round(statistics.fmean(first_hour), 3),
            "accounts_per_campaign": round(statistics.fmean(len(s) for s in per_campaign.values()), 1),
            "cascades_per_account": round(statistics.fmean(acct_cascades.values()), 2),
            "first_hour_reshares_amplified": round(statistics.fmean(fh_amp), 1),
            "first_hour_reshares_organic": round(statistics.fmean(fh_org), 1)}


def run_task(t):
    cfg = SimConfig(**t["cfg"])
    corpus = simulate_corpus(t["n_org"], t["n_amp"], (t["pi"], t["pi"]), N_CAMPAIGNS, cfg, t["seed"])
    y = [1 if c.label == "amplified" else 0 for c in corpus]
    groups = [f"c{c.meta['campaign']}" if c.label == "amplified" else f"o{i}" for i, c in enumerate(corpus)]
    base = {"exp": t["exp"], "strategy": t["strategy"], "pi": t["pi"],
            "pi_realized": round(statistics.fmean(c.meta["pi"] for c in corpus if c.label == "amplified"), 4),
            "m": cfg.mean_offspring, "pool_size": cfg.pool_size, "start_delay_s": cfg.amp_start_median_s,
            "n_org": t["n_org"], "n_amp": t["n_amp"], "seed": t["seed"], "trained_on": "same strategy (CV)",
            "param": t.get("param", ""), "value": t.get("value", "")}
    results, costs, imps = [], [], []
    full_rows = None
    for k in t["views"]:
        rows = extract_all(corpus, prefix_k=k)
        if k is None:
            full_rows = rows
        for s in (t["sets"] if k is None else t["early_sets"]):
            p, imp = out_of_fold(matrix(rows, SETS[s]), y, groups, t["seed"], t["trees"])
            results.append({**base, "view": "full" if k is None else k, "features": s, **metrics(y, p)})
            if t.get("importances") and s in ("all", "structure + timing") and k is None:
                imps += [{"exp": t["exp"], "strategy": t["strategy"], "pi": t["pi"], "seed": t["seed"],
                          "features": s, "feature": f, "importance": round(v, 5)}
                         for f, v in zip(SETS[s], imp)]
    if t.get("transfer"):   # detector trained before the attack: naive campaigns only
        train = simulate_corpus(t["n_org"], t["n_amp"], (t["pi"], t["pi"]), N_CAMPAIGNS, SimConfig(),
                                t["seed"] + 10_000)
        tr_rows = extract_all(train)
        ty = [1 if c.label == "amplified" else 0 for c in train]
        for s in LIGHT_SETS:
            clf = forest(t["seed"], t["trees"]).fit(matrix(tr_rows, SETS[s]), ty)
            p = clf.predict_proba(matrix(full_rows, SETS[s]))[:, 1]
            results.append({**base, "view": "full", "features": s, "trained_on": "naive only", **metrics(y, p)})
    if t.get("costs"):
        costs.append({"exp": t["exp"], "strategy": t["strategy"], "pi": t["pi"], "pool_size": cfg.pool_size,
                      "seed": t["seed"], **attacker_costs(corpus)})
    return results, costs, imps


def build_tasks(quick, n_seeds=10):
    seeds = [0] if quick else list(range(n_seeds))
    n = 100 if quick else 400
    trees = 100 if quick else 150
    tasks = []

    def add(exp, strategy="naive", cfg=None, pi=0.2, n_org=n, n_amp=n, views=(None,), sets=MAIN_SETS,
            early_sets=LIGHT_SETS, seeds_=seeds, **flags):
        for s in seeds_:
            tasks.append({"exp": exp, "strategy": strategy, "cfg": cfg or {}, "pi": pi, "n_org": n_org,
                          "n_amp": n_amp, "views": list(views), "sets": sets, "early_sets": early_sets,
                          "seed": s, "trees": trees, **flags})

    for pi in PIS:
        views = [None] + (PREFIXES if pi in EARLY_PIS else [])
        add("share", pi=pi, views=views, importances=pi in (0.10, 0.30))
    for m in MS:
        for pi in (0.10, 0.30):
            add("virality", cfg={"mean_offspring": m}, pi=pi, sets=["size only"] + LIGHT_SETS)
    for name, kw in STRATEGIES.items():
        for pi in (0.10, 0.30):
            add("strategy", strategy=name, cfg=kw, pi=pi, views=[None, 20], transfer=True, costs=True,
                importances=True)
    for pool in POOLS:
        kw = dict(STRATEGIES["full mimic + rotation"], pool_size=pool)
        add("pool", strategy="full mimic + rotation", cfg=kw, pi=0.20, sets=["reuse", "all"], costs=True)
    for d in START_DELAYS:
        add("start delay", cfg={"amp_start_median_s": d}, pi=0.20, views=[None, 20], sets=LIGHT_SETS)
    n_amp = 50 if quick else 200
    for mult in (1, 9, 49):                                  # amplified = 50%, 10%, 2% of cascades
        for name in ("naive", "organic timing + structure", "full mimic + rotation"):
            add("base rate", strategy=name, cfg=STRATEGIES[name], pi=0.10, n_org=n_amp * mult, n_amp=n_amp,
                sets=LIGHT_SETS)
    for par, values in SENSITIVITY.items():
        for v in values:
            for name, pi in SENS_SETTINGS:
                add("sensitivity", strategy=name, cfg=dict(STRATEGIES[name], **{par: v}), pi=pi,
                    sets=LIGHT_SETS, param=par, value=v)
    return tasks


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="results/study")
    ap.add_argument("--quick", action="store_true", help="1 seed, small corpora (smoke test)")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--seeds", type=int, default=10, help="seeds per setting (default 10)")
    ap.add_argument("--only", help="run only this experiment (for example: strategy)")
    ap.add_argument("--strategy", help="run only this attacker strategy (for example: \"full mimic + rotation\")")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tasks = [t for t in build_tasks(a.quick, a.seeds) if (not a.only or t["exp"] == a.only)
             and (not a.strategy or t["strategy"] == a.strategy)]
    tasks.sort(key=lambda t: -(t["n_org"] + t["n_amp"]))        # biggest first
    files = {name: open(os.path.join(a.out, name), "w", newline="") for name in
             ("results.csv", "costs.csv", "importances.csv")}
    writers = {"results.csv": csv.DictWriter(files["results.csv"], RESULT_COLS),
               "costs.csv": csv.DictWriter(files["costs.csv"], COST_COLS),
               "importances.csv": csv.DictWriter(files["importances.csv"], IMP_COLS)}
    for w in writers.values():
        w.writeheader()
    t0 = time.time()
    print(f"cascadekit {__version__}: {len(tasks)} tasks on {a.workers} workers", flush=True)
    with Pool(a.workers) as pool:
        for i, (res, costs, imps) in enumerate(pool.imap_unordered(run_task, tasks), start=1):
            writers["results.csv"].writerows(res)
            writers["costs.csv"].writerows(costs)
            writers["importances.csv"].writerows(imps)
            for f in files.values():
                f.flush()
            if i % 10 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} tasks, {time.time() - t0:.0f}s", flush=True)
    for f in files.values():
        f.close()
    print("done ->", a.out)


if __name__ == "__main__":
    main()
