# 8. /goal로 남은 이슈 두 개: 실제로 나온 결과

#1과 #2를 고쳐 커밋한 사본에서 새 세션을 열고, 실습 4의 `/goal` 문장 아래에 이슈 #3과 #4의 글을 붙여 보낸 실제 결과예요. 사람은 보낸 뒤에 아무 말도 하지 않았어요.

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-10-23 |
| Claude Code | 2.1.309 |
| 모델 | Sonnet 5.5 |
| 모드 | Auto |
| 걸린 시간 | 27초 |

## 보낸 말

````text
/goal 아래 두 이슈(#3, #4)가 모두 고쳐지고, 이슈마다 회귀 테스트가 tests/test_bugs.py에 있고, python3 -m unittest가 실패 없이 끝나면 완료야. 기존 테스트는 고치지 마. 20턴이 넘으면 멈춰.

#3 [쿠폰] 생일 쿠폰이 한 달에 두 번 나와요

※ 교육용으로 일부러 넣은 버그예요.

## 재현 순서

1. 받은 그대로 `py cafe.py`로 마감을 돌려요. Mac은 `python3 cafe.py`예요.
2. 영수증에서 박노을 님(생일 10월) 줄을 봐요. 10월 17일에 9,000원, 6,000원을 두 번 주문했어요.

## 기대

생일 쿠폰은 생일 달 첫 주문에만 나와요. 두 번째 주문은 6,000원을 다 내요.

## 실제

두 번 다 "생일 쿠폰: -3000 원"이 찍혀요. 두 번째 주문의 결제 금액이 3000 원이에요.

#4 [마감] 포인트 칸이 비어 있으면 마감이 멈춰요

※ 교육용으로 일부러 넣은 버그예요.

## 재현 순서

1. 새 키오스크는 포인트를 안 쓴 주문의 사용 포인트 칸을 비워서 보내요.
2. `data/orders.csv` 맨 아래에 `2026-10-17,M004,4500,` 한 줄을 더해요. 끝의 사용 포인트 칸이 비어 있어요.
3. `py cafe.py`로 마감을 돌려요. Mac은 `python3 cafe.py`예요.

## 기대

빈 칸은 0점으로 보고 마감이 끝까지 돌아요.

## 실제

영수증이 중간에 멈추고 마감 보고가 새로 만들어지지 않아요. 오류 글의 마지막 두 줄은 이래요.

```text
    use = int(o["use_points"])
ValueError: invalid literal for int() with base 10: ''
```
````

## 처음 나온 줄

```text
Goal set: 아래 두 이슈(#3, #4)가 모두 고쳐지고, 이슈마다 회귀 테스트가 tests/test_bugs.py에 있고, python3 -m unittest가 실패 없이 끝나면 완료야. 기존 테스트는 고치지 마. 20턴이 넘으면 멈춰. …
```

## Claude의 마지막 답 (그대로)

#3과 #4를 모두 고쳤고, `python3 -m unittest`는 7개 테스트가 전부 통과했어요(`Ran 7 tests ... OK`). 아직 커밋이나 push는 하지 않았어요.

**#3 생일 쿠폰이 두 번 나옴**
- 기대: 쿠폰은 생일 달 첫 주문에만 나오고, 두 번째 주문은 6,000원을 다 내요.
- 실제: `sseun_kupon` 목록을 확인만 하고 한 번도 채우지 않아서 두 번째 주문에도 쿠폰이 나왔어요.
- 수정: `cafe.py:70`에서 쿠폰을 준 뒤 `sseun_kupon.append(mid + mon)`을 더했어요.

**#4 사용 포인트 칸이 비면 마감이 멈춤**
- 기대: 빈 칸은 0점으로 보고 마감이 끝까지 돌아요.
- 실제: `int('')`에서 `ValueError`가 나서 영수증이 중간에 멈췄어요.
- 수정: `cafe.py:61`을 `int(o["use_points"] or 0)`으로 바꿨어요.

**회귀 테스트**
- `tests/test_bugs.py`에 `Issue3Test`와 `Issue4Test`를 더했어요. 입력은 이슈 그대로예요.
- 고치기 전 코드에서는 둘 다 실패했어요. #4는 `ValueError`로 끝났고, #3은 쿠폰이 두 번 찍혔어요.
- 기존 테스트는 바꾸지 않았어요.

**확인하지 못한 것**
- `data/` 원본은 건드리지 않아서, 이슈에 적힌 `data/orders.csv`에 줄을 더해 `python3 cafe.py`로 돌리는 방식은 실행하지 않았어요. 같은 입력을 `run_cafe`의 임시 폴더로 돌려서 확인했어요.

## 바뀐 줄 (`git diff`)

```diff
diff --git a/cafe.py b/cafe.py
index 7a1dd80..7bddd19 100644
--- a/cafe.py
+++ b/cafe.py
@@ -58,7 +58,7 @@ def run():
                 continue
             a = members[mid]
             points = int(a["points"])
-            use = int(o["use_points"])
+            use = int(o["use_points"] or 0)
             if use > points:
                 use = points
             if use < CHOESO_SAYONG:
@@ -67,6 +67,7 @@ def run():
             mon = o["date"][5:7]
             if a["birth"][5:7] == mon and (mid + mon) not in sseun_kupon and amt >= 5000:
                 kupon = SAENGIL_KUPON
+                sseun_kupon.append(mid + mon)
             gyeolje = amt - kupon - use
             jeoklip = jeoklip_gyesan(gyeolje, a["grade"])
             points = points - use + jeoklip
diff --git a/tests/test_bugs.py b/tests/test_bugs.py
index adc464f..2d5441d 100644
--- a/tests/test_bugs.py
+++ b/tests/test_bugs.py
@@ -23,5 +23,24 @@ class Issue2Test(unittest.TestCase):
         self.assertEqual(result.members["M002"]["points"], "3400")  # 5100 - 2000 + 300
 
 
+class Issue3Test(unittest.TestCase):
+    def test_생일_쿠폰은_생일_달_첫_주문에만_나온다(self):
+        # 이슈 #3: 박노을 님(M003, 생일 10월)이 10월 17일에 9,000원, 6,000원을 두 번 주문했다.
+        result = run_cafe(["2026-10-17,M003,9000,0", "2026-10-17,M003,6000,0"])
+        self.assertEqual(result.code, 0, result.output)
+        self.assertEqual(result.output.count("생일 쿠폰"), 1, result.output)
+        # 6,000원 + 6,000원(쿠폰 없음) = 누적 23000 + 6000 + 6000
+        self.assertEqual(result.members["M003"]["total"], "35000")
+
+
+class Issue4Test(unittest.TestCase):
+    def test_사용_포인트_칸이_비어_있으면_0점으로_본다(self):
+        # 이슈 #4: 주문 줄 맨 끝의 사용 포인트 칸이 비어 있다.
+        result = run_cafe(["2026-10-17,M004,4500,"])
+        self.assertEqual(result.code, 0, result.output)
+        self.assertEqual(result.members["M004"]["total"], "65500")
+        self.assertIn("마감 보고", result.report)
+
+
 if __name__ == "__main__":
     unittest.main()
```

## 고친 뒤 `python3 -m unittest -v`

```text
test_누적이_딱_10만원이_되면_VIP가_된다 (tests.test_bugs.Issue1Test.test_누적이_딱_10만원이_되면_VIP가_된다) ... ok
test_VIP는_결제_금액의_3퍼센트가_쌓인다 (tests.test_bugs.Issue2Test.test_VIP는_결제_금액의_3퍼센트가_쌓인다) ... ok
test_생일_쿠폰은_생일_달_첫_주문에만_나온다 (tests.test_bugs.Issue3Test.test_생일_쿠폰은_생일_달_첫_주문에만_나온다) ... ok
test_사용_포인트_칸이_비어_있으면_0점으로_본다 (tests.test_bugs.Issue4Test.test_사용_포인트_칸이_비어_있으면_0점으로_본다) ... ok
test_마감을_돌리면_보고서가_생긴다 (tests.test_cafe.CafeTest.test_마감을_돌리면_보고서가_생긴다) ... ok
test_일반_회원은_결제_금액의_1퍼센트가_쌓인다 (tests.test_cafe.CafeTest.test_일반_회원은_결제_금액의_1퍼센트가_쌓인다) ... ok
test_포인트는_1000점보다_적으면_못_쓴다 (tests.test_cafe.CafeTest.test_포인트는_1000점보다_적으면_못_쓴다) ... ok
----------------------------------------------------------------------
Ran 7 tests in 0.114s
OK
```

## 볼 곳

- #3은 빠진 한 줄(`sseun_kupon.append(mid + mon)`)을 더했어요. 쿠폰을 쓴 회원을 적어 두는 목록이 늘 비어 있었어요.
- #4는 `int(o["use_points"] or 0)`으로 빈 칸을 0으로 읽게 했어요.
- 회귀 테스트를 먼저 써서 고치기 전에 둘 다 실패하는 것을 본 다음 고쳤어요.
- 조건을 판정하는 작은 모델의 판정 글은 `claude -p` 기록에 남지 않았어요. 앱에서는 `/goal`을 쳐서 판정 이유를 볼 수 있어요.
