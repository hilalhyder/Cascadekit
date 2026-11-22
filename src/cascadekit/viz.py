"""Plotting (needs matplotlib: pip install cascadekit[viz])."""
from __future__ import annotations

import math
from typing import Optional

from .cascade import Cascade


def plot_time_depth(c: Cascade, ax=None, log_time: bool = True, highlight_accounts=None,
                    title: Optional[str] = None):
    """Draw a cascade with time since the start on the x-axis and tree depth on the y-axis.
    Each reshare is a dot joined to its parent. Broadcast-like spreading shows as a dense
    band at depth 1; word-of-mouth spreading climbs to deeper levels over time.
    ``highlight_accounts``: set of accounts drawn in a second colour (for example
    known amplifiers in a synthetic corpus)."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(6, 3.2))
    t0 = c.start_time() or 0.0
    depth = c.depths()
    pos = {}
    for i, n in enumerate(c.nodes):
        t = max((n.ts if n.ts is not None else t0) - t0, 0.0)
        pos[n.id] = (math.log10(t + 1) if log_time else t, depth[i])
    for n in c.nodes[1:]:
        (x0, y0), (x1, y1) = pos[n.parent], pos[n.id]
        ax.plot([x0, x1], [y0, y1], color="#b8b8b8", linewidth=0.5, zorder=1)
    hl = set(highlight_accounts or ())
    xs, ys, cs = [], [], []
    for n in c.nodes:
        x, y = pos[n.id]
        xs.append(x)
        ys.append(y)
        cs.append("#d1495b" if n.account in hl else "#2e6f9e")
    ax.scatter(xs, ys, s=8, c=cs, zorder=2, linewidths=0)
    ax.set_xlabel("log10(seconds since start + 1)" if log_time else "seconds since start")
    ax.set_ylabel("depth")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(title or f"{c.label or c.platform}: {c.size} reshares", fontsize=10, loc="left")
    return ax
