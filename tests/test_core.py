import gzip
import json
import math
import os
import random

import networkx as nx
import pytest

from cascadekit import Cascade, Node, extract, extract_all, simulate_corpus, structural_virality
from cascadekit.build import assign_parents, build_bluesky, build_telegram
from cascadekit.cascade import cascades_from_jsonl, cascades_to_jsonl
from cascadekit.cli import main as cli
from cascadekit.features import FEATURES, wiener_index


def star(k):
    return Cascade("r", [Node("r", "a0", 0.0)] + [Node(f"n{i}", f"a{i}", float(i), "r") for i in range(1, k + 1)])


def chain(k):
    return Cascade("r", [Node("r", "a0", 0.0)] + [Node(f"n{i}", f"a{i}", float(i), "r" if i == 1 else f"n{i-1}")
                                                   for i in range(1, k + 1)])


# ------------------------------------------------------------- data structure

def test_parents_must_precede_children():
    c = Cascade("r", [Node("r", "a", 0.0), Node("x", "b", 5.0, "y"), Node("y", "c", 1.0, "r")])
    assert [n.id for n in c.nodes] == ["r", "y", "x"]          # time order
    assert c.nodes[2].parent == "y"
    c2 = Cascade("r", [Node("r", "a", 0.0), Node("x", "b", 1.0, "missing")])
    assert c2.nodes[1].parent == "r" and c2.nodes[1].rule == "item"


def test_root_must_be_first():
    with pytest.raises(ValueError):
        Cascade("r", [Node("x", "a", 0.0)])


def test_prefix_and_window():
    c = chain(10)
    assert c.prefix(3).size == 3
    assert c.until(4.5).size == 4
    assert c.prefix(3).depths()[-1] == 3


def test_roundtrip(tmp_path):
    cs = simulate_corpus(5, 5, seed=1)
    p = tmp_path / "c.jsonl.gz"
    cascades_to_jsonl(cs, str(p))
    back = cascades_from_jsonl(str(p))
    assert [c.to_dict() for c in back] == [c.to_dict() for c in cs]


def test_anonymise_hides_ids_keeps_shape():
    c = simulate_corpus(1, 1, seed=2)[0]
    a = c.anonymised("salt")
    assert a.size == c.size and a.depths() == c.depths()
    assert not ({n.account for n in a.nodes} & {n.account for n in c.nodes})


# ------------------------------------------------------------- features

@pytest.mark.parametrize("seed", range(5))
def test_wiener_matches_networkx(seed):
    c = simulate_corpus(1, 1, seed=seed)[0]
    g = c.to_networkx().to_undirected()
    assert wiener_index(c.parent_index()) == nx.wiener_index(g)


def test_structural_virality_extremes():
    # star with k leaves: mean distance = 2 - 2/(k+1)... check against networkx
    for c in (star(20), chain(20)):
        n = len(c.nodes)
        assert math.isclose(structural_virality(c), nx.wiener_index(c.to_networkx().to_undirected()) / (n * (n - 1) / 2))
    assert structural_virality(chain(20)) > structural_virality(star(20))


def test_feature_names_complete():
    row = extract(star(5))
    assert set(FEATURES) <= set(row)
    assert row["root_share"] == 1.0 and row["depth"] == 1


def test_regular_vs_bursty_timing():
    reg = Cascade("r", [Node("r", "a", 0.0)] + [Node(f"n{i}", f"a{i}", 10.0 * i, "r") for i in range(1, 30)])
    rng = random.Random(0)
    t, nodes = 0.0, [Node("r", "a", 0.0)]
    for i in range(1, 30):
        t += rng.expovariate(1 / 10) ** 2
        nodes.append(Node(f"n{i}", f"a{i}", t, "r"))
    bursty = Cascade("r", nodes)
    assert extract(reg)["burstiness"] < extract(bursty)["burstiness"]


