# 루틴이 만든 PR 견본 (로컬 리허설)

수업 루틴이 이슈 하나를 처리하면 어떤 PR이 나오는지 미리 본 견본이에요. 2026-10-17에 `make_repo.py`로 만든 실습 저장소에서, `routine-prompt.md`의 요청문을 GitHub 단계(이슈 찾기, push, PR 만들기, 라벨 떼기)만 빼고 Claude Code(Sonnet 5.5)에 보냈어요. 이슈 본문은 `bug-issue-example.md`의 billing 이슈예요. Claude는 `claude/issue-1` 브랜치에 커밋하고, PR 본문을 파일로 썼어요. 아래 글은 고치지 않고 옮겼어요.

- 걸린 시간: 46초, 주고받은 횟수 6
- 바뀐 파일: `report.py`, `tests/test_regression.py` 두 개뿐이에요. `tests/test_contract.py`, `SPEC.md`, `fixtures/`는 그대로예요.
- 직접 다시 확인: PR 브랜치에서 `python tools/reproduce.py`는 `재현 실패 사례: 0/3`, `python -m pytest -q`는 `48 passed`였어요.

실제 클라우드 루틴은 실행마다 답이 달라요. 내 PR이 이것과 달라도 괜찮아요. 아래 "검토할 때 볼 곳"으로 봐요.

## PR 제목

```text
fix: billing 오류율이 66.67%가 아니라 25.0%로 나오는 문제 (#1)
```

## PR 본문 (Claude가 쓴 그대로)

````markdown
Closes #1

## 원인
`summarize`에 서로 독립적인 결함 5개가 있었어요.
1. 오류 기준이 `status >= 400`이었어요(명세: 500 이상). 404가 오류로 셌어요.
2. 느린 요청 기준이 `latency_ms > slow_ms`였어요(명세: slow_ms 이상). 500ms가 빠졌어요.
3. 오류율의 분모가 필터 전 `len(events)`였어요(명세: 필터 후 `total`).
4. 필터 결과가 0건이면 평균 계산에서 `ZeroDivisionError`가 났어요(명세: 0.0).
5. 서비스 필터의 앞뒤 공백을 제거하지 않았어요. 공백만 있는 이름은 이미 `ValueError`로 막혀 있었는데, 공백이 붙은 이름은 일치하지 않아 0건이 되고 4번 때문에 `ZeroDivisionError`가 났어요.

## 바꾼 줄 (`report.py`, `summarize`)
- `if service:` → `if service is not None:` 그리고 `service = service.strip()`
- 필터 비교: `event["service"] == service` → `event["service"].strip() == service`
- `>= 400` → `>= 500`
- `latency_ms > slow_ms` → `latency_ms >= slow_ms`
- `errors / len(events)` → `errors / total`
- `total`이 0이면 `error_rate_pct`, `average_ms`를 `0.0`으로 계산 (예외를 잡아 숨기지 않고 분기)
- `tests/test_regression.py` 추가 (이슈 입력 그대로 4건)

## 실행한 명령과 결과
수정 전:
- `python tools/reproduce.py` → 재현 실패 사례: 3/3
- `python -m pytest -q` → 8 failed, 36 passed

한 원인씩 고친 뒤 재현 실패/pytest 결과: 오류 기준 3/3, 6 failed → 느린 기준 2/3, 4 failed → 분모 1/3, 3 failed → 0건 처리 0/3, 0 failed → 공백 처리(1차 구현) 0/3, 1 failed(`test_trimmed_service`) → 이벤트 쪽도 `strip()` 비교로 수정 후 0 failed.

최종:
- `python tools/reproduce.py` → 재현 실패 사례: 0/3
- `python -m pytest -q` → 48 passed
- 이슈의 공백 명령(`service=' billing '`) 결과는 회귀 테스트 `test_service_filter_is_trimmed`(total == 3)로 확인했어요. 이슈의 `python -c` 명령 자체는 실행하지 않았어요.

