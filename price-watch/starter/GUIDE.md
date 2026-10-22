# 가격 추적 파이프라인 실행 가이드

연습몰(교육용 가상 쇼핑몰)의 판매가와 소식을 날마다 모아 지식베이스(`kb/`)에 쌓고, 쌓인 기록으로 7일 추이를 계산해 리포트를 만드는 폴더예요.
이 폴더를 처음 받은 사람이 위에서부터 따라 하면 되게 썼어요. 데이터는 모두 가상이에요.

## 준비

- Python 3.12 이상이 필요해요. 표준 라이브러리만 써서 `pip install`이 필요 없어요.
- 수집 대상인 연습몰 서버는 이 폴더에 없어요. 교안 저장소의 `labs/price-watch/shop/server.py`를 켜요.

```bash
python3 ~/dbinc-ai-course/labs/price-watch/shop/server.py --port 8766
```

서버를 켠 창은 그대로 두고, 새 창에서 이 폴더로 와서 테스트부터 돌려요.

```bash
python3 -m unittest discover -s tests
```

마지막 줄이 `OK`면 준비가 끝났어요.

## 실행

| 하고 싶은 일 | 명령 | 결과 |
| --- | --- | --- |
| 오늘 것 모으기 | `python3 collect.py` | `kb/prices.csv`, `kb/news.jsonl`, `kb/runs.jsonl`에 덧붙여요 |
| 여러 날 시뮬레이션 | `python3 tools/run_days.py 1 7` | 연습몰 날짜를 하루씩 넘기며 모아요 |
| 연습몰 날짜 보기·바꾸기 | `python3 tools/sim_day.py`, `python3 tools/sim_day.py 8` | 수업 진행용이에요 |
| 위키 숫자와 데이터 점검 | `python3 tools/curate.py` | `kb/wiki/products/*.md`, `kb/wiki/quality.md` |
| 예측 표 | `python3 tools/forecast.py` | `out/forecast.json` |
| 리포트 | `python3 tools/report.py` | `out/report.md` |
| 묶기 | `python3 tools/package.py` | `dist/price-watch.zip` |

`collect.py`가 종료 코드 2로 멈추면 페이지 구조가 바뀐 것을 의심해요. 받은 페이지는 `.runtime/snapshots/products-<날짜>.html`에 남아요.
`kb/wiki/selector-changes.md`를 먼저 읽고, 새 파서를 `PARSERS` 맨 앞에 더하고, 새 테스트 파일을 만든 다음 기록을 남겨요.

## Claude Code 연결

이 폴더 맨 위에서 Claude Code를 열면 아래가 자동으로 잡혀요.

| 파일 | 하는 일 |
| --- | --- |
| `CLAUDE.md` | 이 폴더가 무엇이고 어떤 명령을 쓰는지 |
| `.claude/skills/price-watch-rules/SKILL.md` | 하지 말아야 할 일(하네스) |
| `.claude/skills/price-watch-daily/SKILL.md` | 하루치 일의 순서. `/price-watch-daily`로 불러요 |
| `.claude/agents/collector.md`, `curator.md`, `reporter.md` | 조회, 가공, 리포트 담당 서브에이전트 |
| `.claude/settings.json`, `.claude/hooks/guard.py` | 다른 사이트 요청, 기록 파일 수정, 기존 테스트 수정을 막는 훅 |
| `routine/daily-prompt.md` | `/loop`, 데스크톱 예약 작업, 클라우드 루틴에 넣을 요청문 |

훅은 `python3`로 `guard.py`를 실행해요. `python3`가 없는 PC(Windows 등)에서는 `.claude/settings.json`의 명령을 그 PC의 파이썬 이름으로 바꿔요.

## 파일

| 경로 | 내용 |
| --- | --- |
| `collect.py` | 수집기. 파서 목록 `PARSERS`, 요청 간격 1초, 429 재시도, 0건이면 멈춤 |
| `kb/prices.csv` | 날짜, 상품 코드, 이름, 분류, 판매가, 정가, 가져온 주소, 가져온 시각, 쓴 파서 |
| `kb/news.jsonl` | 소식(id, 날짜, 출처, 제목, 본문, 태그) |
| `kb/runs.jsonl` | 수집할 때마다 남는 실행 기록 |
| `kb/wiki/` | LLM 위키. `index.md`부터 읽어요 |
| `tools/` | 시뮬레이션, 정리, 예측, 리포트, 묶기 스크립트 |
| `tests/` | 단위 테스트와 구조별 스냅숏(`tests/fixtures/`) |
| `out/` | 리포트와 예측 결과 |

## 확인하지 않은 것

- Windows에서는 실행해 보지 않았어요.
- 실제 쇼핑몰에는 쓰지 않았어요. 실제 사이트에 쓰려면 이용약관과 robots.txt, 회사 승인을 먼저 확인하고, `collect.py`의 `ensure_local`과 파서를 그 사이트에 맞게 새로 만들어야 해요.
- 예측은 판매가만으로 계산한 연습용이에요. 되돌아보기 오차율은 마지막 7일 한 번만 잰 값이에요.
