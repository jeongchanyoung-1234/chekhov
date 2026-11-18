"""Checks between a Graph and a Manuscript. Each returns a list of Issue."""
from __future__ import annotations

from ..issues import Issue
from ..manuscript import Manuscript
from ..model import Graph
from . import evidence, rules, structure


def run_all(graph: Graph, ms: Manuscript, excluded: set[str] | None = None,
            packs: list[str] | None = None) -> list[Issue]:
    excluded = excluded or set()
    issues: list[Issue] = []
    issues += graph.validate()
    issues += structure.coverage(graph)
    issues += structure.setup_order(graph)
    issues += evidence.check(graph, ms, excluded)
    issues += rules.check_invariants(graph, ms)
    issues += rules.check_packs(graph, ms, packs)
    return issues
