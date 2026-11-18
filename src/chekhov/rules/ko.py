"""Korean prose conventions (opt-in). All are warnings: a person decides.

  ko/emotion-words     emotion and like/dislike words in narration (for restrained, show-don't-tell styles)
  ko/simile-markers    similes (처럼, 마치, ~듯이) so each comparison is a choice
  ko/hedge-markers     conjecture (것 같다, ~듯하다, ~듯싶다, 모양이다) for narrators who should not guess aloud
  ko/sino-numerals     Sino-Korean numbers and clock times written in hangul (for works that use Arabic numerals)

  ko/metaphor-markers  = simile-markers + hedge-markers (kept for older configs)
"""
from __future__ import annotations

import re

from ..issues import WARNING, Issue
from ..manuscript import Manuscript

EMOTION_WORDS = ["우울", "상처", "죄책감", "절망", "트라우마", "외로", "슬펐", "슬프", "불안", "고독", "서운",
                 "두렵", "두려", "무서", "싫다", "좋다", "좋아한다", "재미있", "즐겁", "행복", "부끄"]
# '듯' inside ordinary words (반듯이, 번듯하다) is not a marker
_NOT_DEUT = r"(?<![반번])"
SIMILE = re.compile(r"처럼|마치|" + _NOT_DEUT + r"듯이")
HEDGE = re.compile(r"것 같[다았은아]|" + _NOT_DEUT + r"듯(?:하|싶|한)|모양이[다었]")

_SINO = r"(?:[일이삼사오육칠팔구]?백)?(?:[일이삼사오육칠팔구]?십)?[일이삼사오육칠팔구]?"
_SINO_COUNTER = re.compile(r"(?<![가-힣])(" + _SINO + r") ?(분|초|평|층|년|학년|월|미터|명|등|교시)(?![가-힣])")
_NATIVE_HOUR = re.compile(r"(?:한|두|세|네|다섯|여섯|일곱|여덟|아홉|열|열한|열두) 시(?!간)")


def _ctx(line: str, i: int, w: int = 18) -> str:
    return line[max(0, i - w): i + w]


def _is_dialogue(line: str) -> bool:
    return line.startswith(('"', "“", "「", "『"))


def emotion_words(ms: Manuscript) -> list[Issue]:
    out = []
    for c in ms.chapter_numbers():
        for line in ms.chapters[c]:
            if _is_dialogue(line):
                continue
            for w in EMOTION_WORDS:
                i = line.find(w)
                if i >= 0:
                    out.append(Issue(WARNING, "ko/emotion-words", f"'{w}': …{_ctx(line, i)}…", chapter=c))
    return out


def _markers(ms: Manuscript, pattern: re.Pattern, code: str) -> list[Issue]:
    out = []
    for c in ms.chapter_numbers():
        for line in ms.chapters[c]:
            for m in pattern.finditer(line):
                out.append(Issue(WARNING, code, f"'{m.group(0)}': …{_ctx(line, m.start())}…", chapter=c))
    return out


def simile_markers(ms: Manuscript) -> list[Issue]:
    return _markers(ms, SIMILE, "ko/simile-markers")


def hedge_markers(ms: Manuscript) -> list[Issue]:
    return _markers(ms, HEDGE, "ko/hedge-markers")


def sino_numerals(ms: Manuscript) -> list[Issue]:
    out = []
    for c in ms.chapter_numbers():
        text = ms.text(c)
        for m in _SINO_COUNTER.finditer(text):
            num, unit = m.group(1), m.group(2)
            if not num or (num in ("이", "일") and unit in ("분", "일")):
                continue  # '이 분'(this person) etc. are left to people
            out.append(Issue(WARNING, "ko/sino-numerals", f"Sino-Korean number in hangul: '{m.group(0).strip()}'",
                             chapter=c))
        for m in _NATIVE_HOUR.finditer(text):
            out.append(Issue(WARNING, "ko/sino-numerals", f"clock time in hangul: '{m.group(0)}'", chapter=c))
    return out


RULES = {
    "emotion-words": emotion_words,
    "simile-markers": simile_markers,
    "hedge-markers": hedge_markers,
    "sino-numerals": sino_numerals,
}

ALIASES = {
    "metaphor-markers": ["simile-markers", "hedge-markers"],
}
