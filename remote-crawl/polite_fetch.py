"""test-server(교육용 원격 서버)의 "입문 키보드" 값을 예의 있게 한 번 모아요.

  python3 polite_fetch.py                   # JSON 길(/api/price)로 한 번
  python3 polite_fetch.py --route html      # 정적 HTML 길(/)로 한 번
  python3 polite_fetch.py --shop            # 원격이 막혔을 때: 내 PC의 연습몰(127.0.0.1:8766)로 한 번

한 번 실행하면 한 번만 물어요. 지난 요청에서 60초가 지나지 않았으면 묻지 않고 저장해 둔 값을 보여 줘요(캐시).
401, 403, 429나 차단 화면을 받으면 다시 두드리지 않고 멈춘 다음 data/incidents.md에 적어요.
파이썬 표준 라이브러리만 써요.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent

# ---------------- 내 것으로 바꿀 곳 ----------------
NAME = "DBInc-training/1.0"   # 나를 밝히는 이름(User-Agent). 예: DBInc-3jo/1.0
ROUTE = "json"                # 기본으로 읽을 길: json 또는 html
MIN_GAP_SECONDS = 60          # 다시 묻기 전에 기다릴 시간(초). 60보다 줄이지 않아요.
# ---------------------------------------------------

BASE = "https://test-server-8az.pages.dev"
SHOP = "http://127.0.0.1:8766"
ROUTES = {"json": "/api/price", "html": "/", "shop": "/products"}
ALLOWED_HOSTS = {"test-server-8az.pages.dev", "127.0.0.1", "localhost"}
STOP_STATUS = {401, 403, 429}
BLOCK_WORDS = ("ip_blocked", "turnstile_required", "session_required", "접속이 차단되었습니다")
FIELDS = ["fetched_at", "route", "name", "price", "stock", "updated_at", "source_url", "user_agent"]
SHOP_SKU = "PW-101"

DATA = ROOT / "data"
STATE = ROOT / ".runtime" / "state.json"


class Stop(Exception):
    """더 묻지 않고 멈춰야 할 때 내는 오류예요. code는 종료 코드예요."""

    def __init__(self, message: str, code: int = 1):
        super().__init__(message)
        self.code = code


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def ensure_allowed(url: str) -> str:
    host = (urlsplit(url).hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise Stop(f"test-server와 내 PC 말고 다른 주소({host})에는 요청하지 않아요.")
    if any(part in urlsplit(url).path for part in ("/admin", "/api/turnstile")):
        raise Stop("관리자 주소와 검증 주소는 부르지 않아요.")
    return url


def get(url: str, name: str) -> tuple[int, dict, str]:
    """요청을 한 번 보내요. 다시 보내지 않아요."""
    request = Request(ensure_allowed(url), headers={"User-Agent": name, "Accept": "*/*"})
    try:
        with urlopen(request, timeout=10) as response:
            return response.status, dict(response.headers), response.read(500_000).decode("utf-8", "replace")
    except HTTPError as error:
        body = error.read(20_000).decode("utf-8", "replace")
        headers = dict(error.headers)
        error.close()
        return error.code, headers, body
    except URLError as error:
        raise Stop(f"연결하지 못했어요: {url} ({error.reason}). 내부망에서 막혔을 수 있어요. README의 막히면을 봐요.") from error


# ---------------------------------------------------------------- 기록

def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def record_incident(route: str, status: int, url: str, note: str) -> None:
    DATA.mkdir(exist_ok=True)
    path = DATA / "incidents.md"
    if not path.exists():
        path.write_text("# 막힌 기록\n\n형식: `- 시각 · 길 · 상태 · 주소 · 한 일`\n\n", encoding="utf-8")
    stamp = now_utc().isoformat(timespec="seconds")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"- {stamp} · {route} · {status} · {url} · {note}\n")


def append_row(row: dict) -> bool:
    """data/live-prices.csv에 한 줄 덧붙여요. 같은 길에서 같은 시각 값이면 다시 저장하지 않아요."""
    DATA.mkdir(exist_ok=True)
    path = DATA / "live-prices.csv"
    rows = []
    if path.exists():
        with path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    same = [r for r in rows if r["route"] == row["route"]]
    if row["updated_at"] and same and same[-1]["updated_at"] == row["updated_at"]:
        return False
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)
    return True


# ---------------------------------------------------------------- 읽기

def digits(text: str) -> int:
    found = re.sub(r"[^0-9]", "", text or "")
    if not found:
        raise ValueError(f"숫자를 찾지 못했어요: {text!r}")
    return int(found)


def parse_json(text: str) -> dict:
    data = json.loads(text)
    return {"name": data["name"], "price": int(data["price"]), "stock": int(data["stock"]),
            "updated_at": data.get("updated_at", ""), "next_update_at": data.get("next_update_at", "")}


class _Home(HTMLParser):
    """정적 HTML: #priceTarget(가격), #stockTarget(재고), .product-title(이름)"""

    def __init__(self):
        super().__init__()
        self.field, self.found = None, {"name": "", "price": "", "stock": ""}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if a.get("id") == "priceTarget":
            self.field = "price"
        elif a.get("id") == "stockTarget":
            self.field = "stock"
        elif "product-title" in classes:
            self.field = "name"

    def handle_data(self, data):
        if self.field:
            self.found[self.field] += data

    def handle_endtag(self, tag):
        self.field = None


