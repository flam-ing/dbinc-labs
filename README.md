# 실습 자료 안내

`labs/` 폴더의 실습 자료를 교시 순서로 모은 안내예요. 폴더마다 어느 교시에 쓰는지, 어떻게 켜고 무엇이 보이면 되는지 적었어요. 2일차 자료는 [2일차 실습 자료](../docs/day2-labs.md)에도 있어요. 안에 나오는 회사, 사람, 상품, 대화는 모두 수업을 위해 지어낸 것이에요.

명령은 실습 폴더를 `~/dbinc-ai-course`에 받았다고 보고 적었어요. 블록마다 `cd ~/dbinc-ai-course`에서 출발해요. Windows에서는 `python3` 대신 `py`로 쳐요.

## 한눈에 보기

| 폴더 | 쓰는 교시 | 들어 있는 것 | 확인하는 법 |
| --- | --- | --- | --- |
| `labs/agent-intro` | 1일차 1교시 | 챗봇에 올리는 `orders.csv`(가상 주문 5건, 합계 89,000원) | 없음 |
| `labs/setup` | 1일차 2교시 | 보내는 말과 실제 답(`examples/`) | 없음 |
| `labs/game-kit`, `labs/onepager` | 1일차 3교시 | 견본 게임 `game-kit/examples/sample-game/`, 미리 만든 미디어 세트, 완성 예시 게임 `onepager/game/` | `python3 labs/onepager/check.py labs/onepager/game` |
| `labs/guestbook` | 1일차 4교시 | 4교시 시작 폴더 `starter/`(인터뷰 스킬 `prd-interview`), 참고 방명록, 확인 도구 | `python3 labs/guestbook/smoke_test.py` |
| `labs/app` | 1일차 번외 | 내 방명록에 복사하는 PWA 파일 `pwa/`와 크롬 확장 `extension/`, 강사 예제 `serve.py` | `python3 labs/app/check_app.py` |
| `labs/legacy-easy` | 1일차 5교시, 2일차 1~3교시(번외 실습 2와 7교시 실습 1에서도 같은 폴더를 열어요) | 카페 포인트 `cafe-points/`, 위키 묶음 `cafe-points-wiki/`(1일차 5교시 실습 6, 2일차 2교시 실습 2), 재미로 해 보는 카톡 대화 `kakao-sample/` | 사본에서 `python3 cafe.py` |
| `labs/rules` | 2일차 3교시 | 규칙 세 줄, 스킬, 테스트, 훅의 실제 결과(`examples/made-by-claude/cafe-points/`) | 없음 |
| `labs/debug` | 2일차 4교시 | 버그 네 개가 든 카페 포인트 코드, 온콜 워크플로, 강사 저장소를 만드는 `tools/make_repo.py` | `cd labs/debug` 뒤 `python3 -m unittest` |
| `labs/harness` | 2일차 번외 | 배포 전 변경 목록 `compare/changes.md`(실습 1·3), 예전 판의 설계서 양식 `design/` | 없음 |
| `labs/roombook` | 2일차 5교시 | 로그인이 있는 연습용 사내 툴 회의실 예약. `py app.py`로 켜요(포트 8010). 강사용 정답 견본과 실행 기록은 `_reference/`(ZIP에 없음) | `python3 labs/roombook/smoke_test.py`(11/11 통과) |
| `labs/day2/cli` | 수업 뒤 연습 | 예전 판 5교시의 방명록 CLI 결과, `gb_example.py`, 권한 규칙 예시 | 없음 |
| `labs/crawl-once` | 2일차 6교시 | Claude가 실제로 만든 `crawl.py`와 답 | 없음 |
| `labs/quant` | 2일차 6교시 | 비트코인 일봉과 공포·탐욕 지수 사본 `snapshot/`, 실제 결과 | 없음 |
| `labs/tdd` | 수업 뒤에 해 볼 것 | 3교시에 해 본 테스트 먼저와 훅을 다른 예제로 한 번 더 해 보는 자료 | [README](tdd/README.md) |

