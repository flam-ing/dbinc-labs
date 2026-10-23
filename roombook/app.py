"""DB Inc 교육용 회의실 예약 화면. Python 표준 라이브러리만 사용한다.

수업에서 쓰는 가상 사내 툴이다. 회사, 사람, 전화번호, 예약은 모두 지어낸 것이다.
공개 API 문서는 없다. 화면(static/)이 부르는 /api/... 요청을 그대로 쓴다.
"""

import argparse
from collections import deque
from datetime import date, datetime, timedelta
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import os
from pathlib import Path
import random
import re
import secrets
import threading
import time
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent
COOKIE = "rb_session"
SESSION_HOURS = 8
READ_LIMIT = 20  # 같은 세션이 READ_WINDOW초 안에 읽을 수 있는 횟수
READ_WINDOW = 10
MAX_BODY = 4096
SERVER_SIZE_MAX = 500

STATIC = {
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}

# 연습 계정. 로그인 화면과 README에도 적혀 있다. 실제 계정이 아니다.
ACCOUNTS = {
    "minji": {"password": "roombook1", "person_id": 1},
    "junho": {"password": "roombook2", "person_id": 2},
    "seoyeon": {"password": "roombook3", "person_id": 3},
}

ROOMS = [
    {"id": "R101", "name": "한라", "floor": 1, "seats": 4},
    {"id": "R102", "name": "설악", "floor": 1, "seats": 6},
    {"id": "R201", "name": "지리", "floor": 2, "seats": 8},
    {"id": "R202", "name": "북한", "floor": 2, "seats": 6},
    {"id": "R301", "name": "태백", "floor": 3, "seats": 12},
    {"id": "R302", "name": "소백", "floor": 3, "seats": 4},
]

NAMES = [
    "김민지", "이준호", "박서연", "최도윤", "정하은", "강지훈", "조유나", "윤서준", "장예린", "임현우",
    "한소율", "오지성", "서다인", "신우진", "권나연", "황태민", "안수빈", "송재원", "전가은", "홍민재",
    "유채원", "고승현", "문지아", "양건우", "손하린", "배준서", "백서윤", "허도현", "남은지", "심시우",
    "노아린", "하윤호", "곽다은", "성지환", "차예나", "주현서", "우태윤", "구민서", "민지율", "진서하",
    "김민수", "김민호", "이서진", "박지호", "최하람", "정우빈", "강서아", "조민혁", "윤가온", "장도하",
    "임채윤", "한시온", "오하율", "서준혁", "신다온", "권태오", "황보미", "안지후", "송이안", "전로하",
]
TEAMS = ["총무팀", "개발팀", "인사팀", "영업1팀", "영업2팀", "재무팀", "디자인팀", "고객지원팀"]
TITLES = ["주간 회의", "고객 미팅", "면접", "1:1 면담", "기획 회의", "디자인 검토", "교육 준비", "분기 정리",
          "신규 입사자 안내", "예산 검토", "제안서 리뷰", "팀 점심 약속 정하기"]

TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def make_people():
    rng = random.Random(20261023)
    people = []
    for index, name in enumerate(NAMES, start=1):
        team = TEAMS[(index - 1) % len(TEAMS)] if index > 3 else TEAMS[index - 1]
        phone = f"010-{rng.randint(2000, 9999)}-{rng.randint(1000, 9999)}"
        people.append({"id": index, "name": name, "team": team, "phone": phone,
                       "email": f"user{index:02d}@dbinc.example"})
    return people


def weekdays_from(start, count):
    days, current = [], start
    while len(days) < count:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def make_reservations(people, today):
    """오늘부터 평일 10일 동안의 가상 예약을 만든다. 서버를 켤 때마다 같은 모양으로 새로 만든다."""
    rng = random.Random(7)
    reservations, next_id = [], 1
    for day in weekdays_from(today, 10):
        for room in ROOMS:
            hour = 9
            while hour < 18:
                if rng.random() < 0.18:
                    length = rng.choice([1, 1, 2])
                    owner = rng.choice(people[3:])
                    reservations.append({
                        "id": next_id, "room_id": room["id"], "date": day.isoformat(),
                        "start": f"{hour:02d}:00", "end": f"{min(hour + length, 19):02d}:00",
                        "title": rng.choice(TITLES), "owner_id": owner["id"],
                    })
                    next_id += 1
                    hour += length
                hour += 1
    # 연습 계정마다 예약 하나씩(내 예약 취소를 연습할 수 있게)
    for person_id, room_id, start, end in [(1, "R102", "16:00", "17:00"), (2, "R201", "17:00", "18:00"),
                                           (3, "R302", "16:30", "17:30")]:
        day = weekdays_from(today + timedelta(days=1), 1)[0]
        clash = [r for r in reservations if r["room_id"] == room_id and r["date"] == day.isoformat()
                 and r["start"] < end and start < r["end"]]
        for item in clash:
            reservations.remove(item)
        reservations.append({"id": next_id, "room_id": room_id, "date": day.isoformat(), "start": start,
                             "end": end, "title": "팀 회의", "owner_id": person_id})
        next_id += 1
    return reservations, next_id