def parse_html(text: str) -> dict:
    parser = _Home()
    parser.feed(text)
    found = parser.found
    if not found["price"]:
        raise ValueError("HTML에서 #priceTarget을 찾지 못했어요. 구조가 바뀌었을 수 있어요.")
    return {"name": found["name"].strip(), "price": digits(found["price"]), "stock": digits(found["stock"]),
            "updated_at": "", "next_update_at": ""}


class _ShopA(HTMLParser):
    """연습몰 1~7일 구조: <li class="product" data-sku=...> 안의 span.name, span.price"""

    def __init__(self, sku: str):
        super().__init__()
        self.sku, self.inside, self.field = sku, False, None
        self.found = {"name": "", "price": ""}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "li" and "product" in classes:
            self.inside = a.get("data-sku") == self.sku
        elif self.inside and tag == "span" and ("name" in classes or "price" in classes):
            self.field = "name" if "name" in classes else "price"

    def handle_data(self, data):
        if self.inside and self.field:
            self.found[self.field] += data

    def handle_endtag(self, tag):
        if tag == "span":
            self.field = None
        if tag == "li":
            self.inside = False


def parse_shop(text: str, sku: str = SHOP_SKU) -> dict:
    parser = _ShopA(sku)
    parser.feed(text)
    if not parser.found["price"]:
        raise ValueError(f"연습몰에서 {sku}를 찾지 못했어요. 이 예시는 1~7일 구조만 읽어요.")
    return {"name": parser.found["name"].strip(), "price": digits(parser.found["price"]), "stock": "",
            "updated_at": "", "next_update_at": ""}


PARSERS = {"json": parse_json, "html": parse_html, "shop": parse_shop}


def is_blocked(status: int, body: str) -> bool:
    return status in STOP_STATUS or any(word in body for word in BLOCK_WORDS)


# ---------------------------------------------------------------- robots.txt

def robots_rules(base: str, name: str, state: dict, target: dict) -> dict:
    """robots.txt는 하루에 한 번만 읽어요. 그 대상의 규칙(막은 주소, 간격)을 돌려줘요."""
    seen = state.setdefault("robots", {}).get(base)
    if seen and time.time() - seen["checked_at"] < 24 * 3600:
        return seen
    status, headers, body = get(base + "/robots.txt", name)
    target["last_request_at"] = time.time()
    kind = next((v for k, v in headers.items() if k.lower() == "content-type"), "")
    rule = {"checked_at": time.time(), "found": False, "disallow": [], "delay": 1.0}
    if status == 200 and kind.startswith("text/plain"):
        rule["found"] = True
        applies = False
        for line in body.splitlines():
            key, _, value = line.partition(":")
            key, value = key.strip().lower(), value.strip()
            if key == "user-agent":
                applies = value == "*" or value.lower() in name.lower()
            elif applies and key == "disallow" and value:
                rule["disallow"].append(value)
            elif applies and key == "crawl-delay":
                try:
                    rule["delay"] = max(1.0, float(value))
                except ValueError:
                    pass
        print(f"robots.txt: 막은 주소 {len(rule['disallow'])}개, 간격 {rule['delay']:.0f}초를 지켜요.")
    else:
        print("robots.txt: 규칙 파일이 없어요(받은 것이 글자 규칙이 아니에요). 없다고 마음대로 해도 된다는 뜻은 아니에요.")
    state["robots"][base] = rule
    return rule


