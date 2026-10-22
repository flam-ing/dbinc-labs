# 실습 검증 기록

이 문서는 실제로 실행한 확인과 실행하지 못한 항목을 나눠 적어요. 날짜는 한국 시각이에요.

## 방명록

2026-10-11에 `labs/guestbook`에서 `PYTHONDONTWRITEBYTECODE=1 python3 smoke_test.py`를 실행했어요. **3개 테스트가 통과했어요.**

- 별도의 Python 서버 프로세스와 임시 SQLite DB를 썼어요.
- GET 200, POST 201, 저장 목록의 최신순 정렬, 입력 앞뒤 공백 제거를 확인했어요.
- 서버 프로세스를 끄고 다시 켠 뒤에도 같은 DB의 기록이 남는 것을 확인했어요.
- 빈 값, 잘못된 자료형, 이름과 내용의 최대 길이 초과, 깨진 JSON은 400, 큰 본문은 413, 잘못된 Content-Type은 415로 끝나는 것을 확인했어요.
- 이름 40자와 내용 500자의 경계 값이 등록되는 것을 확인했어요.
- 등록되지 않은 주소와 DB·소스 경로 요청이 404로 끝나는 것을 확인했어요.
- `node --check static/app.js`가 통과했어요.

마지막 정합성 검토에서 검사 범위를 API 약속과 HTML 응답으로 맞췄어요. 학습자가 바꿔도 되는 제목이나 CSS·JS 파일 이름은 성공 조건으로 고정하지 않아요. UTC 시각은 `+00:00`과 `Z` 표기를 모두 읽어서 확인해요. 이렇게 고친 뒤 같은 스모크 검사를 한 번 더 돌렸어요.

처음에 sandbox 안에서 실행했을 때는 localhost 포트 열기가 막혔어요. 승인된 로컬 실행으로 같은 검사를 다시 해서 통과했어요. 검증하는 동안 외부 서버는 쓰지 않았어요.

Chrome에서 http://127.0.0.1:8000 을 열어 아래를 직접 확인했어요. DB는 배포 파일 안이 아닌 임시 파일 `/private/tmp/dbinc-day1-browser-check.sqlite3`를 썼어요.

