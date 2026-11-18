"""Reading a manuscript and splitting it into chapters, paragraphs and sentences."""
from __future__ import annotations

import re
from pathlib import Path

DEFAULT_CHAPTER_PATTERN = r"^\[(\d+)\]"

# a sentence ends at . ! ? 。 … plus any closing quotes/brackets, followed by space or end of text
_SENTENCE = re.compile(r"\S.*?(?:[.!?。…][\"'”’」』)]*(?=\s|$)|$)", re.S)


def split_sentences(text: str) -> list[str]:
    return [m.group(0).strip() for m in _SENTENCE.finditer(text.strip()) if m.group(0).strip()]


def _read_paragraphs(path: Path) -> list[str]:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        import docx  # python-docx
        return [p.text.strip() for p in docx.Document(str(path)).paragraphs]
    if suffix in (".md", ".txt", ""):
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    raise ValueError(f"unsupported manuscript format: {path.suffix} (use .docx, .md or .txt)")


class Manuscript:
    """Paragraphs grouped by chapter number. Text before the first heading is chapter 0."""

    def __init__(self, paragraphs: list[str], chapter_pattern: str = DEFAULT_CHAPTER_PATTERN,
                 path: Path | None = None):
        self.path = path
        self.pattern = re.compile(chapter_pattern)
        self.chapters: dict[int, list[str]] = {}
        self.headings: dict[int, str] = {}
        current = 0
        for p in paragraphs:
            if not p:
                continue
            m = self.pattern.match(p)
            if m:
                current = int(m.group(1))
                self.headings[current] = p
            self.chapters.setdefault(current, []).append(p)

    @classmethod
    def load(cls, path: str | Path, chapter_pattern: str | None = None) -> "Manuscript":
        path = Path(path)
        return cls(_read_paragraphs(path), chapter_pattern or DEFAULT_CHAPTER_PATTERN, path)

    def text(self, chapter: int) -> str:
        return "\n".join(self.chapters.get(chapter, []))

    def full_text(self) -> str:
        return "\n".join(self.text(k) for k in sorted(self.chapters))

    def body_paragraphs(self, chapter: int) -> list[str]:
        return [p for p in self.chapters.get(chapter, []) if p != self.headings.get(chapter)]

    def chapter_numbers(self) -> list[int]:
        return sorted(k for k in self.chapters if k != 0)
