# 3. 한 줄과 회귀 테스트: 실제로 나온 답

같은 대화에서 모드를 Auto로 바꾸고 보낸 실제 답이에요.

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-10-23 |
| Claude Code | 2.1.309 |
| 모델 | Sonnet 5.5 |
| 모드 | Auto |
| 걸린 시간 | 24초 |

## 보낸 말

```text
계획대로 그 줄만 고쳐 줘. 이슈 입력 그대로 회귀 테스트를 tests/test_bugs.py에 더하고, 고치기 전 코드에서는 그 테스트가 실패하는지도 보여 줘. 마지막에 python3 -m unittest 결과를 그대로 보여 줘.
```

## Claude의 답 (그대로)

이슈 #1을 고쳤습니다. `cafe.py:75`의 `>`를 `>=`로 바꾼 한 줄이 전부입니다. 커밋은 하지 않았습니다.

**회귀 테스트:** `tests/test_bugs.py`의 `Issue1Test`에 더했습니다. 이슈 입력 그대로 김하늘 님(M001, 누적 95,000원)이 5,000원을 냅니다. 마감 뒤 `total`이 100000, 등급이 `VIP`이고 영수증에 "VIP까지"가 없는지 봅니다.

**고치기 전 코드에서 실행** (`python3 -m unittest tests.test_bugs`):
```
FAIL: test_누적이_딱_10만원이_되면_VIP가_된다
AssertionError: '일반' != 'VIP'
Ran 1 test in 0.020s
FAILED (failures=1)
```

**고친 뒤 전체 실행** (`python3 -m unittest`):
```
....
----------------------------------------------------------------------
Ran 4 tests in 0.074s

OK
```

기존 테스트는 지우거나 바꾸지 않았습니다. 고친 뒤에 `python3 cafe.py`를 다시 돌려 영수증을 눈으로 확인하지는 않았고, 확인은 테스트로만 했습니다.

`cafe.py:33`의 `"vip"`와 `"VIP"` 불일치로 VIP 적립이 1%로 계산되는 문제는 그대로 있습니다. 별도 이슈로 올려 주세요.

## 바뀐 줄 (`git diff`)

```diff
diff --git a/cafe.py b/cafe.py
index 11f4859..f33bdde 100644
--- a/cafe.py
+++ b/cafe.py
@@ -72,7 +72,7 @@ def run():
             points = points - use + jeoklip
             a["points"] = str(points)
             a["total"] = str(int(a["total"]) + gyeolje)
-            if int(a["total"]) > VIP_GIJUN:
+            if int(a["total"]) >= VIP_GIJUN:
                 a["grade"] = "VIP"
             maechul = maechul + gyeolje
             jeoklip_hap = jeoklip_hap + jeoklip
```

## Claude가 만든 `tests/test_bugs.py`

```python
"""이슈별 회귀 테스트. 이슈에 적힌 입력을 그대로 써요."""
import unittest

from tests.cafe_runner import run_cafe


class Issue1Test(unittest.TestCase):
    def test_누적이_딱_10만원이_되면_VIP가_된다(self):
        # 이슈 #1: 김하늘 님(M001)은 누적 95,000원이었고 오늘 5,000원을 냈다.
        result = run_cafe(["2026-10-17,M001,5000,0"])
        self.assertEqual(result.code, 0, result.output)
        self.assertEqual(result.members["M001"]["total"], "100000")
        self.assertEqual(result.members["M001"]["grade"], "VIP")
        self.assertNotIn("VIP까지", result.output)


if __name__ == "__main__":
    unittest.main()
```

## 볼 곳

- `cafe.py`에서 기호 하나(`>`를 `>=`로)만 바뀌었어요.
- 고치기 전 코드에서 새 테스트가 `'일반' != 'VIP'`로 실패하는 것을 먼저 보여 줬어요. 고친 뒤에는 테스트 4개가 모두 통과했어요.
- 영수증을 다시 눈으로 보지는 않았다고 스스로 밝혔어요. 이럴 때는 `py cafe.py`로 한 번 더 돌려 봐요.
