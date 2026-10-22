# 디버깅 예시 프롬프트

수업 뒤에 혼자 해 보는 디버깅 연습에서 Claude에게 보내는 말의 예시예요. `labs/day2` 폴더로 Code 탭 세션을 열고 보내요. 그대로 써도 되지만, `<…>`로 표시한 곳은 내 버그와 내 계획에 맞게 바꿔요. 내 말로 바꿔 써도 돼요.

2026-10-17에 이 폴더의 사본에서 2번부터 6번까지의 문장을 Claude Code(모델 Sonnet 5.5)에 차례로 실제로 보내 봤어요. Claude가 실제로 한 말은 같은 폴더의 `01-plan-answer.md`부터 `04-debug-note.md`까지에 있어요. 1번은 같은 명령을 직접 실행해서 출력을 확인했어요. 맨 아래 "레거시로 할 때"의 두 문장도 inventory-py로 실제로 보내 봤고, 답은 `05-legacy-inv80.md`에 있어요.

| 순서 | 실습 | 모드 | 예시 |
| --- | --- | --- | --- |
| 1 | 재현하기 | Manual | 1번 |
| 2 | 사실 · 가설 · 계획 받기 | Plan | 2번 |
| 3 | 하나씩 고치기 | Manual | 3번, 4번 |
| 4 | 회귀 테스트와 기록 | Manual | 5번, 6번 |

Manual에서는 Claude가 파일을 고치거나 명령을 실행하기 전에 카드가 떠요. 카드를 읽고 **Accept**나 **Allow once**를 눌러요.

## 1. 재현하기 (Manual)

```text
tools/start.py debug를 실행하고, tools/reproduce.py로 work/debug/report.py를 재현해서 출력을 그대로 보여 줘.
```

- 이렇게 나오면 돼요: `재현 실패 사례: 3/3`. 같은 출력이 오류 로그 `fixtures/debug.log`에도 있어요.
- 이어서 세 칸으로 정리하게 해도 돼요: `<billing> 사례를 입력, 기대, 실제 세 칸으로 정리해 줘. 기대는 SPEC.md에서 가져와.`
- 바꿀 곳: `<billing>`을 `catalog`, `identity`, 없는 서비스로 바꿔 봐요. 세 칸 견본은 `three-cells.md`에 있어요.

## 2. 사실 · 가설 · 계획 받기 (Plan)

모드 선택기에서 **Plan**을 고른 뒤 보내요.

```text
SPEC.md, work/debug/report.py, fixtures/debug.log를 읽고 tools/reproduce.py로 먼저 재현해 줘. 실행해서 본 사실과 원인 가설을 나눠 줘. 가설마다 관련 줄 번호와, 그 가설이 틀렸는지 가려낼 검사를 붙여 줘. 마지막에 한 번에 한 줄씩 고치는 단계별 계획과 단계마다 바뀌어야 할 값을 적어 줘. reference/와 examples/는 읽지 마.
```

- 꼭 들어가야 하는 것: 재현 먼저, 사실과 가설 나누기, 가설마다 가려낼 검사, 단계별 계획과 바뀔 값, 정답(`reference/`)과 예시(`examples/`) 읽지 않기.
- 바꿀 곳: 레거시를 고른 사람은 읽을 파일(`<SPEC.md, work/debug/report.py, fixtures/debug.log>`)을 `<이슈 파일, 코드 파일, data 파일>`로 바꿔요.
- 계획이 끝나면 승인을 묻는 카드가 떠요. **No, keep planning**을 고르고, 모드를 **Manual**로 바꿔요.
- 실제 답: `01-plan-answer.md`

## 3. 한 단계만 고치기 (Manual)

```text
계획의 <1>단계만 해 줘. work/debug/report.py <10>행만 고치고 다른 줄은 건드리지 마. 고친 다음 reproduce를 다시 실행해서, 실패 개수 말고 어떤 값이 어떻게 바뀌었는지 말해 줘.
```

- 바꿀 곳: 단계 번호와 줄 번호. 내 계획의 순서를 따라요. 계획마다 순서가 달라도 괜찮아요. 같은 2번 문장을 다시 보냈을 때는 8행, 9행, 15행, 10행, 다시 15행 순서의 계획이 나왔어요.
- 15행 분모를 10행보다 먼저 고치는 순서라면, 10행에 0건 처리를 넣은 뒤에도 "없는 서비스"가 같은 `ZeroDivisionError`로 나와요. 이번에는 15행에서 0으로 나누는 거예요. `오류가 난 줄 번호를 보여 줘`라고 부탁하고, 15행에도 0건 처리를 넣어요.
- Accept를 누르기 전에 카드에서 바뀌는 줄이 하나뿐인지 봐요.
- 실제 답: `02-step-answers.md`의 1절

## 4. 남은 단계 (Manual, 시간이 모자랄 때)

