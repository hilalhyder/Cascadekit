# Changelog

## 0.4.0 (2026-11-19)
- Semi-synthetic study on real cascades. `inject()` adds a campaign to a real organic
  cascade by the simulator's rules; `empirical_samplers()` returns `Samplers` fitted to real
  data (organic accounts, reaction delays, (parent depth, delay) edges, reply counts), with
  `host=` taking all but accounts from the cascade that receives the campaign.
- New attacker `amp_attach="empirical"` (with `inject` only): each amplifier reshare copies an
  edge of its host cascade and picks a parent at that depth in proportion to its replies + 1.
- `studies/real_data.py` builds anonymised cascade files from PHEME and the SNAP Higgs
  retweets; `studies/semi_synthetic.py` runs E7 (`--cascades sim:<n>` for the matched
  simulated baseline). `reproduce.sh` downloads both datasets and runs E7.
- `semi_synthetic.py` also runs a base-rate experiment (200 amplified against 200 or 1,800
  organic cascades) and takes `--exps`; `studies/semi_figures.py` draws figure 10;
  `studies/classifier_check.py` (E8) repeats the evasion comparison with gradient boosting
  and logistic regression. `reproduce.sh` runs all of them, plus Higgs windows of 6 h and 72 h.
- Determinism fix: `account_overlap()` sums account weights with `math.fsum`, so reuse
  features no longer depend on set order, which follows Python's per-process string hashing.
  Values change only in the last bits; every published result reproduces unchanged (seven
  single-feature AUROCs in `pool_diagnostic.csv` move by 0.00001). `classifier_check.py`
  results, which depend on gradient boosting's binning, are now identical from run to run.
- `simulate_corpus` and `simulate_cascade` output is unchanged.

## 0.3.0 (2026-11-15)
- Account-reuse features replaced. `reuse_mean` and `reuse_share_5plus` counted raw
  appearances in other cascades, so they measured how active ordinary users were and lost
  the campaign signal as the corpus grew (AUROC 0.858 with 400 cascades, 0.547 with
  10,000). New `account_overlap()` gives four corpus-size-adjusted features,
  `reuse_overlap_max`, `reuse_overlap_top5`, `reuse_shared_max` and `reuse_shared_top5`,
  based on rarity-weighted (IDF) overlap of account sets between cascades. 31 features in total.
- `extract(c, overlap=None)` now takes the cascade's entry from `account_overlap()` in place of `counts`.
- Simulation study: 10 seeds per setting by default, including the base-rate experiment
  (previously 5, and 3 for base rates).
- Base-rate experiment now includes the full mimic + rotation strategy; `--strategy` runs one
  strategy only. New `studies/pool_diagnostic.py` explains the dip in reuse AUROC at a
  2,000-account rotation pool.
- Sensitivity experiment (`--only sensitivity`): four simulator parameters moved one at a
  time for three settings; table E6 in `tables.md`. Result rows gain `param` and `value` columns.
- `studies/reuse_scaling.py` (raw against rarity-weighted reuse as the corpus grows) and
  `studies/paper_figures.py` (example cascades, reuse scaling, attacker trade-off, pool signals,
  sensitivity). `pool_diagnostic.py` also writes `pool_diagnostic.csv`.

## 0.2.0 (2026-11-15)
- Simulator: evasion strategies. `amp_timing` ("regular", "poisson", "mimic"), `amp_attach`
  ("hubs", "mimic", "embedded") and `rotate_accounts`. Defaults reproduce 0.1.0 output exactly.
- `studies/simulation_study.py` and `studies/make_figures.py`: the full simulation study
  (amplified share, early detection, organic virality, evasion strategies and their cost,
  base rates).

## 0.1.0 (2026-11-10)
- First release: Bluesky and Telegram collectors, cascade reconstruction with stored
  parent rules, 29 cascade features in four groups, synthetic corpus generator,
  anonymisation, command-line interface, time-depth plot.
