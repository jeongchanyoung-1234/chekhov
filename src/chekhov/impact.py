"""What breaks if scenes are removed.

Typical use: an abridged edition (a contest version) drops scenes. Every SETS_UP or
RHYMES_WITH link with exactly one end removed leaves the other end without its
partner. Those survivors are what a person must re-read: does the payoff still
stand on what is left?
"""
from __future__ import annotations

from dataclasses import dataclass

from .manuscript import Manuscript
from .model import LINK_RELATIONS, Graph


@dataclass
class BrokenLink:
    relation: str
    removed: str
    kept: str
    note: str = ""


def removed_events(graph: Graph, ms: Manuscript) -> set[str]:
    """Events whose evidence is no longer anywhere in the manuscript."""
    full = ms.full_text()
    return {n["id"] for n in graph.events() if n.get("evidence") and n["evidence"] not in full}


def broken_links(graph: Graph, removed: set[str]) -> list[BrokenLink]:
    out = []
    for e in graph.links_touching(removed, LINK_RELATIONS):
        s, t = e["source"], e["target"]
        if (s in removed) == (t in removed):
            continue  # both kept, or both gone
        gone, kept = (s, t) if s in removed else (t, s)
        out.append(BrokenLink(e["relation"], gone, kept, e.get("note", "")))
    # most-linked survivors first: they lost the most support
    weight: dict[str, int] = {}
    for b in out:
        weight[b.kept] = weight.get(b.kept, 0) + 1
    out.sort(key=lambda b: (-weight[b.kept], b.kept))
    return out
