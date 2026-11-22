"""Command-line interface: ``cascadekit <command> ...``

  collect-bluesky   stream Bluesky posts, reposts and account events (runs until stopped)
  collect-telegram  crawl public Telegram channels and their forwards
  build             reconstruct cascades from collected raw files
  features          compute the cascade fingerprint for every cascade -> CSV
  simulate          generate a labelled synthetic corpus with known amplification
  anonymise         replace account and post ids with salted hashes
  info              summary statistics of a cascade file
"""
from __future__ import annotations

import argparse
import collections
import statistics
import sys

from . import __version__
from .cascade import cascades_from_jsonl, cascades_to_jsonl


def _build(a):
    from .build import build_bluesky, build_telegram
    if a.platform == "bluesky":
        cs = build_bluesky(a.raw, a.min_size, a.fetch_follows)
    else:
        cs = build_telegram(a.raw, a.min_size)
    if a.salt:
        cs = [c.anonymised(a.salt) for c in cs]
    n = cascades_to_jsonl(cs, a.out)
    print(f"{n} cascades with >= {a.min_size} reshares -> {a.out}")


def _features(a):
    from .features import extract_all, write_csv
    cs = cascades_from_jsonl(a.cascades)
    rows = extract_all(cs, prefix_k=a.prefix, window_s=a.window)
    write_csv(rows, a.out)
    print(f"{len(rows)} rows x {len(rows[0]) if rows else 0} columns -> {a.out}")


def _simulate(a):
    from .simulate import SimConfig, simulate_corpus
    cfg = SimConfig(mean_offspring=a.mean_offspring)
    cs = simulate_corpus(a.organic, a.amplified, (a.pi_min, a.pi_max), a.campaigns, cfg, a.seed)
    n = cascades_to_jsonl(cs, a.out)
    print(f"{n} synthetic cascades ({a.organic} organic, {a.amplified} amplified) -> {a.out}")


def _anonymise(a):
    cs = [c.anonymised(a.salt) for c in cascades_from_jsonl(a.cascades)]
    print(f"{cascades_to_jsonl(cs, a.out)} cascades anonymised -> {a.out}")


def _info(a):
    cs = cascades_from_jsonl(a.cascades)
    sizes = [c.size for c in cs]
    rules = collections.Counter(n.rule for c in cs for n in c.nodes[1:])
    print(f"cascades: {len(cs)}   platforms: {dict(collections.Counter(c.platform for c in cs))}")
    print(f"labels: {dict(collections.Counter(c.label for c in cs))}")
    if sizes:
        print(f"size: median {statistics.median(sizes)}, max {max(sizes)}, total reshares {sum(sizes)}")
    print(f"parent rules: {dict(rules)}")
    print(f"complete (root seen): {sum(c.complete for c in cs)}")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # Collectors keep their own argument parsers.
    if argv and argv[0] == "collect-bluesky":
        from .collect.bluesky import main as m
        return m(argv[1:])
    if argv and argv[0] == "collect-telegram":
        from .collect.telegram import main as m
        return m(argv[1:])

    p = argparse.ArgumentParser(prog="cascadekit", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"cascadekit {__version__}")
    sub = p.add_subparsers(dest="cmd", metavar="command")
    sub.add_parser("collect-bluesky", help="see: cascadekit collect-bluesky --help")
    sub.add_parser("collect-telegram", help="see: cascadekit collect-telegram --help")

    b = sub.add_parser("build", help="reconstruct cascades from raw files")
    b.add_argument("platform", choices=["bluesky", "telegram"])
    b.add_argument("--raw", required=True, help="folder written by the collector")
    b.add_argument("--out", required=True, help="output .jsonl or .jsonl.gz")
    b.add_argument("--min-size", type=int, default=10)
    b.add_argument("--fetch-follows", action="store_true", help="Bluesky: fetch follow lists (slow, cached)")
    b.add_argument("--salt", help="anonymise ids with this secret salt")
    b.set_defaults(fn=_build)

    f = sub.add_parser("features", help="cascade fingerprint -> CSV")
    f.add_argument("cascades")
    f.add_argument("--out", required=True)
    g = f.add_mutually_exclusive_group()
    g.add_argument("--prefix", type=int, help="use only the first K reshares (early detection)")
    g.add_argument("--window", type=float, help="use only reshares within this many seconds")
    f.set_defaults(fn=_features)

    s = sub.add_parser("simulate", help="labelled synthetic corpus")
    s.add_argument("--organic", type=int, default=500)
    s.add_argument("--amplified", type=int, default=500)
    s.add_argument("--pi-min", type=float, default=0.2)
    s.add_argument("--pi-max", type=float, default=0.6)
    s.add_argument("--campaigns", type=int, default=10)
    s.add_argument("--mean-offspring", type=float, default=0.8)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--out", required=True)
    s.set_defaults(fn=_simulate)

    an = sub.add_parser("anonymise", help="hash account and post ids")
    an.add_argument("cascades")
    an.add_argument("--salt", required=True)
    an.add_argument("--out", required=True)
    an.set_defaults(fn=_anonymise)

    i = sub.add_parser("info", help="summary of a cascade file")
    i.add_argument("cascades")
    i.set_defaults(fn=_info)

    a = p.parse_args(argv)
    if not getattr(a, "fn", None):
        p.print_help()
        return 1
    a.fn(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