- 빈 목록이 보여요.
- 이름 `교육 실습자`, 내용 `HTML 화면에서 API를 거쳐 저장했습니다.`를 등록하면 기록 번호와 목록이 보여요.
- 브라우저를 새로고침해도 같은 기록이 보여요.
- 이름을 공백으로 넣으면 `이름을 입력해 주세요.` 오류가 보이고 기존 기록 수는 그대로예요.
- 최종 화면의 주황(#FF6F0F), 따뜻한 흰색, 둥근 입력칸과 버튼을 직접 확인했어요.

실제 브라우저에서 휴대폰 화면 폭은 따로 검증하지 않았어요. CSS에는 700px 이하에서 한 열로 바뀌는 배치를 넣었어요.

2026-10-16 재확인: `python3 labs/guestbook/smoke_test.py` 3개 통과, `python3 labs/guestbook/smoke_test.py --app labs/app/serve.py` 3개 통과, `python3 labs/app/check_app.py` 8개 통과예요(`labs/app/extension/background.js`는 3행 주석만 바뀌었어요). 같은 날 이 문서를 고치면서 저장소 사본에서 세 명령을 한 번 더 돌려 같은 결과를 봤어요.

## 레거시 열 개

옛 Python 대체 실습(`labs/legacy`의 `before/`, `after/`, 12개 사례)과 `.NET` 레거시 폴더는 2026-10-16에 지웠어요. 지금 `labs/legacy`에는 가상 회사 누리상사의 레거시 열 개와 강사용 답(`_reference/`)이 있어요.

2026-10-17에 검사 도구(`expected/`와 `verify.py`)를 학생 레거시 폴더에서 `labs/legacy-checks/<폴더>/`로 옮겼어요. 내용은 그대로예요. 학생 폴더에는 이제 `README.md`, 소스, `data/`, `wiki/`, `issues/`만 있고, `wiki/`에 그 시절 기획서(PRD) 한 쪽이 더해졌어요. 검사 도구는 레거시 폴더 복사본에 다시 넣어야 동작해요. `verify.py`가 자기가 있는 폴더를 기준으로 `src/`와 `data/`를 찾기 때문이에요.

검사 도구를 쓰는 법은 전과 같아요. 원본은 `python3 verify.py`, 학습자 코드는 `--cmd`나 `--java`(PHP는 `--src`)로 같은 사례를 검사해요. 열 개 모두 마지막 줄에 `통과 N/N`을 찍어요. 방명록은 Python 길로 만든 앱을 그 폴더에서 `python3 ~/dbinc-ai-course/labs/guestbook/smoke_test.py --app app.py`로, Spring처럼 켜 둔 서버를 `--url http://127.0.0.1:8080`으로 검사해요. 옵션 없이 돌린 기본 검사가 통과해도 학습자 코드가 통과한 것으로 보지 않아요.

2026-10-17에 macOS arm64(Python 3.14.6, Homebrew OpenJDK 17.0.19, Node 24.21.0)에서 옮긴 뒤의 모양 그대로 확인했어요. 레거시마다 학생 폴더를 리포 밖 임시 폴더에 복사하고, `labs/legacy-checks/<폴더>/`의 내용을 그 안에 복사한 다음 실행했어요. 표의 `$REF`는 `labs/legacy/_reference/<폴더>`의 전체 경로예요.

| 폴더 | 원본 `python3 verify.py` | 강사 답 검사 | 결과 |
| --- | --- | --- | --- |
| `settle-cs` | 실행 못 함(.NET 없음) | `--java $REF/port`, `--java $REF/refactored` | 둘 다 `통과 7/7` |
| `claim-cs` | 실행 못 함(.NET 없음) | `--java $REF/refactored` | `통과 6/6` |
| `room-java` | `통과 6/6` | `--java $REF/src` | `통과 6/6` |
| `points-java` | `통과 7/7` | `--java $REF/src` | `통과 7/7` |
| `payroll-java` | `통과 8/8` | `--java $REF/src` | `통과 8/8` |
| `inventory-py` | `통과 6/6` | `--cmd "python3 $REF/src/reorder.py"` | `통과 6/6` |
| `expense-py` | `통과 6/6` | `--cmd "python3 $REF/src/expense_batch.py"` | `통과 6/6` |
| `notice-js` | `통과 6/6` | `--cmd "node $REF/src/bot.js"` | `통과 6/6` |
| `triage-js` | `통과 8/8` | `--cmd "node $REF/cli/triage.js"` | `통과 8/8` |
| `library-php` | 실행 못 함(PHP 없음, `통과 0/8`) | `--src $REF/src`(PHP 필요) | 실행 못 함 |

- 런타임이 없을 때의 안내는 2026-10-16에 봤어요. `settle-cs`와 `claim-cs`는 `준비 실패: .NET 8 SDK를 찾지 못했어요.`로 시작하는 안내와 `통과 0/7`, `통과 0/6`을 찍고 종료 코드 2로 끝났어요. `library-php`는 `verify.py: php를 찾지 못했어요.`로 시작하는 안내와 `통과 0/8`을 찍고 종료 코드 3으로 끝났어요.
- 검사가 만드는 결과 폴더(`actual/`, `verify-out/`)는 레거시 폴더마다 `.gitignore`에 들어 있어요.
- `settle-cs`, `claim-cs`, `library-php`의 원본과 `library-php` 강사 답은 레거시를 만들 때(2026-10-16) 임시로 설치한 .NET 8 SDK와 PHP 8.4로 통과를 확인했어요. 이 PC에서는 다시 돌리지 못했어요.
- 10개 모두 실제 Claude Code(헤드리스 `claude -p`)로 첫 질문, 원본 돌려 보기, `/init`, 인수인계 보고서, 지식베이스를 돌린 기록이 `labs/legacy/_reference/<폴더>/claude-runs/`에 있어요(2026-10-17). `room-java`는 안전망, 리팩토링 계획, 한 단계까지 돌렸고, 그 뒤 코드도 `verify.py --java src`로 `통과 6/6`이었다고 그 폴더의 `README.md`에 적혀 있어요.

## 실습 예시와 실제 실행 기록 (2026-10-17)

교시마다 실습 예시 문장을 학생 자리에서 실제 Claude Code(2.1.301, 헤드리스 `claude -p`)로 보내 봤어요. 실습 폴더를 리포 밖 임시 폴더에 복사하고, 강사 PC의 개인 설정이 끼어들지 않게 `--setting-sources project,local --strict-mcp-config`로 돌렸어요. 통한 문장과 결과 견본은 실습 폴더의 `examples/`에, 원문 기록(보낸 말, 답, 걸린 시간, 비용)은 강사용 `_reference/` 폴더의 README 표에 있어요. Claude가 한 말과 만든 파일은 고치지 않았어요.

| 교시 | 예시와 견본 | 원문 기록 | 실제로 확인한 것 |
| --- | --- | --- | --- |
| 1일차 1교시 | `labs/agent-intro/examples/` | `labs/agent-intro/_reference/claude-runs/`(00~09) | F12 화면, Code 탭 시연(`awk` 명령 뒤 `total.md`), 웹 채팅 실습 2~4와 더 해 보기 둘(도구를 끈 Claude로 확인) |
| 1일차 2교시 | `labs/game-kit/examples/` | `labs/game-kit/_reference/claude-runs/`(01~07) | 게임 프롬프트, 한 줄 고치기, 포스터 프롬프트와 Pollinations 그림, 다시 부탁하기, Code 탭 첫 질문 둘 |
| 1일차 3교시 | `labs/onepager/examples/` | `labs/onepager/_reference/claude-runs/` | 새 폴더에서 한 문장 작업(Sonnet 4분 2초), 사본 폴더 길(덧붙임 없이), 계획과 최고 점수 변경, 작성자 줄을 붙인 첫 커밋(8초) |
| 1일차 4교시 | `labs/guestbook/examples/` | `labs/guestbook/_reference/claude-runs/`(01~08) | 인터뷰로 PRD, 설계와 1단계 서버(`smoke_test.py --url http://127.0.0.1:8080` 3개 ok), 화면 연결(3개 ok), PRD 비교, 커밋 부탁, 8080이 겹칠 때 8081로 옮기기 |
| 1일차 번외 | `labs/app/examples/` | `labs/app/_reference/claude-runs/`(01~07) | React·Python 길 PWA 붙이기, 확장 주소 바꾸기, 테마 색, 팝업 글 수. 브라우저 동작은 headless Chrome으로 확인 |
| 1일차 5교시 | `labs/legacy/examples/5교시/` | `labs/legacy/_reference/<폴더>/claude-runs/`의 `s5a`~`s5f` | 실습 1, 따라 하기 둘, 문장으로 CLAUDE.md(room-java), 다른 레거시의 잘 묻기와 입력 파일(inventory-py), "왜?"(claim-cs) |
| 1일차 6교시 | `labs/legacy-checks/examples/` | `expense-py` 06~10, `triage-js` 07, `inventory-py`·`payroll-java`의 `s6-find-bad-code` | 나쁜 곳 찾기, 안전망, 계획, 첫 단계와 비교, 문서 세 가지, 검사 도구를 넣은 2판 계획 |
| 1일차 번외 2 | `labs/legacy/examples/번외2/` | `room-java`·`inventory-py`·`expense-py`의 `sx2/` | kb 세 쪽(3분대), 같은 질문 두 번, 새 소식 넣기, 점검, `[[ ]]` 링크 |
| 2일차 1교시 | `labs/rules/examples/`, `labs/day2/examples/d2s1/`, `labs/day2/hooks/examples/` | `labs/rules/_reference/claude-runs/`(01~07), `labs/day2/_reference/d2s1/`(03~08) | 같은 요청 비교(B 사본 다시), 내 규칙 한 줄, `/check-change`, `/readme-for-people`, 내 스킬 만들기와 `/run-checks`, `labs/day2` 준비 요청, RED·GREEN·놓친 곳 채우기, 훅을 건 폴더에 명세와 다른 요청 |
| 2일차 2교시 | `labs/debug/examples/`(01~03, 05, 07, 08), `labs/day2/automation/examples/`(내 루틴 설계) | `labs/debug/_reference/claude-runs/`(v2-01~v2-08이 지금 문장, 2026-10-17 Sonnet 5.5 Auto) | 이슈 글을 붙여 넣는 재현·원인(Plan)·한 줄과 회귀 테스트(이슈 #1), 이슈 #2 한 번에, `/goal`로 #3·#4. 루틴 PR 견본(07)은 예전 판 기록. 온콜 워크플로는 GitHub에서 아직 돌려 보지 않음 |
| 2일차 번외 | `labs/harness/examples/` | `labs/harness/_reference/claude-runs/`(01~05) | 같은 요청을 Sonnet 5.5와 Opus 5.5에 한 번씩(숨은 위험 둘 다 2/2), 내 폴더의 하네스 부품 찾기, 에이전트 설계서 쓰기와 질문에 답하기. 하네스 스튜디오는 브라우저로 네 판, 한 단계씩, 초기화, 기록 다시 보기, 내려받기, 390px 폭을 확인 |
| 2일차 3교시 | `labs/day2/integration/examples/`, `labs/day2/cli/examples/` | 같은 폴더의 `_reference/claude-runs/` | `.mcp.json` 등록과 billing 질문(두 번), SDK 스크립트, 가상환경이 없을 때 만들어 달라는 문장(a4, 48초, smoke PASS), Plan으로 CLI 계획, 만들고 확인, 권한 규칙 쓰기(C0)와 적용(C1) |
| 2일차 4교시 | `labs/crawl-once/examples/` | `labs/price-watch/_reference/claude-runs/`(01~13) | 원격 첫 수집, 8일 고치기와 기록, 22일 curator나 reporter 하나에게 맡기기(09, 10, 13), 23일 스킬(정답 수집기, 11), 30일 요약과 묶기(12). 부록 쪽은 서브에이전트 셋, 23일 collector, GUIDE.md, 손 계산 부탁 |

`_reference/` 폴더는 강사용이라 학생용 ZIP과 교안 사이트에 넣지 않아요(루트 `scripts/build_public.py`의 `instructor_only`, `dbinc/scripts/build_docs.py`). 2일차 1·2교시 기록에는 정답 테스트와 구현이 들어 있어서, 학생이 `labs/day2`를 그 자리에서 쓸 때 Claude가 찾아 읽지 않게 하려는 거예요.

## 미실행 항목

- Docker CLI가 없어서 Dockerfile 빌드, Compose 시작, 이름 붙은 볼륨을 쓴 재시작은 실행해서 확인하지 못했어요. 4교시에서는 수업 뒤 과제 A예요.
- 같은 요청을 모델 A/B로 돌리는 비교는 2일차 번외 실습 1에서만 Sonnet 5.5와 Opus 5.5로 한 번씩 했어요(`labs/harness/_reference/claude-runs/01`, `02`). Haiku나 effort Low 비교는 하지 않았어요. 실습의 실제 Claude Code 실행은 위 표의 `_reference/` 기록에 있어요. Code 탭 화면(승인 카드, 권한 모드 고르기, 질문 카드, Plan 승인 글자)에서 같은 요청을 돌려 보지는 않았어요. 기록은 모두 헤드리스로 돌렸고, 웹 채팅(claude.ai) 실습은 같은 문장을 Claude Code나 도구를 끈 Claude로 돌려 모양만 확인했어요.
- 4교시 기본 경로(React와 Vite 5173, Spring Boot 8080)는 2026-10-17 헤드리스 실행으로 `smoke_test.py --url http://127.0.0.1:8080` 3개 ok까지 확인했어요(`labs/guestbook/_reference/claude-runs/smoke-step1.txt`, `smoke-final.txt`). 번외 PWA 붙이기는 Spring 대신 같은 API의 `app.py`(8080)를 켠 연습 폴더에서 확인했어요. Spring에서 CORS 허락 목록을 만든 방명록이 확장 요청을 403으로 거절하는지는 확인하지 못했어요.
- Claude 데스크톱 앱 Code 탭의 `/prd-interview` 스킬 호출과 질문 카드는 실행하지 않았어요. 헤드리스에서는 질문 카드 대신 글로 물었어요.
- 레거시 `settle-cs`, `claim-cs`, `library-php`의 원본 검사와 `library-php` 강사 답 검사는 이 문서를 고친 PC에서 다시 실행하지 못했어요(.NET과 PHP 없음).
- Windows에서는 어떤 명령도 실행해 보지 않았어요.

[공식 skills 문서](https://code.claude.com/docs/en/skills), [공식 CLAUDE.md 문서](https://code.claude.com/docs/en/memory).
