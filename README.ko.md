# chekhov

**원고와 작품의 의미 그래프가 어긋나지 않게 지켜 주는 도구.**

> *1막에서 벽에 총을 걸었다면, 다음 막에서는 그 총을 쏴야 한다.* (안톤 체호프)
>
> chekhov는 그 총들을 기억한다. 모든 복선과 운, 작품의 규칙을 원고 속 문장에 묶어 둔다.
[English README](README.md)

AI 에이전트와 소설을 고치다 보면 에이전트는 잊는다. 결말을 조용히 받치던 문장을 고쳐 버리고, 여섯 장 뒤에서 운을 맞추는 장면을 잘라 내고, 감정에 이름을 붙이지 않던 화자가 어느새 "슬펐다"고 말하게 둔다. chekhov는 작품에 작가와 에이전트가 함께 확인할 수 있는 기억을 준다.

- **그래프**: 주제, 장, 인물, 페르소나 특성, 모티프, 장면. 장면마다 원고에서 그대로 옮긴 근거 문장이 붙는다. 복선은 회수를(`SETS_UP`), 운은 운을(`RHYMES_WITH`) 가리키고, 작품의 규칙은 **불변 규칙(invariants)**으로 적는다.
- **검사기**: LLM 없이 돌아가서 같은 입력에는 늘 같은 결과를 낸다. 원고와 그래프가 어긋나면 알려 준다.
- **작업 규칙과 피드백 로그**: 한 번 준 지적을 두 번 하지 않게 에이전트가 따르고 기록하는 틀.

한 편의 한국어 단편소설을 Claude Code와 50회차 넘게 퇴고하면서 만들어졌다. 아래 도구들은 그 과정에서 끝까지 쓸모가 있었던 것들이다.

## 설치

```bash
pip install git+https://github.com/<owner>/chekhov   # PyPI 등록 전
```

Python 3.10 이상. 원고는 `.docx`, `.md`, `.txt`. 장은 제목 패턴으로 나눈다(기본 `[1] 제목`, 바꿀 수 있음).

## 명령

```bash
chekhov init 내작품 --title "모래시계" --language ko   # 그래프 뼈대, 작업 규칙, 피드백 로그
chekhov check graph.json 원고.docx                     # 그래프와 원고 대조
chekhov impact graph.json 축약판.docx                  # 장면을 빼면 끊기는 것
chekhov audit 원고.docx                                # 장별 문단·문장 호흡
chekhov count 원고.docx                                # 글자 수와 200자 원고지 매수
```

### `check`
- **근거 문장**: 장면의 문장이 그 장에 아직 있는가. 조금 바뀐 문장은 지금 원고에서 가장 가까운 문장과 함께 보여 준다(`evidence-changed`). 사라진 문장은 `evidence-missing`.
- **연결**: 없는 노드를 가리키는 간선, 회수보다 뒤에 있는 복선(의도한 것은 `"reverse": true`).
- **빈자리**: 어떤 장면도 구현하지 않는 주제, 장, 페르소나 특성.
- **규칙**: 기계로 볼 수 있는 `check`가 붙은 불변 규칙(금지어, 주의어, 대사 속 질문, 정규식)과, 언어별 관습을 담은 **규칙 묶음**(`--pack ko`: 감정어, 비유 표지, 아라비아 숫자 표기).
- `--exclude 제외.txt`: 일부러 뺀 장면 목록(공모용 축약판 등).

오류가 있으면 종료 코드 1을 돌려주므로, 커밋 전 훅이나 에이전트의 수정 후 훅에 그대로 걸 수 있다.

### `impact`
장면을 빼면 짝을 잃는 복선과 운을 양쪽 문장과 함께 보여 준다. 축약판에 돌리고, 남은 쪽이 남은 문장만으로 여전히 서는지 다시 읽는다.

## 그래프 형식

[docs/schema.md](docs/schema.md) 참고. 일부러 느슨하다. 노드는 `id`와 `type`, 간선은 `source`, `relation`, `target`만 있으면 되고 나머지는 작품에 맞게 쓴다. 불변 규칙은 먼저 문장이고, 기계가 볼 수 있을 때만 `check`를 붙인다.

```json
{"id": "I-P2", "kind": "persona", "rule": "화자는 마지막 장 전까지 묻지 않는다.",
 "check": {"type": "no_question_dialogue", "chapters": "1-7"}}
```

## 에이전트와 함께 쓰기

`chekhov init`이 `AGENT_RULES.md`(`CLAUDE.md`나 `AGENTS.md`로 저장)와 `FEEDBACK_LOG.md`를 만든다. 효과가 컸던 규칙:

1. 누가 낸 제안이든 비판적으로 검토하고, 적용하지 않은 것은 이유와 함께 보고한다.
2. 고치기 전에 불변 규칙을 읽고, 고친 뒤 그래프를 고치고 `check`를 돌린다.
3. 원본은 고치지 않고, 작업본에 번호를 붙인다.
4. 회차마다 원칙, 작업 기록, 에이전트 자신의 실수를 기록한다.
5. 설계는 작가가 정한다. 설계를 증명하려고 문장을 끼워 넣지 않는다.

### Claude Code 플러그인

```text
/plugin marketplace add jeongchanyoung-1234/chekhov
/plugin install chekhov@chekhov
```

`chekhov` 명령이 PATH에 있어야 한다(위의 설치 먼저).

| 스킬 | 에이전트가 하는 일 |
|---|---|
| `chekhov-setup` | 작가에게 의도를 묻고, 원고에서 그래프 초안을 만들고, 오류 0건까지 검사하고, 자신이 해석해서 넣은 것을 따로 보여 준다 |
| `read-through` | 그래프와 로그를 기준으로 원고 전체를 검토한다. **고치지 않고** "반영할까요?"로 끝낸다 |
| `revise-chapter` | 작업본에서 장 단위로 고치고, 수정마다 비판적으로 검토하고, 그래프를 맞춘다 |
| `abridge` | 장면 단위로 덜어 축약판을 만들고, 짝을 잃은 복선·운을 하나씩 다시 읽는다 |
| `log-round` | 회차를 기록한다: 원칙, 작업 기록, 자신의 실수 |

`PostToolUse` 훅이 수정 뒤 `chekhov hook`을 돌린다. 그래프나 원고가 바뀌었을 때만 검사하고, 둘이 어긋나면 오류를 에이전트에게 보여 줘서 다음으로 넘어가기 전에 고치게 한다. 원고가 Word에 열려 있으면 경고한다.

작품 폴더에 `.chekhov.json`을 두면(`chekhov init`이 만든다) 훅과 `chekhov check`가 어느 파일을 볼지 안다.

```json
{"graph": "graph.json", "manuscript": "drafts/v0.2_작업1.docx", "exclude": null, "packs": ["ko/emotion-words"],
 "editions": {"공모80": {"manuscript": "공모판_80매.docx", "exclude": "공모판_80매_제외.txt"}}}
```

다음 계획은 [docs/roadmap.md](docs/roadmap.md) 참고.

## 라이선스

MIT
