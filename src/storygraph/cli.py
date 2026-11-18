"""Command line: storygraph check | impact | audit | count | stats | init"""
from __future__ import annotations

import argparse
import io
import json
import sys
from dataclasses import asdict
from importlib import resources
from pathlib import Path

from . import __version__, checks, impact, metrics
from .issues import ERROR, INFO, WARNING
from .manuscript import Manuscript
from .model import Graph


def _utf8_stdout() -> None:
    if hasattr(sys.stdout, "buffer") and (sys.stdout.encoding or "").lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def _load_excluded(path: str | None) -> set[str]:
    if not path:
        return set()
    ids = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            ids.add(line)
    return ids


def _manuscript(path: str, graph: Graph | None, pattern: str | None) -> Manuscript:
    return Manuscript.load(path, pattern or (graph.meta.get("chapter_pattern") if graph else None))


# ---- commands -------------------------------------------------------------

def cmd_check(a) -> int:
    g = Graph.load(a.graph)
    ms = _manuscript(a.manuscript, g, a.chapter_pattern)
    issues = checks.run_all(g, ms, _load_excluded(a.exclude), a.pack)
    if a.json:
        print(json.dumps([i.to_dict() for i in issues], ensure_ascii=False, indent=1))
    else:
        s = g.stats()
        print(f"graph: {Path(a.graph).name}  ({s['nodes']} nodes, {s['edges']} edges, {s['invariants']} invariants)")
        print(f"manuscript: {Path(a.manuscript).name}  (chapters {ms.chapter_numbers()})\n")
        for level, title in ((ERROR, "errors"), (WARNING, "warnings"), (INFO, "info")):
            group = [i for i in issues if i.level == level]
            if level == WARNING and a.no_warnings:
                print(f"{title}: {len(group)} (hidden)")
                continue
            print(f"{title}: {len(group)}")
            for i in group:
                print(i)
    return 1 if any(i.level == ERROR for i in issues) else 0


def cmd_impact(a) -> int:
    g = Graph.load(a.graph)
    if a.remove:
        removed = set(a.remove)
    else:
        ms = _manuscript(a.manuscript, g, a.chapter_pattern)
        removed = impact.removed_events(g, ms) - _load_excluded(a.exclude) if a.only_new else impact.removed_events(g, ms)
    broken = impact.broken_links(g, removed)
    if a.write_exclusions:
        Path(a.write_exclusions).write_text("\n".join(sorted(removed)) + "\n", encoding="utf-8")
    if a.json:
        print(json.dumps({"removed": sorted(removed), "broken": [asdict(b) for b in broken]},
                         ensure_ascii=False, indent=1))
        return 0
    print(f"removed events: {len(removed)}")
    print(f"links left with one end: {len(broken)}  (re-read the kept side: does it still stand?)\n")
    for b in broken:
        kept, gone = g.nodes[b.kept], g.nodes[b.removed]
        print(f"  {b.relation:11} kept {b.kept} (ch{kept.get('chapter', '?')}): {kept.get('evidence') or kept.get('label')}")
        print(f"  {'':11} lost {b.removed} (ch{gone.get('chapter', '?')}): {gone.get('evidence') or gone.get('label')}")
    return 0


def cmd_audit(a) -> int:
    g = Graph.load(a.graph) if a.graph else None
    ms = _manuscript(a.manuscript, g, a.chapter_pattern)
    rows = metrics.audit(ms)
    if a.json:
        print(json.dumps([asdict(r) for r in rows], ensure_ascii=False, indent=1))
        return 0
    print("ch  paras  avg-para  avg-sent  short-paras  short-runs")
    for r in rows:
        print(f"{r.chapter:>2}  {r.paragraphs:>5}  {r.avg_paragraph:>8.0f}  {r.avg_sentence:>8.1f}  "
              f"{r.short_paragraphs:>11}  {len(r.short_runs):>10}")
    for r in rows:
        for run in r.short_runs:
            print(f"  ch{r.chapter} short run: {run}")
    return 0