수업 진행은 교시마다 있는 교안을 봐요. 이 문서는 자료를 켜고 확인하는 방법만 모았어요.

## 예시와 강사용 기록

폴더마다 `examples/`가 있어요. 실습에서 보낼 예시 문장과, 강사가 수업 전에 그 문장을 실제로 보내서 받은 결과예요. Claude가 한 말과 만든 파일은 고치지 않았어요. 막혔을 때 비교하는 자료라서 내 작업 폴더에는 복사하지 않아요.

이름이 `_reference`인 폴더는 강사용이에요. 실제 실행 기록과 정답이 들어 있어서 학생용 ZIP과 교안 사이트에는 넣지 않아요.

## 작업 폴더

| 교시 | 작업 폴더 | 만드는 법 |
| --- | --- | --- |
| 1일차 2교시 | 바탕화면 `dbinc-notes` | 빈 폴더를 만들어요 |
| 1일차 3교시 | 바탕화면 `my-game` | 빈 폴더를 만들어요 |
| 1일차 4교시, 번외 | `~/dbinc-work/<내 주제>` | `labs/guestbook/starter`를 복사해요. 숨은 `.claude` 폴더도 같이 와야 해요 |
| 1일차 5교시, 2일차 1~3교시 | `~/legacy/cafe-points` | `labs/legacy-easy/cafe-points`를 복사해요 |
| 2일차 4교시 | `~/cafe-points-oncall` | 강사 저장소를 받거나 `labs/debug`에서 `py tools/make_repo.py`로 만들어요 |
| 2일차 5교시 | `labs/roombook` | 그 자리에서 열어요. 서버는 PowerShell 창에서 `py app.py`로 켜요 |
| 2일차 6교시 | 빈 폴더 `dbinc-crawl`, `dbinc-quant` | 수업 중에 만들어요 |

복사는 탐색기나 Finder로 해도 되고, Claude에게 부탁해도 돼요.

## 포트

| 포트 | 쓰는 곳 |
| --- | --- |
| 5173 | 방명록 화면 React(Vite), 1일차 4교시와 번외 |
| 8080 | 방명록 서버 Spring Boot, 1일차 4교시와 번외 |
| 8000 | 참고 방명록 `labs/guestbook/app.py`, 강사 예제 `labs/app/serve.py`. 한 번에 하나만 켜요 |
| 8010 | 회의실 예약 `labs/roombook/app.py`, 2일차 5교시 |

## 1일차 3교시 · 게임

수강생은 빈 `my-game` 폴더에서 한 문장으로 게임을 만들어요. 5분이 넘도록 파일이 안 생기면 `labs/game-kit/examples/sample-game/index.html`을 `my-game`에 넣어요. 미리 만든 그림과 음악 세트(`media-bright.zip`, `media-space.zip`, `media-forest.zip`)는 학생용 ZIP에 없어서 게시본 3교시 교안에서 받아요.

## 1일차 4교시 · 방명록

4교시에는 `labs/guestbook/starter`를 내 주제 폴더로 복사해서 시작해요. 안에는 인터뷰 스킬 `.claude/skills/prd-interview/SKILL.md`, Python 길 시작 화면 `index.html`, `.gitignore`가 있어요.

참고 방명록은 Python 표준 라이브러리만 써서 설치할 것이 없어요.

```text
python3 labs/guestbook/app.py
```

http://127.0.0.1:8000/ 에서 열려요. 확인 도구는 이렇게 돌려요.

```text
python3 labs/guestbook/smoke_test.py
python3 labs/guestbook/smoke_test.py --url http://127.0.0.1:8080
```

첫 줄은 참고 방명록을 검사하고, 둘째 줄은 내가 켜 둔 Spring 서버를 검사해요. 둘째 줄은 켜 둔 서버의 DB에 이름이 '검사'로 시작하는 글 3개를 남겨요. API 약속은 [방명록 README](guestbook/README.md)에 있어요.

