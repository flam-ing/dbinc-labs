"""연습몰(교육용 가상 쇼핑몰)의 오늘 가격과 소식을 모아 지식베이스(kb/)에 쌓아요.

  python3 collect.py                       # http://127.0.0.1:8766 에서 오늘 것을 모아요
  python3 collect.py --json                # 결과를 JSON으로 보여 줘요

내 컴퓨터 안의 연습몰(127.0.0.1, localhost)만 읽어요. 실제 사이트에는 요청하지 않아요.
페이지 구조가 바뀌어 상품을 찾지 못하면 조용히 0건을 저장하지 않고, 받은 페이지를
.runtime/snapshots/에 저장한 다음 종료 코드 2로 멈춰요.
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
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parent
BASE_URL = "http://127.0.0.1:8766"
USER_AGENT = "DBIncPriceWatch/1.0 (training)"
DELAY_SECONDS = 1.0          # 연습몰 robots.txt의 Crawl-delay와 이용약관 3항
MAX_RETRY_WAIT = 5.0         # Retry-After가 이보다 길면 기다리지 않고 멈춰요
RETRYABLE = {429, 500, 502, 503, 504}
MAX_DAILY_CHANGE = 0.5       # 하루에 50% 넘게 바뀐 가격은 파싱 오류로 봐요
PRICE_FIELDS = ["date", "sku", "name", "category", "price", "list_price", "source_url", "fetched_at", "parser"]
SKU = re.compile(r"^PW-\d{3}$")


class CollectError(Exception):
    """수집을 멈춰야 하는 오류예요. 종료 코드 1이에요."""


class LayoutChanged(CollectError):
    """페이지 구조가 바뀐 것 같을 때 내는 오류예요. 종료 코드 2예요."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = build_opener(NoRedirect)


