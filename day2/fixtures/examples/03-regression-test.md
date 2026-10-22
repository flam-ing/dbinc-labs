# 실제 답 3: 회귀 테스트 만들기

4단계까지 고친 다음 `prompts.md` 5번 문장을 보냈을 때예요. Claude가 한 말과 만든 테스트 파일을 고치지 않고 옮겼어요.

- 날짜: 2026-10-17
- 모델: Sonnet 5.5 (`claude-sonnet-5-5`)
- 권한 모드: Accept edits (수업에서는 Manual로 카드를 보고 Accept)
- 걸린 시간: 27초, 주고받은 횟수 5

## 보낸 말

```text
tests/test_regression.py에 버그 신고 입력 그대로 회귀 테스트를 만들어 줘. fixtures/events.json으로 없는 서비스, billing, catalog 세 사례와, service=" billing "이면 billing 3건을 찾는 사례를 넣어 줘. 테스트 이름에 invalid, validate, bad_event는 넣지 마. 버그가 든 buggy/report.py와 고친 work/debug/report.py에 각각 돌려서 출력을 그대로 보여 줘. report.py는 아직 고치지 마.
```

## Claude의 답

````markdown
`tests/test_regression.py`를 만들었고 두 구현에 각각 돌렸습니다. 버그가 든 `buggy/report.py`는 4건 모두 실패했습니다. 고친 `work/debug/report.py`는 3건 통과, 1건 실패(exit 1)입니다. `report.py`는 더 고치지 않았습니다.

**테스트 구성**
- 입력은 모두 `fixtures/events.json`입니다. 구현은 기존 `conftest.py`의 `report_module` 픽스처가 `--impl`로 고릅니다.
- 테스트 이름은 `test_unknown_service_is_empty`, `test_billing_rate_uses_filtered_total`, `test_catalog_404_and_500ms_boundary`, `test_padded_service_name_finds_billing`입니다. `invalid`, `validate`, `bad_event`는 넣지 않았습니다.
- 기대값은 SPEC.md 계산 기준으로 직접 구했습니다.
  - unknown: 모두 0이고 비율과 평균은 `0.0`입니다.
  - billing: `total` 3, `error_count` 2, `error_rate_pct` 66.67, `slow_count` 2, `average_ms` 506.67입니다.
  - catalog: `total` 3, `error_count` 0, `error_rate_pct` 0.0, `slow_count` 1, `average_ms` 363.0입니다.
  - `service=" billing "`: `total`이 3이고 `service`가 `"billing"`입니다.

**`buggy/report.py` 결과 (4 failed)**
```
tests/test_regression.py FFFF
FAILED test_unknown_service_is_empty            - ZeroDivisionError (buggy/report.py:10)
FAILED test_billing_rate_uses_filtered_total    - error_rate_pct 25.0 != 66.67, slow_count 1 != 2
FAILED test_catalog_404_and_500ms_boundary      - error_rate_pct 12.5 != 0.0, slow_count 0 != 1, error_count 1 != 0
FAILED test_padded_service_name_finds_billing   - ZeroDivisionError (buggy/report.py:10)
4 failed in 0.02s
```

**`work/debug/report.py` 결과 (1 failed, 3 passed)**
```
tests/test_regression.py ...F
FAILED test_padded_service_name_finds_billing - assert 0 == 3
1 failed, 3 passed in 0.01s
```

공백이 붙은 `" billing "`은 `work/debug/report.py` 6행이 `event["service"] == service`로 공백을 제거하지 않아 0건이 됩니다. 앞서 "재현 사례가 못 잡는 부분"으로 짚은 문제이고, 이번 테스트로 드러났습니다. 고치는 일은 지시대로 하지 않았습니다.

`work/`는 `.gitignore`에 들어 있어 git이 추적하지 않습니다.
````

## Claude가 만든 tests/test_regression.py

```python
"""버그 신고 입력(fixtures/events.json) 그대로의 회귀 테스트. 예상 값은 SPEC.md 계산 기준으로 구했다."""
import json
from pathlib import Path

import pytest

EVENTS_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "events.json"


@pytest.fixture
def reported_events():
    return json.loads(EVENTS_PATH.read_text())


def test_unknown_service_is_empty(report_module, reported_events):
    assert report_module.summarize(reported_events, service="unknown") == {
        "service": "unknown", "total": 0, "error_count": 0,
        "error_rate_pct": 0.0, "slow_count": 0, "average_ms": 0.0,
    }


def test_billing_rate_uses_filtered_total(report_module, reported_events):
    assert report_module.summarize(reported_events, service="billing") == {
        "service": "billing", "total": 3, "error_count": 2,
        "error_rate_pct": 66.67, "slow_count": 2, "average_ms": 506.67,
    }


def test_catalog_404_and_500ms_boundary(report_module, reported_events):
    assert report_module.summarize(reported_events, service="catalog") == {
        "service": "catalog", "total": 3, "error_count": 0,
        "error_rate_pct": 0.0, "slow_count": 1, "average_ms": 363.0,
    }


def test_padded_service_name_finds_billing(report_module, reported_events):
    result = report_module.summarize(reported_events, service=" billing ")
    assert result["total"] == 3
    assert result["service"] == "billing"
```
