#!/usr/bin/env python3
"""
Semi-synthetic study: the simulation study's campaigns injected into real organic cascades.

    python studies/semi_synthetic.py --cascades ../data/cascades/pheme.jsonl.gz --out results/semi/pheme
    python studies/semi_synthetic.py --cascades ../data/cascades/higgs.jsonl.gz --out results/semi/higgs
    python studies/semi_synthetic.py --cascades sim:3500 --dataset simulated --out results/semi/simulated

Each run draws 2n distinct real cascades: n stay organic, and n receive a campaign with
share pi under one strategy (10 campaigns, each with its own reused account pool). Nothing
in the background is simulated (``empirical_samplers``): organic users who react to
amplifier reshares are drawn from the corpus, and how many reactions each reshare draws,
their delays and the delays of mimicking campaigns come from the host cascade itself.
Protocol as in simulation_study.py: random forest, 5-fold CV with each campaign in one
fold, AUROC / recall at 1% FPR / average precision. A seventh strategy, "empirical mimic +
rotation", copies the host cascade's own parent-child edges (parent depth and delay drawn
together, the parent chosen at that depth in proportion to its replies + 1). Experiments: "strategy" (seven strategies
at pi = 0.10 and 0.30, plus a detector trained on naive campaigns only) and "share" (pi
sweep for three campaigns) and "base rate" (200 amplified against 200 or 1,800 organic
cascades at pi = 0.10, for four campaigns; skipped when the corpus is too small).
"""
import argparse
import csv
import os
import random
import statistics
import time
from dataclasses import replace
from multiprocessing import Pool

from simulation_study import (LIGHT_SETS, MAIN_SETS, N_CAMPAIGNS, SETS, STRATEGIES, attacker_costs, forest,
                              matrix, metrics, out_of_fold)

from cascadekit import (SimConfig, __version__, cascades_from_jsonl, empirical_samplers, extract_all, inject,
                        simulate_corpus)

# The strongest attacker on real data: copy the platform's own edges (parent depth + delay).
STRATEGIES = dict(STRATEGIES, **{"empirical mimic + rotation": {"amp_attach": "empirical", "rotate_accounts": True,
                                                                 "pool_size": 5000}})

SHARE_PIS = [0.02, 0.05, 0.10, 0.20, 0.40]
SHARE_STRATEGIES = ["naive", "full mimic + rotation", "empirical mimic + rotation"]
BASE_RATE_STRATEGIES = ["naive", "organic timing + structure", "full mimic + rotation", "empirical mimic + rotation"]
BASE_RATES = [(200, 200), (200, 1800)]            # (amplified, organic): 50% and 10% of cascades amplified
EXPS = ("strategy", "share", "base rate")
COLS = ["dataset", "exp", "strategy", "pi", "pi_realized", "n_org", "n_amp", "view", "features", "trained_on",
        "seed", "auroc", "tpr_at_1pct_fpr", "auprc"]
COST_COLS = ["dataset", "strategy", "pi", "seed", "amp_t90_min", "amp_first_hour_share", "accounts_per_campaign",
             "cascades_per_account", "first_hour_reshares_amplified", "first_hour_reshares_organic"]

_BASE = []


def _init(path, max_size):
    """Load the base corpus; "sim:<n>" uses n simulated organic cascades instead (a matched
    baseline: the same protocol on the simulator's own trees)."""
    global _BASE
    if path.startswith("sim:"):
        _BASE = [c for c in simulate_corpus(int(path[4:]), 0, seed=12345) if c.size <= max_size]
    else:
        _BASE = [c for c in cascades_from_jsonl(path) if c.size <= max_size]


def make_corpus(strategy, pi, n, seed, n_org=None):
    """n amplified and n_org (default n) organic cascades, all drawn from distinct real ones."""
    n_org = n if n_org is None else n_org
    rng = random.Random(seed)
    cfg = replace(SimConfig(**STRATEGIES[strategy]), pi=pi)
    picks = rng.sample(range(len(_BASE)), n_org + n)
    pooled = empirical_samplers(_BASE, rng)
    pools = [[f"c{c}_a{j}" for j in range(cfg.pool_size)] for c in range(N_CAMPAIGNS)]
    corpus = []
    for k, i in enumerate(picks):
        base = _BASE[i]
        if k < n_org:
            c = inject(base, replace(cfg, pi=0.0), rng)
        else:
            camp = k % N_CAMPAIGNS
            try:                                  # the campaign copies the thread it joins
                sm = empirical_samplers([base], rng, host=base)
                sm.account = pooled.account
            except ValueError:
                sm = pooled
            c = inject(base, cfg, rng, amp_pool=pools[camp], samplers=sm)
            c.meta["campaign"] = camp
        corpus.append(c)
    rng.shuffle(corpus)
    return corpus


