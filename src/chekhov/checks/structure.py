"""Checks on the graph alone: is every theme, chapter and trait grounded in a scene,
and does every setup come before its payoff."""
from __future__ import annotations

from ..issues import ERROR, WARNING, Issue
from ..model import Graph

# (node type, relation that must point at it, level if nothing does)
DEFAULT_COVERAGE = [
    {"type": "Theme", "relation": "EMBODIES", "level": ERROR},
    {"type": "Chapter", "relation": "OCCURS_IN", "level": ERROR},
    {"type": "PersonaTrait", "relation": "SHOWS_TRAIT", "level": ERROR},
    {"type": "Motif", "relation": "USES_MOTIF", "level": WARNING},
]

REVERSE_MARKERS = ("역방향", "reverse")


def coverage(graph: Graph) -> list[Issue]:
    rules = graph.meta.get("coverage", DEFAULT_COVERAGE)
    issues = []
    for rule in rules:
        pointed = graph.targets(rule["relation"])
        for n in graph.of_type(rule["type"]):
            if n["id"] not in pointed:
                issues.append(Issue(rule.get("level", WARNING), "ungrounded",
                                    f"{rule['type']} '{n.get('label', n['id'])}' has no {rule['relation']} edge",
                                    node=n["id"]))
    return issues


def _is_reverse(edge: dict) -> bool:
    if edge.get("reverse"):
        return True
    note = edge.get("note", "")
    return any(m in note for m in REVERSE_MARKERS)


def setup_order(graph: Graph) -> list[Issue]:
    issues = []
    for e in graph.edges_of("SETS_UP"):
        a, b = graph.nodes.get(e["source"]), graph.nodes.get(e["target"])
        if not a or not b:
            continue
        ca, cb = a.get("chapter"), b.get("chapter")
        if isinstance(ca, int) and isinstance(cb, int) and ca > cb and not _is_reverse(e):
            issues.append(Issue(ERROR, "setup-after-payoff",
                                f"{e['source']} (ch{ca}) sets up {e['target']} (ch{cb}); "
                                f"mark the edge \"reverse\": true if this is intended",
                                node=e["source"]))
    return issues
