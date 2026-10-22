# 8. /goal로 이슈 #3, #4를 한 번에: 실제로 나온 결과

이슈 #1, #2를 고친 사본에서 [prompts.md](prompts.md) 5번의 `/goal` 문장을 보낸 실제 결과예요. 두 이슈의 글을 문장 아래에 붙였어요.

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-10-17 |
| Claude Code | 2.1.302 |
| 모델 | Sonnet 5.5 |
| 모드 | Auto |
| 걸린 시간 | 44초 |

## 보낸 말

```text
/goal 아래 두 이슈(#3, #4)가 모두 고쳐지고, 이슈마다 회귀 테스트가 tests/test_bugs.py에 있고, python3 -m unittest가 실패 없이 끝나면 완료야. 기존 테스트는 고치지 마. 20턴이 넘으면 멈춰.

#3 [화면] 글을 남겨도 목록에 바로 안 나와요

※ 교육용으로 일부러 넣은 버그예요.

## 재현 순서

1. `python3 app.py`로 서버를 켜고 브라우저에서 http://127.0.0.1:8000 을 열어요.
2. 이름에 `김디비`, 내용에 `안녕하세요`를 쓰고 **남기기**를 눌러요.

## 기대

목록 맨 위에 방금 쓴 글이 바로 나와요.

## 실제

"저장했습니다. 기록 번호 #1"은 뜨는데 목록에는 글이 없어요. **새로고침** 단추를 누르면 그때 나와요.

#4 [실행 환경] 새로 배포하면 글이 다 사라져요

※ 교육용으로 일부러 넣은 버그예요.

## 설명

운영 서버에서는 `compose.yaml`로 Docker 컨테이너를 띄워요. 글이 남도록 DB 위치를 볼륨 폴더로 정해 두었어요(`Dockerfile`의 `GUESTBOOK_DB=/data/guestbook.sqlite3`). 그런데 새 버전을 배포해서 컨테이너를 새로 만들 때마다 그동안 남긴 글이 다 없어져요.

## 재현 순서(Docker 없이)

DB 위치를 정하는 환경 변수를 넣고 서버를 켜요.

- macOS: `GUESTBOOK_DB=/tmp/ops-db/guestbook.sqlite3 python3 app.py`
- Windows PowerShell: `$env:GUESTBOOK_DB="$env:TEMP\ops-db\guestbook.sqlite3"; python app.py`

## 기대

서버가 켜질 때 찍는 첫 줄의 `DB:`가 내가 넣은 위치예요.

## 실제

`DB:`가 내가 넣은 위치가 아니라 이 폴더의 `data/guestbook.sqlite3`예요. 컨테이너 안에서는 이 폴더가 새로 만들 때마다 지워져요.
```

## 처음 나온 줄

```text
Goal set: 아래 두 이슈(#3, #4)가 모두 고쳐지고, … 20턴이 넘으면 멈춰.
```

## Claude의 마지막 답 (그대로)

두 이슈를 모두 고쳤고, `python3 -m unittest`는 11개 테스트가 전부 통과했어요(`OK`). 새 테스트 두 개는 고치기 전 코드에서 실패하는 것도 확인했어요.

**#3 글을 남겨도 목록에 바로 안 나와요**
- **원인:** 저장에 성공해도 목록을 다시 불러오지 않았어요. `static/app.js`의 제출 처리에서 "저장했습니다" 표시 뒤에 `loadEntries()` 호출이 없었어요.
- **수정:** 그 줄 바로 아래에 `await loadEntries();`를 한 줄 더했어요.
- **테스트:** `test_이슈3_남기기에_성공하면_목록을_다시_불러온다`예요. 브라우저를 띄우지 못해서 `app.js`의 소스 텍스트에 호출이 있는지만 검사해요. 화면에서 실제로 목록이 바로 갱신되는지는 확인하지 못했어요.
- **브라우저에서 확인하는 순서:** `python3 app.py`로 켜고 http://127.0.0.1:8000 을 열어요. 이름 `김디비`, 내용 `안녕하세요`를 남기면 새로고침 없이 목록 맨 위에 나와야 해요.

