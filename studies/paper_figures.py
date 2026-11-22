#!/usr/bin/env python3
"""
Additional figures for the manuscript (same style as make_figures.py).

    python studies/paper_figures.py --results results/study --scaling results/reuse_scaling

Writes into --results:
  fig0_examples.(png|pdf)     one organic, one naive and one full-mimic cascade, time by depth
  fig5_reuse_scaling.(png|pdf) raw reuse counts against rarity-weighted overlap as the corpus grows
  fig6_tradeoff.(png|pdf)     detection against the attacker's first-hour lift, per strategy
  fig7_pool.(png|pdf)         the two reuse signals across rotation pool sizes
  fig8_sensitivity.(png|pdf)  AUROC when one model parameter is moved
"""
import argparse
import csv
import math
import os
import statistics as st
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from make_figures import CV, GRID, INK, INK2, MUTED, STYLE, load  # noqa: E402  (also applies rcParams)
from simulation_study import N_CAMPAIGNS, STRATEGIES  # noqa: E402

from cascadekit import SimConfig, simulate_corpus  # noqa: E402

ORG, AMP = "#2a78d6", "#d1495b"
STRAT_STYLE = {"naive": ("o", "Naive"), "random timing": ("s", "Random timing"),
               "organic timing": ("^", "Organic timing"),
               "organic timing + structure": ("D", "Organic timing + structure"),
               "full mimic + rotation": ("v", "Full mimic + rotation")}


def save(fig, out, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"{name}.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def mean_sd(xs):
    xs = [float(x) for x in xs]
    return st.fmean(xs), (st.stdev(xs) if len(xs) > 1 else 0.0)


# ------------------------------------------------------------------ fig 0: example cascades

def time_depth(ax, c, title):
    t0 = c.nodes[0].ts
    depth = c.depths()
    pos = {n.id: (math.log10(max(n.ts - t0, 0) + 1), depth[i]) for i, n in enumerate(c.nodes)}
    for n in c.nodes[1:]:
        (x0, y0), (x1, y1) = pos[n.parent], pos[n.id]
        ax.plot([x0, x1], [y0, y1], color="#c9c8c3", linewidth=0.45, zorder=1)
    org = [pos[n.id] for n in c.nodes[1:] if not n.id.startswith("m")]
    amp = [pos[n.id] for n in c.nodes[1:] if n.id.startswith("m")]
    ax.scatter(*zip(*org), s=9, color=ORG, linewidths=0, zorder=2, label="Organic reshare")
    if amp:
        ax.scatter(*zip(*amp), s=11, color=AMP, marker="s", linewidths=0, zorder=3, label="Campaign reshare")
    ax.scatter([0], [0], s=30, color=INK, marker="*", zorder=4, label="Original post")
    ax.set_title(title)
    ax.set_xlabel("log$_{10}$(seconds since post + 1)")
    ax.set_xlim(-0.2, 5.6)
    ax.grid(axis="x", color=GRID, linewidth=0.6)


def pick(corpus, label, lo=50, hi=90):
    """A typical cascade: the first of the given label with 50 to 90 reshares."""
    for c in corpus:
        if c.label == label and lo <= c.size <= hi:
            return c
    return next(c for c in corpus if c.label == label)


def fig_examples(out):
    org = pick(simulate_corpus(40, 0, seed=3), "organic")
    naive = pick(simulate_corpus(0, 40, (0.3, 0.3), N_CAMPAIGNS, SimConfig(), seed=3), "amplified")
    mimic = pick(simulate_corpus(0, 40, (0.3, 0.3), N_CAMPAIGNS,
                                 SimConfig(**STRATEGIES["full mimic + rotation"]), seed=3), "amplified")
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.3), sharey=True)
    time_depth(axes[0], org, "(a) Organic")
    time_depth(axes[1], naive, "(b) Naive, π = 30%")
    time_depth(axes[2], mimic, "(c) Full mimic + rotation, π = 30%")
    axes[0].set_ylabel("Depth in tree")
    h, l = axes[1].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.12))
    fig.subplots_adjust(wspace=0.12)
    save(fig, out, "fig0_examples")


# ------------------------------------------------------------------ fig 5: reuse scaling

