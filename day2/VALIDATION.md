# 제공 자료 검증 기록

2026-10-11 · macOS arm64 · Python 3.12.13 · pytest 9.1.1 · pytest-cov 7.1.0 · MCP SDK 2.2.0

이 기록은 배포하는 기준 구현을 실제로 실행한 결과예요. 수강생이 만든 구현이나 Claude의 응답을 대신 검증한 기록은 아니에요.

| 확인 | 결과 |
| --- | --- |
| TDD 시작 파일과 시작 테스트 | `NotImplementedError`로 1 failed, 종료 코드 1이에요. 일부러 만든 RED(실패로 시작하는 상태)예요 |
| 버그 파일과 제공 계약 검사 | 34 failed, 10 passed, 종료 코드 1이에요 |
| 버그 재현 스크립트 | 3개 사례 모두 실패나 오류를 재현해요 |
| 기준 구현과 학생 시작 테스트·제공 계약 | 45 passed예요 |
| 기준 구현의 집계 함수 커버리지 | statement 30개, branch 20개 모두 100%예요. 프로젝트 전체 수치는 아니에요 |
| `work/tdd` 경로와 동적 import 커버리지 | 같은 기준 구현으로 명령을 점검했고 45 passed, 100%예요 |
| 기준 구현으로 같은 재현 스크립트 | 3개 모두 PASS, 종료 코드 0이에요 |
| 조회·가공·보고서 모듈 단위 검사 | 5 passed예요 |
| stdio MCP 실제 연결 | 도구 2개, 읽기 전용 표시, 서비스, 필터, 2페이지, 없는 서비스, 잘못된 limit, fixture 해시 불변을 확인했어요 |
| 실제 MCP 조회, 집계, Markdown 보고서 | 이벤트 8건, 오류 3건, 느린 요청 4건으로 보고서를 만들었어요 |
| ZIP 만들기 | 고른 구현의 계약·모듈 검사와 통합 실행 뒤 만들어졌어요 |
| ZIP을 다른 임시 폴더에 풀어 실행 | 계약 44건, 모듈 5건, stdio MCP, 보고서가 모두 성공했어요 |

MCP 입력 오류 검사는 일부러 `limit=0`을 보내요. 서버의 짧은 오류 로그 한 줄 뒤에 전체 검사가 PASS로 끝나면 정상이에요.

실제 Claude Code의 연결 승인, 인증, 서브에이전트 위임, Git 커밋은 수업 환경에서 확인해야 해요. 제공 스크립트는 이런 일을 실행하거나 사용자 설정을 고치지 않았어요. Windows 명령은 안내했지만 실제 Windows에서 실행해 검증하지는 않았어요.

기준 구현 검사에 쓴 임시 `work` 폴더는 지웠어요. 학습자는 `tools/start.py`로 자기 작업을 새로 시작할 수 있어요.

## 3교시 추가 자료 검증 (2026-10-14)

macOS arm64 · Python 3.12.13 · MCP SDK 2.2.0 · 크롤링 연습 서버(`demos/revision/crawler/server.py`)를 다른 포트로 따로 켜서 확인했어요. 2026-10-16부터 이 표의 `--query`, `reverse/`, `permissions/` 자료는 수업에서 쓰지 않고 2일차 실습 자료 9절의 혼자 더 해 보기로 남겼어요.

| 확인 | 결과 |
| --- | --- |
| `run_report.py --query`에 시작 파일 | `NotImplementedError`예요. 일부러 만든 시작 상태예요 |
| `run_report.py --query`에 첫 페이지만 읽는 조회 모듈 | `AssertionError: 페이지를 끝까지 읽으면 이벤트는 8건입니다`가 나와요 |
| `run_report.py --query`에 끝까지 읽는 조회 모듈 | PASS 8건, 오류 3건, 느린 요청 4건으로 보고서를 만들어요 |
| `--query` 없이 기존 명령(`run_report.py`, `package.py`) | 출력과 동작이 그대로예요 |
| `reverse/projects_cli.py` | 3쪽, 7건, 중복 2건(proj-003, proj-005)이에요. 첫 실행에서 429와 503을 받고 다시 요청해요. 없는 쪽은 404로 멈춰요. 바깥 주소와 꺼진 서버는 안내와 함께 종료 코드 1로 끝나요 |
| `tools/smoke_reverse.py` | CLI, stdio MCP 도구 2개(읽기 전용), 없는 쪽 오류, 바깥 주소 차단이 PASS예요 |
| `tools/smoke_admin.py` | 운영 도구 MCP 도구 2개(읽기와 삭제 표시), 삭제, 없는 id 오류, 되돌리기, 원본 fixture 불변, 권한 규칙 더하기와 빼기가 PASS예요 |
| `tools/mcp_config.py --all` | 서버 세 개(`dbinc-training-events`, `practice-projects`, `dbinc-training-admin`)를 출력해요. 옵션 없이는 예전처럼 하나예요 |

Claude Code 세션 안의 동작(새 서버 승인, deny 규칙을 넣은 뒤 Claude의 반응, `/sandbox`, Notion 로그인)은 확인하지 않았어요. 수업 전 리허설에서 확인해야 해요.

## 2026-10-16 다시 실행

macOS arm64 · Python 3.12.13 · pytest 9.1.1 · pytest-cov 7.1.0 · mcp 2.2.0 · 저장소 사본에 새로 만든 가상환경에서 실행했어요.

