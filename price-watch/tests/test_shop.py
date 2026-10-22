"""연습몰 서버(shop/) 검사: 같은 날에는 같은 페이지, 정해진 날에 구조 변경, 가격과 소식의 관계."""
import json
import sys
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "shop"))
import market  # noqa: E402
import server  # noqa: E402


class Model(unittest.TestCase):
    def test_same_day_same_page(self):
        for day in (1, 8, 15, 23, 30):
            self.assertEqual(market.products_page(day), market.products_page(day))

    def test_layout_days(self):
        self.assertEqual([market.layout_for(d) for d in (1, 7, 8, 14, 15, 22, 23, 30)],
                         ["A", "A", "B", "B", "C", "C", "D", "D"])

    def test_prices_are_round_and_sane(self):
        for day in range(1, market.MAX_DAY + 1):
            for it in market.catalog(day):
                self.assertEqual(it["price"] % 100, 0)
                self.assertLessEqual(it["price"], it["list_price"])

    def test_one_deal_every_day(self):
        for day in range(1, market.MAX_DAY + 1):
            self.assertEqual(sum(it["deal"] for it in market.catalog(day)), 1)

    def test_promo_follows_news(self):
        audio = [d for d in range(1, 31) if market.catalog(d)[0]["price"] < market.catalog(d)[0]["list_price"] * 0.9]
        self.assertEqual(audio, [12, 13, 14])
        titles = [n["title"] for n in market.news_until(11)]
        self.assertIn("이웃몰 11월 12~14일 오디오 기획전 예고", titles)

    def test_news_only_until_today(self):
        self.assertEqual(len(market.news_until(1)), 1)
        self.assertEqual(len(market.news_until(30)), 10)

    def test_catalog_api_only_from_day_23(self):
        self.assertIsNone(market.catalog_api(22, 1))
        first, second = market.catalog_api(23, 1), market.catalog_api(23, 2)
        self.assertEqual((first["next"], second["next"]), (2, None))
        self.assertEqual(len(first["items"]) + len(second["items"]), 10)

    def test_bad_day(self):
        with self.assertRaises(ValueError):
            market.catalog(31)


class Http(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shop = server.start_shop(0, day=1)
        cls.base = f"http://127.0.0.1:{cls.shop.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.shop.shutdown()
        cls.shop.server_close()

    def get(self, path):
        with urlopen(self.base + path, timeout=5) as r:
            return r.status, dict(r.headers), r.read().decode()

    def set_day(self, day):
        req = Request(self.base + "/admin/day", data=json.dumps({"day": day}).encode(), method="POST")
        with urlopen(req, timeout=5) as r:
            return json.loads(r.read())

    def test_robots_and_terms(self):
        status, _, body = self.get("/robots.txt")
        self.assertEqual(status, 200)
        self.assertIn("Disallow: /admin", body)
        self.assertIn("Crawl-delay: 1", body)
        self.assertIn("1초에 한 번", self.get("/terms")[2])

    def test_day_header_and_429_once(self):
        self.assertEqual(self.set_day(23)["layout"], "D")
        status, headers, _ = self.get("/products")
        self.assertEqual((status, headers["X-Sim-Date"]), (200, "2026-11-23"))
        with self.assertRaises(HTTPError) as ctx:
            self.get("/api/catalog?page=2")
        self.assertEqual((ctx.exception.code, ctx.exception.headers["Retry-After"]), (429, "1"))
        ctx.exception.close()
        self.assertEqual(self.get("/api/catalog?page=2")[0], 200)

    def test_bad_day_is_rejected(self):
        req = Request(self.base + "/admin/day", data=b'{"day": 31}', method="POST")
        with self.assertRaises(HTTPError) as ctx:
            urlopen(req, timeout=5)
        self.assertEqual(ctx.exception.code, 400)
        ctx.exception.close()


if __name__ == "__main__":
    unittest.main()
