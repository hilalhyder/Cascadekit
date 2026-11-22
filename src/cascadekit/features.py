"""Cascade fingerprint: language-agnostic features of a diffusion tree.

Every feature uses only tree structure, timing and anonymised account reuse, never text.

    from cascadekit import extract_all
    rows = extract_all(cascades)          # list of dicts, one per cascade
"""
from __future__ import annotations

import collections
import csv
import math
import statistics
from typing import Dict, Iterable, List, Optional

from .cascade import Cascade

FEATURE_GROUPS = {
    "shape": ["size", "depth", "max_breadth", "structural_virality", "wiener_index",
              "depth1_share", "depth2_share", "depth3plus_share", "mean_depth"],
    "branching": ["root_share", "endogenous_share", "mean_offspring", "offspring_cv", "max_outdeg_nonroot",
                  "root_dominance", "outdeg_gini", "leaf_share"],
    "timing": ["duration_s", "t10_s", "t50_s", "t90_s", "interarrival_cv", "interarrival_entropy",
               "burstiness", "median_delay_s", "delay_ratio_deep_vs_d1"],
    "reuse": ["reuse_overlap_max", "reuse_overlap_top5", "reuse_shared_max", "reuse_shared_top5",
              "distinct_account_share"],
}
FEATURES = [f for g in FEATURE_GROUPS.values() for f in g]

_NAN = float("nan")


def _safe_div(a, b):
    return a / b if b else _NAN


def _cv(xs):
    if len(xs) < 2:
        return _NAN
    m = statistics.fmean(xs)
    return _safe_div(statistics.pstdev(xs), m)


def _gini(xs):
    xs = sorted(xs)
    n, s = len(xs), sum(xs)
    if n == 0 or s == 0:
        return 0.0
    cum = sum((i + 1) * x for i, x in enumerate(xs))
    return (2 * cum) / (n * s) - (n + 1) / n


def wiener_index(parents: List[int]) -> int:
    """Sum of distances over all node pairs of a tree, in O(n), from the parent array
    (parents[i] < i). Uses: each edge separates a subtree of size s from n - s nodes."""
    n = len(parents)
    size = [1] * n
    for i in range(n - 1, 0, -1):
        size[parents[i]] += size[i]
    return sum(size[i] * (n - size[i]) for i in range(1, n))


def structural_virality(c: Cascade) -> float:
    """Mean distance between all pairs of nodes (Goel et al., Management Science 2016)."""
    n = len(c.nodes)
    if n < 2:
        return 0.0
    return wiener_index(c.parent_index()) / (n * (n - 1) / 2)


def shape_features(c: Cascade) -> Dict[str, float]:
    n = len(c.nodes)
    d = c.depths()
    by_depth = collections.Counter(d)
    r = max(c.size, 1)
    return {
        "size": c.size,
        "depth": max(d),
        "max_breadth": max(by_depth.values()),
        "structural_virality": structural_virality(c),
        "wiener_index": wiener_index(c.parent_index()),
        "depth1_share": by_depth.get(1, 0) / r if c.size else _NAN,
        "depth2_share": by_depth.get(2, 0) / r if c.size else _NAN,
        "depth3plus_share": sum(v for k, v in by_depth.items() if k >= 3) / r if c.size else _NAN,
        "mean_depth": statistics.fmean(d[1:]) if n > 1 else _NAN,
    }


def branching_features(c: Cascade) -> Dict[str, float]:
    deg = c.out_degrees()
    nonroot = deg[1:]
    parents = [x for x in deg if x > 0]
    nonroot_parents = [x for x in nonroot if x > 0]
    med = statistics.median(nonroot_parents) if nonroot_parents else 0
    return {
        "root_share": _safe_div(deg[0], c.size),
        "endogenous_share": _safe_div(c.size - deg[0], c.size),   # reshares triggered by other reshares
        "mean_offspring": statistics.fmean(parents) if parents else _NAN,
        "offspring_cv": _cv(parents),
        "max_outdeg_nonroot": max(nonroot) if nonroot else 0,
        "root_dominance": _safe_div(deg[0], med) if med else (float(deg[0]) if deg[0] else _NAN),
        "outdeg_gini": _gini(deg),
        "leaf_share": _safe_div(sum(1 for x in nonroot if x == 0), c.size),
    }