## 확인하지 못한 것 / 검토 요청
- SPEC.md는 "정확히 일치하는 서비스만"이라고 하지만, `tests/test_contract.py::test_trimmed_service`는 서비스 이름이 `" billing "`인 이벤트도 필터 `" billing "`에 일치해야 한다고 해요. 테스트를 통과시키려고 이벤트 쪽 이름도 `strip()`해서 비교했어요. 명세와 테스트가 어긋나는지 사람이 판단해 주세요. 테스트와 명세는 고치지 않았어요.
- 다른 입력(예: 큰 데이터, 비정상 `slow_ms`)은 따로 확인하지 않았어요.
````

## 루틴 세션에 남은 Claude의 말

````markdown
이슈 #1을 재현해서 고쳤고, `claude/issue-1` 브랜치에 커밋했어요(`7e3d502`). 고친 뒤 `python tools/reproduce.py`는 재현 실패 사례가 0/3이고, `python -m pytest -q`는 48개 모두 통과했어요. 커밋 전에는 재현이 3/3 실패였고 pytest는 8개가 실패였어요. PR 본문은 `pr-body.md`에 썼고 커밋하지 않았어요.

`report.py`의 `summarize`에서 원인 5개를 하나씩 고치고, 고칠 때마다 재현과 테스트를 다시 돌렸어요.
1. **오류 기준:** `status >= 400`을 `>= 500`으로 바꿨어요. 404가 오류로 세어지고 있었어요.
2. **느린 요청 기준:** `latency_ms > slow_ms`를 `>=`로 바꿨어요. 500ms가 빠지고 있었어요.
3. **오류율 분모:** 필터 전 전체 건수 `len(events)` 대신 필터 후 건수 `total`로 나눠요.
4. **0건 처리:** 필터 결과가 0건이면 `ZeroDivisionError`가 났어요. 이제 오류율과 평균을 `0.0`으로 돌려주고, 예외를 잡아 숨기지는 않았어요.
5. **공백 필터:** 필터 문자열의 앞뒤 공백을 제거해요.

회귀 테스트는 이슈의 입력으로 4건을 `tests/test_regression.py`에 더했어요. 이슈에 있는 `python -c` 공백 명령 자체는 실행하지 않았고, 같은 입력을 `test_service_filter_is_trimmed` 테스트로 확인했어요.

명세와 테스트가 어긋나는 곳이 하나 있어서 PR 본문에 적었어요. SPEC.md는 "정확히 일치하는 서비스만" 집계한다고 하는데, `test_trimmed_service`는 서비스 이름이 `" billing "`인 이벤트도 필터 `" billing "`과 일치해야 한다고 해요. 테스트를 통과시키려고 이벤트 쪽 이름도 `strip()`해서 비교했어요. 어느 쪽이 맞는지는 사람이 정해 주세요. 테스트와 명세는 고치지 않았어요.
````

## 바뀐 줄: report.py

```diff
diff --git a/report.py b/report.py
index 628cb65..7778ce4 100644
--- a/report.py
+++ b/report.py
@@ -29,17 +29,23 @@ def summarize(events, service=None, slow_ms=500):
         _check_event(event)
 
     rows = events
-    if service:
-        rows = [event for event in events if event["service"] == service]
+    if service is not None:
+        service = service.strip()
+        rows = [event for event in events if event["service"].strip() == service]
     total = len(rows)
-    errors = sum(event["status"] >= 400 for event in rows)
-    slow = sum(event["latency_ms"] > slow_ms for event in rows)
-    average = sum(event["latency_ms"] for event in rows) / total
+    errors = sum(event["status"] >= 500 for event in rows)
+    slow = sum(event["latency_ms"] >= slow_ms for event in rows)
+    if total:
+        error_rate = round(errors / total * 100, 2)
+        average = round(sum(event["latency_ms"] for event in rows) / total, 2)
+    else:
+        error_rate = 0.0
+        average = 0.0
     return {
         "service": service or "all",
         "total": total,
         "error_count": errors,
-        "error_rate_pct": round(errors / len(events) * 100, 2),
+        "error_rate_pct": error_rate,
         "slow_count": slow,
-        "average_ms": round(average, 2),
+        "average_ms": average,
     }
```

## 더한 파일: tests/test_regression.py

