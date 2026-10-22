# 방명록 예제

1일차 4교시 [실습 1-2: 풀스택 프로토타이핑](../../docs/day1-guestbook.md)에서 쓰는 시작 폴더, 완성 참고본, 확인 도구예요. 실습 순서와 문장은 [examples/prompts.md](examples/prompts.md)에 있어요.

| 파일 | 역할 |
| --- | --- |
| `starter/` | 4교시 시작 폴더예요. 인터뷰 스킬(`.claude/skills/prd-interview/SKILL.md`)이 들어 있어요 |
| `app.py`, `static/` | 완성 참고본이에요. Python 표준 라이브러리와 SQLite만 써요 |
| `smoke_test.py` | 어떤 스택으로 만든 방명록이든 API 약속을 지키는지 실제 요청으로 검사해요 |
| `examples/` | 실습 문장과 리허설 결과(PRD, 화면, 확인 도구 출력) |
| [`REQUIREMENTS-PROMPTS.md`](REQUIREMENTS-PROMPTS.md) | 단계별로 나눠 만들 때와 수업 뒤에 쓰는 요청 모음 |
| `Dockerfile`, `compose.yaml` | 완성본을 Docker로 띄울 때 써요 |
| `_reference/claude-runs/` | 강사용 리허설 기록이에요. 학생용 ZIP에는 없어요 |

번외 [웹앱을 앱으로](../../docs/day1-app.md)에서는 `labs/app/serve.py`가 이 폴더의 `app.py`를 불러 써요.

## 시작 폴더

`starter/`는 꼭 수업 저장소 밖으로 복사해서 써요. 완성본 옆에서 작업하면 Claude가 완성본을 읽고 베낄 수 있어요. 홈 폴더 아래 `dbinc-work`에 붙여 넣고 이름을 내 주제로 바꿔요. `.claude`처럼 점으로 시작하는 폴더는 숨겨져 보여도 폴더째 복사하면 함께 복사돼요.

## 완성본 켜기

이 폴더에서 실행해요. Windows는 `py`, macOS는 `python3`을 써요.

```powershell
py app.py
```

브라우저에서 http://127.0.0.1:8000 을 열어요. HTML 파일을 더블클릭하면 API를 부를 수 없으니 꼭 서버 주소로 열어요. 기록은 `data/guestbook.sqlite3`에 남아요. 서버는 `Ctrl+C`로 꺼요. 8000 포트가 차 있으면 `py app.py --port 8001`로 켜요.

## API 약속

PRD에 넣는 약속이에요. React와 Spring, Python 어느 것으로 만들어도 같아요.

| 요청 | 성공 응답 | 내용 |
| --- | --- | --- |
| `GET /api/entries` | 200, `{"entries": [...]}` | 최신 기록부터 최대 200개 |
| `POST /api/entries` | 201, `{"entry": {...}}` | JSON 본문의 `name`, `message`를 저장 |

기록 하나에는 `id`, `name`, `message`, `created_at`이 있어요. 이름은 앞뒤 공백을 지운 뒤 1~40자, 내용은 1~500자예요. 화면의 칸 이름은 주제에 맞게 바꿔도 되지만 JSON 키 `name`, `message`는 그대로 둬요. 더하는 칸은 비어도 201로 저장되는 선택 칸으로만 더해요.

실패하면 `{"error": "설명"}`으로 답해요. 잘못된 값과 깨진 JSON은 400, 8KiB가 넘는 본문은 413, JSON이 아닌 형식은 415, 없는 주소는 404예요.

## 확인 도구

| 명령 | 검사 대상 |
| --- | --- |
| `py smoke_test.py` | 옆의 완성본 `app.py` |
| `py smoke_test.py --app 내파일.py` | 내 Python 서버. 빈 포트와 임시 DB로 따로 띄워 검사해요 |
| `py smoke_test.py --url 주소` | 켜 둔 서버. Spring이면 `http://127.0.0.1:8080`이에요 |

Spring 서버를 켜 둔 상태에서 내 작업 폴더에서 쳐요.

```powershell
py $HOME/dbinc-ai-course/labs/guestbook/smoke_test.py --url http://127.0.0.1:8080
```

`$HOME`은 PowerShell과 macOS 터미널에서 모두 홈 폴더예요. 마지막 줄이 `OK`이면 통과예요. 결과 견본은 [examples/smoke-ok.txt](examples/smoke-ok.txt)예요. `--url`은 검사하면서 이름이 '검사'로 시작하는 기록 3개를 내 DB에 남겨요.

> **주의** React와 Spring은 화면 주소(5173)가 아니라 API 주소(8080)로 검사해요. Vite 개발 서버는 없는 경로에도 200을 돌려줘서 404 검사가 실패해요.

> **주의** `--app`도 `--url`도 없으면 내 코드가 아니라 완성본을 검사해서 늘 통과해요. 첫 줄의 `검사 대상`부터 봐요.

## Docker로 켜기

수업에서는 쓰지 않아요. Docker가 되는 PC에서 이 폴더로 가서 쳐요. 앞에서 켠 `app.py` 서버는 먼저 꺼요.

```powershell
docker compose up --build
```

기록은 `guestbook-data` volume에 남아요. 끝낼 때는 `docker compose down`을 쳐요. `down -v`는 volume까지 지워서 기록이 모두 사라져요.
