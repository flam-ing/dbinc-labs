"""방명록 API 테스트. 서버를 임시 포트와 임시 DB로 띄워서 실제 요청을 보내요.

실행: python3 -m unittest
지금 있는 테스트는 모두 통과해요. 그래도 이슈 네 개의 버그는 그대로 있어요.
"""
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

APP = Path(__file__).resolve().parent.parent / "app.py"


class GuestbookTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        self.server = subprocess.Popen(
            [sys.executable, str(APP), "--port", str(port), "--db", str(Path(self.temp.name) / "test.sqlite3")],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        self.base = f"http://127.0.0.1:{port}"
        for _ in range(50):
            try:
                urlopen(self.base + "/api/entries", timeout=1).close()
                break
            except URLError:
                time.sleep(0.1)

    def tearDown(self):
        self.server.terminate()
        self.server.wait(timeout=5)
        self.temp.cleanup()

    def post(self, name, message):
        body = json.dumps({"name": name, "message": message}).encode()
        request = Request(self.base + "/api/entries", data=body, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            with error:
                return error.code, json.loads(error.read())

    def entries(self):
        with urlopen(self.base + "/api/entries", timeout=3) as response:
            return json.loads(response.read())["entries"]

    def test_글을_남기면_201과_번호를_준다(self):
        status, body = self.post("김디비", "안녕하세요")
        self.assertEqual(status, 201)
        self.assertEqual(body["entry"]["id"], 1)

    def test_남긴_글이_목록에_나온다(self):
        self.post("김디비", "안녕하세요")
        self.assertEqual(self.entries()[0]["message"], "안녕하세요")

    def test_이름이_비면_400(self):
        status, body = self.post("   ", "안녕하세요")
        self.assertEqual(status, 400)
        self.assertIn("이름", body["error"])


if __name__ == "__main__":
    unittest.main()
