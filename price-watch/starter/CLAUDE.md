# 연습몰 가격 추적

교육용 가상 쇼핑몰(연습몰, http://127.0.0.1:8766)의 판매가와 소식을 매일 모아 지식베이스(kb/)에 쌓고,
쌓인 기록으로 추이를 계산해 리포트를 만드는 작업 폴더예요. 데이터는 모두 가상이에요.

## 먼저 읽을 것

- 하지 말 일: `.claude/skills/price-watch-rules/SKILL.md`
- 지금까지 알게 된 것: `kb/wiki/index.md`, 구조 변경 이력은 `kb/wiki/selector-changes.md`

## 명령

- 테스트: `python3 -m unittest discover -s tests`
- 오늘 수집: `python3 collect.py` (구조 변경이 의심되면 종료 코드 2, 스냅숏은 `.runtime/snapshots/`)
- 여러 날 시뮬레이션: `python3 tools/run_days.py 1 7`
- 위키 숫자 갱신과 데이터 점검: `python3 tools/curate.py`
- 예측 표: `python3 tools/forecast.py`
- 리포트: `python3 tools/report.py` → `out/report.md`
- 묶기: `python3 tools/package.py` → `dist/price-watch.zip`

## 담당

- collector: collect.py, 새 테스트, selector-changes.md, incidents.md
- curator: kb/wiki/products/*.md의 메모, incidents.md
- reporter: out/summary.md
- 사람(나): 날짜 넘기기, git add와 commit, 루틴 설정