def test_reuse_features_detect_shared_pool():
    rows = extract_all(simulate_corpus(150, 150, pi_range=(0.3, 0.6), seed=3))
    for f in ("reuse_overlap_max", "reuse_shared_top5"):
        org = [r[f] for r in rows if r["label"] == "organic"]
        amp = [r[f] for r in rows if r["label"] == "amplified"]
        assert sum(amp) / len(amp) > sum(org) / len(org)


def test_reuse_features_hold_up_in_large_corpora():
    """Regression for 0.2.0: raw reuse counts lost the campaign signal as the corpus grew,
    because busy ordinary users appear in ever more cascades. The weighted overlap must not."""
    import statistics as st

    def gap(n_org):
        rows = extract_all(simulate_corpus(n_org, 60, pi_range=(0.1, 0.1), seed=4))
        org = [r["reuse_overlap_max"] for r in rows if r["label"] == "organic"]
        amp = [r["reuse_overlap_max"] for r in rows if r["label"] == "amplified"]
        return st.median(amp) - st.median(org)
    small, large = gap(60), gap(1500)
    assert small > 0 and large > 0.5 * small


def test_account_overlap_by_hand():
    import math

    from cascadekit.features import account_overlap

    def casc(root, accts):
        return Cascade(root, [Node(root, "x", 0.0, None)] + [Node(f"{root}{i}", a, float(i + 1), root)
                                                             for i, a in enumerate(accts)])
    cs = [casc("p", ["a", "b", "u1"]), casc("q", ["a", "b", "u2"]), casc("r", ["u3", "u4"]),
          casc("s", ["u5"])]
    ov = account_overlap(cs, k=2)
    w = math.log(4 / 2) / math.log(4)                      # weight of a and b (in 2 of 4 cascades)
    assert ov[0]["reuse_shared_max"] == pytest.approx(2 * w * w)
    assert ov[0]["reuse_overlap_max"] == pytest.approx(2 * w * w / (2 * w * w + 1))
    assert ov[0]["reuse_shared_top5"] == pytest.approx(w * w)    # mean over k=2; the second is 0
    assert ov[2]["reuse_overlap_max"] == 0.0 and ov[2]["reuse_shared_max"] == 0.0
    assert math.isnan(extract(cs[0])["reuse_overlap_max"])       # needs a corpus


# ------------------------------------------------------------- simulation

def test_simulation_is_reproducible_and_labelled():
    a = simulate_corpus(20, 20, seed=9)
    b = simulate_corpus(20, 20, seed=9)
    assert [c.to_dict() for c in a] == [c.to_dict() for c in b]
    assert {c.label for c in a} == {"organic", "amplified"}
    for c in a:
        if c.label == "amplified":
            assert 0.05 < c.meta["pi"] < 0.9


def test_amplified_cascades_are_shallower():
    rows = extract_all(simulate_corpus(150, 150, seed=4))
    mean = lambda lab, f: sum(r[f] for r in rows if r["label"] == lab) / sum(1 for r in rows if r["label"] == lab)
    assert mean("amplified", "root_share") > mean("organic", "root_share")
    assert mean("amplified", "interarrival_cv") != mean("organic", "interarrival_cv")


# ------------------------------------------------------------- reconstruction

def test_assign_parents_rules():
    evs = [("x1", "u1", 1.0), ("x2", "u2", 2.0), ("x3", "u3", 3.0)]
    item = {e[0]: "root" for e in evs}
    follows = {"u2": {"u1"}, "u3": set()}.get
    out = assign_parents(evs, item, lambda a: follows(a) or set(), via_of={"x3": "x2"})
    assert out == {"x1": ("root", "item"), "x2": ("x1", "follow"), "x3": ("x2", "via")}


def _write(path, recs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wt") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")


