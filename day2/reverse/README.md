# 리버스 엔지니어링 연습 · 화면 뒤 API를 CLI와 MCP로 감싸기

수업 뒤에 혼자 해 보는 자료예요. 2일차 5교시 [사내 시스템 연동](../../../docs/day2-integration.md)에서는 방명록을 MCP와 CLI로 연결했어요. 이 폴더는 같은 흐름을 크롤링 연습 서버(8765)로 한 번 더 해 보고 싶을 때 써요. 공개 API 문서가 없는 화면이라도, 브라우저가 실제로 주고받는 요청을 찾으면 작은 CLI로 감쌀 수 있어요. 그 CLI를 MCP 서버로 등록하면 Claude Code가 도구처럼 불러요. 데이터는 모두 교육용 가상 프로젝트 7건이에요.

| 파일 | 하는 일 |
| --- | --- |
| `projects_cli.py` | 연습 서버의 `/api/projects?page=N`을 부르는 CLI예요. 표준 라이브러리만 써요. 429·503을 받으면 기다렸다가 다시 요청하고, 모든 쪽을 읽을 때는 id로 중복을 빼요. 내 PC(127.0.0.1, localhost) 주소만 불러요. |
| `projects_mcp.py` | 위 CLI의 함수를 MCP 도구 `list_projects(page)`, `list_all_projects()`로 내놓는 stdio 서버예요. 실습 폴더의 `server.py`와 같은 방식으로 만들었어요. |

## 켜는 법

연습 서버는 강의 저장소에 있어요. 터미널 하나에서 켜 두고 그대로 둬요.

```bash
cd ~/dbinc-ai-course/demos/revision/crawler
python3 server.py --port 8765    # Windows는 py server.py --port 8765
```

다른 터미널에서 `labs/day2` 맨 위로 가서 가상환경을 켜고 실행해요. 가상환경 만드는 법은 [labs/day2 README](../README.md)에 있어요.

```bash
python reverse/projects_cli.py page 1
python reverse/projects_cli.py all
```

`all`을 처음 실행하면 연습 서버가 일부러 내는 실패 두 번이 보여요. 2쪽은 429(잠시 뒤에 다시 오라는 응답), 3쪽은 503(잠깐 처리하지 못한다는 응답)이에요. 안내 줄은 표준 오류로 나와요.

```text
429 응답: 1초 기다렸다가 다시 요청해요 (1/3) http://127.0.0.1:8765/api/projects?page=2
503 응답: 0.2초 기다렸다가 다시 요청해요 (1/3) http://127.0.0.1:8765/api/projects?page=3
```

그 뒤에 7건(`proj-001`~`proj-007`)과 `"duplicates": ["proj-003", "proj-005"]`가 나오면 맞아요. 연습 서버는 서버를 켠 뒤 쪽마다 첫 요청만 실패시키니, 두 번째 실행부터는 이 두 줄이 나오지 않아요.

MCP 서버로 등록할 때는 가상환경의 Python 경로를 써야 `mcp` 패키지를 찾아요.

Code 탭에서는 Claude에게 "reverse/projects_mcp.py를 .mcp.json에 practice-projects라는 이름으로 더해 줘. command에는 .venv 안 python의 절대 경로를 넣어 줘"라고 부탁해요. 새 서버는 같은 폴더로 새 세션을 열어야 보여요.

## 확인 명령

```bash
python tools/smoke_reverse.py
```

마지막 줄이 `PASS 리버스 엔지니어링:`으로 시작하면 돼요. 그 앞의 `Tool 'list_projects' failed: ... 404 응답` 한 줄은 없는 4쪽을 일부러 불러 보는 검사라서 정상이에요. 연습 서버가 꺼져 있으면 `연습 서버를 먼저 켜세요`가 나와요. 다른 포트로 켰다면 `--base-url http://127.0.0.1:<포트>`를 붙이고, MCP 서버는 `PRACTICE_BASE_URL` 환경 변수로 주소를 바꿔요.

## 지켜야 할 것

실제 서비스에 같은 방법을 쓸 때는 그 서비스의 이용약관, 법, 회사 보안 정책을 먼저 확인해요. 공식 API나 내보내기 기능이 있으면 그것부터 써요. Network 탭에서 복사한 요청에는 로그인 쿠키나 토큰이 들어 있을 수 있으니, 그대로 Claude에게 붙여 넣거나 파일에 저장하지 않아요.
