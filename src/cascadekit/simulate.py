"""Synthetic cascades with known ground truth.

Organic spread is a continuous-time branching process (Galton-Watson tree with
negative-binomial offspring and log-normal reaction delays). Amplification injects
reshares from a small, reused pool of accounts at near-regular intervals, attached to
the root or to a few amplifier hubs. The amplification share ``pi`` is the fraction
of reshares produced by the amplifier stream; organic cascades have ``pi = 0``.
Amplifier node ids start with ``m``; all other reshares are organic.

Evasion strategies let the campaign hide: ``amp_timing`` ("regular", "poisson",
"mimic"), ``amp_attach`` ("hubs", "mimic") and ``rotate_accounts`` with a larger
``pool_size``. With both set to "mimic", amplifiers reshare from random earlier nodes
after organic reaction delays. ``amp_attach="embedded"`` is a negative control: the
tree is purely organic and campaign accounts only replace some of its accounts, so
structure and timing carry no signal by construction.

    from cascadekit.simulate import SimConfig, simulate_corpus
    cascades = simulate_corpus(n_organic=500, n_amplified=500, seed=7)

The default parameters are illustrative, not fitted to any platform. Calibrate them
against real cascades (sizes, depths, delays, account activity) before drawing
conclusions from synthetic results.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Callable, List, Optional, Sequence, Tuple

from .cascade import Cascade, Node


@dataclass
class SimConfig:
    # organic branching
    root_mean: float = 6.0          # mean direct reshares of the root post
    mean_offspring: float = 0.8     # mean reshares triggered by each reshare (m < 1: subcritical)
    dispersion: float = 0.5         # negative-binomial k; smaller = heavier tail
    delay_median_s: float = 1800.0  # median reaction delay
    delay_sigma: float = 1.3        # log-normal sigma of delays
    min_size: int = 10              # resample organic trees smaller than this
    max_size: int = 3000
    population: int = 200_000       # organic accounts drawn from this many
    activity_exponent: float = 0.7  # Zipf exponent of organic activity: a few heavy users recur often
    # amplification
    pi: float = 0.0                 # target share of amplified reshares
    pool_size: int = 150            # amplifier accounts per campaign (reused across cascades)
    n_hubs: int = 3                 # amplifier hubs that other amplifiers attach to
    root_attach_p: float = 0.7      # P(amplifier attaches to root rather than a hub)
    amp_start_median_s: float = 300.0
    amp_interval_s: float = 20.0    # near-regular spacing of amplifier reshares
    amp_jitter: float = 0.2         # relative jitter of that spacing
    amp_followers_mean: float = 0.15  # organic reshares triggered by each amplifier reshare
    # evasion strategies (defaults reproduce the naive campaign)
    amp_timing: str = "regular"     # "regular": fixed spacing with jitter; "poisson": exponential gaps
                                    # with the same mean; "mimic": each amplifier waits an organic
                                    # reaction delay after its parent
    amp_attach: str = "hubs"        # "hubs": the root or a few amplifier hubs; "mimic": a random
                                    # earlier node, as an ordinary user would; "embedded": no reshares
                                    # are added, campaign accounts simply take the place of a share pi
                                    # of the organic reshares (a negative control: the tree is organic);
                                    # "empirical" (``inject`` only): each amplifier copies a real
                                    # parent-child edge, a parent depth and a delay drawn together,
                                    # and picks a parent at that depth in proportion to its replies + 1
    rotate_accounts: bool = False   # draw amplifier accounts at random from the pool instead of
                                    # always starting from the same core accounts

    def __post_init__(self):
        if self.amp_timing not in ("regular", "poisson", "mimic"):
            raise ValueError("amp_timing must be 'regular', 'poisson' or 'mimic'")
        if self.amp_attach not in ("hubs", "mimic", "embedded", "empirical"):
            raise ValueError("amp_attach must be 'hubs', 'mimic', 'embedded' or 'empirical'")


def _poisson(rng: random.Random, lam: float) -> int:
    if lam <= 0:
        return 0
    if lam > 50:
        return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))
    l, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= l:
            return k
        k += 1


def _negbin(rng: random.Random, mean: float, k: float) -> int:
    """Negative binomial as a gamma-Poisson mixture with mean ``mean``, dispersion ``k``."""
    if mean <= 0:
        return 0
    return _poisson(rng, rng.gammavariate(k, mean / k))


def _delay(rng, median, sigma):
    return math.exp(math.log(median) + sigma * rng.gauss(0, 1))


def _grow(rng, cfg, queue, nodes, mean_for, organic_acct, delay=None, max_size=None, count=None):
    """Breadth-first growth of organic reshares from the (id, ts, mean) items in ``queue``.
    ``delay()`` draws a reaction delay (default: the log-normal of ``cfg``); ``count()``, if
    given, draws each node's number of reactions instead of the negative binomial."""
    delay = delay or (lambda: _delay(rng, cfg.delay_median_s, cfg.delay_sigma))
    max_size = cfg.max_size if max_size is None else max_size
    while queue and len(nodes) <= max_size:
        pid, pts, mean = queue.pop(0)
        for _ in range(count() if count else _negbin(rng, mean, cfg.dispersion)):
            if len(nodes) > max_size:
                break
            nid = f"n{len(nodes)}"
            ts = pts + delay()
            nodes.append(Node(nid, organic_acct(), ts, pid, "sim"))
            queue.append((nid, ts, mean_for))