def cmd_count(a) -> int:
    g = Graph.load(a.graph) if a.graph else None
    ms = _manuscript(a.manuscript, g, a.chapter_pattern)
    c = metrics.count(ms, a.front_matter)
    if a.json:
        print(json.dumps(asdict(c), ensure_ascii=False, indent=1))
        return 0
    print(f"characters (with spaces):    {c.chars_with_spaces}")
    print(f"characters (without spaces): {c.chars_without_spaces}")
    print(f"200-char pages, chars/200:   {c.manuscript_pages_by_chars}")
    print(f"200-char pages, line grid:   {c.manuscript_pages_by_lines}")
    print("per chapter (line grid):     " + ", ".join(f"{k}: {v}" for k, v in c.per_chapter_by_lines.items()))
    return 0


def cmd_stats(a) -> int:
    print(json.dumps(Graph.load(a.graph).stats(), ensure_ascii=False, indent=1))
    return 0


def cmd_init(a) -> int:
    target = Path(a.directory)
    target.mkdir(parents=True, exist_ok=True)
    tpl = resources.files("storygraph") / "templates"
    lang = a.language
    files = {
        "graph.json": "graph.json",
        "AGENT_RULES.md": f"AGENT_RULES.{lang}.md",
        "FEEDBACK_LOG.md": f"FEEDBACK_LOG.{lang}.md",
    }
    for out, src in files.items():
        dest = target / out
        if dest.exists() and not a.force:
            print(f"skip (exists): {dest}")
            continue
        text = (tpl / src).read_text(encoding="utf-8").replace("{{TITLE}}", a.title).replace("{{LANG}}", lang)
        dest.write_text(text, encoding="utf-8")
        print(f"wrote {dest}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="storygraph", description=__doc__)
    p.add_argument("--version", action="version", version=f"storygraph {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp, graph_required=True):
        if graph_required:
            sp.add_argument("graph", help="graph JSON")
        sp.add_argument("manuscript", help=".docx, .md or .txt")
        sp.add_argument("--chapter-pattern", help=r"regex for chapter headings, group 1 = number (default ^\[(\d+)\])")
        sp.add_argument("--json", action="store_true")

    sp = sub.add_parser("check", help="graph vs manuscript: evidence, links, coverage, rules")
    common(sp)
    sp.add_argument("--exclude", help="file of node ids cut on purpose (one per line)")
    sp.add_argument("--pack", action="append", help="rule pack, e.g. ko or ko/emotion-words (repeatable)")
    sp.add_argument("--no-warnings", action="store_true", help="count warnings but do not list them")
    sp.set_defaults(func=cmd_check)

    sp = sub.add_parser("impact", help="which setups/echoes lose their partner when scenes are removed")
    common(sp)
    sp.add_argument("--remove", nargs="+", help="node ids to remove (default: events missing from the manuscript)")
    sp.add_argument("--exclude", help="with --only-new: ids already accepted as cut")
    sp.add_argument("--only-new", action="store_true", help="ignore ids listed in --exclude")
    sp.add_argument("--write-exclusions", help="write the removed ids to this file")
    sp.set_defaults(func=cmd_impact)

    for name, func, helptext in (("audit", cmd_audit, "paragraph and sentence rhythm per chapter"),
                                 ("count", cmd_count, "characters and 200-char manuscript pages")):
        sp = sub.add_parser(name, help=helptext)
        sp.add_argument("manuscript")
        sp.add_argument("--graph", help="graph JSON (only for meta.chapter_pattern)")
        sp.add_argument("--chapter-pattern")
        sp.add_argument("--json", action="store_true")
        if name == "count":
            sp.add_argument("--front-matter", action="store_true", help="also count text before the first chapter")
        sp.set_defaults(func=func)

    sp = sub.add_parser("stats", help="node and edge counts")
    sp.add_argument("graph")
    sp.set_defaults(func=cmd_stats)

    sp = sub.add_parser("init", help="start a project: graph skeleton, agent rules, feedback log")
    sp.add_argument("directory")
    sp.add_argument("--title", default="Untitled")
    sp.add_argument("--language", default="ko", choices=["ko", "en"])
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_init)
    return p


def main(argv: list[str] | None = None) -> int:
    _utf8_stdout()
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
