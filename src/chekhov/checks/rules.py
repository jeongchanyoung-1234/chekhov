"""Machine-checkable rules.

An invariant stays prose for people and agents, and may add a ``check``:

    {"id": "I-P2", "rule": "The narrator asks no questions in ch 1-7.",
     "check": {"type": "no_question_dialogue", "chapters": "1-7"}}

Check types:
  forbidden_terms  {"terms": [...], "chapters"?, "level"?="error"}   term must not appear
  watch_terms      {"terms": [...], "chapters"?, "level"?="warning"} a person should look
  no_question_dialogue {"chapters"?}                                 dialogue ending in '?'
  regex            {"pattern": "...", "message"?, "chapters"?, "level"?="warning"}

Rule packs are language conventions turned on per work (meta.rule_packs or --pack),
e.g. "ko" or "ko/emotion-words". See rules/.
"""
from __future__ import annotations

import re

from ..issues import ERROR, WARNING, Issue
from ..manuscript import Manuscript
from ..model import Graph
from ..rules import ALIASES, PACKS

DIALOGUE_OPEN = ('"', "“", "「", "『")
DIALOGUE_CLOSE = '"”」』'


def parse_chapters(spec, available: list[int]) -> list[int]:
    if spec in (None, "", "all", "*"):
        return available
    out: set[int] = set()
    for part in str(spec).split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out.update(range(int(a), int(b) + 1))
        elif part:
            out.add(int(part))
    return [c for c in available if c in out]


def _context(line: str, i: int, width: int = 18) -> str:
    return line[max(0, i - width): i + width].replace("\n", " ")


def run_check(check: dict, ms: Manuscript, rule_id: str) -> list[Issue]:
    kind = check.get("type")
    chapters = parse_chapters(check.get("chapters"), ms.chapter_numbers())
    issues: list[Issue] = []
    if kind in ("forbidden_terms", "watch_terms"):
        level = check.get("level", ERROR if kind == "forbidden_terms" else WARNING)
        for term in check.get("terms", []):
            for c in chapters:
                for line in ms.chapters[c]:
                    i = line.find(term)
                    if i >= 0:
                        issues.append(Issue(level, rule_id, f"'{term}': …{_context(line, i)}…", chapter=c))
    elif kind == "no_question_dialogue":
        for c in chapters:
            for line in ms.chapters[c]:
                if line.startswith(DIALOGUE_OPEN) and line.rstrip(DIALOGUE_CLOSE).endswith("?"):
                    issues.append(Issue(check.get("level", WARNING), rule_id,
                                        f"question in dialogue (check the speaker): {line}", chapter=c))
    elif kind == "regex":
        pat = re.compile(check["pattern"])
        for c in chapters:
            for line in ms.chapters[c]:
                for m in pat.finditer(line):
                    msg = check.get("message", "pattern matched")
                    issues.append(Issue(check.get("level", WARNING), rule_id,
                                        f"{msg}: …{_context(line, m.start())}…", chapter=c))
    else:
        issues.append(Issue(ERROR, "unknown-check", f"unknown check type '{kind}' in {rule_id}"))
    return issues


def check_invariants(graph: Graph, ms: Manuscript) -> list[Issue]:
    issues: list[Issue] = []
    for inv in graph.invariants:
        checks = inv.get("check")
        if not checks:
            continue
        for chk in checks if isinstance(checks, list) else [checks]:
            issues += run_check(chk, ms, inv.get("id", "?"))
    return issues


def check_packs(graph: Graph, ms: Manuscript, packs: list[str] | None = None) -> list[Issue]:
    wanted = list(graph.meta.get("rule_packs", [])) + list(packs or [])
    issues: list[Issue] = []
    seen = set()
    for name in wanted:
        lang, _, item = name.partition("/")
        pack = PACKS.get(lang)
        if pack is None:
            issues.append(Issue(ERROR, "unknown-pack", f"no rule pack '{lang}'"))
            continue
        items = ALIASES.get(lang, {}).get(item, [item]) if item else list(pack)
        for rule_id in items:
            if rule_id not in pack:
                issues.append(Issue(ERROR, "unknown-pack", f"no rule '{lang}/{rule_id}'"))
                continue
            if (lang, rule_id) in seen:
                continue
            seen.add((lang, rule_id))
            issues += pack[rule_id](ms)
    return issues
