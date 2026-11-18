# chekhov

**Keep a manuscript consistent with a semantic graph of the work.**

> *If in the first act you have hung a pistol on the wall, then in the following one it should be fired.* (Anton Chekhov)
>
> chekhov keeps track of the pistols: every setup, every echo, every rule of the work, anchored to sentences in the manuscript.

[한국어 README](README.ko.md)

## Why this exists

I do not want AI to dominate literature. What I hope for is that, with AI's help, writers who are still learning their craft can develop their own stories into something more valuable, and share them with the world.

chekhov is built on that hope. The story and what it means belong to the writer. The AI helps the writer keep track of what they decided, and the writer always makes the call.

## What it does

When you revise fiction with an AI agent, the agent forgets. It rewrites a sentence that was quietly setting up the ending, cuts a scene whose echo comes six chapters later, or lets the narrator start naming feelings he was never supposed to name. chekhov gives the work a memory that both you and the agent can check:

- a **graph** of the work: themes, chapters, characters, persona traits, motifs, and scenes. Each scene is anchored to a sentence copied from the manuscript. Setups point at payoffs (`SETS_UP`), echoes point at echoes (`RHYMES_WITH`), and the rules of the work are written down as **invariants**.
- a **checker** with no LLM inside, so the same input always gives the same result. It tells you when the manuscript and the graph disagree.
- **working rules and a feedback log** for the agent, so a note you gave once is not needed twice.

It grew out of revising one Korean short story through 50+ rounds with Claude Code. The tools below are the parts that kept paying off.

## Install

```bash
pip install git+https://github.com/<owner>/chekhov   # until it is on PyPI
```

Python 3.10+. Manuscripts can be `.docx`, `.md` or `.txt`. Chapters are found by a heading pattern (default `[1] Title`, configurable).

## Commands

```bash
chekhov init my-novel --title "My Novel" --language en   # graph skeleton, agent rules, feedback log
chekhov check graph.json draft.docx                      # graph vs manuscript
chekhov impact graph.json abridged.docx                  # what a cut breaks
chekhov audit draft.docx                                 # paragraph/sentence rhythm per chapter
chekhov count draft.docx                                 # characters and 200-char manuscript pages
```

### `check`
- **evidence**: is every scene's sentence still in its chapter? A lightly edited sentence is reported with the closest current sentence (`evidence-changed`), so you can update the graph in one step. A sentence that is gone is `evidence-missing`.
- **links**: edges that point at nothing; setups that come after their payoff (mark intended ones `"reverse": true`).
- **coverage**: themes, chapters and persona traits that no scene embodies.
- **rules**: invariants that carry a machine-readable `check` (forbidden terms, watched terms, questions in dialogue, regex), plus opt-in **rule packs** for language conventions (`--pack ko`).
- `--exclude cut.txt` lists scenes cut on purpose (e.g. for a shorter contest edition).

Exit code is 1 when there are errors, so it fits a pre-commit hook or an agent's post-edit hook.

### `impact`
Lists every setup or echo that lost its partner when scenes are removed, with the sentence on each side. Run it on an abridged edition and re-read each surviving side: does it still stand on what is left?

## The graph format

See [docs/schema.md](docs/schema.md). It is intentionally loose: any node needs `id` and `type`, any edge needs `source`, `relation`, `target`, and everything else is yours. An invariant is a sentence first; add a `check` only when a machine can see it:

```json
{"id": "I-P2", "kind": "persona", "rule": "The narrator asks no questions until the last chapter.",
 "check": {"type": "no_question_dialogue", "chapters": "1-7"}}
```

## Working with an agent

`chekhov init` writes `AGENT_RULES.md` (save it as `CLAUDE.md` or `AGENTS.md`) and `FEEDBACK_LOG.md`. The rules that made the difference:

1. Review every change critically, whoever suggested it, and report what was not applied and why.
2. Read the invariants before editing; update the graph and run `check` after.
3. Never edit the original; number working versions.
4. Log every round: principles, the work record, and the agent's own mistakes.
5. The author decides the design. Never insert a sentence just to prove a design.

### Claude Code plugin

```text
/plugin marketplace add jeongchanyoung-1234/chekhov
/plugin install chekhov@chekhov
```

The `chekhov` command must be on your PATH (install it first, above).

| skill | what the agent does |
|---|---|
| `chekhov-setup` | asks you about intent, drafts the graph from the manuscript, checks it to zero errors, and shows you every interpretation it made |
| `read-through` | reviews the whole manuscript against the graph and log, **without editing**, and ends with "apply?" |
| `revise-chapter` | revises one chapter at a time on a working copy, reviews every change critically, keeps the graph in sync |
| `abridge` | makes a shorter edition by cutting whole scenes, then re-reads every setup or echo the cut left alone |
| `log-round` | records the round: principles, work record, its own mistakes |

A `PostToolUse` hook runs `chekhov hook` after edits. It checks only when the graph or manuscript changed, and when the two disagree it shows the errors to the agent so they are fixed before moving on. It also warns when the manuscript is open in Word.

Put a `.chekhov.json` in the work's folder (`chekhov init` writes one) so the hook and `chekhov check` know which files to use:

```json
{"graph": "graph.json", "manuscript": "drafts/v0.2_work1.docx", "exclude": null, "packs": ["ko/emotion-words"],
 "editions": {"contest80": {"manuscript": "contest_80.docx", "exclude": "contest_80_cut.txt"}}}
```

See [docs/roadmap.md](docs/roadmap.md) for what is next.

## License

MIT
