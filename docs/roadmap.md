# Roadmap

## M0 · scaffold (done)
Repository, MIT license, graph format v0.1, packaging, tests.

## M1 · core CLI (done in v0.1, to harden)
- [x] `check`: evidence (exact / changed / missing / wrong chapter), dangling edges, setup order, coverage, invariant checks, rule packs, exclusion lists
- [x] `impact`: links left with one end after a cut
- [x] `audit`, `count`
- [x] `init`: graph skeleton, agent rules, feedback log (ko/en)
- [ ] public-domain example with a full graph (e.g. Hyeon Jin-geon, "A Lucky Day", 1924)
- [ ] `check --fix-evidence`: update changed evidence sentences in the graph after confirmation
- [ ] JSON Schema file for editor validation
- [ ] CI (GitHub Actions) on Windows, macOS, Linux

## M2 · Claude Code plugin
- skills: `build-graph` (agent reads the manuscript and drafts the graph; `check` must pass before it is saved), `read-through`, `revise-chapter`, `abridge` (target length → cut plan → `impact` → re-read survivors), `log-round`
- hook: after an edit to the manuscript, run `storygraph check` and show errors to the agent
- templates wired into `init --agent claude`

## M3 · MCP server and docs
- tools: query nodes, check, impact, count, so any MCP client can use the graph
- docs: concepts (why a graph, what to record), a worked example, a Korean craft guide

## M4 · later
- graph viewer (HTML)
- more formats (`.hwpx`)
- more rule packs (en, ja, ...)
