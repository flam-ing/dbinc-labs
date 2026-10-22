"""PWA 파일과 확장 프로그램 파일이 제대로 나가는지 확인한다.

python3 check_app.py

serve.py를 빈 포트와 임시 DB로 따로 띄워서 화면, manifest, 서비스 워커, 아이콘, API를 실제로 요청한다.
확장 프로그램은 manifest.json 형식과 파일, 아이콘 크기를 보고, Node.js가 있으면 node --check로 문법을 본다.
켜 둔 서버와 그 DB는 건드리지 않는다. 브라우저 설치와 알림은 사람이 직접 확인한다.
"""
import json
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
EXTENSION = HERE / "extension"


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


class PwaServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        cls.process = subprocess.Popen(
            [sys.executable, str(HERE / "serve.py"), "--port", str(port), "--db", str(Path(cls.temp.name) / "t.sqlite3")],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        cls.base = f"http://127.0.0.1:{port}"
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            try:
                with urlopen(cls.base + "/api/entries", timeout=0.2):
                    return
            except (URLError, TimeoutError):
                time.sleep(0.05)
        cls.tearDownClass()
        raise AssertionError("serve.py가 5초 안에 시작하지 못했습니다.")

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.wait(timeout=3)
        cls.temp.cleanup()

    def get(self, path):
        try:
            response = urlopen(self.base + path, timeout=3)
        except HTTPError as error:
            response = error
        with response:
            return response.status, response.headers.get("Content-Type", ""), response.read()

    def test_index_links_manifest_and_script(self):
        code, kind, body = self.get("/")
        self.assertEqual((code, kind.split(";")[0]), (200, "text/html"))
        html = body.decode()
        self.assertIn('<link rel="manifest" href="/manifest.webmanifest">', html)
        self.assertIn('<script src="/pwa.js" defer></script>', html)
        self.assertLess(html.index("/pwa.js"), html.index("</head>"))

    def test_manifest_has_install_fields(self):
        code, kind, body = self.get("/manifest.webmanifest")
        self.assertEqual(code, 200)
        self.assertEqual(kind.split(";")[0], "application/manifest+json")
        manifest = json.loads(body)
        for key in ("name", "short_name", "start_url", "display", "icons"):
            self.assertIn(key, manifest)
        self.assertIn(manifest["display"], {"fullscreen", "standalone", "minimal-ui", "window-controls-overlay"})
        sizes = {icon["sizes"]: icon["src"] for icon in manifest["icons"]}
        self.assertEqual(set(sizes), {"192x192", "512x512"})
        for size, src in sizes.items():
            with self.subTest(icon=src):
                code, kind, data = self.get(src)
                self.assertEqual((code, kind), (200, "image/png"))
                self.assertEqual("%dx%d" % png_size(data), size)

    def test_scripts_are_javascript(self):
        for path in ("/sw.js", "/pwa.js", "/app.js"):
            with self.subTest(path=path):
                code, kind, body = self.get(path)
                self.assertEqual((code, kind.split(";")[0]), (200, "text/javascript"))
                self.assertTrue(body.strip())
        self.assertIn(b"addEventListener('fetch'", self.get("/sw.js")[2])
        self.assertIn(b"showNotification", self.get("/pwa.js")[2])

    def test_api_still_works_and_files_stay_hidden(self):
        request = Request(self.base + "/api/entries", data=json.dumps({"name": "앱", "message": "알림 확인"}).encode(),
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=3) as response:
            self.assertEqual(response.status, 201)
        code, _, body = self.get("/api/entries")
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["entries"][0]["message"], "알림 확인")
        for path in ("/serve.py", "/pwa/sw.js", "/icons/missing.png", "/../app.py"):
            with self.subTest(path=path):
                self.assertEqual(self.get(path)[0], 404)


class ExtensionFilesTest(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((EXTENSION / "manifest.json").read_text(encoding="utf-8"))

    def test_manifest_v3_fields(self):
        m = self.manifest
        self.assertEqual(m["manifest_version"], 3)
        for key in ("name", "version", "background", "action", "icons"):
            self.assertIn(key, m)
        self.assertTrue({"alarms", "notifications", "storage"} <= set(m["permissions"]))
        self.assertIn("http://127.0.0.1:8000/*", m["host_permissions"])
        self.assertTrue((EXTENSION / m["background"]["service_worker"]).is_file())
        self.assertTrue((EXTENSION / m["action"]["default_popup"]).is_file())

    def test_icons_match_declared_sizes(self):
        declared = {**self.manifest["icons"], **self.manifest["action"]["default_icon"]}
        for size, src in declared.items():
            with self.subTest(icon=src):
                self.assertEqual(png_size((EXTENSION / src).read_bytes()), (int(size), int(size)))

    def test_guestbook_address_matches_host_permission(self):
        for name in ("background.js", "popup.js"):
            with self.subTest(file=name):
                self.assertIn("const GUESTBOOK = 'http://127.0.0.1:8000';", (EXTENSION / name).read_text(encoding="utf-8"))

    def test_javascript_syntax(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js가 없어서 문법 검사를 건너뜁니다.")
        files = [EXTENSION / "background.js", EXTENSION / "popup.js", HERE / "pwa" / "sw.js", HERE / "pwa" / "pwa.js"]
        for path in files:
            with self.subTest(file=path.name):
                result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
