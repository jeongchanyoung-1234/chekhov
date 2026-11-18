"""Agent hook: run `check` after a tool call, only when the graph or manuscript changed.

Claude Code calls `storygraph hook` after Edit/Write/Bash (see plugin/hooks/hooks.json)
and passes the tool call as JSON on stdin. Exit codes follow Claude Code's hook contract:
  0  nothing to say (no project, nothing changed, or no errors)
  2  errors found; stderr is shown to the agent so it fixes them before moving on
  1  the hook itself failed; stderr is shown to the user, the agent is not blocked
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from . import checks
from .config import find_config, load_project
from .issues import ERROR
from .manuscript import Manuscript
from .model import Graph

MAX_LINES = 20


def _mtimes(paths: list[Path | None]) -> dict[str, float]:
    return {str(p): p.stat().st_mtime for p in paths if p and p.exists()}


def _word_lock(path: Path) -> Path:
    # Word keeps "~$" + the name without its first two characters while a file is open
    return path.with_name("~$" + path.name[2:])


def run(stdin_text: str = "") -> int:
    try:
        event = json.loads(stdin_text) if stdin_text.strip() else {}
    except json.JSONDecodeError:
        event = {}
    cfg = find_config(event.get("cwd"))
    if not cfg:
        return 0
    project = load_project(cfg)
    watched = [project.graph, project.manuscript, project.exclude]
    now = _mtimes(watched)
    state_file = project.state_file
    try:
        before = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        before = {}
    if before.get("mtimes") == now:
        return 0

    g = Graph.load(project.graph)
    ms = Manuscript.load(project.manuscript, g.meta.get("chapter_pattern"))
    excluded = set()
    if project.exclude and project.exclude.exists():
        excluded = {l.split("#", 1)[0].strip() for l in project.exclude.read_text(encoding="utf-8").splitlines()}
        excluded.discard("")
    errors = [i for i in checks.run_all(g, ms, excluded, project.packs) if i.level == ERROR]

    state_file.parent.mkdir(exist_ok=True)
    state_file.write_text(json.dumps({"mtimes": now, "errors": len(errors)}), encoding="utf-8")

    if _word_lock(project.manuscript).exists():
        print(f"storygraph: {project.manuscript.name} is open in Word; saves from scripts may fail "
              f"until the author closes it.", file=sys.stderr)
    if not errors:
        return 0
    print(f"storygraph: {len(errors)} error(s) between {project.graph.name} and {project.manuscript.name}. "
          f"Fix the graph (evidence/edges) or the manuscript, or list deliberate cuts in the exclusion file.",
          file=sys.stderr)
    for i in errors[:MAX_LINES]:
        print(str(i), file=sys.stderr)
    if len(errors) > MAX_LINES:
        print(f"  … {len(errors) - MAX_LINES} more: run `storygraph check`", file=sys.stderr)
    return 2


def main() -> int:
    try:
        return run(sys.stdin.read() if not sys.stdin.isatty() else "")
    except SystemExit as e:
        print(f"storygraph hook: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # never break the agent's session because of the hook
        print(f"storygraph hook failed: {e!r}", file=sys.stderr)
        return 1