```text
남은 단계를 한 단계씩 차례로 해 줘. 단계마다 한 줄만 고치고, reproduce를 다시 실행해서 어떤 값이 어떻게 바뀌었는지 보여 줘.
```

- 한 요청이어도 단계마다 카드가 따로 떠요. 카드마다 한 줄인지 봐요.
- 실제 답: `02-step-answers.md`의 2절

## 5. 회귀 테스트 만들기 (Manual)

```text
tests/test_regression.py에 버그 신고 입력 그대로 회귀 테스트를 만들어 줘. fixtures/events.json으로 없는 서비스, billing, catalog 세 사례와, service=" billing "이면 billing 3건을 찾는 사례를 넣어 줘. 테스트 이름에 invalid, validate, bad_event는 넣지 마. 버그가 든 buggy/report.py와 고친 work/debug/report.py에 각각 돌려서 출력을 그대로 보여 줘. report.py는 아직 고치지 마.
```

- 이렇게 나오면 돼요: 버그가 든 원본에서는 모두 실패하고(`4 failed`), 내 파일에서는 공백 이름 사례 하나만 실패해요(`1 failed, 3 passed`). 그 하나가 다섯 번째 원인이에요.
- 바꿀 곳: 남길 사례. 레거시를 고른 사람은 `<이슈의 입력>`으로 바꿔요.
- 실제 답과 Claude가 만든 테스트 파일: `03-regression-test.md`

## 6. 다섯 번째 원인 고치고 기록하기 (Manual)

```text
5단계로 서비스 이름 공백 처리를 SPEC.md 규칙대로 고쳐 줘. 서비스 이름 처리 말고는 건드리지 마. 고친 다음 reproduce, tests/test_regression.py, 그리고 입력 검증 테스트(이름에 invalid, validate, bad_event)를 뺀 tests 전체를 work/debug/report.py로 다시 돌려 줘. 그다음 artifacts/debug-note.md에 디버깅 기록을 써 줘. 숫자는 이 대화에서 실행한 출력에서만 가져와.
```

- 이렇게 나오면 돼요: 재현 `0/3`, 회귀 테스트 `4 passed`, 검증 테스트를 뺀 결과에 `failed`가 없어요.
- 필터 값만 공백을 지우면 제공 테스트 `test_trimmed_service`가 새로 실패해요. 실제로 Claude도 처음에 그랬다가 행 쪽도 고쳤어요. 고친 뒤 되던 것이 깨지는 일이 회귀예요.
- 실제 기록: `04-debug-note.md`

## 더 해 보기

- `identity` 서비스로 1번의 세 칸을 다시 해 봐요. 기대 값은 SPEC.md로 직접 계산해요(답은 `three-cells.md` 맨 아래).
- 한 단계는 Claude 없이 내가 직접 고쳐 보고, `reproduce를 다시 실행해서 값이 어떻게 바뀌었는지 말해 줘`라고만 부탁해요.
- 기록을 바탕으로 이슈 댓글 초안을 부탁해요: `debug-note.md를 보고 이 버그 이슈에 남길 댓글 초안을 써 줘. 원인, 바꾼 줄, 확인한 명령과 결과만.`

## 레거시로 할 때

1일차에 본 레거시(`labs/legacy`)의 열린 버그 이슈로 해도 돼요(예: inventory-py의 INV-80, notice-js의 NOTI-70, room-java의 ROOM-23). 복사한 폴더에서 하고, 원본은 고치지 않아요. 목표는 재현, 원인 분석, 수정 계획까지예요.

```text
issues/<ROOM-23>.md를 읽고, 증상이 나오는 입력을 data 폴더에서 찾아 원본을 실행해 줘. 입력, 기대, 실제 세 칸으로 정리해 줘. 아직 아무것도 고치지 마.
```

```text
<ROOM-23>을 고치는 단계별 계획을 세워 줘. 단계마다 바꿀 줄과, 고치면 원본 출력에서 어느 줄이 어떻게 바뀌는지 예측해 줘. 이슈의 결정(보류, 의도된 동작)도 확인해 줘.
```

- 첫 문장은 Manual, 두 번째 문장은 Plan 모드로 보내요. 바꿀 곳은 이슈 키(`<ROOM-23>`)예요.
- 그 언어 런타임이 내 PC에 없으면 원본을 실행하지 못해요. 그때는 이슈에 적힌 출력으로 세 칸을 채워 달라고 해요.
- 실제 답: 두 문장을 inventory-py의 INV-80으로 보내 본 결과가 `05-legacy-inv80.md`에 있어요. 이상한 판매 줄 두 개를 찾아 "기대 2줄, 실제 0줄"로 세 칸을 채웠고, 계획에서는 "리포트의 한 줄만 0줄에서 2줄로 바뀐다"고 예측했어요.