class Store:
    def __init__(self, today=None):
        self.lock = threading.Lock()
        self.people = make_people()
        self.people_by_id = {p["id"]: p for p in self.people}
        self.reservations, self.next_id = make_reservations(self.people, today or date.today())
        self.sessions = {}  # sid -> {"user": login id, "expires": epoch}
        self.reads = {}  # sid -> deque of epoch seconds

    def public(self, item):
        owner = self.people_by_id[item["owner_id"]]
        room = next(r for r in ROOMS if r["id"] == item["room_id"])
        return {**item, "room_name": room["name"], "owner_name": owner["name"], "owner_team": owner["team"]}


def read_allowed(store, sid):
    """같은 세션의 읽기를 10초에 20번까지 받아 준다. 넘으면 기다릴 초를 돌려준다."""
    now = time.monotonic()
    with store.lock:
        window = store.reads.setdefault(sid, deque())
        while window and now - window[0] >= READ_WINDOW:
            window.popleft()
        if len(window) >= READ_LIMIT:
            return max(1, math.ceil(READ_WINDOW - (now - window[0])))
        window.append(now)
        return 0


class RoombookHandler(BaseHTTPRequestHandler):
    server_version = "Roombook/1.0"

    def log_message(self, fmt, *args):
        if not self.server.quiet:
            super().log_message(fmt, *args)

    # ---------- 응답 ----------
    def respond(self, status, body, content_type="application/json; charset=utf-8", headers=None):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, location, cookie=None):
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()

    def page(self, name):
        return self.respond(200, (ROOT / "static" / name).read_bytes(), "text/html; charset=utf-8")

    # ---------- 로그인 ----------
    def session_id(self):
        for part in self.headers.get("Cookie", "").split(";"):
            key, _, value = part.strip().partition("=")
            if key == COOKIE and value:
                return value
        return None

    def current_user(self):
        sid = self.session_id()
        store = self.server.store
        with store.lock:
            session = store.sessions.get(sid)
            if not session or session["expires"] < time.time():
                store.sessions.pop(sid, None)
                return None, None
        account = ACCOUNTS[session["user"]]
        return sid, store.people_by_id[account["person_id"]]

    def read_body(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY:
            return None
        return self.rfile.read(length)

    def handle_login(self):
        body = self.read_body()
        form = parse_qs((body or b"").decode("utf-8", "replace"))
        user = (form.get("id") or [""])[0].strip()
        password = (form.get("password") or [""])[0]
        account = ACCOUNTS.get(user)
        if not account or not hmac.compare_digest(account["password"].encode(), password.encode()):
            return self.redirect("/login?error=1")
        sid = secrets.token_urlsafe(24)
        with self.server.store.lock:
            self.server.store.sessions[sid] = {"user": user, "expires": time.time() + SESSION_HOURS * 3600}
        cookie = f"{COOKIE}={sid}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_HOURS * 3600}"
        return self.redirect("/", cookie)

    def handle_logout(self):
        sid = self.session_id()
        with self.server.store.lock:
            self.server.store.sessions.pop(sid, None)
        return self.redirect("/login", f"{COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0")

    # ---------- GET ----------
    def do_GET(self):
        parts = urlsplit(self.path)
        path, query = parts.path, parse_qs(parts.query)
        if path in STATIC:
            filename, content_type = STATIC[path]
            return self.respond(200, (ROOT / "static" / filename).read_bytes(), content_type)
        if path == "/login":
            return self.page("login.html")
        sid, me = self.current_user()
        if path in ("/", "/index.html"):
            return self.page("index.html") if me else self.redirect("/login")
        if not path.startswith("/api/"):
            return self.respond(404, {"error": "없는 주소예요."})
        if not me:
            return self.respond(401, {"error": "로그인이 필요해요."})
        wait = read_allowed(self.server.store, sid)
        if wait:
            return self.respond(429, {"error": f"요청이 너무 많아요. {wait}초 뒤에 다시 해 주세요."},
                                headers={"Retry-After": str(wait)})
        if path == "/api/me":
            return self.respond(200, {"id": me["id"], "name": me["name"], "team": me["team"]})
        if path == "/api/rooms":
            return self.respond(200, self.rooms(query))
        if path == "/api/reservations":
            return self.reservation_list(query, me)
        if path == "/api/people":
            return self.people(query)
        return self.respond(404, {"error": "없는 주소예요."})

    def rooms(self, query):
        day = (query.get("date") or [date.today().isoformat()])[0]
        now = datetime.now().strftime("%H:%M")
        store, result = self.server.store, []
        with store.lock:
            for room in ROOMS:
                todays = sorted((r for r in store.reservations if r["room_id"] == room["id"] and r["date"] == day),
                                key=lambda r: r["start"])
                in_use = next((r for r in todays if day == date.today().isoformat() and r["start"] <= now < r["end"]), None)
                upcoming = next((r for r in todays if day != date.today().isoformat() or r["start"] > now), None)
                result.append({**room, "date": day, "bookings": len(todays),
                               "in_use": store.public(in_use) if in_use else None,
                               "next": store.public(upcoming) if upcoming else None})
        return {"date": day, "rooms": result}

    def reservation_list(self, query, me):
        def number(key, default):
            try:
                return int((query.get(key) or [default])[0])
            except ValueError:
                return default
        page = max(1, number("page", 1))
        size = min(SERVER_SIZE_MAX, max(1, number("size", 20)))
        store = self.server.store
        with store.lock:
            items = sorted(store.reservations, key=lambda r: (r["date"], r["start"], r["room_id"]))
            if query.get("date"):
                items = [r for r in items if r["date"] == query["date"][0]]
            if query.get("room"):
                items = [r for r in items if r["room_id"] == query["room"][0]]
            if (query.get("mine") or ["0"])[0] == "1":
                items = [r for r in items if r["owner_id"] == me["id"]]
            total = len(items)
            chunk = [store.public(r) for r in items[(page - 1) * size: page * size]]
        return self.respond(200, {"items": chunk, "page": page, "size": size, "total": total,
                                  "pages": max(1, math.ceil(total / size))})

    def people(self, query):
        q = (query.get("q") or [""])[0].strip()
        items = [p for p in self.server.store.people if q in p["name"] or q in p["team"]]
        return self.respond(200, {"items": items, "total": len(items)})

    # ---------- POST / DELETE ----------
    def do_POST(self):
        path = urlsplit(self.path).path
        if path == "/login":
            return self.handle_login()
        if path == "/logout":
            return self.handle_logout()
        if path != "/api/reservations":
            return self.respond(404, {"error": "없는 주소예요."})
        sid, me = self.current_user()
        if not me:
            return self.respond(401, {"error": "로그인이 필요해요."})
        if self.headers.get_content_type() != "application/json":
            return self.respond(415, {"error": "application/json으로 보내 주세요."})
        try:
            value = json.loads(self.read_body() or b"")
            if not isinstance(value, dict):
                raise ValueError
        except ValueError:
            return self.respond(400, {"error": "JSON 형식을 확인해 주세요."})
        error = self.server_checks(value)
        if error:
            return self.respond(error[0], {"error": error[1]})
        item = {"room_id": value["room_id"], "date": value["date"], "start": value["start"], "end": value["end"],
                "title": value["title"].strip(), "owner_id": me["id"]}
        store = self.server.store
        with store.lock:
            clash = next((r for r in store.reservations if r["room_id"] == item["room_id"]
                          and r["date"] == item["date"] and r["start"] < item["end"] and item["start"] < r["end"]), None)
            if clash:
                return self.respond(409, {"error": f"그 시간에는 이미 예약이 있어요({clash['start']}~{clash['end']})."})
            item["id"] = store.next_id
            store.next_id += 1
            store.reservations.append(item)
            return self.respond(201, {"reservation": store.public(item)})

    def server_checks(self, value):
        if value.get("room_id") not in {r["id"] for r in ROOMS}:
            return 400, "없는 회의실이에요."
        try:
            date.fromisoformat(str(value.get("date")))
        except ValueError:
            return 400, "날짜는 2026-10-23 모양으로 보내 주세요."
        if not all(isinstance(value.get(k), str) and TIME_RE.match(value[k]) for k in ("start", "end")):
            return 400, "시간은 09:00 모양으로 보내 주세요."
        if value["start"] >= value["end"]:
            return 400, "끝나는 시간이 시작 시간보다 뒤여야 해요."
        title = value.get("title")
        if not isinstance(title, str) or not title.strip():
            return 400, "제목을 적어 주세요."
        if len(title.strip()) > 200:
            return 400, "제목이 너무 길어요."
        return None

    def do_DELETE(self):
        match = re.fullmatch(r"/api/reservations/(\d+)", urlsplit(self.path).path)
        if not match:
            return self.respond(404, {"error": "없는 주소예요."})
        sid, me = self.current_user()
        if not me:
            return self.respond(401, {"error": "로그인이 필요해요."})
        store, target = self.server.store, int(match.group(1))
        with store.lock:
            item = next((r for r in store.reservations if r["id"] == target), None)
            if not item:
                return self.respond(404, {"error": "없는 예약이에요."})
            store.reservations.remove(item)
        return self.respond(200, {"deleted": target})


def create_server(host="127.0.0.1", port=8010, quiet=False, today=None):
    server = ThreadingHTTPServer((host, port), RoombookHandler)
    server.store = Store(today)
    server.quiet = quiet
    return server


def main():
    parser = argparse.ArgumentParser(description="DB Inc 교육용 회의실 예약 화면")
    parser.add_argument("--host", default=os.getenv("ROOMBOOK_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("ROOMBOOK_PORT", "8010")))
    parser.add_argument("--quiet", action="store_true", help="요청 로그를 찍지 않아요")
    args = parser.parse_args()
    server = create_server(args.host, args.port, args.quiet)
    print(f"회의실 예약: http://{args.host}:{server.server_port}  (끄려면 Ctrl+C)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