_CUM_CACHE = {}


def _zipf_cum(n, s):
    key = (n, s)
    if key not in _CUM_CACHE:
        acc, cum = 0.0, []
        for r in range(1, n + 1):
            acc += r ** -s
            cum.append(acc)
        _CUM_CACHE[key] = cum
    return _CUM_CACHE[key]


def simulate_cascade(cfg: SimConfig, rng: random.Random, cid: str,
                     amp_pool: Optional[Sequence[str]] = None, t0: float = 1.7e9) -> Cascade:
    cum = _zipf_cum(cfg.population, cfg.activity_exponent)
    ranks = range(cfg.population)
    organic_acct = lambda: f"u{rng.choices(ranks, cum_weights=cum)[0]}"
    for _ in range(1000):                                   # resample tiny organic trees
        nodes = [Node(cid, f"src_{cid}", t0)]
        _grow(rng, cfg, [(cid, t0, cfg.root_mean)], nodes, cfg.mean_offspring, organic_acct)
        if len(nodes) - 1 >= cfg.min_size:
            break
    meta = _inject(cfg, rng, cid, nodes, t0, amp_pool, organic_acct,
                   lambda: _delay(rng, cfg.delay_median_s, cfg.delay_sigma), cfg.max_size)
    label = "amplified" if cfg.pi > 0 else "organic"
    return Cascade(cid, nodes, platform="synthetic", label=label, meta=meta)


