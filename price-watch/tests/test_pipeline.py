"""처음부터 끝까지: 시작 자료(starter)로 1~7일 수집 → 8일 구조 변경으로 멈춤 → 정답 수집기로 30일까지 →
위키 정리 → 예측 → 리포트 → 묶기 → 다른 폴더에 풀어서 다시 실행. 연습몰은 빈 포트로 띄워요."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "shop"))
import server  # noqa: E402


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def no_wait(_seconds):
    return None


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shop = server.start_shop(0, day=1)
        cls.base = f"http://127.0.0.1:{cls.shop.server_port}"
        cls.tmp = tempfile.TemporaryDirectory()
        cls.work = Path(cls.tmp.name) / "dbinc-price-watch"
        shutil.copytree(LAB / "starter", cls.work, ignore=shutil.ignore_patterns("__pycache__"))

    @classmethod
    def tearDownClass(cls):
        cls.shop.shutdown()
        cls.shop.server_close()
        cls.tmp.cleanup()

    def set_day(self, day):
        req = Request(self.base + "/admin/day", data=json.dumps({"day": day}).encode(), method="POST")
        urlopen(req, timeout=5).close()

    def collect_days(self, module, first, last):
        for day in range(first, last + 1):
            self.set_day(day)
            result = module.run(self.base, self.work, sleep=no_wait, delay=0)
            self.assertEqual(result["products"], 10, day)

    def py(self, *args, cwd=None):
        return subprocess.run([sys.executable, *args], cwd=cwd or self.work, capture_output=True, text=True)

    def test_whole_month(self):
        starter = load(self.work / "collect.py", "starter_collect")
        self.collect_days(starter, 1, 7)
        self.set_day(8)
        with self.assertRaises(starter.LayoutChanged):
            starter.run(self.base, self.work, sleep=no_wait, delay=0)
        self.assertTrue((self.work / ".runtime/snapshots/products-2026-11-08.html").exists())
        last = json.loads((self.work / "kb/runs.jsonl").read_text().splitlines()[-1])
        self.assertEqual((last["status"], last["kind"], last["date"]), ("fail", "layout", "2026-11-08"))

        # 실제 실행 경로에서도 종료 코드 2로 멈추는지 봐요.
        done = self.py("collect.py", "--base-url", self.base)
        self.assertEqual(done.returncode, 2, done.stderr)
        self.assertIn("상품을 0건 찾았어요", done.stderr)

        # 정답 수집기와 정답 테스트로 바꾸고 30일까지 모아요.
        shutil.copy2(LAB / "reference/collect.py", self.work / "collect.py")
        for f in (LAB / "reference/tests").glob("test_layout_*.py"):
            shutil.copy2(f, self.work / "tests" / f.name)
        for f in (LAB / "reference/tests/fixtures").iterdir():
            shutil.copy2(f, self.work / "tests/fixtures" / f.name)
        reference = load(self.work / "collect.py", "reference_collect")
        self.collect_days(reference, 8, 30)
        tests = self.py("-m", "unittest", "discover", "-s", "tests")
        self.assertEqual(tests.returncode, 0, tests.stderr)

        curate = self.py("tools/curate.py")
        self.assertEqual(curate.returncode, 0, curate.stdout + curate.stderr)
        self.assertIn("가격 300행 · 30일 · 소식 10건 · 중복 0 · 이상한 행 0 · 빠진 날 0 · 수집 실패 2번", curate.stdout)

        forecast = load(self.work / "tools/forecast.py", "fc")
        result = forecast.run(self.work / "kb")
        self.assertEqual(result["base_date"], "2026-11-30")
        warn = {p["sku"]: p["warnings"] for p in result["products"]}
        self.assertEqual(warn["PW-103"], ["12-03~12-05 행사 예고(N-2810)"])
        self.assertEqual(result["backtest"]["hidden"], ["2026-11-24", "2026-11-30"])

        report = self.py("tools/report.py")
        self.assertEqual(report.returncode, 0, report.stderr)
        text = (self.work / "out/report.md").read_text()
        self.assertIn("| 2026-11-12 ~ 2026-11-14 | PW-101 | 12% | N-0904 11-09 이웃몰 11월 12~14일 오디오 기획전 예고 |", text)
        self.assertIn("| 2026-11-19 | PW-107 | 49,000원 → 51,400원 (+4.9%) | N-1606", text)

        # 내 PC 전용 파일은 묶이지 않아야 해요.
        (self.work / ".claude/settings.local.json").write_text("{}")
        pack = self.py("tools/package.py")
        self.assertEqual(pack.returncode, 0, pack.stdout + pack.stderr)
        archive = self.work / "dist/price-watch.zip"
        names = zipfile.ZipFile(archive).namelist()
        self.assertIn("price-watch/GUIDE.md", names)
        self.assertIn("price-watch/kb/prices.csv", names)
        self.assertFalse([n for n in names if "settings.local.json" in n or "/.runtime/" in n or "__pycache__" in n])

        unpacked = Path(self.tmp.name) / "unzip"
        zipfile.ZipFile(archive).extractall(unpacked)
        again = unpacked / "price-watch"
        self.assertEqual(self.py("-m", "unittest", "discover", "-s", "tests", cwd=again).returncode, 0)
        self.assertEqual(self.py("tools/report.py", cwd=again).returncode, 0)
        self.assertEqual((again / "out/report.md").read_text(), text)

    def test_starter_and_reference_share_old_tests(self):
        self.assertEqual((LAB / "starter/tests/test_collect.py").read_text(),
                         (LAB / "reference/tests/test_collect.py").read_text())


if __name__ == "__main__":
    unittest.main()
