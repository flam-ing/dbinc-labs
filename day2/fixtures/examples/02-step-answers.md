# 실제 답 2: 한 단계씩 고치기 (Manual 자리)

1번 답의 계획을 이어서 한 단계씩 고쳤을 때 Claude가 한 말이에요. 고치지 않고 그대로 옮겼어요.

- 날짜: 2026-10-17, 모델: Sonnet 5.5, 같은 대화에서 이어서 보냈어요.
- 권한 모드: 헤드리스 실행이라 카드를 누를 수 없어서 Accept edits로 돌렸어요. 수업에서는 Manual로 두고 카드마다 바뀌는 줄을 본 다음 **Accept**를 눌러요.

## 1. 1단계만 (9초, 주고받은 횟수 3)

### 보낸 말

```text
계획의 1단계만 해 줘. work/debug/report.py 10행만 고치고 다른 줄은 건드리지 마. 고친 다음 reproduce를 다시 실행해서, 실패 개수 말고 어떤 값이 어떻게 바뀌었는지 말해 줘.
```

### Claude의 답

````markdown
1단계로 `work/debug/report.py` 10행만 고쳤습니다. 이제 `total`이 0이면 `average`가 `0.0`이 됩니다.

```python
average = sum(event["latency_ms"] for event in rows) / total if total else 0.0
```

reproduce를 다시 실행한 결과, 바뀐 값은 `unknown` 사례 하나뿐입니다.

| 사례 | 수정 전 | 수정 후 |
| --- | --- | --- |
| `unknown` | 10행에서 `ZeroDivisionError` | `(error_count, error_rate_pct, slow_count)` = `(0, 0.0, 0)`, 기대값과 일치 |
| `billing` | `(2, 25.0, 1)` | 변화 없음 |
| `catalog` | `(1, 12.5, 0)` | 변화 없음 |

- `unknown`의 `error_rate_pct`가 0.0이 된 것은 15행의 `0 / len(events)`가 0.0이기 때문입니다. 분모 `len(events)`는 아직 그대로라 2단계에서 고칩니다.
- `billing`의 25.0(분모 8), slow 1(`>`), `catalog`의 error 1(404을 오류로 셈)과 slow 0은 모두 그대로입니다. 각각 2, 3, 4단계 몫입니다.

`git diff --stat`은 아무것도 출력하지 않았습니다. 저장소에서 이 파일이 추적되지 않는 것 같지만 확인하지는 않았습니다.
````

## 2. 남은 단계를 한 단계씩 (22초, 주고받은 횟수 7)

### 보낸 말

```text
남은 단계를 한 단계씩 차례로 해 줘. 단계마다 한 줄만 고치고, reproduce를 다시 실행해서 어떤 값이 어떻게 바뀌었는지 보여 줘.
```

### Claude의 답

````markdown
2~4단계를 차례로 적용했습니다. 단계마다 한 줄만 고쳤고, 그때마다 reproduce를 다시 실행했습니다. `(error_count, error_rate_pct, slow_count)` 기준으로 바뀐 값은 아래와 같습니다.

| 단계 | 고친 줄 | `billing` | `catalog` |
| --- | --- | --- | --- |
| 2 | 15행: 분모를 `len(events)`에서 `total`로 바꾸고, 0이면 `0.0` | `(2, 25.0, 1)` → `(2, 66.67, 1)`. rate만 바뀌었고 slow는 아직 1입니다. | `(1, 12.5, 0)` → `(1, 33.33, 0)`. rate만 바뀌었습니다. |
| 3 | 9행: `>`를 `>=`로 | `(2, 66.67, 1)` → `(2, 66.67, 2)`. slow가 1에서 2로 바뀌어 기대값과 일치하고 통과했습니다. | `(1, 33.33, 0)` → `(1, 33.33, 1)`. slow가 0에서 1로 바뀌었습니다. error와 rate는 아직 틀립니다. |
| 4 | 8행: `>= 400`을 `>= 500`으로 | 변화 없음. 500과 503만 오류라 `(2, 66.67, 2)` 그대로입니다. | `(1, 33.33, 1)` → `(0, 0.0, 1)`. 404가 오류에서 빠져 error와 rate가 바뀌었고, 기대값과 일치해 통과했습니다. |

- `unknown`은 1단계 이후 `(0, 0.0, 0)`이고 단계 2~4에서 변하지 않았습니다. 2단계에서 15행 분모가 `total`로 바뀌어도 `total`이 0이면 `0.0`을 내는 가드 덕분입니다.
- 사례 1~3이 모두 통과해 reproduce는 `0/3`, exit 0입니다.
- 수정은 `work/debug/report.py` 8, 9, 10, 15행에만 했습니다.
- 입력 검증과 서비스 이름 공백 처리는 아직 구현하지 않았습니다. reproduce는 이 부분을 검사하지 않습니다. `tests/test_contract.py`로 남은 실패를 확인한 뒤 별도로 다루겠습니다.
````

## 다 고친 뒤 바뀐 줄

```diff
8,10c8,10
<     errors = sum(event["status"] >= 400 for event in rows)
<     slow = sum(event["latency_ms"] > slow_ms for event in rows)
<     average = sum(event["latency_ms"] for event in rows) / total
---
>     errors = sum(event["status"] >= 500 for event in rows)
>     slow = sum(event["latency_ms"] >= slow_ms for event in rows)
>     average = sum(event["latency_ms"] for event in rows) / total if total else 0.0
15c15
<         "error_rate_pct": round(errors / len(events) * 100, 2),
---
>         "error_rate_pct": round(errors / total * 100, 2) if total else 0.0,
```
