"""The semantic graph of a work.

The format is deliberately loose: every node needs ``id`` and ``type``; every edge
needs ``source``, ``relation`` and ``target``. Anything else is free-form and kept
as-is, so a writer can record whatever their work needs. A few node types and
relations have meaning for the checks (see docs/schema.md):

* ``Event`` nodes carry ``chapter`` and ``evidence`` (a sentence copied verbatim
  from the manuscript). This anchors the graph to the text.
* ``SETS_UP`` (setup -> payoff) and ``RHYMES_WITH`` (echo) are the links that
  break when a scene is cut.
* ``invariants`` are rules of the work. Prose rules are for people and agents to
  read; a rule may add a machine-readable ``check`` (see checks/rules.py).
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Iterable

from .issues import ERROR, WARNING, Issue

LINK_RELATIONS = ("SETS_UP", "RHYMES_WITH")


class Graph:
    def __init__(self, data: dict, path: Path | None = None):
        self.data = data
        self.path = path
        self.meta: dict = data.get("meta", {})
        self.nodes: dict[str, dict] = {}
        self.duplicate_ids: list[str] = []
        for n in data.get("nodes", []):
            nid = n.get("id")
            if nid in self.nodes:
                self.duplicate_ids.append(nid)
            self.nodes[nid] = n
        self.edges: list[dict] = data.get("edges", [])
        self.invariants: list[dict] = data.get("invariants", [])
        self.facts: list = data.get("facts", [])

    @classmethod
    def load(cls, path: str | Path) -> "Graph":
        path = Path(path)
        with path.open(encoding="utf-8") as f:
            return cls(json.load(f), path)

    def save(self, path: str | Path | None = None) -> None:
        path = Path(path or self.path)
        self.data["nodes"] = list(self.nodes.values())
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=1)
            f.write("\n")

    # ---- queries -------------------------------------------------------
    def of_type(self, type_: str) -> list[dict]:
        return [n for n in self.nodes.values() if n.get("type") == type_]

    def events(self) -> list[dict]:
        return self.of_type("Event")

    def edges_of(self, relation: str) -> list[dict]:
        return [e for e in self.edges if e.get("relation") == relation]

    def targets(self, relation: str) -> set[str]:
        return {e["target"] for e in self.edges_of(relation)}

    def links_touching(self, ids: Iterable[str], relations=LINK_RELATIONS) -> list[dict]:
        ids = set(ids)
        return [e for e in self.edges
                if e.get("relation") in relations and (e.get("source") in ids or e.get("target") in ids)]

    def language(self) -> str:
        return self.meta.get("language", "")

    def stats(self) -> dict:
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "invariants": len(self.invariants),
            "node_types": dict(Counter(n.get("type") for n in self.nodes.values())),
        }

    # ---- shape ---------------------------------------------------------
    def validate(self) -> list[Issue]:
        issues: list[Issue] = []
        for nid in self.duplicate_ids:
            issues.append(Issue(ERROR, "duplicate-id", f"node id used twice: {nid}", node=nid))
        for n in self.data.get("nodes", []):
            if not n.get("id") or not n.get("type"):
                issues.append(Issue(ERROR, "node-shape", f"node needs id and type: {n}"))
            if n.get("type") == "Event":
                if not isinstance(n.get("chapter"), int):
                    issues.append(Issue(ERROR, "event-shape", "Event needs an integer 'chapter'", node=n.get("id")))
                if not n.get("evidence"):
                    issues.append(Issue(WARNING, "event-shape", "Event has no 'evidence' sentence", node=n.get("id")))
        for e in self.edges:
            for end in ("source", "target"):
                if e.get(end) not in self.nodes:
                    issues.append(Issue(ERROR, "dangling-edge",
                                        f"{e.get('source')} -[{e.get('relation')}]-> {e.get('target')}: "
                                        f"'{e.get(end)}' is not a node"))
        for inv in self.invariants:
            if not inv.get("id"):
                issues.append(Issue(ERROR, "invariant-shape", f"invariant needs an id: {inv}"))
        return issues
