"""예측, 위키 정리, 하네스 훅 검사."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import curate  # noqa: E402
import forecast  # noqa: E402

GUARD = ROOT / ".claude" / "hooks" / "guard.py"


class Forecast(unittest.TestCase):
    def test_moving_average(self):
        self.assertEqual(forecast.moving_average([1, 2, 3, 4, 5, 6, 7, 8]), 5)

    def test_straight_line_is_found_exactly(self):
        slope, intercept = forecast.linear_fit([100, 110, 120, 130])
        self.assertAlmostEqual(slope, 10)
        self.assertAlmostEqual(intercept, 100)
        self.assertEqual([round(v) for v in forecast.predict([100, 110, 120, 130], "linear", 2)], [140, 150])

    def test_mape(self):
        self.assertAlmostEqual(forecast.mape([100, 200], [110, 180]), 10.0)

    def test_promo_window_from_title(self):
        news = [{"id": "N-1", "title": "이웃몰 12월 3~5일 전원기기 기획전 예고", "tags": ["경쟁사행사", "전원"]},
                {"id": "N-2", "title": "택배 물량 늘어", "tags": ["물류"]}]
        windows = forecast.promo_windows(news, 2026)
        self.assertEqual(windows, [{"news_id": "N-1", "title": news[0]["title"], "start": "2026-12-03",
                                    "end": "2026-12-05", "categories": ["전원"]}])


class Curate(unittest.TestCase):
    def test_memo_is_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "PW-101.md"
            curate.product_page(page, "PW-101", "이름", "오디오", "숫자 1")
            text = page.read_text(encoding="utf-8").replace("아직 없어요.", "- 내가 쓴 메모")
            page.write_text(text, encoding="utf-8")
            curate.product_page(page, "PW-101", "이름", "오디오", "숫자 2")
            text = page.read_text(encoding="utf-8")
            self.assertIn("숫자 2", text)
            self.assertNotIn("숫자 1", text)
            self.assertIn("- 내가 쓴 메모", text)

    def test_discount_runs_are_grouped(self):
        points = [{"date": f"2026-11-{d:02d}", "price": p, "list_price": 100} for d, p in
                  [(1, 100), (2, 88), (3, 88), (4, 88), (5, 95), (6, 100)]]
        self.assertEqual(curate.discount_runs(points), [("2026-11-02", "2026-11-04", 12), ("2026-11-05", "2026-11-05", 5)])


class Guard(unittest.TestCase):
    def run_guard(self, tool, data):
        event = {"tool_name": tool, "tool_input": data, "cwd": str(ROOT)}
        return subprocess.run([sys.executable, str(GUARD)], input=json.dumps(event), text=True, capture_output=True)

    def test_blocks_real_sites(self):
        result = self.run_guard("Bash", {"command": "curl -s https://shop.example.com/products"})
        self.assertEqual(result.returncode, 2)
        self.assertIn("하네스", result.stderr)

    def test_allows_practice_shop(self):
        self.assertEqual(self.run_guard("Bash", {"command": "curl -s http://127.0.0.1:8766/products"}).returncode, 0)

    def test_blocks_admin_by_hand(self):
        self.assertEqual(self.run_guard("Bash", {"command": "curl -X POST http://127.0.0.1:8766/admin/day"}).returncode, 2)

    def test_blocks_editing_records_and_old_tests(self):
        self.assertEqual(self.run_guard("Edit", {"file_path": str(ROOT / "kb" / "prices.csv")}).returncode, 2)
        self.assertEqual(self.run_guard("Edit", {"file_path": str(ROOT / "tests" / "test_collect.py")}).returncode, 2)

    def test_allows_new_test_and_wiki(self):
        self.assertEqual(self.run_guard("Write", {"file_path": str(ROOT / "tests" / "test_new_layout.py")}).returncode, 0)
        self.assertEqual(self.run_guard("Edit", {"file_path": str(ROOT / "kb" / "wiki" / "selector-changes.md")}).returncode, 0)


if __name__ == "__main__":
    unittest.main()
