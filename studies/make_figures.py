#!/usr/bin/env python3
"""
Figures and summary tables for the simulation study.

    python studies/make_figures.py --results results/study

Reads results.csv, costs.csv and importances.csv written by simulation_study.py and writes,
into the same folder:
  fig1_share.(png|pdf)       detection vs amplified share, by feature group
  fig2_early.(png|pdf)       detection vs number of reshares seen
  fig3_virality.(png|pdf)    detection vs organic mean offspring
  fig4_strategies.(png|pdf)  detection under each evasion strategy
  summary.csv                mean, standard deviation and count for every setting
  tables.md                  the tables used in the write-up
Each series has its own marker shape as well as colour, so figures survive greyscale printing.
"""
import argparse
import csv
import os
import statistics
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

INK, INK2, GRID, MUTED = "#0b0b0b", "#52514e", "#e4e3de", "#8a8984"
# Colour follows the feature set in every figure (fixed order from a validated palette).
STYLE = {
    "all":                {"color": INK,       "marker": "o", "label": "All features"},
    "reuse":              {"color": "#eb6834", "marker": "s", "label": "Account reuse"},
    "timing":             {"color": "#1baf7a", "marker": "^", "label": "Timing"},
    "shape":              {"color": "#2a78d6", "marker": "D", "label": "Shape"},
    "branching":          {"color": "#eda100", "marker": "v", "label": "Branching"},
    "structure + timing": {"color": "#e87ba4", "marker": "P", "label": "Structure + timing"},
    "size only":          {"color": MUTED,     "marker": "x", "label": "Size only (baseline)"},
}
RAMP = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]          # one hue, light to dark, for ordered pi
STRATEGY_ORDER = ["naive", "random timing", "organic timing", "organic timing + structure",
                  "full mimic + rotation", "control: embedded accounts"]
STRATEGY_LABEL = {"naive": "Naive", "random timing": "Random timing", "organic timing": "Organic timing",
                  "organic timing + structure": "Organic timing\n+ structure",
                  "full mimic + rotation": "Full mimic\n+ rotation",
                  "control: embedded accounts": "Control:\nembedded accounts"}
CV = "same strategy (CV)"

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "axes.linewidth": 0.8,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.titlesize": 9.5,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "legend.frameon": False,
    "axes.spines.top": False, "axes.spines.right": False, "savefig.facecolor": "white",
    "figure.facecolor": "white", "pdf.fonttype": 42,
})


def load(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def agg(rows, by, metric="auroc"):
    g = defaultdict(list)
    for r in rows:
        g[tuple(r[k] for k in by)].append(float(r[metric]))
    return {k: (statistics.fmean(v), statistics.stdev(v) if len(v) > 1 else 0.0, len(v)) for k, v in g.items()}


def pct(p):
    return f"{float(p) * 100:g}%"


def base_axes(ax, ylabel=True, lo=0.45):
    ax.set_ylim(lo, 1.012)
    ax.axhline(0.5, color=MUTED, linewidth=0.8, linestyle=(0, (2, 3)), zorder=0)
    ax.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=3)
    if ylabel:
        ax.set_ylabel("AUROC")


def line(ax, xs, stats, style, **kw):
    mean = [s[0] for s in stats]
    sd = [s[1] for s in stats]
    dashed = style["marker"] == "x"
    ax.fill_between(xs, [m - s for m, s in zip(mean, sd)], [min(1.0, m + s) for m, s in zip(mean, sd)],
                    color=style["color"], alpha=0.14, linewidth=0, zorder=1)
    ax.plot(xs, mean, color=style["color"], marker=style["marker"], markersize=5.5, linewidth=1.8,
            linestyle="--" if dashed else "-", markeredgecolor="white" if not dashed else style["color"],
            markeredgewidth=0.7 if not dashed else 1.2, label=style["label"], zorder=3, **kw)


