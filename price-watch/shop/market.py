"""연습몰(교육용 가상 쇼핑몰)의 상품, 가격, 소식, 페이지 구조를 날짜별로 만들어요.

모든 값은 시드를 고정한 계산 결과라서 같은 날짜에는 언제나 같은 페이지가 나와요.
상품, 가격, 회사 이름, 소식은 모두 수업을 위해 지어낸 것이에요. 실제 상품과 가격이 아니에요.
"""
from __future__ import annotations

import html
import json
import random
import re
from datetime import date, timedelta

SEED = 20261101
START = date(2026, 11, 1)
MAX_DAY = 30

# 페이지 구조가 바뀌는 날이에요. 8일, 15일, 23일에 바뀌어요.
LAYOUTS = [(1, "A"), (8, "B"), (15, "C"), (23, "D")]

# (상품 코드, 이름, 분류, 처음 정가)
PRODUCTS = [
    ("PW-101", "무선 이어폰 A1", "오디오", 59000),
    ("PW-102", "블루투스 스피커 S2", "오디오", 45000),
    ("PW-103", "보조배터리 10000", "전원", 29900),
    ("PW-104", "고속 충전기 65W", "전원", 39000),
    ("PW-105", "기계식 키보드 K87", "입력", 89000),
    ("PW-106", "무선 마우스 M3", "입력", 32000),
    ("PW-107", "USB-C 허브 7in1", "연결", 49000),
    ("PW-108", "웹캠 FHD", "영상", 69000),
    ("PW-109", "모니터암 싱글", "사무", 79000),
    ("PW-110", "노트북 거치대", "사무", 35000),
]

# 가상 소식이에요. 일부 소식은 며칠 뒤 가격 변화와 관계가 있어요(예측 연습용).
NEWS = [
    (1, "연습몰 공지", "연습몰 11월 가격 안내 페이지를 새로 열었어요", "상품 목록 페이지에서 매일 바뀌는 판매가와 정가를 함께 보여 줘요.", ["공지"]),
    (3, "가상 경제신문", "배터리 셀 원가 오름세, 충전기·보조배터리 값 영향 전망", "부품 원가가 몇 주째 오르고 있어 전원 기기 판매가가 조금씩 오를 수 있다는 전망이 나왔어요.", ["원가", "전원"]),
    (5, "가상 경제신문", "가상 물류센터 확장, 배송일 하루 단축 기대", "수도권 물류센터가 넓어져 배송이 빨라질 것으로 보여요.", ["물류"]),
    (9, "이웃몰 공지", "이웃몰 11월 12~14일 오디오 기획전 예고", "이웃몰이 이어폰과 스피커를 사흘 동안 할인한다고 알렸어요.", ["경쟁사행사", "오디오"]),
    (12, "가상 경제신문", "주요 쇼핑몰 카드 무이자 할부 행사 이어져", "연말을 앞두고 여러 쇼핑몰이 무이자 할부 기간을 늘렸어요.", ["결제"]),
    (16, "가상 경제신문", "환율 부담 커져 수입 주변기기 값 오를 듯", "수입 비중이 큰 허브와 웹캠 같은 주변기기 판매가가 오를 수 있어요.", ["환율", "연결", "영상"]),
    (20, "이웃몰 공지", "이웃몰 11월 25~27일 입력기기 특가 예고", "이웃몰이 키보드와 마우스를 사흘 동안 할인한다고 알렸어요.", ["경쟁사행사", "입력"]),
    (22, "가상 경제신문", "연말 성수기 앞두고 택배 물량 늘어", "택배 물량이 늘어 일부 지역 배송이 늦어질 수 있어요.", ["물류"]),
    (24, "가상 업계소식", "모니터암 신모델 출시 예고, 기존 모델 정리 할인 가능성", "새 모델이 나오면 기존 모델 값이 조금씩 내려갈 수 있어요.", ["신제품", "사무"]),
    (28, "이웃몰 공지", "이웃몰 12월 3~5일 전원기기 기획전 예고", "이웃몰이 충전기와 보조배터리를 사흘 동안 할인한다고 알렸어요.", ["경쟁사행사", "전원"]),
]


def day_date(day: int) -> date:
    return START + timedelta(days=day - 1)


def check_day(day: int) -> int:
    if not isinstance(day, int) or not 1 <= day <= MAX_DAY:
        raise ValueError(f"day는 1~{MAX_DAY} 사이 정수여야 해요")
    return day


def layout_for(day: int) -> str:
    current = "A"
    for first, name in LAYOUTS:
        if day >= first:
            current = name
    return current


def round100(value: float) -> int:
    return int(round(value / 100.0)) * 100


def _adjustments():
    """추세가 없는 상품에 생기는 작은 가격 조정(오르거나 내리고 그대로 남아요)."""
    rng = random.Random(SEED)
    plain = ["PW-101", "PW-102", "PW-105", "PW-106", "PW-110"]
    result = {}
    for _ in range(6):
        sku = rng.choice(plain)
        day = rng.randint(4, 29)
        pct = rng.choice([-3, -2, -1, 1, 2, 3])
        result.setdefault(sku, []).append((day, pct))
    return result


