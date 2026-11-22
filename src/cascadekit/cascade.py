"""Core data structure: a timed diffusion tree (Information Dissemination Tree)."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Iterable, List, Optional


@dataclass
class Node:
    """One reshare (or the root post).

    id       unique identifier of this post/repost/forward
    account  account (or channel) that made it; None if unknown
    ts       time in seconds since the Unix epoch; None if unknown
    parent   id of the node it was reshared from; None for the root
    rule     how the parent was chosen: "via", "follow", "item", "sim", or None for the root
    """
    id: str
    account: Optional[str]
    ts: Optional[float]
    parent: Optional[str] = None
    rule: Optional[str] = None


@dataclass
class Cascade:
    """A rooted, timed tree. ``nodes[0]`` is the root; the rest are kept in time order
    and every parent precedes its child (parents that would break this are re-attached
    to the root with rule ``"item"``)."""
    root: str
    nodes: List[Node]
    platform: str = "unknown"
    complete: bool = True
    label: Optional[str] = None
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        self.nodes = [n if isinstance(n, Node) else Node(**n) for n in self.nodes]
        if not self.nodes or self.nodes[0].id != self.root:
            raise ValueError("nodes[0] must be the root node")
        root, rest = self.nodes[0], self.nodes[1:]
        root.parent, root.rule = None, None
        rest.sort(key=lambda n: (n.ts is None, n.ts if n.ts is not None else 0.0))
        self.nodes = [root] + rest
        pos = {}
        for i, n in enumerate(self.nodes):
            if n.id in pos:
                raise ValueError(f"duplicate node id {n.id!r}")
            pos[n.id] = i
        for i, n in enumerate(self.nodes[1:], start=1):
            p = pos.get(n.parent)
            if p is None or p >= i:
                n.parent, n.rule = root.id, "item"

    # ------------------------------------------------------------- structure
    @property
    def size(self) -> int:
        """Number of reshares (root excluded)."""
        return len(self.nodes) - 1

    def parent_index(self) -> List[int]:
        """parents[i] = index of node i's parent; parents[0] = -1."""
        pos = {n.id: i for i, n in enumerate(self.nodes)}
        return [-1] + [pos[n.parent] for n in self.nodes[1:]]

    def depths(self) -> List[int]:
        par = self.parent_index()
        d = [0] * len(par)
        for i in range(1, len(par)):
            d[i] = d[par[i]] + 1
        return d

    def out_degrees(self) -> List[int]:
        par = self.parent_index()
        deg = [0] * len(par)
        for p in par[1:]:
            deg[p] += 1
        return deg

    def start_time(self) -> Optional[float]:
        """Root time if known, else the first reshare's time."""
        for n in self.nodes:
            if n.ts is not None:
                return n.ts
        return None

    # ------------------------------------------------------------- slicing
    def prefix(self, k: int) -> "Cascade":
        """The cascade as it looked after its first ``k`` reshares (for early detection)."""
        return self._subset(self.nodes[: k + 1])

    def until(self, seconds: float) -> "Cascade":
        """Reshares made within ``seconds`` of the cascade's start."""
        t0 = self.start_time()
        if t0 is None:
            return self._subset(self.nodes)
        keep = [self.nodes[0]] + [n for n in self.nodes[1:] if n.ts is not None and n.ts - t0 <= seconds]
        return self._subset(keep)

    def _subset(self, nodes):
        ids = {n.id for n in nodes}
        copy = [Node(**asdict(n)) for n in nodes]
        for n in copy[1:]:
            if n.parent not in ids:
                n.parent, n.rule = self.root, "item"
        return Cascade(self.root, copy, self.platform, self.complete, self.label, dict(self.meta))

    # ------------------------------------------------------------- privacy
    def anonymised(self, salt: str) -> "Cascade":
        """Copy with account ids replaced by salted SHA-256 hashes (first 16 hex chars).
        Node and root ids are hashed too, because platform ids embed account ids."""
        h = lambda s: None if s is None else hashlib.sha256((salt + str(s)).encode()).hexdigest()[:16]
        nodes = [Node(h(n.id), h(n.account), n.ts, h(n.parent), n.rule) for n in self.nodes]
        meta = {k: v for k, v in self.meta.items() if k != "text"}
        return Cascade(h(self.root), nodes, self.platform, self.complete, self.label, meta)

    # ------------------------------------------------------------- export
    def to_dict(self) -> dict:
        return {"root": self.root, "platform": self.platform, "complete": self.complete,
                "label": self.label, "meta": self.meta, "nodes": [asdict(n) for n in self.nodes]}

    @classmethod
    def from_dict(cls, d: dict) -> "Cascade":
        return cls(d["root"], d["nodes"], d.get("platform", "unknown"), d.get("complete", True),
                   d.get("label"), d.get("meta") or {})

    def to_networkx(self):
        """Directed tree (parent -> child) with node attributes account, ts, rule."""
        import networkx as nx
        g = nx.DiGraph()
        for n in self.nodes:
            g.add_node(n.id, account=n.account, ts=n.ts, rule=n.rule)
            if n.parent is not None:
                g.add_edge(n.parent, n.id)
        return g

    def __repr__(self):
        return f"Cascade(root={self.root!r}, size={self.size}, platform={self.platform!r}, label={self.label!r})"


def cascades_to_jsonl(cascades: Iterable[Cascade], path: str) -> int:
    """Write cascades as JSON lines (gzip if the path ends in .gz). Returns the count."""
    from .io import open_text
    n = 0
    with open_text(path, "w") as fh:
        for c in cascades:
            fh.write(json.dumps(c.to_dict(), ensure_ascii=False) + "\n")
            n += 1
    return n


def cascades_from_jsonl(path: str) -> List[Cascade]:
    from .io import open_text
    with open_text(path, "r") as fh:
        return [Cascade.from_dict(json.loads(line)) for line in fh if line.strip()]
