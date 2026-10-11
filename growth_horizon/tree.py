# SPDX-License-Identifier: Apache-2.0
"""Linear tree passes for nearest training leaves, with deterministic ties."""
from __future__ import annotations

import gzip
import math
from pathlib import Path

from Bio import Phylo

Candidate = tuple[float, str]


class TreeIndex:
    def __init__(self, children: list[list[int]], length: list[float], names: dict[str, int]):
        self.children = children
        self.length = length
        self.names = names
        self.parent = [-1] * len(children)
        self.order = [0]
        for node in self.order:
            for child in children[node]:
                self.parent[child] = node
                self.order.append(child)
        if any(x < 0 or not math.isfinite(x) for x in length):
            raise ValueError('Tree branch lengths must be finite and nonnegative')

    @classmethod
    def read(cls, path: Path) -> TreeIndex:
        with gzip.open(path, 'rt') as stream:
            tree = Phylo.read(stream, 'newick')  # type: ignore[attr-defined,no-untyped-call]
        nodes = [tree.root]
        children: list[list[int]] = []
        lengths: list[float] = []
        names: dict[str, int] = {}
        for i, clade in enumerate(nodes):
            ids = list(range(len(nodes), len(nodes) + len(clade.clades)))
            nodes.extend(clade.clades)
            children.append(ids)
            lengths.append(float(clade.branch_length or 0.0))
            if not clade.clades:
                names[str(clade.name)] = i
        return cls(children, lengths, names)

    def nearest(self, sources: set[str]) -> dict[str, Candidate]:
        """Return the closest source for every leaf. No phenotype values are used."""
        best: list[Candidate] = [(math.inf, '') for _ in self.children]
        for name in sources:
            if name in self.names:
                best[self.names[name]] = (0.0, name)
        for node in reversed(self.order[1:]):
            parent = self.parent[node]
            distance, name = best[node]
            best[parent] = min(best[parent], (distance + self.length[node], name))
        for node in self.order[1:]:
            distance, name = best[self.parent[node]]
            best[node] = min(best[node], (distance + self.length[node], name))
        return {name: best[node] for name, node in self.names.items()}

    def prune(self, leaves: set[str]) -> TreeIndex:
        """Retain labelled leaves and sum unary edges without changing path distances."""
        wanted = {self.names[name] for name in leaves if name in self.names}
        alive = set(wanted)
        for node in reversed(self.order[1:]):
            if node in alive:
                alive.add(self.parent[node])
        if not alive:
            return TreeIndex([[]], [0.0], {})
        children: list[list[int]] = [[]]
        lengths = [0.0]
        names = {}
        reverse_names = {v: k for k, v in self.names.items()}
        queue = [(0, 0)]
        for old, new in queue:
            if old in wanted:
                names[reverse_names[old]] = new
            for child in self.children[old]:
                if child not in alive:
                    continue
                length = self.length[child]
                retained = [c for c in self.children[child] if c in alive]
                while len(retained) == 1 and child not in wanted:
                    child = retained[0]
                    length += self.length[child]
                    retained = [c for c in self.children[child] if c in alive]
                index = len(children)
                children[new].append(index)
                children.append([])
                lengths.append(length)
                queue.append((child, index))
        return TreeIndex(children, lengths, names)