| 확인 | 결과 |
| --- | --- |
| `python -m pytest tests --impl reference/report.py -q` | 45 passed |
| `python -m pytest -q` | 45 passed |
| `python tools/start.py tdd` 뒤 `python -m pytest tests/test_student_report.py --impl work/tdd/report.py -q` | `NotImplementedError`로 1 failed |
| `python tools/reproduce.py --impl reference/report.py` | `재현 실패 사례: 0/3` |
| `python tools/reproduce.py --impl buggy/report.py` | `재현 실패 사례: 3/3`, 종료 코드 1 |
| `python -m pytest tests/test_contract.py --impl buggy/report.py -q` | 34 failed, 10 passed |
| 버그 코드 사본에 2교시 단계별 수정을 하나씩 넣기 | 재현 실패 사례가 차례로 3/3, 2/3, 1/3, 0/3이에요. 계약 테스트는 차례로 34 failed 10 passed, 32 failed 12 passed, 29 failed 15 passed, 26 failed 18 passed예요 |
| `python tools/smoke_mcp.py`, `python tools/smoke_admin.py` | 마지막 줄이 모두 PASS |
| `python -m pytest integration/tests -q` | 5 passed |
| `python tools/run_report.py` | `PASS 조회→가공→보고서: 8건 / 오류 3건 / 500ms 이상 4건`. 다시 쓴 `artifacts/day2-report.md`는 저장소의 파일과 같아요 |
| `python3 hooks/run_tests.py ... < hooks/samples/post-edit.json`(기준 구현) | 출력 없이 종료 코드 0 |
| 같은 훅에 `>=`를 `>`로 바꾼 사본 | `{"decision": "block", ...}`와 3 failed, 42 passed. `stop-again.json` 입력에는 `systemMessage`만 나와요 |
| `python3 automation/make_repo.py <새 폴더>`와 그 폴더의 `python3 -m pytest -q` | `재현 실패 사례: 3/3`, 8 failed, 36 passed |

## 3교시 실습 B 자료 검증 (2026-10-16)

macOS arm64 · Python 3 표준 라이브러리 · 참고 방명록(`labs/guestbook/app.py`)을 빈 포트와 새 DB로 켜서 확인했어요.

| 확인 | 결과 |
| --- | --- |
| `cli/gb_example.py write "실습자" "CLI로 남긴 첫 기록"` | `보내지 않았어요: 확인이 필요해요. 보내려면 --yes를 붙여요.` 종료 코드 1이고, 서버로 요청을 보내지 않았어요 |
| 같은 명령에 `--yes` | `저장했어요: #1 실습자` 종료 코드 0이에요. 서버 로그에는 `POST /api/entries` 201 한 줄만 찍혔어요 |
| 빈 이름, 41자 이름, 빈 내용 | `보내지 않았어요:` 뒤에 차례로 `이름을 입력해 주세요.`, `이름은 40자 이내로 입력해 주세요. (지금 41자)`, `내용을 입력해 주세요.`가 나와요. 종료 코드 1이고, 서버로 요청을 보내지 않았어요 |
| `list`, `list --json` | `#1 실습자: CLI로 남긴 첫 기록`과 `1개 (전체 1개)`가 나와요. `--json`은 JSON 배열을 찍어요 |
| 서버가 꺼졌거나, JSON이 아닌 응답이 올 때 | `방명록 서버에 연결하지 못했어요: … (Connection refused)`, `목록을 받지 못했어요: 404 JSON이 아닌 응답이에요. 주소가 API 주소인지 확인해요.`가 나와요. 둘 다 종료 코드 2예요 |

주소는 `--url`이나 `GB_URL` 환경 변수로 바꿔요. 기본값은 `http://127.0.0.1:8000`이에요. Claude 데스크톱 앱에서 이 CLI를 권한 규칙(`cli/settings.example.json`)과 함께 쓰는 장면은 실행하지 않았어요. 수업 전 리허설에서 확인해야 해요.

## 3교시 실습 B와 따라 하기 C 헤드리스 실행 (2026-10-17)

참고 방명록을 리포 밖에 복사해 켜고, Claude Code 2.1.301(claude-opus-5-5)을 헤드리스(`claude -p`)로 돌렸어요. 기록은 `cli/_reference/claude-runs/`, 학생용 견본은 `cli/examples/`예요.

| 확인 | 결과 |
| --- | --- |
| B1: Plan 모드로 화면이 부르는 API와 막는 것, `tools/gb.py` 계획 | 1분 12초. 화면의 `required`는 완전히 빈 칸만 막고, 공백만 넣은 값은 서버가 400으로 막는다는 것을 찾아내고 CLI에서도 막을지 물었어요 |
| B2: 답하고 만들기, 켜 둔 방명록에 여섯 번 실행 | 1분 9초. 틀린 값 세 번은 서버 로그에 새 줄이 0이었어요(보내기 전에 막음) |
| C0: 따라 하기 C 첫 문장으로 `.claude/settings.json` 만들기 | 22초. `.claude/settings.json`은 Accept edits에서도 쓰기 승인을 기다렸어요. Claude는 인자 없이 부르는 줄을 포함해 규칙 여덟 줄을 준비하고 멈췄어요 |
| C1: 규칙을 넣은 뒤 새 세션에서 목록 보기와 글 남기기 | 26초. 신뢰하지 않은 폴더라서 `.claude/settings.json`의 allow 줄 3개가 무시됐다는 안내가 나왔고, 목록 명령도 막혔어요. Claude가 부르려던 명령은 `python3 tools/gb.py list --limit 3`으로, 규칙 `Bash(python3 tools/gb.py list *)`와 같은 모양이에요. 막히자 `curl` 같은 다른 길로 돌아가지 않고 멈춰서 물었어요 |

그래서 `cli/settings.example.json`에 `python3` 줄을 더했어요. 데스크톱 앱에서 폴더를 열 때 신뢰를 묻는지, 규칙이 바로 적용되는지는 리허설 때 확인해야 해요.
