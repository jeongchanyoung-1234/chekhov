"""Project config: `.storygraph.json` in the work's folder (or any parent).

    {
     "graph": "graph.json",
     "manuscript": "drafts/v0.2_work1.docx",   # the working copy the agent edits
     "exclude": null,                          # exclusion list, for abridged editions
     "packs": ["ko/emotion-words"],
     "editions": {                             # optional named editions
       "contest80": {"manuscript": "contest_80.docx", "exclude": "contest_80_cut.txt"}
     }
    }

Paths are relative to the config file. With a config, `storygraph check` needs no arguments.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_NAME = ".storygraph.json"
STATE_DIR = ".storygraph"


@dataclass
class Project:
    root: Path
    graph: Path
    manuscript: Path
    exclude: Path | None = None
    packs: list[str] = field(default_factory=list)

    @property
    def state_file(self) -> Path:
        return self.root / STATE_DIR / "state.json"


def find_config(start: str | Path | None = None) -> Path | None:
    here = Path(start or Path.cwd()).resolve()
    for d in [here, *here.parents]:
        cfg = d / CONFIG_NAME
        if cfg.is_file():
            return cfg
    return None


def load_project(cfg_path: Path, edition: str | None = None) -> Project:
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    root = cfg_path.parent
    if edition:
        try:
            data = {**data, **data["editions"][edition]}
        except KeyError:
            raise SystemExit(f"no edition '{edition}' in {cfg_path}")
    for key in ("graph", "manuscript"):
        if not data.get(key):
            raise SystemExit(f"{cfg_path}: '{key}' is required")
    return Project(
        root=root,
        graph=root / data["graph"],
        manuscript=root / data["manuscript"],
        exclude=(root / data["exclude"]) if data.get("exclude") else None,
        packs=list(data.get("packs", [])),
    )
