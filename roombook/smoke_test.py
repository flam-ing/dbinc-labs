"""회의실 예약 서버가 제대로 켜지는지 확인해요. Python 표준 라이브러리만 써요.

py smoke_test.py                              (macOS는 python3 smoke_test.py) 옆의 app.py를 빈 포트로 띄워서 검사
py smoke_test.py --url http://127.0.0.1:8010  이미 켜 둔 서버를 검사
"""
import argparse
from datetime import date, timedelta
import http.client
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.parse import urlencode, urlsplit

APP = Path(__file__).resolve().with_name("app.py")


class Client:
    def __init__(self, base):
        parts = urlsplit(base)
        self.host, self.port = parts.hostname, parts.port or 80
        self.cookie = ""

    def call(self, method, path, body=None, form=None):
        headers = {"Cookie": self.cookie} if self.cookie else {}
        data = None
        if form is not None:
            data = urlencode(form).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        connection = http.client.HTTPConnection(self.host, self.port, timeout=5)
        try:
            connection.request(method, path, body=data, headers=headers)
            response = connection.getresponse()
            raw = response.read()
            value = json.loads(raw) if "json" in (response.getheader("Content-Type") or "") else raw
            return response.status, dict(response.getheaders()), value
        finally:
            connection.close()


def next_weekday(days_ahead):
    day = date.today() + timedelta(days=days_ahead)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day.isoformat()


def run_checks(base):
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {name}{'  ' + detail if detail and not ok else ''}")

    guest = Client(base)
    status, headers, _ = guest.call("GET", "/")
    check("로그인 전에 첫 화면을 열면 로그인 화면으로 보내요", status == 303 and headers.get("Location") == "/login")
    status, _, _ = guest.call("GET", "/api/me")
    check("로그인 전에 API를 부르면 401이에요", status == 401, str(status))
    status, headers, _ = guest.call("POST", "/login", form={"id": "minji", "password": "wrong"})
    check("비밀번호가 틀리면 다시 로그인 화면으로 보내요", status == 303 and "error" in headers.get("Location", ""))

    user = Client(base)
    status, headers, _ = user.call("POST", "/login", form={"id": "minji", "password": "roombook1"})
    cookie = headers.get("Set-Cookie", "")
    check("연습 계정으로 로그인하면 HttpOnly 쿠키를 줘요", status == 303 and "HttpOnly" in cookie, cookie)
    user.cookie = cookie.split(";", 1)[0]
    status, _, me = user.call("GET", "/api/me")
    check("로그인 뒤 /api/me가 내 이름을 돌려줘요", status == 200 and me.get("name") == "김민지", str(me))
    status, _, rooms = user.call("GET", "/api/rooms")
    check("회의실 현황이 6개 나와요", status == 200 and len(rooms.get("rooms", [])) == 6)
    status, _, page = user.call("GET", "/api/reservations?page=1&size=20")
    check("예약 목록이 20건씩 나와요", status == 200 and len(page.get("items", [])) == 20 and page.get("pages", 0) >= 2,
          str({k: page.get(k) for k in ("total", "pages")}))

    booking = {"room_id": "R302", "date": next_weekday(40), "start": "10:00", "end": "11:00", "title": "확인 도구 예약"}
    status, _, made = user.call("POST", "/api/reservations", body=booking)
    check("예약을 만들 수 있어요", status == 201, str(made))
    status, _, _ = user.call("POST", "/api/reservations", body=booking)
    check("같은 회의실 같은 시간은 409로 거절해요", status == 409, str(status))
    if isinstance(made, dict) and made.get("reservation"):
        status, _, _ = user.call("DELETE", f"/api/reservations/{made['reservation']['id']}")
        check("내 예약을 취소할 수 있어요", status == 200, str(status))

    reader = Client(base)
    _, headers, _ = reader.call("POST", "/login", form={"id": "junho", "password": "roombook2"})
    reader.cookie = headers.get("Set-Cookie", "").split(";", 1)[0]
    statuses, retry = [], None
    for _ in range(25):
        status, headers, _ = reader.call("GET", "/api/rooms")
        statuses.append(status)
        retry = retry or headers.get("Retry-After")
    check("10초에 20번 넘게 읽으면 429와 Retry-After를 줘요",
          statuses[:20].count(200) == 20 and 429 in statuses and retry is not None,
          f"200={statuses.count(200)} 429={statuses.count(429)} Retry-After={retry}")

    passed = sum(results)
    print(f"\n{passed}/{len(results)} 통과")
    return passed == len(results)


def main():
    parser = argparse.ArgumentParser(description="회의실 예약 서버 확인")
    parser.add_argument("--url", help="이미 켜 둔 서버 주소. 없으면 app.py를 빈 포트로 띄워요")
    args = parser.parse_args()
    if args.url:
        return 0 if run_checks(args.url.rstrip("/")) else 1
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process = subprocess.Popen([sys.executable, str(APP), "--port", str(port), "--quiet"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        return 0 if run_checks(f"http://127.0.0.1:{port}") else 1
    finally:
        process.terminate()
        process.wait(timeout=5)


if __name__ == "__main__":
    sys.exit(main())
