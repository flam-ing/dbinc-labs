"""collect.py 검사. 연습몰 없이 저장해 둔 스냅숏으로 확인해요."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import collect  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class LayoutA(unittest.TestCase):
    def setUp(self):
        self.html = (FIXTURES / "products-2026-11-01.html").read_text(encoding="utf-8")

    def test_reads_ten_products(self):
        name, items = collect.parse_products(self.html)
        self.assertEqual(name, "parse_list_a")
        self.assertEqual(len(items), 10)
        self.assertEqual(items[0], {"sku": "PW-101", "name": "무선 이어폰 A1", "category": "오디오",
                                    "price": 59000, "list_price": 59000})

    def test_deal_has_sale_and_list_price(self):
        _, items = collect.parse_products(self.html)
        deal = [it for it in items if it["price"] < it["list_price"]]
        self.assertEqual([(d["sku"], d["price"], d["list_price"]) for d in deal], [("PW-109", 75000, 79000)])


class FailLoudly(unittest.TestCase):
    def test_unknown_layout_finds_nothing(self):
        self.assertEqual(collect.parse_products("<html><body><div class='x'>59,000원</div></body></html>"), (None, []))

    def test_big_jump_is_layout_error(self):
        items = [{"sku": "PW-101", "name": "a", "category": "오디오", "price": 5900, "list_price": 5900}]
        with self.assertRaises(collect.LayoutChanged):
            collect.validate(items, {"PW-101": 59000})

    def test_fewer_items_is_layout_error(self):
        items = [{"sku": "PW-101", "name": "a", "category": "오디오", "price": 59000, "list_price": 59000}]
        with self.assertRaises(collect.LayoutChanged):
            collect.validate(items, {f"PW-1{n:02d}": 1000 for n in range(1, 11)})

    def test_only_local_urls(self):
        with self.assertRaises(collect.CollectError):
            collect.ensure_local("https://example.com/products")
        with self.assertRaises(collect.CollectError):
            collect.ensure_local("http://127.0.0.1:8766/admin/day")


class Storage(unittest.TestCase):
    def test_same_day_is_not_saved_twice(self):
        items = [{"sku": "PW-101", "name": "a", "category": "오디오", "price": 59000, "list_price": 59000}]
        with tempfile.TemporaryDirectory() as tmp:
            kb = Path(tmp)
            self.assertEqual(collect.append_prices(kb, "2026-11-01", items, "u", "t", "p"), 1)
            self.assertEqual(collect.append_prices(kb, "2026-11-01", items, "u", "t", "p"), 0)
            with (kb / "prices.csv").open(encoding="utf-8") as f:
                self.assertEqual(len(list(csv.DictReader(f))), 1)

    def test_parse_won(self):
        self.assertEqual(collect.parse_won(" 59,000원 "), 59000)
        with self.assertRaises(ValueError):
            collect.parse_won("품절")


if __name__ == "__main__":
    unittest.main()