def save(fig, out, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"{name}.{ext}"), dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_share(rows, out):
    rows = [r for r in rows if r["exp"] == "share" and r["view"] == "full" and r["trained_on"] == CV]
    a = agg(rows, ["pi", "features"])
    pis = sorted({k[0] for k in a}, key=float)
    xs = list(range(len(pis)))
    fig, ax = plt.subplots(figsize=(7.0, 3.9))
    shown = [f for f in STYLE if f != "structure + timing"]     # the combined set appears in figures 2-4
    order = sorted(shown, key=lambda f: -a.get((pis[2], f), (0,))[0])
    for f in order:
        if (pis[0], f) in a:
            line(ax, xs, [a[(p, f)] for p in pis], STYLE[f])
    base_axes(ax)
    ax.set_xticks(xs, [pct(p) for p in pis])
    ax.set_xlabel("Amplified share of reshares (π)")
    ax.text(xs[-1], 0.507, "chance", color=MUTED, fontsize=8, ha="right", va="bottom")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), handlelength=2.6, labelspacing=0.7)
    save(fig, out, "fig1_share")


def fig_early(rows, out):
    rows = [r for r in rows if r["exp"] == "share" and r["trained_on"] == CV]
    a = agg(rows, ["features", "pi", "view"])
    pis = sorted({k[1] for k in a if (k[0], k[1], "5") in a}, key=float)
    views = ["5", "10", "20", "50", "100", "full"]
    xs = list(range(len(views)))
    sets = ["structure + timing", "reuse", "all"]
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.3), sharey=True)
    for ax, f in zip(axes, sets):
        for p, col in zip(pis, RAMP):
            line(ax, xs, [a[(f, p, v)] for v in views],
                 {"color": col, "marker": "o", "label": f"π = {pct(p)}"})
        base_axes(ax, ylabel=ax is axes[0])
        ax.set_title(STYLE[f]["label"])
        ax.set_xticks(xs, ["5", "10", "20", "50", "100", "all"])
        ax.set_xlabel("Reshares seen")
    axes[-1].legend(loc="center left", bbox_to_anchor=(1.02, 0.5), title="Amplified share", alignment="left",
                    handlelength=2.4, labelspacing=0.7)
    fig.subplots_adjust(wspace=0.08)
    save(fig, out, "fig2_early")


def fig_virality(rows, out):
    rows = [r for r in rows if r["exp"] == "virality" and r["trained_on"] == CV]
    a = agg(rows, ["pi", "features", "m"])
    pis = sorted({k[0] for k in a}, key=float)
    ms = sorted({k[2] for k in a}, key=float)
    xs = list(range(len(ms)))
    fig, axes = plt.subplots(1, len(pis), figsize=(8.2, 3.3), sharey=True)
    for ax, p in zip(axes, pis):
        for f in ["all", "reuse", "structure + timing", "size only"]:
            line(ax, xs, [a[(p, f, m)] for m in ms], STYLE[f])
        base_axes(ax, ylabel=ax is axes[0])
        ax.set_title(f"Amplified share π = {pct(p)}")
        ax.set_xticks(xs, [f"{float(m):g}" for m in ms])
        ax.set_xlabel("Organic mean offspring (m)")
    axes[-1].legend(loc="center left", bbox_to_anchor=(1.02, 0.5), handlelength=2.6, labelspacing=0.7)
    fig.subplots_adjust(wspace=0.08)
    save(fig, out, "fig3_virality")


def fig_strategies(rows, out):
    rows = [r for r in rows if r["exp"] == "strategy" and r["view"] == "full"]
    a = agg(rows, ["pi", "strategy", "features", "trained_on"])
    pis = sorted({k[0] for k in a}, key=float)
    strategies = [s for s in STRATEGY_ORDER if any(k[1] == s for k in a)]
    series = [("structure + timing", CV, -0.27, "Structure + timing, retrained"),
              ("reuse", CV, -0.09, "Account reuse, retrained"),
              ("all", CV, 0.09, "All features, retrained"),
              ("all", "naive only", 0.27, "All features, trained on naive only")]
    fig, axes = plt.subplots(1, len(pis), figsize=(9.0, 4.3), sharey=True)
    ys = list(range(len(strategies)))
    for ax, p in zip(axes, pis):
        for f, trained, dy, label in series:
            st = STYLE[f]
            hollow = trained != CV
            for i, s in enumerate(strategies):
                mean, sd, _ = a[(p, s, f, trained)]
                ax.errorbar(mean, i + dy, xerr=sd, color=st["color"], linewidth=1.0, capsize=0, zorder=2)
                ax.plot(mean, i + dy, linestyle="none", marker=st["marker"], markersize=6.5,
                        color="white" if hollow else st["color"], markeredgecolor=st["color"],
                        markeredgewidth=1.4 if hollow else 0.7, zorder=3, label=label if i == 0 else None)
        for i in ys[:-1]:
            ax.axhline(i + 0.5, color=GRID, linewidth=0.6, zorder=0)
        ax.axvline(0.5, color=MUTED, linewidth=0.8, linestyle=(0, (2, 3)), zorder=0)
        ax.set_xlim(0.28, 1.02)
        ax.set_ylim(len(strategies) - 0.5, -0.5)
        ax.set_yticks(ys, [STRATEGY_LABEL[s] for s in strategies])
        ax.tick_params(length=3)
        ax.tick_params(axis="y", length=0)
        ax.set_xlabel("AUROC")
        ax.set_title(f"Amplified share π = {pct(p)}")
        ax.text(0.507, -0.44, "chance", color=MUTED, fontsize=8, ha="left", va="top")
    axes[0].legend(loc="upper center", bbox_to_anchor=(1.02, -0.14), ncol=2, handletextpad=0.4,
                   columnspacing=2.0)
    fig.subplots_adjust(wspace=0.06)
    save(fig, out, "fig4_strategies")