**#4 새로 배포하면 글이 다 사라져요**
- **원인:** `app.py`가 환경 변수 `GUESTBOOK_DB_PATH`를 읽는데, `Dockerfile`은 `GUESTBOOK_DB`를 설정해요. 이름이 달라서 DB 위치가 항상 기본값 `data/guestbook.sqlite3`가 됐어요.
- **수정:** `app.py`의 `--db` 기본값이 읽는 변수를 `GUESTBOOK_DB`로 바꿨어요. 이슈와 `Dockerfile`이 쓰는 이름에 코드를 맞췄어요.
- **재현:** 고치기 전에 `GUESTBOOK_DB=/tmp/ops-db/guestbook.sqlite3`로 켜 보니 `DB:`가 `data/guestbook.sqlite3`로 찍혔어요.
- **테스트:** `test_이슈4_GUESTBOOK_DB로_DB_위치를_정할_수_있다`는 서버를 그 환경 변수로 띄우고 첫 줄의 `DB:`를 확인해요.

수정한 파일은 `app.py`, `static/app.js`, `tests/test_bugs.py`예요. 기존 테스트는 건드리지 않았어요. 새 #4 테스트를 `-v`로 돌릴 때 `ResourceWarning: unclosed file`이 한 번 떴어요. 서버 출력을 읽는 파이프를 닫지 않아서인데, 테스트 결과에는 영향이 없어요.

실제 Docker 컨테이너는 띄워 보지 않았어요. 커밋, push, PR도 만들지 않았고, 변경은 작업 폴더에 그대로 있어요.

## 바뀐 줄 (`git diff`)

```diff
diff --git a/app.py b/app.py
index 05fe8c8..c7f3d20 100644
--- a/app.py
+++ b/app.py
@@ -117,7 +117,7 @@ def main():
     parser = argparse.ArgumentParser(description=__doc__)
     parser.add_argument("--host", default=os.getenv("GUESTBOOK_HOST", "127.0.0.1"))
     parser.add_argument("--port", type=int, default=int(os.getenv("GUESTBOOK_PORT", "8000")))
-    parser.add_argument("--db", default=os.getenv("GUESTBOOK_DB_PATH", str(ROOT / "data" / "guestbook.sqlite3")))
+    parser.add_argument("--db", default=os.getenv("GUESTBOOK_DB", str(ROOT / "data" / "guestbook.sqlite3")))
     args = parser.parse_args()
     server = create_server(args.host, args.port, args.db)
     print(f"방명록: http://{args.host}:{server.server_port} / DB: {server.db_path}", flush=True)
diff --git a/static/app.js b/static/app.js
index 540d098..d5a1c85 100644
--- a/static/app.js
+++ b/static/app.js
@@ -53,6 +53,7 @@ form.addEventListener('submit', async (event) => {
     if (!response.ok) throw new Error(data.error || '저장하지 못했습니다.');
     form.elements.message.value = '';
     status(formStatus, `저장했습니다. 기록 번호 #${data.entry.id}`);
+    await loadEntries();
   } catch (error) {
     status(formStatus, error.message || '서버 연결을 확인해 주세요.', true);
   } finally {
```

## 볼 곳

- 사람이 "다음"을 한 번도 말하지 않았어요. 두 이슈를 재현하고, 테스트를 먼저 쓰고, 두 곳을 고치고, 전체 테스트를 돌릴 때까지 혼자 이어 갔어요.
- 첫 차례 안에 조건을 다 채워서 목표가 그대로 끝났어요. 이 기록은 `claude -p`로 돌려서 평가자의 판정 글은 남지 않았어요. 앱에서 판정이 어떻게 보이는지는 리허설 때 확인해요.
- 화면 버그(#3)는 소스에 `loadEntries()`가 있는지만 검사했다고 스스로 밝혔어요. 화면은 사람이 브라우저로 한 번 봐요.
