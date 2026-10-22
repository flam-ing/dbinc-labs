"""[정답 예시] 2026-11-08 구조(B) 테스트. 예전 테스트(test_collect.py)는 그대로 두고 새 파일로 더해요."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import collect  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def read(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


class LayoutB(unittest.TestCase):
    """2026-11-08부터: article.card, 행사 상품은 <del>정가</del> <strong>판매가</strong>"""

    def test_cards(self):
        name, items = collect.parse_products(read("products-2026-11-08.html"))
        self.assertEqual(name, "parse_cards_b")
        self.assertEqual(len(items), 10)
        self.assertEqual(items[0], {"sku": "PW-101", "name": "무선 이어폰 A1", "category": "오디오",
                                    "price": 59600, "list_price": 59600})

    def test_deal_uses_strong_not_del(self):
        _, items = collect.parse_products(read("products-2026-11-08.html"))
        deal = next(it for it in items if it["sku"] == "PW-108")
        self.assertEqual((deal["price"], deal["list_price"]), (65600, 69000))


if __name__ == "__main__":
    unittest.main()