ADJUSTMENTS = _adjustments()


def _deal_of_day(day: int) -> str:
    """오늘의 특가 상품 하나(5% 할인). 행사 중인 상품은 고르지 않아요."""
    rng = random.Random(SEED * 31 + day)
    candidates = [sku for sku, *_ in PRODUCTS if _promo_pct(sku, day) == 0]
    return rng.choice(candidates)


def _promo_pct(sku: str, day: int) -> int:
    category = next(c for s, _, c, _ in PRODUCTS if s == sku)
    if category == "오디오" and 12 <= day <= 14:
        return 12
    if category == "입력" and 25 <= day <= 27:
        return 10
    return 0


def list_price(sku: str, day: int) -> int:
    base = next(p for s, _, _, p in PRODUCTS if s == sku)
    category = next(c for s, _, c, _ in PRODUCTS if s == sku)
    factor = 1.0
    if category == "전원" and day >= 6:
        factor *= 1.02 ** ((day - 6) // 4 + 1)
    if category in ("연결", "영상") and day >= 19:
        factor *= 1.05
    if sku == "PW-109" and day >= 26:
        factor *= 0.985 ** ((day - 26) // 2 + 1)
    for when, pct in ADJUSTMENTS.get(sku, []):
        if day >= when:
            factor *= 1 + pct / 100
    return round100(base * factor)


def sale_price(sku: str, day: int) -> int:
    price = list_price(sku, day)
    promo = _promo_pct(sku, day)
    if promo:
        return round100(price * (1 - promo / 100))
    if _deal_of_day(day) == sku:
        return round100(price * 0.95)
    return price


def catalog(day: int) -> list[dict]:
    check_day(day)
    deal = _deal_of_day(day)
    rows = []
    for sku, name, category, _ in PRODUCTS:
        rows.append({
            "sku": sku,
            "name": name,
            "category": category,
            "price": sale_price(sku, day),
            "list_price": list_price(sku, day),
            "deal": sku == deal,
            "promo": _promo_pct(sku, day) > 0,
        })
    return rows


def news_until(day: int) -> list[dict]:
    check_day(day)
    items = []
    for n, (when, source, title, body, tags) in enumerate(NEWS, start=1):
        if when <= day:
            items.append({
                "id": f"N-{when:02d}{n:02d}",
                "date": day_date(when).isoformat(),
                "source": source,
                "title": title,
                "body": body,
                "tags": tags,
            })
    return items


# ---------------------------------------------------------------- 페이지 만들기

NOTICE = "교육용 가상 쇼핑몰 · 실제 상품과 가격이 아니에요"


def won(value: int) -> str:
    return f"{value:,}원"


def _page(title: str, body: str, day: int, scripts: str = "") -> str:
    d = day_date(day).isoformat()
    return (
        "<!doctype html>\n<html lang=\"ko\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{html.escape(title)}</title>\n<link rel=\"stylesheet\" href=\"/static/shop.css\">\n</head>\n<body>\n"
        f"<p class=\"notice\">{NOTICE}</p>\n"
        "<nav><a href=\"/\">연습몰</a> · <a href=\"/products\">상품</a> · <a href=\"/news\">소식</a> · <a href=\"/terms\">이용약관</a></nav>\n"
        f"<p class=\"today\">오늘 {d}</p>\n{body}\n{scripts}</body>\n</html>\n"
    )


def products_page(day: int) -> str:
    layout = layout_for(day)
    items = catalog(day)
    if layout == "A":
        lines = ["<h1>상품 목록</h1>", "<ul class=\"product-list\">"]
        for it in items:
            badge = " <span class=\"badge\">오늘의 특가</span>" if it["deal"] else ""
            badge += " <span class=\"badge\">기획전</span>" if it["promo"] else ""
            old = f" <s class=\"list-price\">{won(it['list_price'])}</s>" if it["price"] < it["list_price"] else ""
            lines.append(
                f"  <li class=\"product\" data-sku=\"{it['sku']}\" data-category=\"{html.escape(it['category'])}\">\n"
                f"    <span class=\"name\">{html.escape(it['name'])}</span>\n"
                f"    <span class=\"price\">{won(it['price'])}</span>{old}{badge}\n"
                "  </li>"
            )
        lines.append("</ul>")
        return _page("연습몰 · 상품 목록", "\n".join(lines), day)
    if layout == "B":
        lines = ["<h1>오늘의 상품</h1>", "<section class=\"grid\">"]
        for it in items:
            tag = "<span class=\"card__tag\">오늘의 특가</span>" if it["deal"] else ""
            tag += "<span class=\"card__tag\">기획전</span>" if it["promo"] else ""
            if it["price"] < it["list_price"]:
                price = f"<del>{won(it['list_price'])}</del> <strong>{won(it['price'])}</strong>"
            else:
                price = f"<strong>{won(it['price'])}</strong>"
            lines.append(
                f"  <article class=\"card\" data-item-id=\"{it['sku']}\">\n"
                f"    <p class=\"card__cat\">{html.escape(it['category'])}</p>\n"
                f"    <h3 class=\"card__title\">{html.escape(it['name'])}</h3>\n"
                f"    <div class=\"card__price\">{price}</div>{tag}\n"
                "  </article>"
            )
        lines.append("</section>")
        return _page("연습몰 · 오늘의 상품", "\n".join(lines), day)
    if layout == "C":
        state = {
            "date": day_date(day).isoformat(),
            "products": [
                {"code": it["sku"], "label": it["name"], "group": it["category"],
                 "pricing": {"current": it["price"], "regular": it["list_price"]},
                 "flags": (["deal"] if it["deal"] else []) + (["promo"] if it["promo"] else [])}
                for it in items
            ],
        }
        raw = json.dumps(state, ensure_ascii=False).replace("</", "<\\/")
        body = "<h1>오늘의 상품</h1>\n<div id=\"list\" class=\"loading\">상품을 불러오는 중...</div>"
        scripts = (f"<script id=\"__SHOP_STATE__\" type=\"application/json\">{raw}</script>\n"
                   "<script src=\"/static/render-c.js\"></script>\n")
        return _page("연습몰 · 오늘의 상품", body, day, scripts)
    body = "<h1>오늘의 상품</h1>\n<div id=\"app\" data-version=\"4\">상품을 불러오는 중...</div>"
    return _page("연습몰 · 오늘의 상품", body, day, "<script src=\"/static/app-d.js\"></script>\n")


PAGE_SIZE = 5


def catalog_api(day: int, page: int) -> dict | None:
    """D 구조(23일부터)에서 화면이 부르는 JSON API예요. 그 전에는 없어요(None)."""
    if layout_for(day) != "D":
        return None
    items = catalog(day)
    pages = (len(items) + PAGE_SIZE - 1) // PAGE_SIZE
    if not 1 <= page <= pages:
        return {"synthetic": True, "date": day_date(day).isoformat(), "page": page, "next": None, "items": []}
    chunk = items[(page - 1) * PAGE_SIZE: page * PAGE_SIZE]
    return {
        "synthetic": True,
        "date": day_date(day).isoformat(),
        "page": page,
        "next": page + 1 if page < pages else None,
        "items": [
            {"sku": it["sku"], "title": it["name"], "category": it["category"],
             "price": {"amount": it["price"], "list": it["list_price"], "currency": "KRW"}}
            for it in chunk
        ],
    }


def news_page(day: int) -> str:
    lines = ["<h1>소식</h1>", "<div class=\"news-list\">"]
    for it in reversed(news_until(day)):
        lines.append(
            f"  <article class=\"news\" data-id=\"{it['id']}\" data-date=\"{it['date']}\">\n"
            f"    <h2>{html.escape(it['title'])}</h2>\n"
            f"    <p class=\"meta\">{it['date']} · {html.escape(it['source'])}</p>\n"
            f"    <p>{html.escape(it['body'])}</p>\n  </article>"
        )
    lines.append("</div>")
    return _page("연습몰 · 소식", "\n".join(lines), day)


def home_page(day: int) -> str:
    body = (
        "<h1>연습몰</h1>\n"
        "<p>수업에서 가격 수집을 연습하는 가상 쇼핑몰이에요. 판매가는 매일 바뀌고, 상품 페이지 구조도 가끔 바뀌어요.</p>\n"
        "<ul><li><a href=\"/products\">상품 목록</a></li><li><a href=\"/news\">소식</a></li>"
        "<li><a href=\"/terms\">이용약관</a></li><li><a href=\"/robots.txt\">robots.txt</a></li></ul>"
    )
    return _page("연습몰", body, day)


def terms_page(day: int) -> str:
    body = (
        "<h1>이용약관(교육용)</h1>\n<ol>\n"
        "<li>이 사이트는 수업 연습용 가상 쇼핑몰이에요. 실제 거래는 없어요.</li>\n"
        "<li>자동 수집은 교육 목적에서만 허용해요.</li>\n"
        "<li>자동 수집기는 1초에 한 번보다 자주 요청하지 않아요.</li>\n"
        "<li>/admin 아래 주소는 수업 진행용이라 자동 수집기가 부르면 안 돼요.</li>\n"
        "<li>수집기는 User-Agent 헤더에 이름을 밝혀요.</li>\n</ol>"
    )
    return _page("연습몰 · 이용약관", body, day)


ROBOTS = """# 연습몰(교육용 가상 사이트) 수집 규칙
User-agent: *
Disallow: /admin
Crawl-delay: 1
"""

PROMO_RANGE = re.compile(r"(\d{1,2})월 (\d{1,2})~(\d{1,2})일")
