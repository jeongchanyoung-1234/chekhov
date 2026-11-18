"""Findings reported by checks."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional

ERROR = "error"      # the graph and the manuscript disagree; fix before moving on
WARNING = "warning"  # a person should look (the tool cannot decide)
INFO = "info"


@dataclass
class Issue:
    level: str
    code: str
    message: str
    node: Optional[str] = None
    chapter: Optional[int] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}

    def __str__(self) -> str:
        mark = {"error": "✗", "warning": "·", "info": "i"}.get(self.level, "?")
        where = []
        if self.node:
            where.append(self.node)
        if self.chapter is not None:
            where.append(f"ch{self.chapter}")
        prefix = f"[{', '.join(where)}] " if where else ""
        return f"  {mark} {self.code}: {prefix}{self.message}"
