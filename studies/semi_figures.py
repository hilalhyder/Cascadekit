#!/usr/bin/env python3
"""
Figure for the semi-synthetic study (E7), in the style of make_figures.py.

    python studies/semi_figures.py --results results/semi

Writes fig9_real.(png|pdf) into --results: AUROC (all features) against the amplified share
pi for the naive, full-mimic and empirical-mimic campaigns, one panel per organic background
(simulated, PHEME, Higgs). Bands are +-1 s.d. over seeds.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from make_figures import CV, INK, INK2, MUTED, STYLE, agg, base_axes, line, load, pct, save  # noqa: E402

BACKGROUNDS = [("simulated", "(a) Simulated organic trees"), ("pheme", "(b) PHEME replies"),
               ("higgs", "(c) Higgs retweets")]
# Same convention as figure 7: naive in ink, the simulator's mimic in the reuse orange; the
# empirical mimic takes the next hue of the validated palette.
CAMPAIGNS = {
    "naive":                      {"color": INK, "marker": "o", "label": "Naive"},
    "full mimic + rotation":      {"color": STYLE["reuse"]["color"], "marker": "v",
                                   "label": "Full mimic + rotation"},
    "empirical mimic + rotation": {"color": STYLE["shape"]["color"], "marker": "D",
                                   "label": "Empirical mimic + rotation"},
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default="results/semi")
    a = ap.parse_args()
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.6), sharey=True)
    for i, (ax, (bg, title)) in enumerate(zip(axes, BACKGROUNDS)):
        rows = [r for r in load(os.path.join(a.results, bg, "results.csv"))
                if r["exp"] == "share" and r["features"] == "all" and r["trained_on"] == CV]
        s = agg(rows, ["strategy", "pi"])
        pis = sorted({k[1] for k in s}, key=float)
        xs = list(range(len(pis)))
        for name, style in CAMPAIGNS.items():
            stats = [s[(name, p)] for p in pis]
            line(ax, xs, stats, style)
        base_axes(ax, ylabel=i == 0)
        ax.set_xticks(xs, [pct(p) for p in pis])
        ax.set_xlabel("Amplified share of reshares (π)")
        ax.set_title(title)
        if i == 0:
            ax.text(xs[-1], 0.507, "chance", color=MUTED, fontsize=8, ha="right", va="bottom")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.005), handlelength=2.6,
               columnspacing=2.2)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, a.results, "fig9_real")
    print("wrote", os.path.join(a.results, "fig9_real.png"))


if __name__ == "__main__":
    main()
