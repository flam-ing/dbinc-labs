# 셀렉터 변경 기록

연습몰 상품 페이지 구조가 바뀌어 수집기를 고칠 때마다 맨 아래에 한 항목을 더해요.
다음에 구조가 또 바뀌면 Claude와 사람이 이 파일을 먼저 읽어요. 같은 실수를 줄이고 더 빨리 고치려는 기록이에요.

형식

```
## YYYY-MM-DD · 한 줄 제목 (바뀌기 전 구조 → 바뀐 구조)
- 증상: collect.py가 낸 메시지와 종료 코드
- 원인: 무엇이 바뀌었나요(태그, 클래스 이름, 데이터 위치)
- 고친 곳: 더한 파서 이름, 바꾼 줄
- 확인: 더한 테스트 파일, 다시 모은 날짜와 건수
- 다음에 볼 것: 코드만 봐서는 모르는 함정
- 걸린 시간: 대략
```

## 2026-11-01 · 처음 구조 (A)
- 상품 목록은 `<li class="product" data-sku="...">`이고, 이름은 `span.name`, 판매가는 `span.price`, 할인할 때만 정가가 `s.list-price`에 나와요.
- 파서: `parse_list_a`
- 확인: tests/test_collect.py (스냅숏 tests/fixtures/products-2026-11-01.html)

## 2026-11-08 · 목록이 카드형으로 바뀜 (A → B)
- 증상: `python3 tools/run_days.py 8`에서 "상품을 0건 찾았어요", 종료 코드 2
- 원인: `li.product`가 `article.card`로, `data-sku`가 `data-item-id`로 바뀌었어요. 분류는 `p.card__cat`, 이름은 `h3.card__title`, 판매가는 `strong`, 할인할 때만 정가가 `del`에 먼저 나와요.
- 고친 곳: `parse_cards_b` 추가, `PARSERS = [parse_cards_b, parse_list_a]`
- 확인: tests/test_layout_b.py (스냅숏 tests/fixtures/products-2026-11-08.html, 할인 상품 PW-108 판매가 65,600원·정가 69,000원), 8~14일차 다시 모음
- 다음에 볼 것: 할인 상품은 `card__price` 안에 숫자가 두 개예요. 첫 숫자는 정가라서 판매가로 읽으면 안 돼요.
- 걸린 시간: (실제로 잰 시간을 적어요. 이 예시는 재지 않았어요.)

## 2026-11-15 · 화면을 JavaScript가 그리고 데이터는 스크립트 안 JSON (B → C)
- 증상: 15일차에 "상품을 0건 찾았어요", 종료 코드 2
- 원인: HTML에는 "상품을 불러오는 중..."만 있고 카드가 없어요. 데이터는 `<script id="__SHOP_STATE__" type="application/json">` 안에 있어요. 키 이름도 바뀌었어요(code, label, group, pricing.current, pricing.regular). 가격이 "원" 없는 숫자예요.
- 고친 곳: `parse_state_c` 추가, `PARSERS = [parse_state_c, parse_cards_b, parse_list_a]`
- 확인: tests/test_layout_c.py (스냅숏 products-2026-11-15.html, 할인 상품 PW-101 56,600원·59,600원), 15~22일차 다시 모음
- 다음에 볼 것: 브라우저 화면만 보면 카드가 보여서 HTML에 있다고 착각하기 쉬워요. curl 결과나 스냅숏에서 찾아요.
- 걸린 시간: (실제로 잰 시간을 적어요.) B 기록의 "새 파서를 맨 앞에, 테스트는 새 파일" 순서를 그대로 따랐어요.

## 2026-11-23 · 빈 껍데기와 JSON API (C → D)
- 증상: 23일차에 "상품을 0건 찾았어요", 종료 코드 2
- 원인: HTML에는 `<div id="app">`과 `/static/app-d.js`만 있어요. app-d.js가 `/api/catalog?page=N`을 `next`가 null일 때까지 불러요. 한 쪽에 5개씩 2쪽이에요.
- 고친 곳: `is_app_shell_d`, `fetch_catalog_d` 추가, `collect_products`에서 파서가 0건이고 빈 껍데기면 API를 읽게 함
- 확인: tests/test_layout_d.py (스냅숏 products-2026-11-23.html, catalog-2026-11-23-p1.json, -p2.json), 23~30일차 다시 모음
- 다음에 볼 것: 2쪽 첫 요청은 날마다 429가 와요. collect.py의 Fetcher가 Retry-After 1초를 기다렸다가 다시 보내요(요청 4번 중 재시도 1번). 화면 JavaScript를 실행하지 말고 API를 바로 읽어요.
- 걸린 시간: (실제로 잰 시간을 적어요.)
