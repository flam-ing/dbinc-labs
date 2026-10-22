# 3. 한 줄과 회귀 테스트: 실제로 나온 답

같은 대화에서 모드를 Auto로 바꾸고 보낸 실제 답이에요.

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-10-17 |
| Claude Code | 2.1.302 |
| 모델 | Sonnet 5.5 |
| 모드 | Auto |
| 걸린 시간 | 34초 |

## 보낸 말

```text
계획대로 그 줄만 고쳐 줘. 이슈 입력 그대로 회귀 테스트를 tests/test_bugs.py에 더하고, 고치기 전 코드에서는 그 테스트가 실패하는지도 보여 줘. 마지막에 python3 -m unittest 결과를 그대로 보여 줘.
```

## Claude의 답 (그대로)

이슈 #1을 고쳤고, `python3 -m unittest`는 8개 모두 통과했습니다.

## 바꾼 것
- `app.py:41`: `>=`를 `>`로 바꿨습니다. 이 줄만 고쳤습니다.
- `tests/test_bugs.py` 새 파일:
  - `test_이슈1_이름을_딱_40자로_쓰면_저장된다`: `가`×40과 `안녕하세요`를 보내 201을 기대합니다.
  - `test_이슈1_이름이_41자면_400`: 상한이 그대로 유지되는지 봅니다.

## 고치기 전 코드에서의 실패
40자 테스트는 `AssertionError: 400 != 201`로 실패했고, 41자 테스트는 통과했습니다.

## 고친 뒤 `python3 -m unittest -v`
```
test_글을_남기면_201과_번호를_준다 (tests.test_bugs.BugTest...) ... ok
test_남긴_글이_목록에_나온다 (tests.test_bugs.BugTest...) ... ok
test_이름이_비면_400 (tests.test_bugs.BugTest...) ... ok
test_이슈1_이름을_딱_40자로_쓰면_저장된다 (tests.test_bugs.BugTest...) ... ok
test_이슈1_이름이_41자면_400 (tests.test_bugs.BugTest...) ... ok
test_글을_남기면_201과_번호를_준다 (tests.test_guestbook.GuestbookTest...) ... ok
test_남긴_글이_목록에_나온다 (tests.test_guestbook.GuestbookTest...) ... ok
test_이름이_비면_400 (tests.test_guestbook.GuestbookTest...) ... ok

Ran 8 tests in 0.911s
OK
```

## 알아 둘 점
- 기존 테스트가 두 번 돕니다. `BugTest`가 `GuestbookTest`를 상속해서 서버 띄우는 코드를 재사용하기 때문에, 기존 3개가 `BugTest` 쪽에서도 한 번 더 실행됩니다. 고유한 테스트는 5개입니다.
- 내용 500자 경계는 확인하지 않았습니다. 같은 줄이라 함께 고쳐졌을 것으로 보이지만, 재현해 보거나 테스트를 넣지 않았습니다. 이슈 범위 밖이라 그대로 뒀습니다.
- 브라우저 화면에서는 확인하지 않았습니다. API 요청과 테스트로만 확인했습니다.
- 커밋과 PR은 만들지 않았습니다. `app.py` 수정과 `tests/test_bugs.py` 추가가 작업 트리에 남아 있습니다.

## 바뀐 줄 (`git diff`)

```diff
diff --git a/app.py b/app.py
index 32c28f7..7f3c98a 100644
--- a/app.py
+++ b/app.py
@@ -39,7 +39,7 @@ def validate_entry(value):
         if not isinstance(raw, str) or not raw.strip():
             raise ValueError(f"{label}을 입력해 주세요.")
         result[key] = raw.strip()
-        if len(result[key]) >= maximum:
+        if len(result[key]) > maximum:
             raise ValueError(f"{label}은 {maximum}자 이내로 입력해 주세요.")
     return result
```

## Claude가 만든 `tests/test_bugs.py`

```python
"""고친 버그의 회귀 테스트. 이슈의 입력을 그대로 써요."""
import unittest

from tests import test_guestbook


class BugTest(test_guestbook.GuestbookTest):
    def test_이슈1_이름을_딱_40자로_쓰면_저장된다(self):
        status, body = self.post("가" * 40, "안녕하세요")
        self.assertEqual(status, 201)
        self.assertEqual(body["entry"]["name"], "가" * 40)

    def test_이슈1_이름이_41자면_400(self):
        status, body = self.post("가" * 41, "안녕하세요")
        self.assertEqual(status, 400)
        self.assertIn("40자", body["error"])


if __name__ == "__main__":
    unittest.main()
```
