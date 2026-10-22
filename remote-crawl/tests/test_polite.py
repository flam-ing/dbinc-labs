"""polite_fetch.py 검사예요. 인터넷 없이 돌아가요(받아 둔 응답 파일만 읽어요).

  python3 -m unittest discover -s tests
"""
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import polite_fetch as pf  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def read(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


SHOP_A = """<ul class="product-list">
  <li class="product" data-sku="PW-101" data-category="오디오">
    <span class="name">무선 이어폰 A1</span>
    <span class="price">59,000원</span>
  </li>
</ul>"""


class Parse(unittest.TestCase):
    def test_json(self):
        item = pf.parse_json(read("price.json"))
        self.assertEqual((item["name"], item["price"], item["stock"]), ("입문 키보드", 39900, 11))
        self.assertEqual(item["updated_at"], "2026-10-15T16:03:00.000Z")

    def test_html(self):
        item = pf.parse_html(read("home-card.html"))
        self.assertEqual((item["name"], item["price"], item["stock"]), ("입문 키보드", 39900, 11))

    def test_shop_day1(self):
        item = pf.parse_shop(SHOP_A)
        self.assertEqual((item["name"], item["price"]), ("무선 이어폰 A1", 59000))

    def test_html_changed_layout_is_an_error(self):
        with self.assertRaises(ValueError):
            pf.parse_html("<div id='app'>불러오는 중...</div>")


class Manners(unittest.TestCase):
    def test_stop_words(self):
        self.assertTrue(pf.is_blocked(403, ""))
        self.assertTrue(pf.is_blocked(429, ""))
        self.assertTrue(pf.is_blocked(200, '{"error":"ip_blocked"}'))
        self.assertFalse(pf.is_blocked(200, read("price.json")))

    def test_only_allowed_hosts(self):
        with self.assertRaises(pf.Stop):
            pf.ensure_allowed("https://www.example.com/")
        with self.assertRaises(pf.Stop):
            pf.ensure_allowed("https://test-server-8az.pages.dev/api/turnstile")
        self.assertTrue(pf.ensure_allowed("https://test-server-8az.pages.dev/api/price"))

    def test_gap_uses_cache_without_asking(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(pf, "STATE", Path(tmp) / "state.json"), \
                 mock.patch.object(pf, "DATA", Path(tmp) / "data"), \
                 mock.patch.object(pf, "get", side_effect=AssertionError("묻지 말아야 해요")):
                pf.save_state({"targets": {pf.BASE: {"last_request_at": time.time() - 10,
                                                     "last_result": {"name": "입문 키보드", "price": 39900}}}})
                self.assertEqual(pf.run("json", "DBInc-test/1.0", pf.BASE), 0)

    def test_blocked_stops_and_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(pf, "STATE", Path(tmp) / "state.json"), \
                 mock.patch.object(pf, "DATA", Path(tmp) / "data"), \
                 mock.patch.object(pf.time, "sleep"), \
                 mock.patch.object(pf, "get", side_effect=[(200, {"Content-Type": "text/html"}, "<html></html>"),
                                                           (429, {"Retry-After": "30"}, "{}")]):
                self.assertEqual(pf.run("json", "DBInc-test/1.0", pf.BASE), 2)
                self.assertIn("429", (Path(tmp) / "data" / "incidents.md").read_text(encoding="utf-8"))
                self.assertGreater(pf.load_state()["targets"][pf.BASE]["blocked_until"], time.time())

    def test_same_value_is_saved_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(pf, "DATA", Path(tmp)):
                row = {"fetched_at": "t", "route": "json", "name": "입문 키보드", "price": 39900, "stock": 11,
                       "updated_at": "2026-10-15T16:03:00.000Z", "source_url": "u", "user_agent": "a"}
                self.assertTrue(pf.append_row(row))
                self.assertFalse(pf.append_row(dict(row, fetched_at="t2")))


if __name__ == "__main__":
    unittest.main()
