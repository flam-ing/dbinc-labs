"""방명록 참고 구현(labs/guestbook/app.py)에 PWA 파일을 더해서 한 서버로 내보낸다.

python3 serve.py            → http://127.0.0.1:8000 (방명록 API + 화면 + PWA 파일)
python3 serve.py --port 8001 --db /tmp/test.sqlite3

서비스 워커는 페이지와 같은 출처(같은 주소와 포트)에서 와야 하고, 페이지가 부르는 /api/entries도
같은 출처에 있어야 CORS 설정 없이 동작한다. 그래서 PWA 파일을 다른 서버로 따로 띄우지 않고,
방명록 서버가 같이 내보내게 했다. 방명록 코드(app.py)는 고치지 않고 불러와서 쓴다.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
GUESTBOOK = HERE.parent / "guestbook"
PWA = HERE / "pwa"

sys.dont_write_bytecode = True  # 방명록 폴더에 __pycache__를 만들지 않는다.
spec = importlib.util.spec_from_file_location("guestbook_app", GUESTBOOK / "app.py")
guestbook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guestbook)

# 방명록이 원래 내보내는 파일(/, /style.css, /app.js)에 더해서 내보낼 PWA 파일 목록이다.
# 목록에 없는 경로는 원래 방명록 서버가 처리한다(API 또는 404).
PWA_FILES = {
    "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json; charset=utf-8"),
    "/sw.js": ("sw.js", "text/javascript; charset=utf-8"),
    "/pwa.js": ("pwa.js", "text/javascript; charset=utf-8"),
    "/icons/icon-192.png": ("icons/icon-192.png", "image/png"),
    "/icons/icon-512.png": ("icons/icon-512.png", "image/png"),
}

# 방명록 index.html의 </head> 앞에 끼워 넣는 줄이다. 내 방명록에서는 index.html에 직접 적는다.
HEAD_LINES = """  <link rel="manifest" href="/manifest.webmanifest">
  <meta name="theme-color" content="#FF6F0F">
  <link rel="icon" href="/icons/icon-192.png">
  <link rel="apple-touch-icon" href="/icons/icon-192.png">
  <script src="/pwa.js" defer></script>
"""


def index_with_pwa():
    html = (GUESTBOOK / "static" / "index.html").read_text(encoding="utf-8")
    if "</head>" not in html:
        raise RuntimeError("방명록 index.html에 </head>가 없습니다.")
    return html.replace("</head>", HEAD_LINES + "</head>", 1).encode("utf-8")


class PwaHandler(guestbook.GuestbookHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ("/", "/index.html"):
            return self.respond(200, index_with_pwa(), "text/html; charset=utf-8")
        if path in PWA_FILES:
            filename, content_type = PWA_FILES[path]
            return self.respond(200, (PWA / filename).read_bytes(), content_type)
        return super().do_GET()


def create_server(host="127.0.0.1", port=8000, db_path=None):
    server = guestbook.create_server(host, port, db_path)
    server.RequestHandlerClass = PwaHandler
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default=os.getenv("GUESTBOOK_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("GUESTBOOK_PORT", "8000")))
    parser.add_argument("--db", default=os.getenv("GUESTBOOK_DB", str(GUESTBOOK / "data" / "guestbook.sqlite3")))
    args = parser.parse_args()
    server = create_server(args.host, args.port, args.db)
    print(f"방명록 앱(PWA): http://{args.host}:{server.server_port} / DB: {server.db_path}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
