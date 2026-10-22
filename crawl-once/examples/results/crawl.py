"""상품 페이지에서 상품 이름과 가격을 가져오는 크롤러 (표준 라이브러리만 사용)."""

from html.parser import HTMLParser
from urllib.request import Request, urlopen

URL = "https://test-server-8az.pages.dev/"


class ProductParser(HTMLParser):
    """h2.product-title 과 strong#priceTarget 의 텍스트를 수집한다."""

    def __init__(self):
        super().__init__()
        self.name = None
        self.price = None
        self._target = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = (attrs.get("class") or "").split()
        if tag == "h2" and "product-title" in classes:
            self._target = "name"
        elif attrs.get("id") == "priceTarget":
            self._target = "price"

    def handle_endtag(self, tag):
        self._target = None

    def handle_data(self, data):
        if self._target and data.strip():
            setattr(self, self._target, data.strip())


def fetch_product(url=URL):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (crawl.py)"})
    with urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8")
    parser = ProductParser()
    parser.feed(html)
    return parser.name, parser.price


if __name__ == "__main__":
    name, price = fetch_product()
    print(f"상품 이름: {name}")
    print(f"가격: {price}")