def _entropy_log_bins(xs, lo=-1.0, hi=7.0, bins=16):
    """Normalised entropy of log10 inter-arrival times (seconds) over fixed bins."""
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return _NAN
    counts = [0] * bins
    for x in xs:
        v = math.log10(max(x, 0.1))
        k = min(bins - 1, max(0, int((v - lo) / (hi - lo) * bins)))
        counts[k] += 1
    tot = sum(counts)
    h = -sum(cn / tot * math.log(cn / tot) for cn in counts if cn)
    return h / math.log(bins)


def timing_features(c: Cascade) -> Dict[str, float]:
    t0 = c.start_time()
    ts = [n.ts for n in c.nodes[1:] if n.ts is not None]
    out = {k: _NAN for k in FEATURE_GROUPS["timing"]}
    if t0 is None or not ts:
        return out
    rel = sorted(t - t0 for t in ts)
    q = lambda p: rel[min(len(rel) - 1, max(0, math.ceil(p * len(rel)) - 1))]
    gaps = [b - a for a, b in zip([0.0] + rel[:-1], rel)]
    out.update({"duration_s": rel[-1], "t10_s": q(0.10), "t50_s": q(0.50), "t90_s": q(0.90)})
    if len(gaps) >= 2:
        m, s = statistics.fmean(gaps), statistics.pstdev(gaps)
        out["interarrival_cv"] = _safe_div(s, m)
        out["burstiness"] = _safe_div(s - m, s + m)       # -1 regular, 0 Poisson, +1 bursty
        out["interarrival_entropy"] = _entropy_log_bins(gaps)
    pos = {n.id: n for n in c.nodes}
    d = c.depths()
    delays, d1, deep = [], [], []
    for i, n in enumerate(c.nodes[1:], start=1):
        p = pos[n.parent]
        if n.ts is not None and p.ts is not None:
            x = max(0.0, n.ts - p.ts)
            delays.append(x)
            (d1 if d[i] == 1 else deep).append(x)
    if delays:
        out["median_delay_s"] = statistics.median(delays)
    if d1 and deep:
        out["delay_ratio_deep_vs_d1"] = _safe_div(statistics.median(deep), statistics.median(d1))
    return out


def account_counts(cascades: Iterable[Cascade]) -> collections.Counter:
    """In how many cascades each account appears (counted once per cascade)."""
    cnt = collections.Counter()
    for c in cascades:
        cnt.update({n.account for n in c.nodes[1:] if n.account is not None})
    return cnt


