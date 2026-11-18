---
name: chekhov-setup
description: Build the semantic graph for a novel or short story before revising it with an agent (소설 원고의 의미 그래프를 처음 만들 때). Use when the author starts revising a manuscript with chekhov, asks to "make a graph", or a folder has a manuscript but no .chekhov.json.
---

# 작품의 의미 그래프 만들기

그래프는 작품의 기억이다. 에이전트가 고치다 잊는 것(복선, 운, 인물의 규칙)을 원고 문장에 묶어 두고, `chekhov check`가 어긋남을 잡는다. 그래프를 만드는 동안 원고는 고치지 않는다.

## 0. 준비
- `chekhov --version`이 안 되면 작가에게 설치를 권한다: `pip install git+https://github.com/jeongchanyoung-1234/chekhov`
- **원본은 손대지 않는다.** 원고를 복사해 작업본(예: `제목_v0.1_작업1.docx`)을 만든다.
- `chekhov init . --title "제목" --manuscript 작업본.docx` → `graph.json`, `AGENT_RULES.md`(이것을 `CLAUDE.md`로 저장할지 작가에게 묻는다), `FEEDBACK_LOG.md`, `.chekhov.json`.
- 장 제목 형식이 `[1] 제목`이 아니면 `graph.json`의 `meta.chapter_pattern`을 맞춘다.

## 1. 작가에게 묻는다 (원고만 읽어서는 알 수 없는 것)
한 번에 몇 개씩, 작가의 말로 답을 받는다. 답은 `FEEDBACK_LOG.md` 2부 "확정된 설계"에 [작가]로 적는다.
- 주제를 몇 단계로 말하면? (출발점 → 도착점)
- 화자·문체의 의도는? (예: 감정을 직접 말하지 않는다, 짧고 담담하게)
- 상징·인물의 의미 중 작가가 정해 둔 것은? **AI가 혼자 의미를 정하지 않는다.**
- 바꾸면 안 되는 것, 바꿔도 되는 것(허용 범위)

## 2. 노드
| type | 무엇 | 주의 |
|---|---|---|
| `Chapter` | 장마다 하나 | `order` |
| `Theme` | 주제의 단계마다 하나 | 작가의 말로 |
| `Character` | 인물 | |
| `PersonaTrait` | 화자/주인공의 변하지 않는 특성 | 장면으로 근거를 대야 한다 |
| `Motif` | 되풀이되는 사물·이미지 | |
| `Event` | 장면·박자 | `chapter`(정수), `evidence`(**원고 문장을 그대로 복사**: 한 문장 또는 고유한 구절) |

Event는 의미가 걸린 장면만 만든다. 모든 문장이 노드일 필요는 없다.

## 3. 간선
- 근거: `OCCURS_IN`(Event→Chapter), `EMBODIES`(→Theme), `SHOWS_TRAIT`(→PersonaTrait), `USES_MOTIF`(→Motif)
- 연결: `SETS_UP`(복선→회수), `RHYMES_WITH`(꿈↔현실, 장↔장의 운). `note`에 왜 이어지는지 한 문장.
- 복선이 회수보다 뒤에 있는 의도된 경우는 `"reverse": true`.

## 4. 불변 규칙
작가가 말한 의도를 규칙 문장으로 적는다. 기계가 볼 수 있으면 `check`를 붙인다(docs/schema.md). 예: 감정어를 쓰지 않는 문체 → `meta.rule_packs`에 `"ko/emotion-words"`.

## 5. 검사와 보고
- `chekhov check`가 오류 0건이 될 때까지 고친다(`evidence-changed`는 대개 복사 실수).
- 작가에게 보고: 노드·간선 수, 주제 단계별 근거 장면, **AI가 해석해서 넣은 것**(상징의 의미, 운의 이유) 목록을 따로 보여 주고 확인받는다.
- `FEEDBACK_LOG.md` 2부에 0회차로 기록한다.