def ensure_local(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme != "http" or parts.hostname not in ("127.0.0.1", "localhost") or parts.username:
        raise CollectError(f"연습몰(http://127.0.0.1 또는 localhost)만 읽어요: {url}")
    if parts.path.startswith("/admin"):
        raise CollectError("/admin은 수업 진행용 주소라서 수집기가 부르지 않아요.")
    return url


class Fetcher:
    """요청 간격을 지키고, 일시적인 실패는 Retry-After만큼 기다렸다가 다시 보내요."""

    def __init__(self, base_url: str, sleep=time.sleep, delay: float = DELAY_SECONDS, attempts: int = 3,
                 state: Path | None = None):
        self.base_url = ensure_local(base_url.rstrip("/"))
        self.sleep = sleep
        self.delay = delay
        self.attempts = attempts
        # 마지막 요청 시각을 파일에 적어 두면, collect.py를 연달아 실행해도 간격을 지켜요.
        self.state = state
        self.last = None
        if state and state.exists():
            try:
                self.last = float(state.read_text())
            except ValueError:
                self.last = None
        self.trace = []
        self.headers = {}

    def _wait_turn(self):
        if self.last is not None:
            gap = time.time() - self.last
            if 0 <= gap < self.delay:
                self.sleep(self.delay - gap)

    def get(self, path: str):
        url = ensure_local(urljoin(self.base_url + "/", path.lstrip("/")))
        for attempt in range(1, self.attempts + 1):
            self._wait_turn()
            self.last = time.time()
            if self.state:
                self.state.parent.mkdir(parents=True, exist_ok=True)
                self.state.write_text(str(self.last))
            entry = {"url": url, "attempt": attempt, "status": None}
            self.trace.append(entry)
            try:
                request = Request(url, headers={"User-Agent": USER_AGENT})
                with OPENER.open(request, timeout=5) as response:
                    body = response.read(2_000_001)
                    if len(body) > 2_000_000:
                        raise CollectError("응답이 2MB를 넘었어요.")
                    entry["status"] = response.status
                    self.headers = dict(response.headers)
                    return body.decode("utf-8"), self.headers
            except HTTPError as error:
                entry["status"] = error.code
                retry = error.headers.get("Retry-After")
                error.close()
                if error.code not in RETRYABLE or attempt == self.attempts:
                    raise CollectError(f"{error.code} 응답: {url} ({attempt}번 시도)") from error
                wait = float(retry) if retry and retry.isdigit() else 0.5 * 2 ** (attempt - 1)
                if wait > MAX_RETRY_WAIT:
                    raise CollectError(f"{wait:.0f}초를 기다리라고 해서 멈춰요: {url}") from error
                entry["retry_after"] = wait
                self.sleep(wait)
            except URLError as error:
                raise CollectError(f"연습몰에 연결하지 못했어요: {url} ({error.reason}). 서버를 켰는지 확인해요.") from error
        raise CollectError(f"요청 실패: {url}")


# ---------------------------------------------------------------- 파서

def parse_won(text: str) -> int:
    """"59,000원" 같은 글자를 59000으로 바꿔요."""
    digits = re.sub(r"[^0-9]", "", text or "")
    if not digits:
        raise ValueError(f"가격 숫자를 찾지 못했어요: {text!r}")
    return int(digits)


class _ListA(HTMLParser):
    """A 구조: <li class="product" data-sku=...> 안의 span.name, span.price, s.list-price"""

    def __init__(self):
        super().__init__()
        self.items, self.item, self.field = [], None, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "li" and "product" in classes and a.get("data-sku"):
            self.item = {"sku": a["data-sku"], "category": a.get("data-category", ""), "name": "", "price": "", "list_price": ""}
        elif self.item is not None and tag == "span" and "name" in classes:
            self.field = "name"
        elif self.item is not None and tag == "span" and "price" in classes:
            self.field = "price"
        elif self.item is not None and tag == "s" and "list-price" in classes:
            self.field = "list_price"

    def handle_data(self, data):
        if self.item is not None and self.field:
            self.item[self.field] += data

    def handle_endtag(self, tag):
        if tag in ("span", "s"):
            self.field = None
        if tag == "li" and self.item is not None:
            self.items.append(self.item)
            self.item = None


def parse_list_a(html: str) -> list[dict]:
    parser = _ListA()
    parser.feed(html)
    rows = []
    for it in parser.items:
        price = parse_won(it["price"])
        rows.append({
            "sku": it["sku"].strip(),
            "name": it["name"].strip(),
            "category": it["category"].strip(),
            "price": price,
            "list_price": parse_won(it["list_price"]) if it["list_price"].strip() else price,
        })
    return rows


# 구조가 바뀌면 새 파서를 맨 앞에 더해요. 예전 파서는 지우지 않아요.
# 예전 스냅숏으로 만든 테스트가 계속 통과해야 하기 때문이에요.
PARSERS = [parse_list_a]


def parse_products(html: str):
    """PARSERS를 차례로 써 보고 상품을 찾은 첫 파서의 이름과 결과를 돌려줘요."""
    for parser in PARSERS:
        items = parser(html)
        if items:
            return parser.__name__, items
    return None, []


# ---------------------------------------------------------------- 검사와 저장

def last_prices(kb: Path) -> tuple[str | None, dict]:
    path = kb / "prices.csv"
    if not path.exists():
        return None, {}
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None, {}
    last_date = max(r["date"] for r in rows)
    return last_date, {r["sku"]: int(r["price"]) for r in rows if r["date"] == last_date}


def validate(items: list[dict], previous: dict) -> None:
    seen = set()
    for it in items:
        if not SKU.match(it["sku"]):
            raise LayoutChanged(f"상품 코드 모양이 이상해요: {it['sku']!r}")
        if it["sku"] in seen:
            raise CollectError(f"같은 상품이 두 번 나왔어요: {it['sku']}")
        seen.add(it["sku"])
        if not it["name"]:
            raise LayoutChanged(f"{it['sku']}의 이름이 비어 있어요.")
        if it["price"] <= 0 or it["list_price"] < it["price"]:
            raise LayoutChanged(f"{it['sku']} 가격이 이상해요: 판매가 {it['price']}, 정가 {it['list_price']}")
        before = previous.get(it["sku"])
        if before and abs(it["price"] - before) / before > MAX_DAILY_CHANGE:
            raise LayoutChanged(f"{it['sku']} 가격이 하루에 50% 넘게 바뀌었어요({before} → {it['price']}). 엉뚱한 숫자를 읽었을 수 있어요.")
    if previous and len(items) < 0.8 * len(previous):
        raise LayoutChanged(f"상품이 {len(items)}건이에요. 지난번 {len(previous)}건보다 많이 줄었어요.")


def append_prices(kb: Path, date: str, items, url: str, fetched_at: str, parser: str) -> int:
    path = kb / "prices.csv"
    existing = set()
    if path.exists():
        with path.open(encoding="utf-8", newline="") as f:
            existing = {(r["date"], r["sku"]) for r in csv.DictReader(f)}
    new = [it for it in items if (date, it["sku"]) not in existing]
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PRICE_FIELDS)
        if write_header:
            writer.writeheader()
        for it in new:
            writer.writerow({"date": date, "sku": it["sku"], "name": it["name"], "category": it["category"],
                             "price": it["price"], "list_price": it["list_price"], "source_url": url,
                             "fetched_at": fetched_at, "parser": parser})
    return len(new)


