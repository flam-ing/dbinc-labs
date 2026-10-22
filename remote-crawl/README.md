# 원격 수집 연습 (remote-crawl)

예전 2일차 4교시의 "내 수집기" 실습 폴더예요. 지금 [6교시](../../docs/day2-knowledge.md)는 test-server를 한 번 가져오는 실습만 하고, 이 폴더는 수업 뒤 심화로 남겼어요.
교육용 원격 서버 test-server의 상품 하나("입문 키보드")의 가격과 재고를 예의 있게 모아요.
test-server는 강의용으로 다른 클라우드 계정에 올린 공개 서버예요. 그래서 우리 요청은 실제 인터넷을 지나 상대 서버의 기록에 남아요.
파이썬 표준 라이브러리만 써서 `pip install`이 필요 없어요.

## 시작하기

1. 이 폴더를 홈 폴더에 `dbinc-remote-crawl`이라는 이름으로 복사해요. 탐색기(macOS는 Finder)로 복사해도 되고, Claude에게 부탁해도 돼요.
2. Claude 데스크톱 앱의 Code 탭에서 **+ New session**을 누르고 **Select folder**로 복사한 폴더를 골라요.
3. 첫 요청으로 이렇게 물어봐요. "README.md와 polite-crawl 스킬을 읽고, 이 폴더에서 할 수 있는 일을 세 줄로 알려 줘."
4. 실습에서 보낼 말의 예시는 [examples/prompts.md](examples/prompts.md)에 있어요. 2026-10-17에 실제로 돌려 본 결과는 [examples/results.md](examples/results.md)에 있어요.

## 대상

| 길 | 주소 | 값이 있는 곳 |
| --- | --- | --- |
| 정적 HTML | https://test-server-8az.pages.dev/ | `#priceTarget`(가격), `#stockTarget`(재고), `.product-title`(이름) |
| JSON | https://test-server-8az.pages.dev/api/price | `price`, `stock`, `updated_at`, `next_update_at` |
| v2(빈 껍데기) | https://test-server-8az.pages.dev/v2/ | 화면에는 값이 보이지만 받은 HTML에는 없어요. `/v2/session`에서 세션 쿠키를 받은 뒤 `/v2/api/price`를 읽어요 |

값은 1분마다 바뀌어요. 같은 분에는 모든 길이 같은 값을 줘요.

## 지킬 것

교실 30명은 회사 출구 하나로 나가서 상대 서버에는 IP 하나로 보여요. 한 사람이 너무 빨리 두드리면 모두가 같이 막힐 수 있어요.

- 1분에 한 번보다 자주 묻지 않아요. 1분 안에 다시 실행하면 예시 수집기는 묻지 않고 저장해 둔 값을 보여 줘요(캐시).
- User-Agent에 우리 이름을 밝혀요. 예: `DBInc-3jo/1.0`
- 401, 403, 429를 받거나 "접속이 차단되었습니다"가 보이면 다시 두드리지 않고 멈춰요.
- 관리자 화면과 사람 확인(Turnstile) 주소는 부르지 않아요. 관리자 화면은 강사만 다뤄요.

자세한 규칙은 `.claude/skills/polite-crawl/SKILL.md`에 있고, 꼭 막아야 하는 것은 훅(`.claude/hooks/guard.py`)이 한 번 더 막아요.

## 예시 수집기

```bash
python3 polite_fetch.py --name DBInc-3jo/1.0
```

처음 실행하면 이렇게 나와요. 값은 그때그때 달라요.

```text
robots.txt: 규칙 파일이 없어요(받은 것이 글자 규칙이 아니에요). 없다고 마음대로 해도 된다는 뜻은 아니에요.
[json] 입문 키보드 39,900원 · 재고 19개 · data/live-prices.csv에 한 줄 더했어요
다음 값은 2026-10-15T16:12:00.000Z(UTC)에 나와요. 그 전에는 다시 묻지 않아요.
```

1분 안에 다시 실행하면 묻지 않아요.

```text
캐시: 지난 요청이 20초 전이라 묻지 않았어요. 마지막 값 입문 키보드 39,900원 · 40초 뒤에 다시 물을 수 있어요.
```

`polite_fetch.py` 위쪽의 "내 것으로 바꿀 곳"에서 이름(`NAME`)과 기본 길(`ROUTE`)을 바꿀 수 있어요.

## 내가 고를 것

- 어느 길로 읽을지: HTML, JSON, v2(세션부터)
- 무엇을 모을지: 가격, 재고, 바뀐 시각
- 나를 밝히는 이름
- 언제 다시 물을지: 1분 넘게 띄우기, `next_update_at` 쓰기
- 멈출 조건과 기록 모양
- 저장 모양: CSV 한 줄, JSON 한 줄

## 확인

```bash
python3 -m unittest discover -s tests
```

마지막 줄이 `OK`예요. 이 테스트는 받아 둔 응답 파일만 읽어서 인터넷 없이 돌아가요.

## 막히면

| 증상 | 해결 |
| --- | --- |
| `연결하지 못했어요`가 나오고 브라우저로도 test-server가 안 열려요 | 회사 내부망이 막았을 수 있어요. 연습몰로 같은 실습을 해요. 터미널에서 `python3 ~/dbinc-ai-course/labs/price-watch/shop/server.py --port 8766`으로 켜고 `python3 polite_fetch.py --shop`을 실행해요 |
| `CERTIFICATE_VERIFY_FAILED`가 나와요 | 회사 장비가 HTTPS를 중간에서 풀어 보는 경우일 수 있어요. 인증서 검사를 끄지 말고 강사에게 알린 다음 연습몰로 가요 |
| `막혔어요(403)`, `막혔어요(429)`가 나와요 | 강사가 방어 스위치를 켰거나 교실 IP가 잠깐 막혔을 수 있어요. 다시 두드리지 말고 1분 넘게 기다린 뒤 한 번만 다시 해요 |
| Windows에서 `python3`를 찾지 못해요 | `python` 또는 `py -3`로 바꿔요. `.claude/settings.json`의 훅 명령도 같이 바꿔요 |
