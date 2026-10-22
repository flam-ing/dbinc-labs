"""연습몰: 2일차 4교시 가격 추적 실습용 가상 쇼핑몰 서버예요.

내 컴퓨터 안(127.0.0.1)에서만 열려요. 상품과 가격, 소식은 모두 지어낸 것이에요.
날짜는 시뮬레이션이에요. 수업 진행용 주소 /admin/day로 바꾸고, 날짜에 따라 가격과 페이지 구조가 바뀌어요.

  python3 server.py --port 8766          # 1일차(2026-11-01)부터 시작
  python3 server.py --port 8766 --day 8  # 8일차부터 시작
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock, Thread
from urllib.parse import parse_qs, urlsplit

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import market  # noqa: E402

STATIC = {
    "/static/shop.css": ("shop.css", "text/css; charset=utf-8"),
    "/static/render-c.js": ("render-c.js", "application/javascript; charset=utf-8"),
    "/static/app-d.js": ("app-d.js", "application/javascript; charset=utf-8"),
}


class ShopServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port=8766, day=1, failures=True, log=True):
        super().__init__(("127.0.0.1", port), Handler)
        self.day = market.check_day(day)
        self.failures = failures
        self.log = log
        self.attempts = Counter()
        self.last_request = {}
        self.lock = Lock()


class Handler(BaseHTTPRequestHandler):
    server_version = "PracticeShop/1.0"

    def log_message(self, *_args):
        pass

    def _log(self, method, path, status):
        server = self.server
        if not server.log:
            return
        now = time.monotonic()
        agent = self.headers.get("User-Agent", "-")
        with server.lock:
            before = server.last_request.get(agent)
            server.last_request[agent] = now
        gap = "첫 요청" if before is None else f"지난 요청 후 {now - before:.1f}초"
        if path.startswith("/admin"):
            gap = "수업 진행용"
        d = market.day_date(server.day)
        print(f"[{d:%m-%d} · {server.day}일차] {method} {path} {status} · {gap} · {agent}", flush=True)

    def send(self, status, body, content_type="text/html; charset=utf-8", retry=None, method="GET"):
        raw = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Sim-Day", str(self.server.day))
        self.send_header("X-Sim-Date", market.day_date(self.server.day).isoformat())
        if retry is not None:
            self.send_header("Retry-After", str(retry))
        self.end_headers()
        self.wfile.write(raw)
        self._log(method, self.path, status)

    def send_json(self, status, data, retry=None, method="GET"):
        self.send(status, json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                  "application/json; charset=utf-8", retry, method)

    def do_GET(self):
        parts = urlsplit(self.path)
        day = self.server.day
        path = parts.path
        if path == "/":
            return self.send(200, market.home_page(day))
        if path == "/products":
            return self.send(200, market.products_page(day))
        if path == "/news":
            return self.send(200, market.news_page(day))
        if path == "/api/news":
            return self.send_json(200, {"synthetic": True, "date": market.day_date(day).isoformat(),
                                        "items": market.news_until(day)})
        if path == "/api/catalog":
            try:
                page = int(parse_qs(parts.query).get("page", ["1"])[0])
            except ValueError:
                return self.send_json(400, {"error": "page는 정수예요"})
            data = market.catalog_api(day, page)
            if data is None:
                return self.send_json(404, {"error": "없는 주소예요"})
            key = (day, page)
            with self.server.lock:
                self.server.attempts[key] += 1
                first = self.server.attempts[key] == 1
            # 실제 사이트에서 자주 만나는 실패를 일부러 한 번 내요. 날마다 2쪽 첫 요청만이에요.
            if self.server.failures and page == 2 and first:
                return self.send_json(429, {"error": "요청이 너무 많아요. 잠시 뒤에 다시 와요."}, retry=1)
            return self.send_json(200, data)
        if path == "/terms":
            return self.send(200, market.terms_page(day))
        if path == "/robots.txt":
            return self.send(200, market.ROBOTS, "text/plain; charset=utf-8")
        if path in STATIC:
            name, kind = STATIC[path]
            return self.send(200, (HERE / "static" / name).read_text(encoding="utf-8"), kind)
        if path == "/admin/day":
            return self.send_json(200, self._day_info())
        return self.send(404, "<!doctype html><meta charset=\"utf-8\"><p>없는 페이지예요.</p>")

    def do_POST(self):
        parts = urlsplit(self.path)
        if parts.path != "/admin/day":
            return self.send_json(404, {"error": "없는 주소예요"}, method="POST")
        length = int(self.headers.get("Content-Length") or 0)
        if length > 1000:
            return self.send_json(413, {"error": "본문이 너무 커요"}, method="POST")
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
            if data.get("next"):
                day = self.server.day + 1
            else:
                day = data["day"]
            market.check_day(day)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            return self.send_json(400, {"error": f"day는 1~{market.MAX_DAY} 사이 정수예요 ({error})"}, method="POST")
        self.server.day = day
        return self.send_json(200, self._day_info(), method="POST")

    def _day_info(self):
        day = self.server.day
        return {"day": day, "date": market.day_date(day).isoformat(),
                "layout": market.layout_for(day), "max_day": market.MAX_DAY}


def start_shop(port=0, day=1, failures=True, log=False):
    """테스트용: 빈 포트로 서버를 띄우고 돌려줘요."""
    server = ShopServer(port, day, failures, log)
    Thread(target=server.serve_forever, daemon=True).start()
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--day", type=int, default=1)
    parser.add_argument("--no-failures", action="store_true", help="429 같은 일부러 넣은 실패를 끕니다")
    parser.add_argument("--quiet", action="store_true", help="요청 기록을 찍지 않습니다")
    args = parser.parse_args()
    try:
        server = ShopServer(args.port, args.day, not args.no_failures, not args.quiet)
    except ValueError as error:
        parser.error(str(error))
    except OSError as error:
        parser.exit(1, f"{args.port} 포트를 열 수 없어요: {error}\n이미 켜 둔 서버가 있는지 확인해요.\n")
    d = market.day_date(server.day)
    print(f"연습몰(교육용 가상 쇼핑몰): http://127.0.0.1:{server.server_port}/products", flush=True)
    print(f"시뮬레이션 날짜: {d} ({server.day}일차) · 끄려면 Ctrl+C", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
