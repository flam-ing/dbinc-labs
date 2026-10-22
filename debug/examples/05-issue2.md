# 5. 이슈 #2를 한 번에: 실제로 나온 답

이슈 #1을 고친 사본에서, 이슈 #2(DB, 작은따옴표)를 문장 하나로 맡긴 실제 답이에요. 실습에서는 1~3번처럼 세 번에 나눠 보내도 되고, 시간이 빠듯하면 이 문장 하나로 보내요([prompts.md](prompts.md) 4번).

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-10-17 |
| Claude Code | 2.1.302 |
| 모델 | Sonnet 5.5 |
| 모드 | Auto |
| 걸린 시간 | 26초 |

## 보낸 말

```text
아래 이슈를 재현하고 원인 줄을 찾아서 그 줄만 고쳐 줘. 이슈 입력 그대로 회귀 테스트를 tests/test_bugs.py에 더하고, 고치기 전에는 실패하는지 먼저 보여 줘. 끝나면 python3 -m unittest 결과를 그대로 보여 줘.

#2 [DB] 내용에 작은따옴표(')가 있으면 저장이 안 돼요

※ 교육용으로 일부러 넣은 버그예요.

## 재현 순서

1. `python3 app.py`로 서버를 켜고 http://127.0.0.1:8000 을 열어요.
2. 이름에 `김디비`, 내용에 `오늘 회의 '정말' 좋았어요`를 쓰고 **남기기**를 눌러요.

## 기대

저장되고 목록에 나와요.

## 실제

"저장하지 못했습니다. 다시 시도해 주세요."가 떠요. 따옴표를 빼면 저장돼요.
```

## Claude의 답 (그대로)

이슈 #2를 고쳤습니다. 내용에 작은따옴표(')가 있어도 저장되고 목록에 나옵니다.

**재현**
- 기대: `김디비` / `오늘 회의 '정말' 좋았어요`가 저장되고 목록에 나온다.
- 실제: 서버가 500을 돌려줘서 화면에 "저장하지 못했습니다."가 뜬다.
- 브라우저는 열지 않고, 같은 입력을 테스트 서버로 보내서 재현했습니다.

**원인**
- `app.py:99-100`에서 이름, 내용, 시각을 f-string으로 SQL 문장에 그대로 끼워 넣고 있었습니다.
- 내용의 `'`가 SQL 문자열을 중간에 닫아서 `sqlite3.Error`가 났고, 이 오류가 500 응답으로 이어졌습니다.

**고친 줄**
- 값을 `?` 자리표시자로 바꾸고 튜플로 따로 넘겼습니다. 이 줄만 바꿨습니다.

```diff
-                    "INSERT INTO entries(name, message, created_at) "
-                    f"VALUES ('{entry['name']}', '{entry['message']}', '{entry['created_at']}')"
+                    "INSERT INTO entries(name, message, created_at) VALUES (?, ?, ?)",
+                    (entry["name"], entry["message"], entry["created_at"]),
```

**회귀 테스트**
- `tests/test_bugs.py`에 `test_이슈2_내용에_작은따옴표가_있어도_저장된다`를 더했습니다. 이슈의 입력을 그대로 쓰고, 응답이 201인지와 목록에 같은 내용이 나오는지 확인합니다.
- 고치기 전 코드에서는 이 테스트가 `AssertionError: 500 != 201`로 실패했습니다.

**`python3 -m unittest` 결과(고친 뒤)**
```
.........
----------------------------------------------------------------------
Ran 9 tests in 1.046s

OK
```

브라우저에서 직접 눌러 보지는 않았습니다. 확인하려면 `python3 app.py`로 서버를 켜고 http://127.0.0.1:8000 에서 이슈의 입력으로 **남기기**를 눌러 보세요.

커밋, 브랜치, PR은 만들지 않았습니다. 필요하면 말씀해 주세요.

## 바뀐 줄 (`git diff`)

```diff
diff --git a/app.py b/app.py
index 7f3c98a..05fe8c8 100644
--- a/app.py
+++ b/app.py
@@ -96,8 +96,8 @@ class GuestbookHandler(BaseHTTPRequestHandler):
         try:
             with sqlite3.connect(self.server.db_path) as db:
                 cursor = db.execute(
-                    "INSERT INTO entries(name, message, created_at) "
-                    f"VALUES ('{entry['name']}', '{entry['message']}', '{entry['created_at']}')"
+                    "INSERT INTO entries(name, message, created_at) VALUES (?, ?, ?)",
+                    (entry["name"], entry["message"], entry["created_at"]),
                 )
                 entry["id"] = cursor.lastrowid
             return self.respond(201, {"entry": entry})
```

## 볼 곳

- 따옴표를 바꿔 넣는 식으로 고치지 않고, 값 자리를 `?`로 바꿔 따로 넘겼어요. 같은 원인이 SQL 주입 구멍이라서 이렇게 고쳐야 해요.
- 고치기 전 코드에서 새 테스트가 `500 != 201`로 실패한 것을 먼저 보여 줬어요.