# ---------------------------------------------------------------------------- tables

def ms(stat, digits=3):
    return f"{stat[0]:.{digits}f} ± {stat[1]:.{digits}f}"


def write_summary(rows, out):
    by = ["exp", "strategy", "pi", "m", "pool_size", "start_delay_s", "n_org", "n_amp", "view", "features",
          "trained_on", "param", "value"]
    stats = {m: agg(rows, by, m) for m in ("auroc", "tpr_at_1pct_fpr", "auprc")}
    realized = agg(rows, by, "pi_realized")
    with open(os.path.join(out, "summary.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(by + ["n_seeds", "pi_realized", "auroc_mean", "auroc_sd", "tpr1_mean", "tpr1_sd",
                         "auprc_mean", "auprc_sd"])
        for k in sorted(stats["auroc"]):
            a, t, p = stats["auroc"][k], stats["tpr_at_1pct_fpr"][k], stats["auprc"][k]
            w.writerow(list(k) + [a[2], f"{realized[k][0]:.4f}", f"{a[0]:.4f}", f"{a[1]:.4f}", f"{t[0]:.4f}",
                                  f"{t[1]:.4f}", f"{p[0]:.4f}", f"{p[1]:.4f}"])


def write_tables(rows, costs, imps, out):
    L = []
    cv = [r for r in rows if r["trained_on"] == CV]

    L.append("## E1. AUROC by amplified share (full cascades)\n")
    sub = [r for r in cv if r["exp"] == "share" and r["view"] == "full"]
    a, t, real = agg(sub, ["pi", "features"]), agg(sub, ["pi", "features"], "tpr_at_1pct_fpr"), \
        agg(sub, ["pi"], "pi_realized")
    pis = sorted({k[0] for k in a}, key=float)
    sets = ["size only", "shape", "branching", "timing", "reuse", "structure + timing", "all"]
    L.append("| π target | π realised | " + " | ".join(sets) + " | all: recall at 1% FPR |")
    L.append("|" + " --- |" * (len(sets) + 3))
    for p in pis:
        L.append(f"| {pct(p)} | {real[(p,)][0] * 100:.1f}% | " + " | ".join(ms(a[(p, f)]) for f in sets)
                 + f" | {ms(t[(p, 'all')], 2)} |")

    L.append("\n## E2. AUROC by reshares seen\n")
    sub = [r for r in cv if r["exp"] == "share"]
    a = agg(sub, ["features", "pi", "view"])
    views = ["5", "10", "20", "50", "100", "full"]
    L.append("| Features | π | " + " | ".join("first " + v if v != "full" else "all" for v in views) + " |")
    L.append("|" + " --- |" * (len(views) + 2))
    for f in ["structure + timing", "reuse", "all"]:
        for p in sorted({k[1] for k in a if (f, k[1], "5") in a}, key=float):
            L.append(f"| {f} | {pct(p)} | " + " | ".join(ms(a[(f, p, v)]) for v in views) + " |")

    L.append("\n## E3. AUROC by organic mean offspring m\n")
    sub = [r for r in cv if r["exp"] == "virality"]
    a = agg(sub, ["pi", "features", "m"])
    mvals = sorted({k[2] for k in a}, key=float)
    L.append("| π | Features | " + " | ".join(f"m = {float(m):g}" for m in mvals) + " |")
    L.append("|" + " --- |" * (len(mvals) + 2))
    for p in sorted({k[0] for k in a}, key=float):
        for f in ["size only", "structure + timing", "reuse", "all"]:
            L.append(f"| {pct(p)} | {f} | " + " | ".join(ms(a[(p, f, m)]) for m in mvals) + " |")

    L.append("\n## E4. Evasion strategies (full cascades)\n")
    sub = [r for r in rows if r["exp"] == "strategy" and r["view"] == "full"]
    a = agg(sub, ["pi", "strategy", "features", "trained_on"])
    t = agg(sub, ["pi", "strategy", "features", "trained_on"], "tpr_at_1pct_fpr")
    L.append("| π | Strategy | Size only | Structure + timing | Reuse | All | All: recall at 1% FPR | "
             "All, trained on naive only |")
    L.append("|" + " --- |" * 8)
    for p in sorted({k[0] for k in a}, key=float):
        for s in STRATEGY_ORDER:
            if (p, s, "all", CV) in a:
                L.append(f"| {pct(p)} | {s} | {ms(a[(p, s, 'size only', CV)])} | "
                         f"{ms(a[(p, s, 'structure + timing', CV)])} | {ms(a[(p, s, 'reuse', CV)])} | "
                         f"{ms(a[(p, s, 'all', CV)])} | {ms(t[(p, s, 'all', CV)], 2)} | "
                         f"{ms(a[(p, s, 'all', 'naive only')])} |")
    sub20 = [r for r in cv if r["exp"] == "strategy" and r["view"] == "20"]
    a20 = agg(sub20, ["pi", "strategy", "features"])
    L.append("\nFirst 20 reshares only:\n")
    L.append("| π | Strategy | Structure + timing | Reuse | All |")
    L.append("|" + " --- |" * 5)
    for p in sorted({k[0] for k in a20}, key=float):
        for s in STRATEGY_ORDER:
            if (p, s, "all") in a20:
                L.append(f"| {pct(p)} | {s} | " + " | ".join(ms(a20[(p, s, f)]) for f in
                                                           ["structure + timing", "reuse", "all"]) + " |")

    L.append("\n## E4. What each strategy costs the attacker\n")
    cols = ["amp_t90_min", "amp_first_hour_share", "accounts_per_campaign", "cascades_per_account",
            "first_hour_reshares_amplified", "first_hour_reshares_organic"]
    c = {m: agg([r for r in costs if r["exp"] == "strategy"], ["pi", "strategy"], m) for m in cols}
    L.append("| π | Strategy | Minutes until 90% of amplifier reshares land | Amplifier reshares in first hour | "
             "Accounts used per campaign | Cascades per account | Reshares in first hour, amplified | "
             "Reshares in first hour, organic |")
    L.append("|" + " --- |" * 8)
    for p in sorted({k[0] for k in c[cols[0]]}, key=float):
        for s in STRATEGY_ORDER:
            if (p, s) in c[cols[0]]:
                k = (p, s)
                L.append(f"| {pct(p)} | {s} | {c[cols[0]][k][0]:.0f} | {c[cols[1]][k][0] * 100:.0f}% | "
                         f"{c[cols[2]][k][0]:.0f} | {c[cols[3]][k][0]:.1f} | {c[cols[4]][k][0]:.1f} | "
                         f"{c[cols[5]][k][0]:.1f} |")

    L.append("\n## E4b. Account rotation under the full-mimic strategy (π = 20%)\n")
    sub = [r for r in cv if r["exp"] == "pool"]
    a = agg(sub, ["pool_size", "features"])
    c = {m: agg([r for r in costs if r["exp"] == "pool"], ["pool_size"], m) for m in cols}
    L.append("| Pool size per campaign | Accounts actually used | Cascades per account | Reuse AUROC | All AUROC |")
    L.append("|" + " --- |" * 5)
    for pool in sorted({k[0] for k in a}, key=float):
        L.append(f"| {int(float(pool)):,} | {c[cols[2]][(pool,)][0]:.0f} | {c[cols[3]][(pool,)][0]:.2f} | "
                 f"{ms(a[(pool, 'reuse')])} | {ms(a[(pool, 'all')])} |")

    L.append("\n## E4c. Late start of a naive campaign (π = 20%)\n")
    sub = [r for r in cv if r["exp"] == "start delay"]
    a = agg(sub, ["start_delay_s", "view", "features"])
    L.append("| Start delay | View | Structure + timing | Reuse | All |")
    L.append("|" + " --- |" * 5)
    for d in sorted({k[0] for k in a}, key=float):
        for v in ("20", "full"):
            L.append(f"| {float(d) / 60:g} min | {'first 20' if v == '20' else 'all'} | "
                     + " | ".join(ms(a[(d, v, f)]) for f in ["structure + timing", "reuse", "all"]) + " |")

    L.append("\n## E5. Base rate (π = 10%, 200 amplified cascades)\n")
    sub = [r for r in cv if r["exp"] == "base rate"]
    stats = {m: agg(sub, ["strategy", "n_org", "features"], m) for m in ("auroc", "auprc", "tpr_at_1pct_fpr")}
    L.append("| Strategy | Amplified share of corpus | Features | AUROC | Average precision | Recall at 1% FPR |")
    L.append("|" + " --- |" * 6)
    for s in STRATEGY_ORDER:
        for n in sorted({k[1] for k in stats["auroc"] if k[0] == s}, key=float):
            for f in ["structure + timing", "reuse", "all"]:
                k = (s, n, f)
                share = 200 / (200 + float(n)) if float(n) >= 200 else 0.5
                L.append(f"| {s} | {share * 100:.0f}% | {f} | {ms(stats['auroc'][k])} | "
                         f"{ms(stats['auprc'][k])} | {ms(stats['tpr_at_1pct_fpr'][k], 2)} |")

    sens = [r for r in cv if r["exp"] == "sensitivity" and r["features"] == "all"]
    if sens:
        L.append("\n## E6. Sensitivity: AUROC (all features) with one parameter moved from its default\n")
        base = agg([r for r in cv if r["exp"] == "strategy" and r["features"] == "all" and r["view"] == "full"],
                   ["strategy", "pi"], "auroc")
        st_ = agg(sens, ["param", "value", "strategy", "pi"], "auroc")
        settings = [("naive", "0.1"), ("organic timing + structure", "0.1"), ("full mimic + rotation", "0.3")]
        names = {"root_mean": "Direct reshares of the post (default 6)",
                 "delay_sigma": "Spread of reaction delays (default 1.3)",
                 "amp_followers_mean": "Reactions per amplifier reshare (default 0.15)",
                 "activity_exponent": "Activity skew of users (default 0.7)"}
        L.append("| Parameter | Value | " + " | ".join(f"{s}, π = {pct(p)}" for s, p in settings) + " |")
        L.append("|" + " --- |" * (2 + len(settings)))
        L.append("| All at default | | " + " | ".join(ms(base[(s, p)]) for s, p in settings) + " |")
        for par in names:
            for v in sorted({k[1] for k in st_ if k[0] == par}, key=float):
                L.append(f"| {names[par]} | {float(v):g} | " + " | ".join(ms(st_[(par, v, s, p)]) for s, p in settings) + " |")

    L.append("\n## Feature importances (mean over seeds, top 8)\n")
    g = agg(imps, ["exp", "strategy", "pi", "features", "feature"], "importance")
    combos = sorted({k[:4] for k in g})
    for combo in combos:
        top = sorted(((v[0], k[4]) for k, v in g.items() if k[:4] == combo), reverse=True)[:8]
        L.append(f"- **{combo[0]} / {combo[1]} / π = {pct(combo[2])} / {combo[3]}:** "
                 + ", ".join(f"{name} ({val:.2f})" for val, name in top))

    with open(os.path.join(out, "tables.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default="results/study")
    a = ap.parse_args()
    rows = load(os.path.join(a.results, "results.csv"))
    costs = load(os.path.join(a.results, "costs.csv"))
    imps = load(os.path.join(a.results, "importances.csv"))
    write_summary(rows, a.results)
    write_tables(rows, costs, imps, a.results)
    fig_share(rows, a.results)
    fig_early(rows, a.results)
    fig_virality(rows, a.results)
    fig_strategies(rows, a.results)
    print("figures, summary.csv and tables.md ->", a.results)


if __name__ == "__main__":
    main()
