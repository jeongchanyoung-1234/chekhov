"""Is every Event's evidence sentence still in the manuscript, in its chapter?

A sentence that was lightly edited is reported as ``evidence-changed`` together with
the closest sentence in the chapter, so the graph can be updated in one step.
A sentence that is gone is ``evidence-missing``: either the scene was cut on purpose
(list the node in an exclusion file) or a setup/payoff was broken by accident.
"""
from __future__ import annotations

from difflib import SequenceMatcher

from ..issues import ERROR, INFO, Issue
from ..manuscript import Manuscript, split_sentences
from ..model import Graph

CHANGED_THRESHOLD = 0.7


def _ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b, autojunk=False).ratio()


def similarity(evidence: str, sentence: str) -> float:
    """How likely `sentence` is an edited version of `evidence` (0..1).

    Whole-string ratio, or, when one is much shorter (evidence is often a clause),
    the best ratio of the shorter against same-length windows of the longer,
    discounted by the length gap so a short common phrase does not win.
    """
    whole = _ratio(evidence, sentence)
    short, long_ = sorted((evidence, sentence), key=len)
    if not short:
        return 0.0
    n = len(short)
    partial = max(_ratio(short, long_[i:i + n]) for i in range(len(long_) - n + 1))
    return max(whole, partial * (0.7 + 0.3 * n / len(long_)))


def closest_sentence(evidence: str, text: str) -> tuple[float, str]:
    best = (0.0, "")
    for s in split_sentences(text.replace("\n", " ")):
        score = similarity(evidence, s)
        if score > best[0]:
            best = (score, s)
    return best


def check(graph: Graph, ms: Manuscript, excluded: set[str]) -> list[Issue]:
    issues: list[Issue] = []
    skipped = 0
    for n in graph.events():
        ev, ch = n.get("evidence"), n.get("chapter")
        if not ev or not isinstance(ch, int):
            continue
        if n["id"] in excluded:
            skipped += 1
            continue
        if ev in ms.text(ch):
            continue
        elsewhere = [k for k in ms.chapters if k != ch and ev in ms.text(k)]
        if elsewhere:
            issues.append(Issue(ERROR, "evidence-wrong-chapter",
                                f"found in chapter {elsewhere}, not {ch}: {ev}", node=n["id"], chapter=ch))
            continue
        score, sent = closest_sentence(ev, ms.text(ch))
        if score >= CHANGED_THRESHOLD:
            issues.append(Issue(ERROR, "evidence-changed",
                                f"'{ev}' → closest now: '{sent}' ({score:.0%})", node=n["id"], chapter=ch))
        else:
            issues.append(Issue(ERROR, "evidence-missing", ev, node=n["id"], chapter=ch))
    if skipped:
        issues.append(Issue(INFO, "excluded", f"{skipped} event(s) skipped by the exclusion list"))
    return issues