def run_task(t):
    n_org = t.get("n_org", t["n"])
    corpus = make_corpus(t["strategy"], t["pi"], t["n"], t["seed"], n_org)
    y = [1 if c.label == "amplified" else 0 for c in corpus]
    groups = [f"c{c.meta['campaign']}" if y[i] else f"o{i}" for i, c in enumerate(corpus)]
    base = {"dataset": t["dataset"], "exp": t["exp"], "strategy": t["strategy"], "pi": t["pi"],
            "pi_realized": round(statistics.fmean(c.meta["pi"] for c in corpus if c.label == "amplified"), 4),
            "n_org": n_org, "n_amp": t["n"], "seed": t["seed"], "trained_on": "same strategy (CV)"}
    out, costs = [], []
    full = None
    for k in t["views"]:
        rows = extract_all(corpus, prefix_k=k)
        full = rows if k is None else full
        for s in (t["sets"] if k is None else LIGHT_SETS):
            p, _ = out_of_fold(matrix(rows, SETS[s]), y, groups, t["seed"], t["trees"])
            out.append({**base, "view": "full" if k is None else k, "features": s, **metrics(y, p)})
    if t.get("transfer"):
        train = make_corpus("naive", t["pi"], t["n"], t["seed"] + 10_000)
        tr_rows, ty = extract_all(train), [1 if c.label == "amplified" else 0 for c in train]
        for s in LIGHT_SETS:
            clf = forest(t["seed"], t["trees"]).fit(matrix(tr_rows, SETS[s]), ty)
            p = clf.predict_proba(matrix(full, SETS[s]))[:, 1]
            out.append({**base, "view": "full", "features": s, "trained_on": "naive only", **metrics(y, p)})
        costs.append({"dataset": t["dataset"], "strategy": t["strategy"], "pi": t["pi"], "seed": t["seed"],
                      **attacker_costs(corpus)})
    return out, costs


def build_tasks(dataset, n, seeds, trees, exps=EXPS, n_base=None):
    tasks = []
    for s in range(seeds):
        common = {"dataset": dataset, "n": n, "seed": s, "trees": trees}
        if "base rate" in exps:
            for name in BASE_RATE_STRATEGIES:
                for n_amp, n_org in BASE_RATES:
                    if n_base is None or n_amp + n_org <= n_base:
                        tasks.append({**common, "exp": "base rate", "strategy": name, "pi": 0.10, "n": n_amp,
                                      "n_org": n_org, "views": [None], "sets": LIGHT_SETS})
        for name in (STRATEGIES if "strategy" in exps else []):
            for pi in (0.10, 0.30):
                tasks.append({**common, "exp": "strategy", "strategy": name, "pi": pi, "views": [None, 20],
                              "sets": MAIN_SETS, "transfer": True})
        for name in (SHARE_STRATEGIES if "share" in exps else []):
            for pi in SHARE_PIS:
                tasks.append({**common, "exp": "share", "strategy": name, "pi": pi, "views": [None],
                              "sets": LIGHT_SETS})
    return tasks


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cascades", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dataset", help="name in the output (default: file name)")
    ap.add_argument("--n", type=int, default=400, help="organic and amplified cascades per run (default 400)")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--trees", type=int, default=150)
    ap.add_argument("--max-size", type=int, default=2000, help="drop larger real cascades (default 2000)")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    ap.add_argument("--quick", action="store_true", help="1 seed, n = 100, 100 trees")
    ap.add_argument("--exps", default=",".join(EXPS), help="comma-separated experiments (default: all)")
    a = ap.parse_args()
    if a.quick:
        a.seeds, a.n, a.trees = 1, 100, 100
    name = a.dataset or os.path.basename(a.cascades).split(".")[0]
    _init(a.cascades, a.max_size)
    if len(_BASE) < 2 * a.n:
        raise SystemExit(f"{name}: only {len(_BASE)} cascades, need {2 * a.n}")
    tasks = build_tasks(name, a.n, a.seeds, a.trees, exps=a.exps.split(","), n_base=len(_BASE))
    tasks.sort(key=lambda t: -(t["n"] + t.get("n_org", t["n"])))         # biggest first
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    print(f"cascadekit {__version__}: {name}, {len(_BASE)} real cascades, {len(tasks)} tasks", flush=True)
    with open(os.path.join(a.out, "results.csv"), "w", newline="") as fr, \
            open(os.path.join(a.out, "costs.csv"), "w", newline="") as fc, \
            Pool(a.workers, initializer=_init, initargs=(a.cascades, a.max_size)) as pool:
        wr, wc = csv.DictWriter(fr, COLS), csv.DictWriter(fc, COST_COLS)
        wr.writeheader()
        wc.writeheader()
        for i, (res, costs) in enumerate(pool.imap_unordered(run_task, tasks), start=1):
            wr.writerows(res)
            wc.writerows(costs)
            fr.flush()
            fc.flush()
            if i % 10 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} tasks, {time.time() - t0:.0f}s", flush=True)
    print("done ->", a.out)


if __name__ == "__main__":
    main()