def _inject(cfg, rng, cid, nodes, t0, amp_pool, organic_acct, delay, max_size, edge=None, offspring=None):
    """Add a campaign with share ``cfg.pi`` to the organic tree ``nodes`` (root first, in
    time order) in place, and return the cascade's ground-truth meta."""
    n_org = len(nodes) - 1
    meta = {"pi": 0.0, "n_organic": n_org}
    if cfg.pi > 0 and cfg.amp_attach == "embedded":
        pool = list(amp_pool) if amp_pool else [f"a{j}" for j in range(cfg.pool_size)]
        n_amp = min(n_org, max(1, round(cfg.pi * n_org)))
        chosen = rng.sample(range(1, len(nodes)), n_amp)
        if cfg.rotate_accounts and n_amp <= len(pool):
            accts = rng.sample(pool, n_amp)
        elif cfg.rotate_accounts:
            accts = [rng.choice(pool) for _ in range(n_amp)]
        else:
            accts = [pool[j] if j < len(pool) else rng.choice(pool) for j in range(n_amp)]
        rename = {}
        for j, idx in enumerate(chosen):
            rename[nodes[idx].id] = f"m{j}"
            nodes[idx].account = accts[j]
        for n in nodes:
            n.id, n.parent = rename.get(n.id, n.id), rename.get(n.parent, n.parent)
        meta.update({"pi": round(n_amp / n_org, 4), "n_organic": n_org - n_amp, "n_amplified": n_amp,
                     "n_organic_triggered_by_amp": 0})
    elif cfg.pi > 0:
        pool = list(amp_pool) if amp_pool else [f"a{j}" for j in range(cfg.pool_size)]
        n_amp = max(1, round(cfg.pi / (1 - cfg.pi) * n_org))
        accts = None                                        # None: fixed order, core accounts first
        if cfg.rotate_accounts:
            accts = (rng.sample(pool, n_amp) if n_amp <= len(pool)
                     else [rng.choice(pool) for _ in range(n_amp)])
        t = t0 + _delay(rng, cfg.amp_start_median_s, 0.5)
        hubs, amp_nodes = [], []
        ts_of = {cid: t0}
        if cfg.amp_attach == "empirical":
            if edge is None:
                raise ValueError("amp_attach='empirical' needs an edge sampler (see empirical_samplers)")
            depth_of, kids, by_depth = {}, {}, {}
            for n in nodes:                                 # parents precede children
                d = 0 if n.parent is None else depth_of.get(n.parent, 0) + 1
                depth_of[n.id] = d
                by_depth.setdefault(d, []).append(n)
                if n.parent is not None:
                    kids[n.parent] = kids.get(n.parent, 0) + 1
        for j in range(n_amp):
            nid = f"m{j}"
            if cfg.amp_attach == "empirical":
                # Copy a real edge: a parent depth and a delay drawn together; within that depth,
                # reply where others already reply (weight = replies + 1).
                d, gap = edge()
                d = min(d, max(by_depth))
                while d not in by_depth:
                    d -= 1
                cands = by_depth[d]
                par = rng.choices(cands, weights=[kids.get(n.id, 0) + 1 for n in cands])[0]
                acct = accts[j] if accts is not None else (pool[j] if j < len(pool) else rng.choice(pool))
                node = Node(nid, acct, par.ts + gap, par.id, "sim")
                nodes.append(node)
                kids[par.id] = kids.get(par.id, 0) + 1
                depth_of[nid] = d + 1
                by_depth.setdefault(d + 1, []).append(node)
                ts_of[nid] = node.ts
                amp_nodes.append((nid, node.ts))
                continue
            if cfg.amp_attach == "mimic":
                # Behave like an ordinary user: reshare from any node that already exists.
                if cfg.amp_timing == "mimic":
                    par = rng.choice(nodes)
                else:
                    earlier = [n for n in nodes if n.ts <= t]
                    par = rng.choice(earlier) if earlier else nodes[0]
                parent, pts = par.id, par.ts
            elif hubs and len(hubs) >= cfg.n_hubs and rng.random() > cfg.root_attach_p:
                parent = rng.choice(hubs)
                pts = ts_of[parent]
            else:
                parent, pts = cid, t0
            acct = accts[j] if accts is not None else (pool[j] if j < len(pool) else rng.choice(pool))
            if cfg.amp_timing == "mimic":
                ts = pts + delay()
            else:
                ts = max(t, pts)
                gap = (rng.expovariate(1.0 / cfg.amp_interval_s) if cfg.amp_timing == "poisson"
                       else cfg.amp_interval_s * (1 + cfg.amp_jitter * rng.uniform(-1, 1)))
                t += gap
            nodes.append(Node(nid, acct, ts, parent, "sim"))
            ts_of[nid] = ts
            amp_nodes.append((nid, ts))
            if len(hubs) < cfg.n_hubs:
                hubs.append(nid)
        # Amplification raises visibility, so a few organic users react to amplifier reshares:
        # by the simulator's rule, or, given ``offspring()``, as often as a real reshare draws replies.
        follow_q = [(nid, ts, cfg.amp_followers_mean) for nid, ts in amp_nodes]
        before = len(nodes)
        _grow(rng, replace(cfg, dispersion=1.0), follow_q, nodes, cfg.mean_offspring, organic_acct,
              delay, max_size, count=offspring)
        meta.update({"pi": round(n_amp / (len(nodes) - 1), 4), "n_amplified": n_amp,
                     "n_organic_triggered_by_amp": len(nodes) - before})
    return meta


def simulate_corpus(n_organic: int = 500, n_amplified: int = 500,
                    pi_range=(0.2, 0.6), n_campaigns: int = 10,
                    cfg: Optional[SimConfig] = None, seed: int = 0) -> List[Cascade]:
    """A labelled corpus. Amplified cascades are spread over ``n_campaigns`` campaigns,
    each with its own reused account pool, and draw ``pi`` uniformly from ``pi_range``."""
    cfg = cfg or SimConfig()
    rng = random.Random(seed)
    pools = [[f"c{c}_a{j}" for j in range(cfg.pool_size)] for c in range(n_campaigns)]
    out = []
    for i in range(n_organic):
        out.append(simulate_cascade(replace(cfg, pi=0.0), rng, f"org{i}", t0=1.7e9 + i * 3600))
    for i in range(n_amplified):
        camp = i % n_campaigns
        c = simulate_cascade(replace(cfg, pi=rng.uniform(*pi_range)), rng, f"amp{i}",
                             amp_pool=pools[camp], t0=1.7e9 + i * 3600)
        c.meta["campaign"] = camp
        out.append(c)
    rng.shuffle(out)
    return out


