"""[정답 예시] 2026-11-23 구조(D) 테스트. 예전 테스트(test_collect.py)는 그대로 두고 새 파일로 더해요."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import collect  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def read(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


class FakeFetcher:
    def __init__(self):
        self.paths = []

    def get(self, path):
        self.paths.append(path)
        page = path.rsplit("=", 1)[1]
        return read(f"catalog-2026-11-23-p{page}.json"), {}


class LayoutD(unittest.TestCase):
    """2026-11-23부터: HTML은 빈 껍데기, /api/catalog?page=N을 next가 null일 때까지"""

    def test_shell_is_detected(self):
        html = read("products-2026-11-23.html")
        self.assertEqual(collect.parse_products(html), (None, []))
        self.assertTrue(collect.is_app_shell_d(html))

    def test_reads_all_pages(self):
        fetcher = FakeFetcher()
        items = collect.fetch_catalog_d(fetcher)
        self.assertEqual(fetcher.paths, ["/api/catalog?page=1", "/api/catalog?page=2"])
        self.assertEqual(len(items), 10)
        self.assertEqual(len({it["sku"] for it in items}), 10)
        deal = next(it for it in items if it["price"] < it["list_price"])
        self.assertEqual((deal["sku"], deal["price"], deal["list_price"]), ("PW-108", 68800, 72400))


if __name__ == "__main__":
    unittest.main()
