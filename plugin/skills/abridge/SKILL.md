---
name: abridge
description: Make a shorter edition of a manuscript (e.g. 70 or 80 manuscript pages for a contest) by cutting whole scenes, then use the graph to find setups and echoes the cut broke (공모용 축약판 만들기). Use when the author needs to fit a length limit.
---

# 축약판 만들기

**문장을 깎지 말고 장면을 고른다.** 문장마다 조금씩 덜면 퇴고로 얻은 호흡이 무너진다. 빼는 기준은 하나다: *그 장면이 하는 일을 다른 장면이 이미 하고 있는가.*

## 1. 목표와 파일
- `chekhov count 원고`로 지금 분량을 잰다(글자÷200과 줄 단위 둘 다 보고한다).
- 축약판은 **별도 파일**이다. 완료본은 그대로 둔다. `.chekhov.json`의 `editions`에 축약판과 제외 목록 경로를 적는다.
- 응모처가 있으면 분량 기준("안팎")과 규정(AI 사용, 중복 응모, 미발표)을 먼저 확인한다. AI가 쓴 문장이 있는 원고는 AI 활용을 금지하는 공모에 낼 수 없다.

## 2. 지도부터 확인받는다
장별 목표 매수, 통째로 뺄 장면, 짧게 접을 장면, **반드시 지키는 연결**(그래프의 `SETS_UP`/`RHYMES_WITH`), **빼면서 잃는 것**을 표로 보여 주고 작가의 승인을 받는다. 클라이맥스의 대화 박자와 결말은 줄이지 않는 것이 기본이다.

## 3. 적용과 대조
1. 축약판 파일에 적용 → `chekhov count`. 목표에 못 미치면 다음 후보 장면을 지도에 추가해 다시 묻거나, 보고 때 밝힌다.
2. `chekhov impact --edition 이름`(또는 `impact graph.json 축약판.docx`) → 짝을 잃은 복선·운 목록.
3. **남은 쪽을 하나씩 다시 읽는다.** 남은 문장만으로 서면 둔다. 사슬의 가운데 고리가 빠져 끝의 변화가 안 보이면(예: 1장 → 4장 → 8장으로 이어지는 변화의 4장), 한 문장으로 되살린다.
4. 이음매(장면을 빼서 갑자기 붙은 두 문단)를 새로 잇는다.
5. `chekhov impact ... --write-exclusions 제외.txt` → `chekhov check --edition 이름` 오류 0건.

## 4. 보고
최종 매수, 뺀 장면, 되살린 것, 이음매, **아까운 것**(잃은 기능)을 솔직하게. 더 짧은 판(80 → 70)은 확정된 판에서 다시 같은 과정을 밟는다.
