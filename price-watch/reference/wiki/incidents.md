# 장애와 대응 메모

수집이 멈추거나 데이터가 이상할 때 무엇을 보고 어떻게 했는지 적어요. 구조 변경은 selector-changes.md에 따로 적어요.

형식: `- YYYY-MM-DD · 무슨 일 · 어떻게 알았나 · 어떻게 했나 · 남은 일`

- 2026-11-01 · 수집 시작 전 확인 · 연습몰 /robots.txt와 /terms를 읽음 · /admin 금지, Crawl-delay 1, User-Agent 밝히기를 collect.py에 반영 · 없음
- 2026-11-08, 11-15, 11-23 · 구조 변경으로 수집 중단 · collect.py 종료 코드 2와 스냅숏 · 파서를 더하고 그날부터 다시 모음 · 빠진 날 없음(quality.md)
- 2026-11-23~ · /api/catalog 2쪽 첫 요청 429 · kb/runs.jsonl의 retried 1 · Retry-After 1초를 지켜 다시 요청, 따로 할 일 없음 · 429가 두 번 이어지면 사람에게 알림