## 1일차 번외 · 앱으로 만들기

수강생은 `labs/app/pwa`의 파일 세 개(`manifest.webmanifest`, `sw.js`, `pwa.js`)를 내 방명록 `web/public`에 복사해요. 실습 2에서는 `labs/app/extension`을 Claude에게 내 프로젝트로 복사하게 하고, 그 복사본을 `chrome://extensions`에서 올려요. 강사 예제는 `serve.py`로 켜요. `labs/guestbook/app.py`와 같은 8000번이라 하나를 끄고 켜요.

```text
python3 labs/app/serve.py
python3 labs/app/check_app.py
```

자세한 순서는 [앱 만들기 README](app/README.md)에 있어요.

## 1일차 5교시와 2일차 1~3교시 · 카페 포인트

카페 포인트는 수업용으로 지어낸 동네카페 포인트 프로그램이에요. Python 표준 라이브러리만 써요. 탐색기나 Finder로 `labs/legacy-easy/cafe-points`를 `~/legacy` 안에 복사한 다음, 그 폴더에서 돌려요.

```text
cd ~/legacy/cafe-points
python3 cafe.py
```

`out/report.txt`에 주문 6건, 매출 36,800원, 적립 703점이 나오면 돼요. 끝나기 전에 1초쯤 멈추는 것은 정상이에요.

| 폴더 | 언제 | 하는 일 |
| --- | --- | --- |
| `cafe-points-wiki/` | 1일차 5교시 실습 6, 2일차 2교시 실습 2 | 위키, 메신저, 회의록, 고객 문의, 메일 다섯 장이에요. 1일차에는 폴더째 `cafe-points` 안에 복사하고 코드와 다른 곳을 물어요. 2일차 2교시에는 `메신저-2021-03-마감-1초.md` 한 장을 `cafe-points` 안에 복사해서 지식베이스에 넣어요 |
| [`kakao-sample/`](legacy-easy/kakao-sample/README.md) | 수업 뒤 재미로 | `카톡_카페포인트팀.txt`와 `카톡_카페포인트팀_새대화.txt`예요. 수업 실습에서는 쓰지 않아요 |

`examples/`와 `_reference/`는 복사하지 않아요. 안내는 [쉬운 레거시 README](legacy-easy/README.md)에 있어요.

## 2일차 4교시 · 버그 네 개 카페 포인트

`labs/debug`는 1일차 카페 포인트 코드와 같은 프로그램에 버그를 네 개 넣은 폴더예요. 오전 `~/legacy/cafe-points`와는 따로 받아요. 강사가 이 폴더로 강사 저장소를 만들어요. 받은 직후에는 테스트 3개가 통과해요. 버그를 잡는 테스트가 아직 없어서 그래요.

```text
cd labs/debug
python3 -m unittest
```

강사 저장소를 만드는 순서와 이슈를 올리는 시각은 [강사용 README](debug/_reference/README.md)에 있어요.

## 그 밖의 폴더

위 표에 없는 폴더는 예전 판에서 쓰던 자료예요. 이번 수업에서는 쓰지 않아요. 누리상사 레거시 열 개(`labs/legacy`)의 안내는 [레거시 10개 안내](../docs/legacy-catalog.md)에 있어요.

## 막히면

| 증상 | 이렇게 해요 |
| --- | --- |
| `python3`를 찾지 못해요 | Windows는 `py`로 쳐요 |
| 포트가 이미 쓰이고 있어요 | 앞에서 켠 서버 터미널에서 `Ctrl+C`를 눌러 꺼요 |
| 복사한 폴더에 `.claude`가 없어요 | 탐색기에서 숨김 항목 보기를 켜고 폴더째 다시 복사해요 |
| `cafe-points-wiki` 폴더가 없어요 | ZIP을 다시 받아요 |
| HTML 화면이 비어 보여요 | 더블클릭 대신 `http://` 주소로 열어요 |
