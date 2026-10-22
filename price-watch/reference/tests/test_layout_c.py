"""[정답 예시] 2026-11-15 구조(C) 테스트. 예전 테스트(test_collect.py)는 그대로 두고 새 파일로 더해요."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import collect  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def read(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


class LayoutC(unittest.TestCase):
    """2026-11-15부터: 화면은 JavaScript가 그리고 데이터는 <script id="__SHOP_STATE__"> 안 JSON"""

    def test_embedded_json(self):
        name, items = collect.parse_products(read("products-2026-11-15.html"))
        self.assertEqual(name, "parse_state_c")
        self.assertEqual(len(items), 10)
        deal = next(it for it in items if it["price"] < it["list_price"])
        self.assertEqual((deal["sku"], deal["price"], deal["list_price"]), ("PW-101", 56600, 59600))


if __name__ == "__main__":
    unittest.main()
