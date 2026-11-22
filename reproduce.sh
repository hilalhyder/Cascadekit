#!/usr/bin/env bash
# One-command reproduction (also used as the Code Ocean capsule entry point).
#   bash reproduce.sh            tests, quickstart, and the full simulation study (about 30 min on 14 cores)
#   bash reproduce.sh --quick    tests, quickstart, and a 1-seed smoke run of the study
set -euo pipefail
pip install -e ".[dev]"
pytest -q
python examples/quickstart.py --out results
if [[ "${1:-}" == "--quick" ]]; then
  python studies/simulation_study.py --out results/quick --quick
  python studies/make_figures.py --results results/quick
  exit 0
fi
python studies/simulation_study.py --out results/study          # E1-E6 (710 runs)
python studies/make_figures.py --results results/study          # figures 3-6, tables.md
python studies/followup_checks.py > results/study/followup_checks.txt
python studies/pool_diagnostic.py > results/study/pool_diagnostic.txt
python studies/reuse_scaling.py --out results/reuse_scaling     # corpus-size experiment (25 runs)
python studies/paper_figures.py --results results/study --scaling results/reuse_scaling   # figures 1, 2, 7-9

# E7: real organic cascades (Section 6.7). Downloads PHEME (figshare, CC BY 4.0) and the SNAP
# Higgs retweets into ../data/raw on first run; cascade files go to ../data/cascades.
DATA=${DATA:-../data}
if [[ ! -d $DATA/raw/pheme/all-rnr-annotated-threads ]]; then
  mkdir -p $DATA/raw/pheme
  curl -sL -o $DATA/raw/pheme/PHEME_veracity.tar.bz2 https://ndownloader.figshare.com/files/11767817
  tar -xzf $DATA/raw/pheme/PHEME_veracity.tar.bz2 -C $DATA/raw/pheme   # gzip despite the name
fi
if [[ ! -f $DATA/raw/higgs/higgs-activity_time.txt.gz ]]; then
  mkdir -p $DATA/raw/higgs
  curl -sL -o $DATA/raw/higgs/higgs-activity_time.txt.gz https://snap.stanford.edu/data/higgs-activity_time.txt.gz
fi
python studies/real_data.py pheme --raw $DATA/raw/pheme/all-rnr-annotated-threads --out $DATA/cascades/pheme.jsonl.gz
python studies/real_data.py higgs --raw $DATA/raw/higgs/higgs-activity_time.txt.gz --out $DATA/cascades/higgs.jsonl.gz
python studies/semi_synthetic.py --cascades $DATA/cascades/pheme.jsonl.gz --out results/semi/pheme
python studies/semi_synthetic.py --cascades $DATA/cascades/higgs.jsonl.gz --out results/semi/higgs
python studies/semi_synthetic.py --cascades sim:3500 --dataset simulated --out results/semi/simulated
# E7 robustness: Higgs trees rebuilt with 6 h and 72 h windows (Section 6.7)
for w in 6 72; do
  python studies/real_data.py higgs --raw $DATA/raw/higgs/higgs-activity_time.txt.gz --out $DATA/cascades/higgs_w$w.jsonl.gz --window $w
  python studies/semi_synthetic.py --cascades $DATA/cascades/higgs_w$w.jsonl.gz --dataset higgs_w$w --out results/semi/higgs_w$w --exps strategy,share
done
python studies/semi_figures.py --results results/semi                 # figure 10 (Section 6.7)
# E8: the evasion comparison with three classifiers (Section 6.7)
(cd studies && python classifier_check.py --background sim --out ../results/classifiers/simulated.csv \
  && python classifier_check.py --background ../$DATA/cascades/pheme.jsonl.gz --out ../results/classifiers/pheme.csv \
  && python classifier_check.py --background ../$DATA/cascades/higgs.jsonl.gz --out ../results/classifiers/higgs.csv)