# ---------------------------------------------------------------- 실행

def run(route: str, name: str, base: str) -> int:
    state = load_state()
    target = state.setdefault("targets", {}).setdefault(base, {})
    gap = max(MIN_GAP_SECONDS, 60)
    left = target.get("blocked_until", 0) - time.time()
    if left > 0:
        print(f"아직 기다려요. 상대가 기다리라고 한 시간이 {left:.0f}초 남았어요. 지금은 묻지 않아요.")
        return 2
    since = time.time() - target.get("last_request_at", 0)
    if since < gap:
        last = target.get("last_result")
        if last:
            print(f"캐시: 지난 요청이 {since:.0f}초 전이라 묻지 않았어요. 마지막 값 {last['name']} {last['price']:,}원"
                  f" · {gap - since:.0f}초 뒤에 다시 물을 수 있어요.")
            return 0
        print(f"지난 요청이 {since:.0f}초 전이라 아직 묻지 않아요. {gap - since:.0f}초 뒤에 다시 해요.")
        return 2
    path = ROUTES[route]
    url = base + path
    rule = robots_rules(base, name, state, target)
    if any(path.startswith(blocked) for blocked in rule["disallow"]):
        save_state(state)
        raise Stop(f"robots.txt가 막은 주소라서 {path}는 부르지 않아요.")
    if target.get("last_request_at") and time.time() - target["last_request_at"] < rule["delay"]:
        time.sleep(rule["delay"])
    status, headers, body = get(url, name)
    target["last_request_at"] = time.time()
    if is_blocked(status, body):
        retry = next((v for k, v in headers.items() if k.lower() == "retry-after"), "")
        wait = int(retry) if retry.isdigit() else 60
        target["blocked_until"] = time.time() + wait
        save_state(state)
        record_incident(route, status, url, f"멈췄어요. {wait}초 동안 다시 묻지 않아요.")
        print(f"막혔어요({status}). 다시 두드리지 않고 멈춰요. data/incidents.md에 적었어요.")
        return 2
    if status != 200:
        save_state(state)
        record_incident(route, status, url, "200이 아니라서 멈췄어요.")
        raise Stop(f"{status} 응답이에요: {url}")
    try:
        item = PARSERS[route](body)
    except (ValueError, KeyError) as error:
        snap = ROOT / ".runtime" / "snapshots" / f"{route}-{now_utc():%Y%m%dT%H%M%S}.txt"
        snap.parent.mkdir(parents=True, exist_ok=True)
        snap.write_text(body, encoding="utf-8")
        save_state(state)
        where = snap.relative_to(ROOT).as_posix()
        record_incident(route, status, url, f"읽지 못했어요. 받은 것을 {where}에 저장했어요.")
        raise Stop(f"{error} 받은 것: {where}") from error
    row = {"fetched_at": now_utc().isoformat(timespec="seconds"), "route": route, "name": item["name"],
           "price": item["price"], "stock": item["stock"], "updated_at": item["updated_at"],
           "source_url": url, "user_agent": name}
    saved = append_row(row)
    target["last_result"] = {"name": item["name"], "price": item["price"]}
    save_state(state)
    stock = f" · 재고 {item['stock']}개" if item["stock"] != "" else ""
    note = "data/live-prices.csv에 한 줄 더했어요" if saved else "같은 시각 값이라 다시 저장하지 않았어요"
    print(f"[{route}] {item['name']} {item['price']:,}원{stock} · {note}")
    if item["next_update_at"]:
        print(f"다음 값은 {item['next_update_at']}(UTC)에 나와요. 그 전에는 다시 묻지 않아요.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--route", choices=["json", "html"], default=ROUTE)
    parser.add_argument("--shop", action="store_true", help="원격이 막혔을 때 내 PC 연습몰에서 PW-101 하나를 읽어요")
    parser.add_argument("--name", default=NAME, help="User-Agent로 보낼 내 이름")
    args = parser.parse_args(argv)
    if args.name == "DBInc-training/1.0":
        print("알림: 내 이름을 정해요. polite_fetch.py 위쪽 NAME이나 --name DBInc-3jo/1.0 처럼요.")
    route, base = ("shop", SHOP) if args.shop else (args.route, BASE)
    try:
        return run(route, args.name, base)
    except Stop as error:
        print(f"멈췄어요: {error}", file=sys.stderr)
        return error.code


if __name__ == "__main__":
    sys.exit(main())
