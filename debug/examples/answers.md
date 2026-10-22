# 정답: 버그 네 개의 원인과 고친 줄

강사용이에요. 수강생 저장소(`tools/make_repo.py`로 만든 폴더)에는 들어가지 않아요.
줄 번호는 처음 상태의 파일 기준이에요.

수업에서 이슈가 도착하는 순서와 이 파일의 이름은 이렇게 짝이에요. #1 = BUG-2(서버), #2 = BUG-3(DB), #3 = BUG-1(화면), #4 = BUG-4(실행 환경).

## BUG-1 [화면] 글을 남겨도 목록에 바로 안 나와요

- 원인 파일과 줄: `static/app.js` 55번 줄 바로 다음(빠진 줄)
- 원래 줄(55번 줄, 이 다음 줄이 없어요):

  ```js
      status(formStatus, `저장했습니다. 기록 번호 #${data.entry.id}`);
  ```

- 고친 줄(55번 줄 다음에 한 줄 더해요):

  ```js
      await loadEntries();
  ```

- 왜: 글은 서버에 잘 저장되는데, 화면이 저장한 다음에 목록을 다시 불러오지 않아서 새로고침을 눌러야 보여요.

## BUG-2 [서버] 이름을 딱 40자로 쓰면 거절돼요

- 원인 파일과 줄: `app.py` 42번 줄
- 원래 줄:

  ```python
          if len(result[key]) >= maximum:
  ```

- 고친 줄:

  ```python
          if len(result[key]) > maximum:
  ```

- 왜: "40자 이내"는 40자까지 된다는 뜻인데, `>=`로 비교해서 딱 40자도 거절했어요.

## BUG-3 [DB] 내용에 작은따옴표(')가 있으면 저장이 안 돼요

- 원인 파일과 줄: `app.py` 99~100번 줄(`db.execute(...)` 안의 SQL 문장)
- 원래 줄:

  ```python
                      "INSERT INTO entries(name, message, created_at) "
                      f"VALUES ('{entry['name']}', '{entry['message']}', '{entry['created_at']}')"
  ```

- 고친 줄:

  ```python
                      "INSERT INTO entries(name, message, created_at) VALUES (?, ?, ?)",
                      (entry["name"], entry["message"], entry["created_at"]),
  ```

- 왜: 사용자가 쓴 글을 SQL 문장에 그대로 끼워 넣어서, 글 속 작은따옴표가 SQL 문장을 끊어 버렸어요. `?` 자리에 값을 따로 넘기면 따옴표가 있어도 글로만 다뤄져요. 같은 구멍으로 남의 글을 지우는 SQL도 넣을 수 있었으니 보안 버그이기도 해요.

## BUG-4 [실행 환경] 새로 배포하면 글이 다 사라져요

- 원인 파일과 줄: `app.py` 120번 줄
- 원래 줄:

  ```python
      parser.add_argument("--db", default=os.getenv("GUESTBOOK_DB_PATH", str(ROOT / "data" / "guestbook.sqlite3")))
  ```

- 고친 줄:

  ```python
      parser.add_argument("--db", default=os.getenv("GUESTBOOK_DB", str(ROOT / "data" / "guestbook.sqlite3")))
  ```

- 왜: 운영(`Dockerfile`)은 `GUESTBOOK_DB`라는 이름으로 DB 위치를 알려 주는데 앱은 `GUESTBOOK_DB_PATH`를 찾아서, 위치를 못 받고 컨테이너 안 폴더에 DB를 만들었어요. 컨테이너를 새로 만들면 그 폴더가 지워져서 글이 사라졌어요.
- 덧붙임: `Dockerfile` 쪽 이름을 `GUESTBOOK_DB_PATH`로 바꿔도 증상은 사라져요. 하지만 이슈는 "운영이 정한 이름을 앱이 못 읽는다"는 신고라서, 앱 한 줄을 고치는 쪽을 정답으로 봐요.
