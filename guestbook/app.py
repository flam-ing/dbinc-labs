"""DB Inc 교육용 방명록. Python 표준 라이브러리만 사용한다."""

import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sqlite3
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
MAX_BODY = 8192
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


def initialize_database(db_path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")


def validate_entry(value):
    if not isinstance(value, dict):
        raise ValueError("JSON 객체를 보내 주세요.")
    result = {}
    for key, maximum, label in [("name", 40, "이름"), ("message", 500, "내용")]:
        raw = value.get(key)
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError(f"{label}을 입력해 주세요.")
        result[key] = raw.strip()
        if len(result[key]) > maximum:
            raise ValueError(f"{label}은 {maximum}자 이내로 입력해 주세요.")
    return result


class GuestbookHandler(BaseHTTPRequestHandler):
    def respond(self, status, body, content_type="application/json; charset=utf-8"):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in STATIC:
            filename, content_type = STATIC[path]
            return self.respond(200, (ROOT / "static" / filename).read_bytes(), content_type)
        if path == "/api/entries":
            try:
                with sqlite3.connect(self.server.db_path) as db:
                    db.row_factory = sqlite3.Row
                    rows = db.execute(
                        "SELECT id, name, message, created_at FROM entries "
                        "ORDER BY id DESC LIMIT 200"
                    ).fetchall()
                return self.respond(200, {"entries": [dict(row) for row in rows]})
            except sqlite3.Error:
                return self.respond(500, {"error": "목록을 불러오지 못했습니다."})
        return self.respond(404, {"error": "찾을 수 없는 경로입니다."})

    def do_POST(self):
        if urlsplit(self.path).path != "/api/entries":
            return self.respond(404, {"error": "찾을 수 없는 경로입니다."})
        if self.headers.get_content_type() != "application/json":
            return self.respond(415, {"error": "application/json으로 보내 주세요."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self.respond(400, {"error": "Content-Length가 올바르지 않습니다."})
        if length <= 0:
            return self.respond(400, {"error": "JSON 본문이 필요합니다."})
        if length > MAX_BODY:
            return self.respond(413, {"error": "요청 본문이 너무 큽니다."})
        try:
            entry = validate_entry(json.loads(self.rfile.read(length)))
        except (ValueError, UnicodeDecodeError) as error:
            message = str(error) if not isinstance(error, (json.JSONDecodeError, UnicodeDecodeError)) else "JSON 형식을 확인해 주세요."
            return self.respond(400, {"error": message})
        entry["created_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        try:
            with sqlite3.connect(self.server.db_path) as db:
                cursor = db.execute(
                    "INSERT INTO entries(name, message, created_at) VALUES (?, ?, ?)",
                    (entry["name"], entry["message"], entry["created_at"]),
                )
                entry["id"] = cursor.lastrowid
            return self.respond(201, {"entry": entry})
        except sqlite3.Error:
            return self.respond(500, {"error": "저장하지 못했습니다. 다시 시도해 주세요."})


def create_server(host="127.0.0.1", port=8000, db_path=None):
    database = Path(db_path or ROOT / "data" / "guestbook.sqlite3").resolve()
    initialize_database(database)
    server = ThreadingHTTPServer((host, port), GuestbookHandler)
    server.db_path = database
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.getenv("GUESTBOOK_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("GUESTBOOK_PORT", "8000")))
    parser.add_argument("--db", default=os.getenv("GUESTBOOK_DB", str(ROOT / "data" / "guestbook.sqlite3")))
    args = parser.parse_args()
    server = create_server(args.host, args.port, args.db)
    print(f"방명록: http://{args.host}:{server.server_port} / DB: {server.db_path}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
