---
name: revise-chapter
description: Revise a manuscript chapter by chapter with critical review of every change, keeping the semantic graph and feedback log in sync (장 단위 퇴고). Use when the author asks to apply review findings, revise a chapter, or "반영".
---

# 장 단위 퇴고

## 고치기 전에
1. `FEEDBACK_LOG.md`(1부 원칙, 2부 "다음에 정할 것")와 `graph.json` invariants를 읽는다.
2. **작업본에서만 고친다.** 원본·완료본은 건드리지 않는다. `.chekhov.json`의 `manuscript`가 작업본을 가리키는지 확인한다.
3. **작가가 직접 고친 곳을 먼저 찾는다.** 마지막으로 내가 저장한 판과 지금 파일을 비교한다. 작가의 수정도 비판적으로 검토하되, 말없이 덮어쓰지 않는다.
4. 파일이 Word에 열려 있으면(같은 폴더의 `~$` 파일) 저장이 실패한다. 작가에게 닫아 달라고 하고, 닫은 뒤 다시 3을 한다.

## 수정마다 묻는다 (누가 낸 제안이든)
- 인물(페르소나)과 맞는가 · 주제에 기여하는가 · 그 장의 상황과 맞는가 · 앞뒤 사실이 맞는가 · 문장으로서 좋은가
- 설계를 증명하려고 끼워 넣는 문장이 아닌가. 설계는 새 문장이 아니라 기존 장면의 감각을 고르는 기준으로 쓴다.
- 문장을 끼워 넣기만 하고 문단의 호흡은 그대로 두지 않았나. 고친 뒤 **장 전체를 다시 읽는다.**

## 고친 뒤에
1. 그래프를 맞춘다: 바뀐 근거 문장(`evidence`), 새 장면의 Event와 간선, 빠진 장면의 노드 정리(지운 이유는 `meta.removed`에). 규칙 문장 안의 설명처럼 검사기가 못 잡는 곳도 고친다.
2. `chekhov check` → 오류 0건. (플러그인 훅이 수정 뒤 자동으로 돌리고, 오류가 있으면 알려 준다.)
3. `log-round` 스킬로 로그를 갱신한다.
4. 작가에게 보고한다: 바꾼 것(장면별), **적용하지 않았거나 다르게 적용한 것과 이유**, 작가가 정할 질문. 다음 장으로 넘어갈지 묻는다.

## docx를 고칠 때
- python-docx로 문단 단위로 바꾼다. 바꿀 문단이 정확히 하나인지 확인하고(assert), 첫 run에 새 텍스트를 넣고 나머지 run은 지운다.
- 저장 전 파일 잠금을 확인한다. 저장 실패를 덮어쓰기로 해결하지 않는다.
