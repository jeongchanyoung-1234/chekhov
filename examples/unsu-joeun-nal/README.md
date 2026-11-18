# 예제: 현진건 「운수 좋은 날」 (발췌)

- 원문: 현진건, 「운수 좋은 날」(1924). [위키문헌](https://ko.wikisource.org/wiki/운수_좋은_날)의 본문. 작가가 1943년에 세상을 떠나 공유 저작물이다.
- `story.md`는 네 대목을 원문 그대로 발췌하고 `[1]`~`[4]` 제목만 붙였다(약 4,000자, 원고지 약 20매).
- `graph.json`의 해석(`[해석]`)은 예시다. 실제 작업에서는 작가에게 묻고 작가의 말로 적는다.

| 대목 | 들어 있는 것 |
|---|---|
| [1] 운수 좋은 아침 | 얼다 만 비, 오래간만의 행운, 아내의 기침, 설렁탕 국물을 조르는 아내 |
| [2] 정거장 | 이어지는 행운이 겁나는 김 첨지, "오늘은 나가지 말아요" |
| [3] 선술집 | 웃다가 울며 "우리 마누라가 죽었다네" |
| [4] 설렁탕 | 기침 소리 없는 집, 천장만 보는 눈, "운수가 좋더니만" |

## 해 보기

이 폴더에서 (`.chekhov.json`이 그래프와 원고를 알려 준다):

```bash
chekhov check                 # 오류 0건
chekhov check --pack ko       # 비유·짐작 표지를 사람이 볼 수 있게
chekhov count
chekhov audit
```

에이전트가 실제로 저지르는 일을 흉내 내 보자. 원고를 복사해서:

1. **문장을 다듬다 근거를 건드림.** `설렁탕 국물이 마시고 싶다고`를 `설렁탕 한 그릇이 먹고 싶다고`로 바꾸고 `chekhov check` → `evidence-changed`가 바뀐 문장과 함께 나온다. 이 문장은 결말의 "왜 먹지를 못하니"를 받치는 복선이다.
2. **규칙을 어김.** [2]에 "죽었다"는 말을 넣으면 `I-S1`(아내의 죽음은 마지막 대목에서 처음 확인된다)이 오류를 낸다.
3. **축약판.** [3] 선술집을 통째로 빼고 `chekhov impact graph.json 축약.md` → 짝을 잃은 연결 세 개가 나온다. 그중 하나: 4장의 "천장만 보느냐"는 3장의 취중 예감("우리 마누라가 죽었다네")을 잃는다. 남은 문장만으로 결말이 여전히 서는지 다시 읽을 곳이다.

## Example (English summary)

A verbatim excerpt of Hyeon Jin-geon's "A Lucky Day" (1924, public domain) with a 39-node graph: the wife's craving for seolleongtang soup sets up the ending, her plea "don't go out today" sets up her unseeing eyes, and the drunk man's "my wife is dead" in the tavern foreshadows what he finds at home. Try `chekhov check`, then break an evidence sentence, violate `I-S1`, or cut section [3] and run `chekhov impact`.