def test_build_bluesky(tmp_path):
    root = "at://did:root/app.bsky.feed.post/p0"
    t = 1_760_000_000_000_000
    recs = [{"t": "post", "did": "did:root", "rkey": "p0", "ts": t, "langs": ["hi"], "text": "x"}]
    for i in range(12):
        recs.append({"t": "repost", "did": f"did:u{i}", "rkey": f"r{i}", "ts": t + (i + 1) * 10**6, "subject": root,
                     "via": f"at://did:u{i-1}/app.bsky.feed.repost/r{i-1}" if i == 5 else None})
    recs.append({"t": "post", "did": "did:q", "rkey": "q", "ts": t + 50 * 10**6, "quote": root, "langs": ["en"]})
    recs.append({"t": "repost", "did": "did:z", "rkey": "rz", "ts": t + 60 * 10**6,
                 "subject": "at://did:q/app.bsky.feed.post/q"})
    recs.append({"t": "follow", "did": "did:u3", "rkey": "f", "ts": 1, "subject": "did:u2"})
    recs.append({"t": "acct", "did": "did:u7", "ts": 2, "status": "takendown"})
    _write(str(tmp_path / "2026/01/01/00.jsonl.gz"), recs)
    cs = build_bluesky(str(tmp_path), min_size=5)
    assert len(cs) == 1
    c = cs[0]
    assert c.size == 14 and c.complete and c.meta["takedown_accounts"] == 1
    by = {n.id: n for n in c.nodes}
    assert by["at://did:u3/app.bsky.feed.repost/r3"].parent == "at://did:u2/app.bsky.feed.repost/r2"
    assert by["at://did:u5/app.bsky.feed.repost/r5"].rule == "via"
    assert by["at://did:z/app.bsky.feed.repost/rz"].parent == "at://did:q/app.bsky.feed.post/q"


def test_build_telegram(tmp_path):
    _write(str(tmp_path / "messages/100.jsonl.gz"),
           [{"chan": 100, "msg": 5, "date": "2026-07-01T10:00:00+00:00", "views": 900, "forwards": 40}])
    for c in range(200, 212):
        recs = [{"chan": c, "msg": 1, "date": f"2026-07-01T{11 + (c - 200) // 4:02d}:{(c * 7) % 60:02d}:00+00:00",
                 "fwd_chan": 100, "fwd_post": 5}]
        if c > 205:
            recs.append({"chan": c, "msg": 0, "date": "2026-06-01T00:00:00+00:00", "fwd_chan": c - 3, "fwd_post": 9})
        _write(str(tmp_path / f"messages/{c}.jsonl.gz"), recs)
    cs = build_telegram(str(tmp_path), min_size=5)
    assert len(cs) == 1 and cs[0].size == 12 and cs[0].meta["root_forwards_total"] == 40
    assert any(n.rule == "follow" for n in cs[0].nodes[1:])


# ------------------------------------------------------------- CLI

def test_cli_end_to_end(tmp_path, capsys):
    sim, feats = str(tmp_path / "sim.jsonl.gz"), str(tmp_path / "f.csv")
    assert cli(["simulate", "--organic", "20", "--amplified", "20", "--out", sim, "--seed", "1"]) == 0
    assert cli(["features", sim, "--out", feats]) == 0
    assert cli(["features", sim, "--out", feats, "--prefix", "10"]) == 0
    assert cli(["info", sim]) == 0
    lines = open(feats).read().splitlines()
    assert len(lines) == 41 and lines[0].startswith("root,label,pi,size")


# ------------------------------------------------------------- evasion strategies

from cascadekit import SimConfig  # noqa: E402

STRATS = [
    {},
    {"amp_timing": "poisson"},
    {"amp_timing": "mimic"},
    {"amp_timing": "mimic", "amp_attach": "mimic"},
    {"amp_timing": "regular", "amp_attach": "mimic"},
    {"amp_timing": "mimic", "amp_attach": "mimic", "rotate_accounts": True, "pool_size": 5000},
    {"amp_attach": "embedded"},
    {"amp_attach": "embedded", "rotate_accounts": True, "pool_size": 5000},
]