def account_overlap(cascades: List[Cascade], k: int = 5) -> List[Dict[str, float]]:
    """Corpus-level account-reuse features, one dict per cascade.

    A coordinated campaign shows up as the *same group* of accounts resharing many
    cascades, not as individually busy accounts: in a large corpus the most active
    ordinary users appear in far more cascades than any campaign account. Each account
    therefore gets an inverse-document-frequency weight

        w(a) = log(N / n_a) / log(N)

    where N is the number of cascades and n_a the number containing account a (0 for an
    account in every cascade, 1 for one in a single cascade). Scaling by log N keeps the
    weights on the same 0-1 scale for any corpus size. For cascade c:

    * ``reuse_overlap_max`` / ``reuse_overlap_top5``: cosine similarity of the weighted
      account sets of c and its most similar other cascade (or the mean over the k most
      similar). Adjusted for cascade size, between 0 and 1.
    * ``reuse_shared_max`` / ``reuse_shared_top5``: the weighted number of accounts c
      shares with its most-overlapping other cascade (sum of w(a) squared; or the mean over
      the top k). Rare accounts count nearly fully, ubiquitous ones hardly at all.

    The root account is excluded. Cost is the sum over accounts of n_a squared.
    """
    sets = [{n.account for n in c.nodes[1:] if n.account is not None} for c in cascades]
    n_casc = len(sets)
    df = collections.Counter(a for s in sets for a in s)
    log_n = math.log(n_casc) if n_casc > 1 else 1.0
    w2 = {a: (math.log(n_casc / v) / log_n) ** 2 for a, v in df.items()}
    # Sums over account sets use math.fsum: set order follows string hashing, which changes
    # between Python processes, and fsum's exactly rounded result does not depend on order.
    norm = [math.sqrt(math.fsum(w2[a] for a in s)) for s in sets]
    index = collections.defaultdict(list)                  # account -> cascades, shared accounts only
    for i, s in enumerate(sets):
        for a in s:
            if df[a] > 1:
                index[a].append(i)
    out = []
    for i, s in enumerate(sets):
        if not s:
            out.append({"reuse_overlap_max": _NAN, "reuse_overlap_top5": _NAN,
                        "reuse_shared_max": _NAN, "reuse_shared_top5": _NAN})
            continue
        parts = collections.defaultdict(list)
        for a in s:
            if df[a] > 1:
                x = w2[a]
                for j in index[a]:
                    parts[j].append(x)
        parts.pop(i, None)
        shared = {j: math.fsum(v) for j, v in parts.items()}
        cos = sorted((v / (norm[i] * norm[j]) if norm[i] and norm[j] else 0.0 for j, v in shared.items()),
                     reverse=True)[:k]
        raw = sorted(shared.values(), reverse=True)[:k]
        cos += [0.0] * (k - len(cos))
        raw += [0.0] * (k - len(raw))
        out.append({"reuse_overlap_max": cos[0], "reuse_overlap_top5": sum(cos) / k,
                    "reuse_shared_max": raw[0], "reuse_shared_top5": sum(raw) / k})
    return out


def reuse_features(c: Cascade, overlap: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """``distinct_account_share`` for one cascade, plus the corpus-level overlap features
    from :func:`account_overlap` if given (otherwise NaN)."""
    accts = [n.account for n in c.nodes[1:] if n.account is not None]
    out = {"distinct_account_share": _safe_div(len(set(accts)), len(accts)) if accts else _NAN,
           "reuse_overlap_max": _NAN, "reuse_overlap_top5": _NAN,
           "reuse_shared_max": _NAN, "reuse_shared_top5": _NAN}
    if overlap:
        out.update(overlap)
    return out


def extract(c: Cascade, overlap: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """All features for one cascade. The account-reuse features compare a cascade with the
    rest of a corpus, so pass its entry from :func:`account_overlap` (as
    :func:`extract_all` does) or they are NaN."""
    row = {}
    row.update(shape_features(c))
    row.update(branching_features(c))
    row.update(timing_features(c))
    row.update(reuse_features(c, overlap))
    return row


def extract_all(cascades: List[Cascade], prefix_k: Optional[int] = None,
                window_s: Optional[float] = None) -> List[Dict]:
    """Feature rows for a corpus, with ``root`` and ``label`` columns first.
    ``prefix_k`` / ``window_s`` compute features on early views of each cascade."""
    views = [c.prefix(prefix_k) if prefix_k else c.until(window_s) if window_s else c for c in cascades]
    overlap = account_overlap(views)
    rows = []
    for c, ov in zip(views, overlap):
        r = {"root": c.root, "label": c.label}
        if "pi" in c.meta:
            r["pi"] = c.meta["pi"]
        r.update(extract(c, ov))
        rows.append(r)
    return rows


def write_csv(rows: List[Dict], path: str) -> None:
    if not rows:
        raise ValueError("no rows to write")
    cols = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if isinstance(v, float) and math.isnan(v) else v) for k, v in r.items()})
