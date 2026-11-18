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

## M2 · Claude Code plugin (v0.1 done, to field-test)
- [x] `.storygraph.json` project config with named editions; `check`/`impact` without arguments
- [x] `storygraph hook`: checks only on change, exit 2 shows errors to the agent, warns on Word lock files
- [x] skills: `storygraph-setup`, `read-through`, `revise-chapter`, `abridge`, `log-round`
- [x] marketplace entry at the repo root
- [ ] field test on a full revision cycle with a public-domain story; tune the skills from what goes wrong
- [ ] `init --agent claude` writes `CLAUDE.md` directly

## M3 · MCP server and docs
- tools: query nodes, check, impact, count, so any MCP client can use the graph
- docs: concepts (why a graph, what to record), a worked example, a Korean craft guide

## M4 · later
- graph viewer (HTML)
- more formats (`.hwpx`)
- more rule packs (en, ja, ...)
