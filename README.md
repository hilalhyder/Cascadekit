# cascadekit

**Collect social-media diffusion cascades, rebuild them as timed trees, and compute
language-agnostic structural and temporal fingerprints.**

`cascadekit` covers the whole path from raw platform data to a feature table:

| Step | Command | What it does |
| --- | --- | --- |
| Collect | `cascadekit collect-bluesky` | Streams Bluesky posts, reposts, deletions and account takedowns from Jetstream, with resume after restarts |
| | `cascadekit collect-telegram` | Crawls public Telegram channels and their forwards, snowballing to new channels and filtering by script (for example Devanagari or Urdu) |
| Rebuild | `cascadekit build` | Turns raw records into Information Dissemination Trees. Each reshare's parent is chosen by an explicit rule (`via`, `follow`, `item`) that is stored on the node, so results can be checked under each rule |
| Describe | `cascadekit features` | Computes 31 features in four groups (shape, branching, timing, account reuse), on full cascades or on early views (first *k* reshares, first *t* seconds) |
| Simulate | `cascadekit simulate` | Generates labelled synthetic cascades: organic branching plus injected amplification with a known share `pi` |
| Protect | `cascadekit anonymise` | Replaces account and post ids with salted hashes before data is shared |

The core library uses only the Python standard library. Platform collectors and plotting
are optional extras.

## Install

```bash
pip install cascadekit                  # core: build, features, simulate
pip install "cascadekit[bluesky]"       # + Bluesky collector
pip install "cascadekit[telegram]"      # + Telegram collector
pip install "cascadekit[all]"           # everything
```

From source:

```bash
git clone https://github.com/hilalhyder/cascadekit && cd cascadekit
pip install -e ".[dev]" && pytest
```

## Five-minute tour (no platform data needed)

```bash
cascadekit simulate --organic 300 --amplified 300 --out sim.jsonl.gz
cascadekit info sim.jsonl.gz
cascadekit features sim.jsonl.gz --out features.csv
cascadekit features sim.jsonl.gz --out features_k20.csv --prefix 20   # early detection
python examples/quickstart.py --out results/                         # AUC per feature group + figure
```

In Python:

```python
from cascadekit import simulate_corpus, extract_all, structural_virality

cascades = simulate_corpus(n_organic=200, n_amplified=200, seed=1)
rows = extract_all(cascades)               # list of dicts: root, label, pi, 31 features
c = cascades[0]
print(c, structural_virality(c), c.prefix(20).size)
```

## Evasion strategies in the simulator

By default a simulated campaign is naive: regular timing, reshares attached to the
original post or a few hubs, and a small account pool. `SimConfig` can make it hide:

```python
from cascadekit import SimConfig, simulate_corpus

cfg = SimConfig(amp_timing="mimic",      # "regular" | "poisson" | "mimic" (human-like delays)
                amp_attach="mimic",      # "hubs" | "mimic" (random earlier reshare) | "embedded" (control)
                rotate_accounts=True, pool_size=5000)
cascades = simulate_corpus(400, 400, pi_range=(0.1, 0.1), cfg=cfg, seed=0)
```

`amp_attach="embedded"` is a negative control: the tree is purely organic and campaign
accounts only replace some of its accounts, so structure and timing features must score
at chance.

## Simulation study

`studies/` holds a complete study built on the package: detection against the amplified
share, early detection, organic virality, six attacker strategies and what each costs the
attacker, and realistic base rates.

```bash
python studies/simulation_study.py --out results/study      # 10 seeds per setting; use --workers
python studies/make_figures.py --results results/study      # figures, summary.csv, tables.md
python studies/simulation_study.py --out results/quick --quick   # 1-seed smoke run, about 1 minute
```

## Collecting real data

**Bluesky** (run continuously, for example in `tmux` or as a systemd service):

```bash
cascadekit collect-bluesky --out data/bluesky --text-langs hi,ur,ks,en
cascadekit build bluesky --raw data/bluesky --out cascades_bsky.jsonl.gz --fetch-follows
```

**Telegram** (public channels only; get `api_id`/`api_hash` at https://my.telegram.org):

```bash
export TG_API_ID=... TG_API_HASH=...
cascadekit collect-telegram --seeds seeds.txt --since 2026-06-01 --snowball 2
cascadekit build telegram --raw data/telegram --out cascades_tg.jsonl.gz
```

### How parents are reconstructed

Neither platform records the account a reshare came through: a Bluesky repost and a
Telegram forward both point to the original post. `cascadekit` assigns each reshare's
parent using the first rule that applies:

1. `via`: the record names the reshare it was seen through (Bluesky, when present).
2. `follow`: the most recent earlier resharer of the same item whom this account follows
   (Telegram: a channel this channel has forwarded from before).
3. `item`: otherwise, the item being reshared (the root, or a quote post).

The rule is stored on every node. Re-run your analysis per rule to report sensitivity.

## Features

| Group | Features |
| --- | --- |
| shape | size, depth, max_breadth, structural_virality, wiener_index, depth1/2/3plus_share, mean_depth |
| branching | root_share, endogenous_share, mean_offspring, offspring_cv, max_outdeg_nonroot, root_dominance, outdeg_gini, leaf_share |
| timing | duration_s, t10_s, t50_s, t90_s, interarrival_cv, interarrival_entropy, burstiness, median_delay_s, delay_ratio_deep_vs_d1 |
| reuse | reuse_overlap_max, reuse_overlap_top5, reuse_shared_max, reuse_shared_top5, distinct_account_share |

The account-reuse features compare each cascade with the rest of the corpus. A campaign
shows up as the same group of accounts resharing many cascades, while in a large corpus
the busiest ordinary users appear in far more cascades than any campaign account. Each
account is therefore weighted by how rare it is, `log(N / n_a) / log(N)` (N cascades, n_a
of them containing the account), and each cascade is scored by its weighted overlap with
its most similar other cascades: cosine similarity (`reuse_overlap_*`) and the weighted
number of shared accounts (`reuse_shared_*`). Unlike raw reuse counts (0.2.0), these keep
their meaning as the corpus grows. They need a corpus: `extract_all` computes them, while
`extract` on a single cascade returns NaN for them.

Structural virality follows Goel et al. (2016) and is computed in O(n) from the
subtree-size form of the Wiener index.

## Cascade file format

One JSON object per line (optionally gzipped):

```json
{"root": "...", "platform": "bluesky", "complete": true, "label": null, "meta": {...},
 "nodes": [{"id": "...", "account": "...", "ts": 1760000000.0, "parent": null, "rule": null}, ...]}
```

`nodes[0]` is the root; the other nodes are in time order, and every parent comes before
its child. `ts` is in seconds since the Unix epoch.

## Ethics

Collect only public data, get approval from your institution's ethics committee, keep raw
files on encrypted storage, and share only anonymised, text-free cascade files
(`cascadekit anonymise` or `build --salt`).

## Citing

If you use cascadekit, please cite it using `CITATION.cff` (GitHub shows a "Cite this
repository" button).

## Licence

MIT
