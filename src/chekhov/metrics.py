"""Rhythm audit and length counts. Numbers for a person to read, not verdicts."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .manuscript import Manuscript, split_sentences

SHORT_SENTENCE = 15   # characters
SHORT_RUN = 4         # this many short sentences in a row is worth a look


@dataclass
class ChapterAudit:
    chapter: int
    paragraphs: int
    avg_paragraph: float
    avg_sentence: float
    short_paragraphs: int
    short_runs: list[str] = field(default_factory=list)


def _is_dialogue(p: str) -> bool:
    return p.startswith(('"', "“", "「", "『"))


def audit(ms: Manuscript) -> list[ChapterAudit]:
    out = []
    for c in ms.chapter_numbers():
        paras = [p for p in ms.body_paragraphs(c) if not _is_dialogue(p)]
        if not paras:
            continue
        sents = [s for p in paras for s in split_sentences(p)]
        runs = []
        for p in paras:
            run: list[str] = []
            for s in split_sentences(p) + [""]:
                if s and len(s) < SHORT_SENTENCE:
                    run.append(s)
                    continue
                if len(run) >= SHORT_RUN:
                    runs.append(" ".join(run))
                run = []
        out.append(ChapterAudit(
            chapter=c,
            paragraphs=len(paras),
            avg_paragraph=sum(map(len, paras)) / len(paras),
            avg_sentence=sum(map(len, sents)) / max(1, len(sents)),
            short_paragraphs=sum(1 for p in paras if len(p) < 80),
            short_runs=runs,
        ))
    return out


@dataclass
class Count:
    chars_with_spaces: int
    chars_without_spaces: int
    manuscript_pages_by_chars: float   # chars / 200: the quick estimate most people use
    manuscript_pages_by_lines: float   # 20x10 grid, paragraph indent, each paragraph starts a new line
    per_chapter_by_lines: dict[int, float]


def count(ms: Manuscript, include_front_matter: bool = False) -> Count:
    chapters = sorted(ms.chapters) if include_front_matter else ms.chapter_numbers()
    paras = [(c, p) for c in chapters for p in ms.chapters[c]]
    per: dict[int, int] = {}
    for c, p in paras:
        per[c] = per.get(c, 0) + math.ceil((len(p) + 1) / 20)
    chars = sum(len(p) for _, p in paras)
    return Count(
        chars_with_spaces=chars,
        chars_without_spaces=sum(len(p.replace(" ", "")) for _, p in paras),
        manuscript_pages_by_chars=round(chars / 200, 1),
        manuscript_pages_by_lines=round(sum(per.values()) / 10, 1),
        per_chapter_by_lines={c: round(v / 10, 1) for c, v in per.items()},
    )