```diff
diff --git a/tests/test_regression.py b/tests/test_regression.py
new file mode 100644
index 0000000..9d9e49f
--- /dev/null
+++ b/tests/test_regression.py
@@ -0,0 +1,30 @@
+"""이슈 #1 회귀 테스트. 이슈의 입력을 그대로 씁니다."""
+import json
+from pathlib import Path
+
+import report
+
+EVENTS = json.loads((Path(__file__).resolve().parents[1] / "fixtures/events.json").read_text())
+
+
+def _triple(service):
+    value = report.summarize(EVENTS, service=service)
+    return value["error_count"], value["error_rate_pct"], value["slow_count"]
+
+
+def test_billing_error_rate_uses_filtered_total():
+    assert _triple("billing") == (2, 66.67, 2)
+
+
+def test_catalog_404_is_not_error_and_500ms_is_slow():
+    assert _triple("catalog") == (0, 0.0, 1)
+
+
+def test_unknown_service_returns_zeros():
+    value = report.summarize(EVENTS, service="unknown")
+    assert (value["total"], value["error_count"], value["error_rate_pct"],
+            value["slow_count"], value["average_ms"]) == (0, 0, 0.0, 0, 0.0)
+
+
+def test_service_filter_is_trimmed():
+    assert report.summarize(EVENTS, service=" billing ")["total"] == 3
```

## 검토할 때 볼 곳

- 바뀐 파일이 둘뿐이에요. 테스트, 명세, 데이터는 그대로예요.
- 본문에 원인 다섯 개, 바꾼 줄, 실행한 명령과 결과, 확인하지 못한 것이 있어요.
- `except Exception`으로 오류를 숨기지 않고, 0건일 때만 `0.0`으로 분기했어요.
- "확인하지 못한 것"에 사람이 정할 일이 하나 있어요. 명세는 "정확히 일치"라고 하는데, 제공 테스트는 데이터 쪽 이름의 공백도 지우고 비교하라고 해요. Claude는 테스트를 따랐고, 어느 쪽이 맞는지는 사람에게 물었어요. 이런 줄이 있으면 머지 전에 답을 정해요.

## Claude 초안으로 올린 이슈였다면 (검토 때 실제 실행)

위 견본의 이슈 본문은 사람이 쓴 `bug-issue-example.md`라서 공백이 붙은 이름까지 입력과 기대에 적혀 있었어요. 수업에서는 Claude에게 받은 초안(`issue-draft.md`, billing만 적은 이슈)을 올려요. 그 초안을 그대로 이슈 #1로 넣고 같은 요청문을 다시 돌려 봤어요(2026-10-17, Claude Code 2.1.302, Sonnet 5.5, 48초).

- 바뀐 파일: `report.py`, `tests/test_regression.py` 두 개로 같아요.
- 고친 원인: 분모, 404, 500ms, 0건 넷이에요. 하나씩 고치고 고칠 때마다 재현과 pytest를 다시 돌렸어요.
- 결과: `재현 실패 사례: 0/3`, `47 passed`(기존 44개와 회귀 테스트 3개)
- PR 본문의 "확인하지 못한 것"에서 두 줄을 골랐어요(Claude가 쓴 그대로).

```text
- 이슈 본문의 `--impl buggy/report.py`는 이 저장소에 없는 경로라 실행하지 못했습니다. 저장소의 `report.py`로 재현했습니다.
- `SPEC.md`는 "필터 문자열은 앞뒤 공백을 제거해 일치"라고 하는데 `report.py`는 공백을 제거하지 않습니다 (`service=" a "`가 0건). 현재 `tests/test_contract.py`는 이를 검사하지 않아 통과합니다. 이슈 범위 밖이라 고치지 않았습니다. 별도 이슈가 필요합니다.
```

볼 점은 두 가지예요.

- **루틴은 이슈와 테스트에 드러난 것까지만 고쳐요.** 공백 문제는 이슈에도 없고 제공 테스트도 잡지 못해서 고치지 않았어요. 범위를 지킨 맞는 동작이에요. 이 줄을 보면 공백 문제로 이슈를 하나 더 써서 맡겨요. 입력 칸에는 `../bug-issue-example.md`의 공백 명령(`python -c …`)을 옮겨 써요.
- **첫 줄은 이슈를 옮길 때 생긴 일이에요.** 초안의 "`--impl buggy/report.py` 실행 결과입니다" 줄을 지우고 옮기면 이 줄은 나오지 않아요(`issue-draft.md`의 "GitHub에 옮기기" 3).