@pytest.mark.parametrize("kw", STRATS)
def test_strategies_give_valid_trees(kw):
    cs = simulate_corpus(15, 15, pi_range=(0.3, 0.3), cfg=SimConfig(**kw), seed=5)
    for c in cs:
        assert all(n.rule == "sim" for n in c.nodes[1:])          # no parent had to be repaired
        pos = {n.id: n for n in c.nodes}
        assert all(pos[n.parent].ts <= n.ts for n in c.nodes[1:])
        if c.label == "amplified":
            n_amp = sum(1 for n in c.nodes if n.id.startswith("m"))
            assert n_amp == c.meta["n_amplified"] >= 1


def test_mimic_hides_structure_and_rotation_hides_reuse():
    def mean_feat(kw, f):
        rows = extract_all(simulate_corpus(100, 100, pi_range=(0.3, 0.3), cfg=SimConfig(**kw), seed=6))
        amp = [r[f] for r in rows if r["label"] == "amplified"]
        return sum(amp) / len(amp)
    assert mean_feat(STRATS[3], "root_share") < mean_feat(STRATS[0], "root_share")
    assert mean_feat(STRATS[5], "reuse_overlap_max") < mean_feat(STRATS[3], "reuse_overlap_max")


def test_bad_strategy_rejected():
    with pytest.raises(ValueError):
        SimConfig(amp_timing="sneaky")


def test_embedded_control_keeps_the_organic_tree():
    import random as _r
    from cascadekit.simulate import simulate_cascade
    org = simulate_cascade(SimConfig(), _r.Random(11), "x")
    emb = simulate_cascade(SimConfig(pi=0.3, amp_attach="embedded"), _r.Random(11), "x")
    assert emb.size == org.size and emb.depths() == org.depths()
    assert emb.label == "amplified" and abs(emb.meta["pi"] - 0.3) < 0.06


def test_inject_into_real_tree():
    import random
    from cascadekit import Cascade, Node, SimConfig, empirical_samplers, inject
    base = Cascade("r", [Node("r", "A", 0.0)] + [Node(f"x{i}", f"U{i % 7}", 60.0 * i, "r" if i < 5 else f"x{i - 4}")
                                                  for i in range(1, 31)], platform="real")
    rng = random.Random(1)
    org = inject(base, SimConfig(pi=0.0), rng)
    assert org.label == "organic" and [n.id for n in org.nodes] == [n.id for n in base.nodes]
    sm = empirical_samplers([base], rng, host=base)
    for kw in ({}, {"amp_timing": "mimic", "amp_attach": "mimic", "rotate_accounts": True}, {"amp_attach": "embedded"},
               {"amp_attach": "empirical", "rotate_accounts": True}):
        c = inject(base, SimConfig(pi=0.3, **kw), rng, samplers=sm)
        amp = [n for n in c.nodes if n.id.startswith("m")]
        assert c.label == "amplified" and amp and c.platform == "real"
        assert abs(c.meta["pi"] - len(amp) / c.size) < 1e-3
        assert all(n.ts >= c.nodes[0].ts for n in c.nodes)
    assert len(base.nodes) == 31                                  # base left untouched
    with pytest.raises(ValueError):
        inject(base, SimConfig(pi=0.3, amp_attach="empirical"), rng)


def test_features_do_not_depend_on_hash_seed():
    """Set iteration order follows PYTHONHASHSEED; the features must not."""
    import subprocess
    import sys
    code = ("import hashlib, json; from cascadekit import simulate_corpus, extract_all, SimConfig; "
            "cs = simulate_corpus(40, 40, cfg=SimConfig(rotate_accounts=True, pool_size=300), seed=5); "
            "print(hashlib.sha256(json.dumps(extract_all(cs), default=str).encode()).hexdigest())")
    outs = {subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True,
                           env={**os.environ, "PYTHONHASHSEED": str(seed)}).stdout for seed in (1, 2, 3)}
    assert len(outs) == 1
