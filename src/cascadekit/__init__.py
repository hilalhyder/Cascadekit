"""cascadekit: collect social-media diffusion cascades, rebuild them as timed trees, and
compute language-agnostic structural and temporal fingerprints."""

__version__ = "0.4.0"

from .cascade import Cascade, Node, cascades_from_jsonl, cascades_to_jsonl
from .features import FEATURE_GROUPS, FEATURES, extract, extract_all, structural_virality, write_csv
from .simulate import Samplers, SimConfig, empirical_samplers, inject, simulate_cascade, simulate_corpus

__all__ = [
    "Cascade", "Node", "cascades_from_jsonl", "cascades_to_jsonl",
    "FEATURE_GROUPS", "FEATURES", "extract", "extract_all", "structural_virality", "write_csv",
    "Samplers", "SimConfig", "empirical_samplers", "inject", "simulate_cascade", "simulate_corpus", "__version__",
]
