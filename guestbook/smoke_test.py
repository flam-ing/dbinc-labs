"""실제 HTTP 요청으로 방명록 API 약속(저장·검증·오류 응답)을 확인한다.

python3 smoke_test.py                           옆의 app.py를 임시 포트·임시 DB로 띄워서 검사
python3 smoke_test.py --app app.py              내 app.py를 임시 포트·임시 DB로 띄워서 검사(재시작 뒤 유지까지)
python3 smoke_test.py --url http://127.0.0.1:3000  이미 켜 둔 서버(Next.js, Spring 등)의 API 약속만 검사
"""
import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

APP_PATH = Path(__file__).resolve().with_name("app.py")
BASE_URL = None  # --url로 받은 켜 둔 서버 주소


class RequestMixin:
    timeout = 3

    def request(self, path, value=None, raw=None, content_type="application/json"):
        data = raw if raw is not None else (json.dumps(value).encode() if value is not None else None)
        request = Request(self.base + path, data=data, headers={"Content-Type": content_type})
        try:
            response = urlopen(request, timeout=self.timeout)
        except HTTPError as error:
            response = error
        with response:
            body = response.read()
            if "application/json" in response.headers.get("Content-Type", ""):
                body = json.loads(body)
            return response.status, body


class GuestbookSmokeTest(RequestMixin, unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "test.sqlite3"
        self.start_server()

    def start_server(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        self.process = subprocess.Popen(
            [sys.executable, str(APP_PATH), "--port", str(port), "--db", str(self.db)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        self.base = f"http://127.0.0.1:{port}"
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise AssertionError(f"서버가 시작 중 종료되었습니다: {APP_PATH}")
            try:
                with urlopen(self.base + "/api/entries", timeout=0.2):
                    return
            except (URLError, TimeoutError):
                time.sleep(0.05)
        self.stop_server()
        raise AssertionError("서버가 5초 안에 시작하지 못했습니다.")

    def stop_server(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=3)

    def tearDown(self):
        self.stop_server()
        self.temp.cleanup()

    def test_http_contract_and_persistence(self):
        self.assertEqual(self.request("/api/entries"), (200, {"entries": []}))
        payload = {"name": "  실습자  ", "message": "<script>alert(1)</script>\n첫 기록"}
        code, result = self.request("/api/entries", payload)
        self.assertEqual(code, 201)
        first = result["entry"]
        self.assertEqual(first["name"], "실습자")
        self.assertEqual(first["message"], payload["message"])
        created_at = datetime.fromisoformat(first["created_at"].replace("Z", "+00:00"))
        self.assertEqual(created_at.utcoffset(), timedelta(0))
        code, second = self.request("/api/entries", {"name": "다음", "message": "두 번째"})
        self.assertEqual(code, 201)
        ids = [row["id"] for row in self.request("/api/entries")[1]["entries"]]
        self.assertEqual(ids, [second["entry"]["id"], first["id"]])
        self.stop_server()
        self.start_server()
        self.assertEqual([row["id"] for row in self.request("/api/entries")[1]["entries"]], ids)

    def test_validation_rejects_without_inserting(self):
        cases = [
            {}, {"name": " ", "message": "a"}, {"name": "a", "message": " "},
            {"name": "가" * 41, "message": "a"}, {"name": "a", "message": "가" * 501},
            {"name": 1, "message": "a"}, ["not", "an object"],
        ]
        for value in cases:
            with self.subTest(value=str(value)[:50]):
                self.assertEqual(self.request("/api/entries", value)[0], 400)
        self.assertEqual(self.request("/api/entries", raw=b"{")[0], 400)
        self.assertEqual(self.request("/api/entries", raw=b"\xff")[0], 400)
        self.assertEqual(self.request("/api/entries", raw=b"x" * 8193)[0], 413)
        self.assertEqual(self.request("/api/entries", raw=b"name=a", content_type="text/plain")[0], 415)
        self.assertEqual(self.request("/api/entries"), (200, {"entries": []}))
        self.assertEqual(self.request("/api/entries", {"name": "가" * 40, "message": "나" * 500})[0], 201)

    def test_static_routes_and_unknown_paths(self):
        with urlopen(self.base + "/", timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get_content_type(), "text/html")
            self.assertTrue(response.read().strip(), "HTML 응답이 비어 있습니다.")
        for path in ["/missing", "/../app.py", "/data/guestbook.sqlite3"]:
            self.assertEqual(self.request(path)[0], 404)
        self.assertEqual(self.request("/missing", {"name": "a", "message": "b"})[0], 404)


class RunningServerContractTest(RequestMixin, unittest.TestCase):
    """--url로 켜 둔 서버를 검사한다. 서버를 끄고 켜지 않으므로 재시작 뒤 유지는 직접 확인한다.

    검사용 기록 3개가 켜 둔 서버의 DB에 남는다. 이름은 모두 '검사'로 시작한다.
    """
    timeout = 30  # Next.js 개발 서버는 처음 요청 때 코드를 묶느라 몇 초 걸릴 수 있다.

    @classmethod
    def setUpClass(cls):
        if not BASE_URL:
            raise unittest.SkipTest("--url을 줄 때만 실행합니다.")
        cls.base = BASE_URL.rstrip("/")

    def latest_ids(self):
        code, body = self.request("/api/entries")
        self.assertEqual(code, 200, f"GET /api/entries가 200이 아닙니다: {body!r:.200}")
        self.assertIsInstance(body, dict, "GET /api/entries가 JSON 객체를 돌려주지 않습니다.")
        self.assertIsInstance(body.get("entries"), list, '응답에 "entries" 목록이 없습니다.')
        self.assertLessEqual(len(body["entries"]), 200)
        return [row["id"] for row in body["entries"]]

    def test_http_contract(self):
        self.latest_ids()
        payload = {"name": "  검사  ", "message": "<script>alert(1)</script>\nsmoke_test가 남긴 첫 기록"}
        code, result = self.request("/api/entries", payload)
        self.assertEqual(code, 201, f"정상 입력이 201이 아닙니다: {result!r:.200}")
        first = result["entry"]
        self.assertEqual(first["name"], "검사")
        self.assertEqual(first["message"], payload["message"])
        created_at = datetime.fromisoformat(first["created_at"].replace("Z", "+00:00"))
        self.assertEqual(created_at.utcoffset(), timedelta(0))
        code, second = self.request("/api/entries", {"name": "검사 2", "message": "smoke_test가 남긴 두 번째 기록"})
        self.assertEqual(code, 201)
        self.assertEqual(self.latest_ids()[:2], [second["entry"]["id"], first["id"]])

    def test_validation_rejects_without_inserting(self):
        before = self.latest_ids()[:1]
        cases = [
            {}, {"name": " ", "message": "a"}, {"name": "a", "message": " "},
            {"name": "가" * 41, "message": "a"}, {"name": "a", "message": "가" * 501},
            {"name": 1, "message": "a"}, ["not", "an object"],
        ]
        for value in cases:
            with self.subTest(value=str(value)[:50]):
                self.assertEqual(self.request("/api/entries", value)[0], 400)
        self.assertEqual(self.request("/api/entries", raw=b"{")[0], 400)
        self.assertEqual(self.request("/api/entries", raw=b"\xff")[0], 400)
        self.assertEqual(self.request("/api/entries", raw=b"x" * 8193)[0], 413)
        self.assertEqual(self.request("/api/entries", raw=b"name=a", content_type="text/plain")[0], 415)
        self.assertEqual(self.latest_ids()[:1], before, "거절해야 할 요청이 저장됐습니다.")
        boundary = {"name": "검사" + "가" * 38, "message": ("smoke_test 경계값 기록. " * 30)[:500]}
        self.assertEqual(self.request("/api/entries", boundary)[0], 201)

    def test_unknown_paths(self):
        for path in ["/api/missing", "/data/guestbook.sqlite3"]:
            with self.subTest(path=path):
                self.assertEqual(self.request(path)[0], 404)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--app", type=Path)
    parser.add_argument("--url")
    args, remaining = parser.parse_known_args()
    if args.url and args.app:
        parser.error("--app과 --url은 함께 쓸 수 없습니다.")
    if args.url:
        BASE_URL = args.url
        print(f"검사 대상: {BASE_URL} (켜 둔 서버. 재시작 뒤 기록 유지는 직접 확인하고, 검사용 기록 3개가 남습니다)", flush=True)
        default = "RunningServerContractTest"
    else:
        APP_PATH = (args.app or APP_PATH).resolve()
        if not APP_PATH.is_file():
            parser.error(f"서버 파일이 없습니다: {APP_PATH}")
        note = "" if args.app else " (--app이 없어서 smoke_test.py 옆의 app.py를 검사합니다)"
        print(f"검사 대상: {APP_PATH}{note}", flush=True)
        default = "GuestbookSmokeTest"
    unittest.main(argv=[sys.argv[0], *remaining], defaultTest=default, verbosity=2)
