# 실제 답 1: 사실, 가설, 단계별 계획 (Plan 모드)

`prompts.md` 2번 문장을 Plan 모드로 보냈을 때 Claude가 한 말이에요. 고치지 않고 그대로 옮겼어요. 같은 문장을 보내도 가설 이름, 표 모양, 고칠 순서는 사람마다 조금씩 달라요. 순서가 달라도 "한 번에 한 줄, 값으로 확인"은 같아요.

- 날짜: 2026-10-17
- 모델: Sonnet 5.5 (`claude-sonnet-5-5`)
- 권한 모드: Plan (명령 실행만 허락)
- 걸린 시간: 1분 18초, 주고받은 횟수 8
- 폴더: 2일차 실습 폴더 사본. `CLAUDE.md`에 1교시의 `.venv` 줄과 "reference/report.py는 열지 않는다" 줄이 있고, `python tools/start.py debug`를 먼저 실행해 둔 상태예요.
- Claude가 읽은 파일: `SPEC.md`, `work/debug/report.py`, `fixtures/debug.log`, `tools/reproduce.py`. 실행한 명령: `.venv/bin/python tools/reproduce.py`. `reference/`와 `examples/`는 열지 않았어요.
- 소스 파일은 하나도 바뀌지 않았어요. 계획은 Plan 창(데스크톱 앱 오른쪽)에 따로 보여요.
- 답 첫 문단의 계획 파일 경로에서 강사 PC의 사용자 이름만 `…`로 줄였어요. 나머지는 원문 그대로예요.

## 보낸 말

```text
SPEC.md, work/debug/report.py, fixtures/debug.log를 읽고 tools/reproduce.py로 먼저 재현해 줘. 실행해서 본 사실과 원인 가설을 나눠 줘. 가설마다 관련 줄 번호와, 그 가설이 틀렸는지 가려낼 검사를 붙여 줘. 마지막에 한 번에 한 줄씩 고치는 단계별 계획과 단계마다 바뀌어야 할 값을 적어 줘. reference/와 examples/는 읽지 마.
```

## Claude의 답

````markdown
`tools/reproduce.py`로 재현했습니다. 3개 사례가 모두 실패했고(exit 1), `fixtures/debug.log`의 기록과 같은 출력입니다. 계획 모드라 코드는 고치지 않았습니다. 가설 검사도 아직 실행하지 않았습니다. 계획은 `/Users/…/.claude/plans/spec-md-work-debug-report-py-fixtures-de-generic-unicorn.md`에 있습니다.

## 실행해서 본 사실

| 사례 | 실제 | 기대 |
| --- | --- | --- |
| 없는 서비스 `unknown` | `ZeroDivisionError` | (0, 0.0, 0) |
| `billing` | error 2, rate 25.0, slow 1 | (2, 66.67, 2) |
| `catalog` | error 1, rate 12.5, slow 0 | (0, 0.0, 1) |

- 25.0은 2/8이고, 8은 필터 후 3건이 아니라 전체 이벤트 수입니다.
- catalog의 error 1은 evt-005(404)이고, 500ms 행(evt-006)은 slow에서 빠졌습니다.

## 원인 가설과 반증 검사

| # | 가설 | 줄 | 틀렸는지 가리는 검사 |
| --- | --- | --- | --- |
| H1 | 0건일 때 평균 계산에서 0으로 나눕니다. | 10 | `unknown`과 `summarize([])`의 트레이스백 마지막 줄이 10행이 아니면 틀린 가설입니다. |
| H2 | 오류율 분모가 `total`이 아니라 `len(events)`입니다. | 15 | 필터 없음(`None`)에서는 결과가 맞고 billing에서만 25.0이면 맞습니다. `None`에서도 틀리면 틀린 가설입니다. |
| H3 | 느린 요청 비교가 `>`라서 500ms가 빠집니다. | 9 | 500ms 단독 행으로 `slow_ms=500`일 때 0이면 맞습니다. 499/501 행은 `>`와 `>=`의 결과가 같아야 합니다. |
| H4 | 오류 기준이 `>= 400`이라 404도 오류로 셉니다. | 8 | 404 단독 행에서 error 1이면 맞습니다. 499 상태 행도 1이어야 하고, 500 상태 행은 수정 전후 모두 1이어야 합니다. |

## 단계별 수정 계획 (한 번에 한 줄, 매 단계 후 재현 스크립트 재실행)

| 단계 | 줄 | 변경 | 바뀌어야 할 값 |
| --- | --- | --- | --- |
| 1 | 10 | `total`이 0이면 average를 `0.0`으로 합니다. | unknown은 예외 대신 (0, 0.0, 0)이 되어 사례 1이 통과합니다. |
| 2 | 15 | 분모를 `total`로 바꾸고, 0이면 `0.0`으로 합니다. | billing rate 25.0 → 66.67, catalog rate 12.5 → 33.33. 사례 2는 slow가 1이라 아직 실패합니다. |
| 3 | 9 | `>`를 `>=`로 바꿉니다. | billing slow 1 → 2(사례 2 통과), catalog slow 0 → 1. |
| 4 | 8 | `>= 400`을 `>= 500`으로 바꿉니다. | catalog error 1 → 0, rate 0.0(사례 3 통과). billing은 2 그대로입니다. |

- 단계 1을 단계 2보다 먼저 해야 합니다. 2를 먼저 하면 unknown에서 15행이 `total`로 0을 나눕니다.
- 사례 2와 사례 3은 단계 두 개가 모두 있어야 통과합니다. 중간 단계에서 실패가 남는 것이 정상입니다.

## 재현 사례가 못 잡는 부분

입력 검증(`ValueError`)이 없습니다. 서비스 이름의 공백 제거도 없고, 4행 `if service:`는 빈 문자열을 필터 없음으로 처리합니다. 위 4단계에는 넣지 않았고, 4단계가 끝난 뒤 `tests/test_contract.py`로 남은 실패를 확인한 다음 별도 단계로 다루려 합니다.

`reference/`와 `examples/`는 읽지 않았습니다.
````
