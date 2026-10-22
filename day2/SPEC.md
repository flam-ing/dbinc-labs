# 서비스 이벤트 집계 명세

이 실습의 서비스 이름과 이벤트는 모두 교육용 가상 데이터입니다. 실제 DB Inc 시스템이나 고객 데이터는 사용하지 않습니다.

## 만들 함수

```python
summarize(events, service=None, slow_ms=500)
```

`events`는 딕셔너리의 리스트입니다. 원본 리스트와 딕셔너리를 바꾸지 않습니다.

| 필드 | 조건 |
| --- | --- |
| `service` | 공백을 제거했을 때 비어 있지 않은 문자열 |
| `status` | 100~599 정수. `True`/`False`는 정수가 아닌 것으로 처리 |
| `latency_ms` | 0 이상 정수. `True`/`False`, 실수, 문자열은 허용하지 않음 |
| `id` | 조회 결과를 구분하는 교육용 ID. 집계 함수는 이 필드를 요구하거나 중복 제거하지 않음 |

`service=None`이면 전체를 집계합니다. 필터가 문자열이면 앞뒤 공백을 제거해 정확히 일치하는 서비스만 집계합니다. 알 수 없는 서비스는 0건입니다.

모든 입력 행의 유효성을 먼저 검사합니다. 필터에 포함되지 않는 행도 잘못된 필드가 있으면 `ValueError`입니다. 누락된 필드, 잘못된 타입, 범위를 벗어난 값도 `ValueError`입니다. 메시지의 정확한 문장은 고정하지 않습니다.

`slow_ms`는 0 이상 정수입니다. `service` 필터는 `None` 또는 공백을 제거했을 때 비어 있지 않은 문자열입니다. 잘못된 인자는 `ValueError`입니다.

## 계산 기준

- `total`: 필터를 적용한 이벤트 수
- `error_count`: HTTP 상태가 **500 이상**인 이벤트 수
- `error_rate_pct`: `round(error_count / total * 100, 2)`
- `slow_count`: 응답 시간이 **slow_ms 이상**인 이벤트 수
- `average_ms`: `round(응답 시간 합 / total, 2)`
- 필터 결과가 0건이면 수량은 `0`, 비율과 평균은 `0.0`
- 소수점 처리는 Python `round(value, 2)`를 사용

## 출력

```json
{
  "service": "billing",
  "total": 3,
  "error_count": 2,
  "error_rate_pct": 66.67,
  "slow_count": 2,
  "average_ms": 506.67
}
```

위 결과는 `fixtures/events.json`에서 billing만 골랐을 때입니다. 전체 집계의 `service` 값은 `"all"`입니다. 출력 키 6개를 그대로 유지합니다.

## 먼저 생각해 볼 테스트

빈 리스트, 없는 서비스, 499/500 상태 코드, 499/500/501ms, 0ms, 필터를 적용한 오류율의 분모, 공백이 붙은 서비스 이름, 잘못된 입력, 실행 전후 원본이 같은지 확인해 보세요.

테스트를 만들 때 `reference/` 구현을 읽지 말고 이 명세로 예상 값을 계산합니다. `tests/test_contract.py`는 마지막에 실행할 제공 검사입니다.