def fig_scaling(out, scaling_dir):
    rows = load(os.path.join(scaling_dir, "results.csv"))
    fig, ax = plt.subplots(figsize=(4.6, 3.1))
    styles = {"raw counts": (MUTED, "x", "Raw reuse counts (0.2.0)"),
              "rarity-weighted overlap": (STYLE["reuse"]["color"], "s", "Rarity-weighted overlap (0.3.0)")}
    for name, (col, mk, lab) in styles.items():
        sizes = sorted({int(r["n_cascades"]) for r in rows if r["features"] == name})
        m = [mean_sd(r["auroc"] for r in rows if r["features"] == name and int(r["n_cascades"]) == s) for s in sizes]
        ax.errorbar(sizes, [x[0] for x in m], yerr=[x[1] for x in m], color=col, marker=mk, ms=5,
                    linewidth=1.4, capsize=2.5, label=lab)
    ax.set_xscale("log")
    ax.set_xticks([400, 1000, 2000, 5000, 10000], ["400", "1,000", "2,000", "5,000", "10,000"])
    ax.set_xlabel("Cascades in the corpus (half amplified)")
    ax.set_ylabel("AUROC, account-reuse features")
    ax.set_ylim(0.45, 1.01)
    ax.axhline(0.5, color=MUTED, linewidth=0.8, linestyle=(0, (2, 3)), zorder=0)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.legend(loc="lower left")
    save(fig, out, "fig5_reuse_scaling")


# ------------------------------------------------------------------ fig 6: trade-off

def fig_tradeoff(out, results, costs):
    auc = defaultdict(list)
    for r in results:
        if r["exp"] == "strategy" and r["features"] == "all" and r["view"] == "full" and r["trained_on"] == CV:
            auc[(r["strategy"], r["pi"])].append(float(r["auroc"]))
    lift, accts = defaultdict(list), defaultdict(list)
    for r in costs:
        if r["exp"] == "strategy":
            k = (r["strategy"], r["pi"])
            a, o = float(r["first_hour_reshares_amplified"]), float(r["first_hour_reshares_organic"])
            lift[k].append(100 * (a - o) / o)
            accts[k].append(float(r["accounts_per_campaign"]))
    short = {"naive": "Naive /\nrandom timing", "organic timing": "Organic timing",
             "organic timing + structure": "Organic timing\n+ structure", "full mimic + rotation": "Full mimic\n+ rotation"}
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6), sharey=True)
    for ax, pi, title in zip(axes, ("0.1", "0.3"), ("(a) π = 10%", "(b) π = 30%")):
        xmax = max(st.fmean(lift[(s, pi)]) for s in short)
        for s, lab in short.items():
            k = (s, pi)
            x, y = st.fmean(lift[k]), st.fmean(auc[k])
            evasive = s == "full mimic + rotation"
            ax.scatter([x], [y], s=46, marker=STRAT_STYLE[s][0], color=STYLE["reuse"]["color"] if evasive else INK,
                       linewidths=0, zorder=3)
            # label placement per strategy: beside the point for the low-lift ones, below for the others
            off, ha = {"naive": ((4, -9), "right"), "organic timing": ((0, -9), "center")}.get(s, ((8, -2), "left"))
            ax.annotate(f"{lab}\n{st.fmean(accts[k]):,.0f} accounts", (x, y), xytext=off,
                        textcoords="offset points", ha=ha, va="top", fontsize=7.5, color=INK2)
        ax.set_title(title)
        ax.set_xlabel("First-hour lift over an organic cascade (%)")
        ax.set_xlim(-0.05 * xmax, 1.12 * xmax)
        ax.set_ylim(0.6, 1.02)
        ax.grid(color=GRID, linewidth=0.6)
    axes[0].set_ylabel("AUROC, all features")
    save(fig, out, "fig6_tradeoff")


# ------------------------------------------------------------------ fig 7: pool sizes

