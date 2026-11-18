---
name: read-through
description: Read the whole manuscript and review it for literary quality, readability and immersion against the work's graph and feedback log, without editing (원고 통독 검토). Use when the author asks for a read-through, a review, "어떻게 생각해", or before finalizing a version.
---

# 통독 검토

**고치지 않는다.** 이 단계의 산출물은 판단과 제안이다. 고치는 것은 작가가 고른 뒤 `revise-chapter`로 한다.

## 읽기 전에
- `FEEDBACK_LOG.md` 1부(원칙)와 2부 "다음에 정할 것"을 읽는다.
- `graph.json`의 invariants를 읽는다.
- `storygraph check`(오류가 있으면 먼저 보고)와 `storygraph audit`(장별 호흡 수치)를 돌린다. 수치는 읽을 곳을 고르는 데만 쓴다. 판정은 사람이 읽고 한다.

## 읽으며 볼 것
1. **문학성**: 주제를 화자의 말로 진술하는 문장, 장치를 위한 장치, 예쁘지만 기능이 없는 문장, 장소의 일반적인 색.
2. **가독성**: 장면이 이름표("조회 시간에")로 훅 바뀌는 곳, 짧은 문단·단문이 긴장도 아닌데 이어지는 곳, 감정을 절제한 자리가 감각 없이 비어 있는 곳.
3. **몰입감**: 인과·시간·사실의 어긋남(누가 언제 어떻게 알았나), 인물이 설계의 표본처럼 움직이는 곳.
4. **그래프**: 복선과 회수, 꿈과 현실의 운이 **원고에서도** 보이는가. 그래프에만 적혀 있고 원고에서는 다른 말로 쓰여 독자에게 이어지지 않는 연결은 없는가.
5. 외부 평가(다른 AI, 합평)가 함께 오면 그대로 받지 않는다. 원고와 대조해 놓친 것·맞는 것·주제를 바꾸는 것을 가른다.

## 보고 형식
- 장·문단 위치, 문제, 제안(고칠 문장 초안), 근거(로그의 원칙 번호나 invariant id).
- **적용하지 않을 것**도 이유와 함께 적는다.
- 설계를 바꾸는 질문(인물의 의미, 결말)은 따로 모아 작가에게 묻는다.
- 마지막에 "반영할까요?"로 끝내고, 작가가 고른 것만 다음 단계에서 고친다.