def append_news(kb: Path, items) -> int:
    path = kb / "news.jsonl"
    seen = set()
    if path.exists():
        seen = {json.loads(line)["id"] for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}
    new = [it for it in items if it["id"] not in seen]
    with path.open("a", encoding="utf-8") as f:
        for it in new:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    return len(new)


def log_run(kb: Path, record: dict) -> None:
    with (kb / "runs.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def save_snapshot(root: Path, date: str, name: str, body: str) -> Path:
    """받은 페이지를 .runtime/snapshots/<name>-<date>.html로 저장해요. 테스트 스냅숏과 같은 이름 규칙이에요."""
    folder = root / ".runtime" / "snapshots"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}-{date}.html"
    path.write_text(body, encoding="utf-8")
    return path


# ---------------------------------------------------------------- 수집

def collect_products(fetcher: Fetcher, root: Path, previous: dict):
    html, headers = fetcher.get("/products")
    date = headers.get("X-Sim-Date") or datetime.now().date().isoformat()
    parser, items = parse_products(html)
    if not items:
        snap = save_snapshot(root, date, "products", html)
        raise LayoutChanged(
            f"상품을 0건 찾았어요. 페이지 구조가 바뀌었을 수 있어요.\n"
            f"- 지금 파서: {', '.join(p.__name__ for p in PARSERS)} (지난번 {len(previous)}건)\n"
            f"- 받은 페이지를 저장했어요: {snap.relative_to(root)}\n"
            f"- 다음 할 일: kb/wiki/selector-changes.md를 읽고, 스냅숏을 보고 파서를 더해요."
        )
    try:
        validate(items, previous)
    except LayoutChanged:
        save_snapshot(root, date, "products", html)
        raise
    return date, parser, items, fetcher.base_url + "/products"


def collect_news(fetcher: Fetcher):
    body, _ = fetcher.get("/api/news")
    data = json.loads(body)
    if data.get("synthetic") is not True or not isinstance(data.get("items"), list):
        raise CollectError("소식 JSON 모양이 달라요.")
    for it in data["items"]:
        if not all(isinstance(it.get(k), str) and it[k] for k in ("id", "date", "title")):
            raise CollectError("소식 항목에 id, date, title이 있어야 해요.")
    return data["items"]


def run(base_url: str = BASE_URL, root: Path = ROOT, sleep=time.sleep, delay: float = DELAY_SECONDS) -> dict:
    kb = root / "kb"
    kb.mkdir(exist_ok=True)
    fetcher = Fetcher(base_url, sleep=sleep, delay=delay, state=root / ".runtime" / "last-request.txt")
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    _, previous = last_prices(kb)
    record = {"fetched_at": fetched_at, "status": "fail"}
    try:
        date, parser, items, url = collect_products(fetcher, root, previous)
        record.update(date=date, parser=parser, products=len(items))
        inserted = append_prices(kb, date, items, url, fetched_at, parser)
        news = collect_news(fetcher)
        news_inserted = append_news(kb, news)
        record.update(status="ok", inserted=inserted, news_inserted=news_inserted)
        return record
    except CollectError as error:
        record["error"] = str(error).splitlines()[0]
        record["kind"] = "layout" if isinstance(error, LayoutChanged) else "error"
        raise
    finally:
        record["requests"] = len(fetcher.trace)
        record["retried"] = sum(1 for t in fetcher.trace if t["status"] != 200)
        record.setdefault("date", fetcher.headers.get("X-Sim-Date"))
        log_run(kb, record)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--json", action="store_true", help="결과를 JSON으로 보여 줘요")
    args = parser.parse_args(argv)
    try:
        result = run(args.base_url)
    except LayoutChanged as error:
        print(f"수집 중단(구조 변경 의심): {error}", file=sys.stderr)
        return 2
    except CollectError as error:
        print(f"수집 중단: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['date']} 상품 {result['products']}건(새로 {result['inserted']}건) · 새 소식 {result['news_inserted']}건"
              f" · 요청 {result['requests']}번(재시도 {result['retried']}) · 파서 {result['parser']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
