# Graph format (v0.1)

One JSON file per work. Unknown keys are kept and ignored by the checker, so you can record whatever your work needs.

```json
{
 "meta": {...},
 "invariants": [...],
 "facts": [...],
 "nodes": [...],
 "edges": [...]
}
```

## meta

| key | meaning |
|---|---|
| `title` | title of the work |
| `language` | e.g. `ko`, `en` |
| `chapter_pattern` | regex for chapter headings; group 1 is the chapter number. Default `^\[(\d+)\]` |
| `rule_packs` | rule packs to run on every check, e.g. `["ko/emotion-words"]` |
| `coverage` | optional override of the coverage rules (see below) |
| `based_on` | which manuscript file the graph currently describes |

## nodes

Every node has `id` and `type`. Types the checker knows:

| type | used for | checked |
|---|---|---|
| `Event` | a scene or beat. Needs `chapter` (int) and `evidence` (a sentence copied verbatim from that chapter) | evidence is still in the chapter |
| `Theme` | a stage of the theme | something `EMBODIES` it |
| `Chapter` | a chapter | something `OCCURS_IN` it |
| `PersonaTrait` | a stable trait of the narrator or protagonist | something `SHOWS_TRAIT` it |
| `Motif` | a recurring image | warned if nothing `USES_MOTIF` it |

Any other type (`Character`, `PersonaState`, `Belief`, ...) is fine and simply not checked.

## edges

`{"source": "...", "relation": "...", "target": "...", "note": "optional"}`

| relation | meaning | checked |
|---|---|---|
| `SETS_UP` | setup → payoff | the setup's chapter is not after the payoff's, unless `"reverse": true` (or the note contains "reverse"/"역방향"); used by `impact` |
| `RHYMES_WITH` | an echo between two scenes (dream ↔ waking, chapter ↔ chapter) | used by `impact` |
| `OCCURS_IN`, `EMBODIES`, `SHOWS_TRAIT`, `USES_MOTIF` | grounding | coverage |

Any other relation is allowed.

## invariants

```json
{"id": "I-P1", "kind": "persona", "chapters": "1-8",
 "rule": "The narrator never names an emotion; he reports actions and senses.",
 "check": {"type": "watch_terms", "terms": ["sad", "lonely"]}}
```

`rule` is the source of truth and is for people and agents. `check` is optional and may be a list.

| check type | fields | level |
|---|---|---|
| `forbidden_terms` | `terms`, `chapters`? | error |
| `watch_terms` | `terms`, `chapters`? | warning |
| `no_question_dialogue` | `chapters`? | warning (the speaker is for a person to judge) |
| `regex` | `pattern`, `message`?, `chapters`? | warning |

`chapters` accepts `"all"`, `"3"`, `"1-7"`, `"1,3,5-8"`. Any check can override `level`.

## coverage (optional)

Default:

```json
[{"type": "Theme", "relation": "EMBODIES", "level": "error"},
 {"type": "Chapter", "relation": "OCCURS_IN", "level": "error"},
 {"type": "PersonaTrait", "relation": "SHOWS_TRAIT", "level": "error"},
 {"type": "Motif", "relation": "USES_MOTIF", "level": "warning"}]
```

## exclusion files

Plain text, one node id per line, `#` comments allowed. Pass with `--exclude`. Use one per abridged edition; `chekhov impact --write-exclusions` can create it.