@dataclass
class Samplers:
    """Draws fitted to real cascades, for ``inject``.

    account()    account of an organic user (drawn with observed activity)
    delay()      a parent-to-child reaction delay in seconds
    edge()       one observed edge as (depth of its parent, its delay), drawn together
    offspring()  the number of reactions an ordinary (non-root) reshare receives
    """
    account: Callable[[], str]
    delay: Callable[[], float]
    edge: Callable[[], Tuple[int, float]]
    offspring: Callable[[], int]


def empirical_samplers(corpus: Sequence[Cascade], rng: random.Random,
                       host: Optional[Cascade] = None) -> Samplers:
    """Fit ``Samplers`` to a real corpus. With ``host``, delays, edges and offspring come from
    that one cascade (an attacker copying the thread it joins), falling back to the corpus
    when the host has no usable edges; accounts always come from the whole corpus."""
    def tally(cs):
        accts, edges, kids = [], [], []
        for c in cs:
            ts = {n.id: n.ts for n in c.nodes}
            depth = c.depths()
            pos = {n.id: i for i, n in enumerate(c.nodes)}
            out = [0] * len(c.nodes)
            for n in c.nodes[1:]:
                if n.account is not None:
                    accts.append(n.account)
                out[pos[n.parent]] += 1
                pt = ts.get(n.parent)
                if n.ts is not None and pt is not None and n.ts > pt:
                    edges.append((depth[pos[n.parent]], n.ts - pt))
            kids += out[1:]
        return accts, edges, kids

    accts, edges, kids = tally(corpus)
    if host is not None:
        _, h_edges, h_kids = tally([host])
        if h_edges:
            edges, kids = h_edges, h_kids
    if not accts or not edges or not kids:
        raise ValueError("corpus has no accounts, no non-root reshares or no positive parent-child delays")
    return Samplers(account=lambda: rng.choice(accts), delay=lambda: rng.choice(edges)[1],
                    edge=lambda: rng.choice(edges), offspring=lambda: rng.choice(kids))


def inject(base: Cascade, cfg: SimConfig, rng: random.Random, amp_pool: Optional[Sequence[str]] = None,
           samplers: Optional[Samplers] = None) -> Cascade:
    """Semi-synthetic cascade: a copy of the real (organic) cascade ``base`` with a campaign
    of share ``cfg.pi`` injected by the same rules as ``simulate_cascade``.

    With ``samplers`` (see ``empirical_samplers``), everything that is not the campaign's own
    choice comes from real data: the accounts and delays of organic users who react to
    amplifier reshares, how many such reactions each reshare draws, and the delays of
    mimicking campaigns. ``amp_attach="empirical"`` needs them. Without ``samplers``, the
    simulator's rules apply. Returns ``base`` relabelled as organic when ``cfg.pi`` is 0."""
    nodes = [Node(n.id, n.account, n.ts, n.parent, n.rule) for n in base.nodes]
    t0 = base.start_time()
    nodes[0].ts = t0
    meta = dict(base.meta, pi=0.0, n_organic=len(nodes) - 1)
    if cfg.pi > 0:
        if samplers is None and cfg.amp_attach == "empirical":
            raise ValueError("amp_attach='empirical' needs samplers (see empirical_samplers)")
        sm = samplers
        acct = sm.account if sm else (lambda: f"u{rng.randrange(cfg.population)}")
        delay = sm.delay if sm else (lambda: _delay(rng, cfg.delay_median_s, cfg.delay_sigma))
        meta.update(_inject(cfg, rng, nodes[0].id, nodes, t0, amp_pool, acct, delay,
                            max_size=len(nodes) * 3 + 50, edge=sm.edge if sm else None,
                            offspring=sm.offspring if sm else None))
    label = "amplified" if cfg.pi > 0 else "organic"
    return Cascade(nodes[0].id, nodes, platform=base.platform, complete=base.complete, label=label, meta=meta)
