# 실제 답 4: 다섯 번째 원인 고치고 기록하기

`prompts.md` 6번 문장을 보냈을 때예요. Claude가 한 말과 Claude가 쓴 `artifacts/debug-note.md`를 고치지 않고 옮겼어요. 이 기록이 오늘의 "회귀 테스트 통과 기록"이에요.

- 날짜: 2026-10-17
- 모델: Sonnet 5.5 (`claude-sonnet-5-5`)
- 권한 모드: Accept edits (수업에서는 Manual로 카드를 보고 Accept)
- 걸린 시간: 46초, 주고받은 횟수 7

## 보낸 말

```text
5단계로 서비스 이름 공백 처리를 SPEC.md 규칙대로 고쳐 줘. 서비스 이름 처리 말고는 건드리지 마. 고친 다음 reproduce, tests/test_regression.py, 그리고 입력 검증 테스트(이름에 invalid, validate, bad_event)를 뺀 tests 전체를 work/debug/report.py로 다시 돌려 줘. 그다음 artifacts/debug-note.md에 디버깅 기록을 써 줘. 숫자는 이 대화에서 실행한 출력에서만 가져와.
```

## Claude의 답

````markdown
5단계로 서비스 이름 공백 처리를 고쳤고, 요청한 검사는 모두 통과했습니다. 디버깅 기록은 `artifacts/debug-note.md`에 썼습니다.

**수정 (`work/debug/report.py`, 서비스 이름 처리만)**
- 필터가 `None`이 아닐 때, 문자열이 아니거나 공백뿐이면 `ValueError`를 냅니다. 그 외에는 앞뒤 공백을 제거합니다. 출력의 `"service"`도 제거한 이름입니다.
- 비교 쪽도 `event["service"].strip() == service`로 고쳤습니다. 처음에는 필터 쪽만 고쳤는데, 제공 검사 `test_trimmed_service`가 `assert 0 == 1`로 실패했습니다. 이 검사는 행 `service`가 `" billing "`이어도 필터 `" billing "`과 일치해야 한다고 봅니다. SPEC에는 행 쪽 공백 규칙이 없습니다. 그래서 제공 검사를 기준으로 판단했고, 이 판단을 기록에도 남겼습니다.

**재실행 결과 (`work/debug/report.py`)**
- **`tools/reproduce.py`:** 재현 실패 사례 0/3, exit 0입니다.
- **`tests/test_regression.py`:** 4 passed입니다. 앞서 실패하던 `" billing "` 사례가 `total` 0에서 3으로 바뀌어 통과했습니다.
- **`tests` 전체(invalid/validate/bad_event 제외):** 23 passed, 26 deselected입니다. 필터만 고친 직후에는 22 passed, 1 failed였습니다.

**남은 일**
- 제외한 26개를 참고로 돌리면 22 failed, 4 passed입니다. 이벤트 필드 검증과 `slow_ms` 검증이 아직 없어서입니다. 예를 들어 `test_invalid_threshold[...]`와 `test_validate_before_filter`가 실패합니다.
- 행의 `service`가 문자열이 아니면 `.strip()`에서 `AttributeError`가 납니다. 이 부분은 입력 검증 단계에서 `ValueError`로 다뤄야 합니다.

`debug-note.md`의 숫자는 모두 이 대화에서 실행한 출력에서 가져왔습니다.
````

## Claude가 쓴 artifacts/debug-note.md

````markdown
# 디버깅 기록: summarize() 집계 버그

대상: `work/debug/report.py` (고의 버그 실습). 줄 번호는 수정 전 원본 기준이다. 아래 숫자는 모두 이 작업 중 실행한 출력에서 가져왔다.

## 증상 (수정 전, `tools/reproduce.py`)
`(error_count, error_rate_pct, slow_count)` 기준.

| 사례 | 실제 | 기대 |
| --- | --- | --- |
| 없는 서비스 `unknown` | `ZeroDivisionError` | (0, 0.0, 0) |
| `billing` | (2, 25.0, 1) | (2, 66.67, 2) |
| `catalog` | (1, 12.5, 0) | (0, 0.0, 1) |

## 원인과 수정
| 단계 | 원본 줄 | 원인 | 수정 | 바뀐 값 |
| --- | --- | --- | --- | --- |
| 1 | 10 | 0건일 때 `/ total`에서 0으로 나눔 | `total`이 0이면 평균 `0.0` | unknown: 예외 → (0, 0.0, 0) |
| 2 | 15 | 오류율 분모가 `len(events)`(전체 8건) | 분모를 `total`로, 0이면 `0.0` | billing 25.0 → 66.67, catalog 12.5 → 33.33 |
| 3 | 9 | 느린 요청 비교가 `>` | `>=` | billing slow 1 → 2, catalog slow 0 → 1 |
| 4 | 8 | 오류 기준이 `>= 400` (404도 오류로 셈) | `>= 500` | catalog (1, 33.33, 1) → (0, 0.0, 1), billing은 변화 없음 |
| 5 | 4~6 | 필터에 공백 제거가 없고 `if service:`가 공백뿐인 필터를 통과시킴 | 문자열이 아니거나 공백뿐이면 `ValueError`, 아니면 앞뒤 공백 제거. 행의 `service`도 공백을 제거해 비교 | `service=" billing "` 결과 `total` 0 → 3 |

단계 1~4는 reproduce를 단계마다 다시 실행해 위 값이 바뀌는 것을 확인했다. 5단계 결과는 아래 회귀 테스트와 제공 검사로 확인했다.

## 5단계에서 내린 판단
- SPEC은 "필터는 공백을 제거해 정확히 일치"라고만 쓰여 있다. 행 쪽 `service` 값의 공백은 말하지 않는다.
- 필터만 고친 직후 `tests/test_contract.py::test_trimmed_service`가 실패했다(`assert 0 == 1`). 이 검사는 행 `{"service": " billing "}`과 필터 `" billing "`이 일치해야 한다고 본다.
- 제공 검사를 기준으로 행의 `service`도 공백을 제거해 비교하도록 고쳤다. SPEC 문장만으로는 확정되지 않는 부분이므로 근거를 남긴다.
- 출력의 `"service"` 값은 공백을 제거한 필터 이름이다.

## 회귀 테스트
`tests/test_regression.py`에 `fixtures/events.json` 그대로 4건을 넣었다(없는 서비스, billing, catalog, `" billing "`).

| 구현 | 결과 |
| --- | --- |
| `buggy/report.py` | 4 failed |
| `work/debug/report.py` (4단계까지) | 3 passed, 1 failed (`" billing "`이 `total` 0) |
| `work/debug/report.py` (5단계 후) | 4 passed |

## 최종 검증 (`work/debug/report.py`)
- `tools/reproduce.py`: 재현 실패 사례 0/3, exit 0
- `tests/test_regression.py`: 4 passed
- `tests` 전체에서 이름에 invalid, validate, bad_event가 든 테스트를 뺀 실행: 23 passed, 26 deselected
  - 5단계에서 행의 `service` 공백 비교를 고치기 전에는 22 passed, 1 failed(`test_trimmed_service`)였다.

## 남은 일 (고치지 않음)
- 제외한 26개를 참고로 돌리면 22 failed, 4 passed다(`test_invalid_threshold[...]`, `test_validate_before_filter` 등). 이벤트 필드 검증과 `slow_ms` 검증이 아직 없다.
- 이 작업에서는 서비스 필터 인자 검증만 구현했다. 행의 `service`가 문자열이 아니면 `.strip()`에서 `AttributeError`가 난다. 이것도 입력 검증 단계에서 `ValueError`로 다뤄야 한다.
````
