# 원격 수집 연습

교육용 원격 서버 test-server(https://test-server-8az.pages.dev)의 상품 하나("입문 키보드")의 가격과 재고를 예의 있게 모으는 폴더예요.
test-server는 강의용으로 다른 클라우드 계정에 올린 공개 서버예요. 값은 1분마다 바뀌고, 우리 요청은 상대 서버의 기록에 남아요.

## 먼저 읽을 것

- 지킬 규칙: `.claude/skills/polite-crawl/SKILL.md`
- 예시 수집기: `polite_fetch.py` (한 번 실행하면 한 번만 물어요)
- 값은 `polite_fetch.py`로 모아요. WebFetch와 이름(-A) 없는 curl은 훅(`.claude/hooks/guard.py`)이 막아요.

## 대상

| 길 | 주소 | 값이 있는 곳 |
| --- | --- | --- |
| 정적 HTML | `/` | `#priceTarget`, `#stockTarget`, `.product-title` |
| JSON | `/api/price` | `price`, `price_text`, `stock`, `updated_at`, `next_update_at` |
| v2(빈 껍데기) | `/v2/`, `/v2/session`, `/v2/api/price` | 세션 쿠키를 받은 뒤의 JSON |

## 명령

- 한 번 모으기: `python3 polite_fetch.py`
- 길 고르기: `python3 polite_fetch.py --route html`
- 내 이름 정하기: `python3 polite_fetch.py --name DBInc-3jo/1.0` 또는 파일 위쪽 `NAME`
- 테스트(인터넷 없이): `python3 -m unittest discover -s tests`
- 원격이 막혔을 때: `python3 polite_fetch.py --shop` (내 PC 연습몰 127.0.0.1:8766이 켜져 있어야 해요)

## 결과

- `data/live-prices.csv`: 모을 때마다 한 줄. 같은 시각 값은 다시 저장하지 않아요.
- `data/incidents.md`: 막혔을 때 남는 기록