def fig_pool(out, results, diag_path):
    diag = load(diag_path)
    reuse = defaultdict(list)
    for r in results:
        if r["exp"] == "pool" and r["features"] == "reuse" and r["trained_on"] == CV:
            reuse[int(r["pool_size"])].append(float(r["auroc"]))
    pools = sorted(reuse)
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    m = [mean_sd(reuse[p]) for p in pools]
    ax.errorbar(pools, [x[0] for x in m], yerr=[x[1] for x in m], color=STYLE["reuse"]["color"], marker="s",
                ms=5, linewidth=1.5, capsize=2.5, label="All reuse features (classifier)")
    for f, col, mk, lab in (("reuse_overlap_top5", INK, "o", "Cosine overlap alone"),
                            ("reuse_shared_top5", INK2, "^", "Shared-account count alone")):
        mm = [mean_sd(r["auroc_alone"] for r in diag if r["feature"] == f and int(r["pool_size"]) == p) for p in pools]
        ax.errorbar(pools, [x[0] for x in mm], yerr=[x[1] for x in mm], color=col, marker=mk, ms=4.5,
                    linewidth=1.1, capsize=2, linestyle="--", label=lab)
    ax.axhline(0.5, color=MUTED, linewidth=0.8, linestyle=(0, (2, 3)), zorder=0)
    ax.set_xscale("log")
    ax.set_xticks(pools, [f"{p:,}" for p in pools])
    ax.set_xlabel("Accounts per campaign (rotation pool)")
    ax.set_ylabel("AUROC")
    ax.set_ylim(0.3, 1.01)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.legend(loc="lower left", fontsize=7.5)
    save(fig, out, "fig7_pool")


# ------------------------------------------------------------------ fig 8: sensitivity

def fig_sensitivity(out, results):
    settings = [("naive", "0.1", "(a) Naive, π = 10%"), ("organic timing + structure", "0.1",
                "(b) Organic timing + structure, 10%"), ("full mimic + rotation", "0.3",
                "(c) Full mimic + rotation, 30%")]
    params = [("root_mean", "Direct reshares μ₀ (3 / 6 / 12)"), ("delay_sigma", "Delay spread σ (0.8 / 1.3 / 1.8)"),
              ("amp_followers_mean", "Reactions per campaign reshare (0 / 0.15 / 0.5)"),
              ("activity_exponent", "Activity skew (0.5 / 0.7 / 0.9)")]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.1), sharey=True)
    for ax, (s, pi, title) in zip(axes, settings):
        base = st.fmean(float(r["auroc"]) for r in results if r["exp"] == "strategy" and r["strategy"] == s
                        and r["pi"] == pi and r["features"] == "all" and r["view"] == "full" and r["trained_on"] == CV)
        ax.axvline(base, color=MUTED, linewidth=1, linestyle=(0, (3, 2)), zorder=0)
        for i, (p, _) in enumerate(params):
            vals = sorted({float(r["value"]) for r in results if r["exp"] == "sensitivity" and r["param"] == p})
            lo, hi = (st.fmean(float(r["auroc"]) for r in results if r["exp"] == "sensitivity" and r["param"] == p
                               and float(r["value"]) == v and r["strategy"] == s and r["features"] == "all"
                               and r["trained_on"] == CV) for v in vals)
            y = len(params) - 1 - i
            ax.plot([lo, hi], [y, y], color=GRID, linewidth=3, zorder=1, solid_capstyle="round")
            ax.scatter([lo], [y], marker="<", color=INK2, s=28, zorder=2, label="Lower value" if i == 0 else None)
            ax.scatter([hi], [y], marker=">", color=STYLE["reuse"]["color"], s=28, zorder=2,
                       label="Higher value" if i == 0 else None)
            ax.scatter([base], [y], marker="|", color=INK, s=60, zorder=3, label="Default" if i == 0 else None)
        ax.set_title(title)
        ax.set_xlim(0.84, 0.99)
        ax.set_xlabel("AUROC, all features")
        ax.grid(axis="x", color=GRID, linewidth=0.6)
    axes[0].set_yticks(range(len(params)), [lab for _, lab in params][::-1])
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.6, -0.14))
    fig.subplots_adjust(wspace=0.1)
    save(fig, out, "fig8_sensitivity")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results/study")
    ap.add_argument("--scaling", default="results/reuse_scaling")
    a = ap.parse_args()
    results = load(os.path.join(a.results, "results.csv"))
    costs = load(os.path.join(a.results, "costs.csv"))
    fig_examples(a.results)
    fig_scaling(a.results, a.scaling)
    fig_tradeoff(a.results, results, costs)
    fig_pool(a.results, results, os.path.join(a.results, "pool_diagnostic.csv"))
    fig_sensitivity(a.results, results)
    print("paper figures ->", a.results)


if __name__ == "__main__":
    main()
