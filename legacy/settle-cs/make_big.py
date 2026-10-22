"""정산 배치 연습용 주문·상품 CSV를 만들어요. 모두 가상 데이터예요.

같은 --seed를 주면 언제나 같은 파일이 나와요.

  python3 make_big.py --orders 300000 --products 3000 --dir big
  python3 make_big.py --orders 2000 --products 50 --seed 7 --dir data/many

만든 파일: <dir>/orders.csv, <dir>/products.csv
"""
import argparse
import datetime as dt
import random
from pathlib import Path

STORES = ["ST01", "ST02", "ST03", "ST04", "ST05"]
OLD_POS = {"ST03"}  # 구POS 매장(대학로점)은 날짜를 2006/04/03처럼 보내요
MEMOS = ["단순 변심", "행사가", "포장 요청", "재방문 고객", "직원 할인"]


def main():
    parser = argparse.ArgumentParser(description="정산 배치 연습용 가상 CSV 만들기")
    parser.add_argument("--orders", type=int, default=300000, help="주문 줄 수")
    parser.add_argument("--products", type=int, default=3000, help="상품 수")
    parser.add_argument("--seed", type=int, default=1, help="난수 씨앗(같으면 같은 파일)")
    parser.add_argument("--date", default="2006-04-03", help="영업일 yyyy-MM-dd")
    parser.add_argument("--dir", default="big", help="만들 폴더")
    args = parser.parse_args()

    rnd = random.Random(args.seed)
    out = Path(args.dir)
    out.mkdir(parents=True, exist_ok=True)
    biz = dt.datetime.strptime(args.date, "%Y-%m-%d")

    skus = ["P%05d" % i for i in range(1, args.products + 1)]
    # 상품 하나가 하루에 팔리는 양(대략)만큼 재고를 깔아 두어, 일부만 재고 부족에 걸리게 해요
    base = int(args.orders * 2.04 / max(args.products, 1))
    with open(out / "products.csv", "w", encoding="utf-8", newline="\n") as f:
        f.write("sku,name,stock\n")
        for i, sku in enumerate(skus, 1):
            f.write("%s,가상 상품 %d,%d\n" % (sku, i, base + rnd.randint(0, 60)))

    with open(out / "orders.csv", "w", encoding="utf-8", newline="\n") as f:
        f.write("order_id,order_dt,store,pay,sku,qty,unit_price,status,memo\n")
        for n in range(1, args.orders + 1):
            f.write(order_line(rnd, 100000 + n, biz, skus) + "\n")

    print("만들었어요: %s (주문 %d줄), %s (상품 %d개)" % (
        out / "orders.csv", args.orders, out / "products.csv", args.products))


def order_line(rnd, order_id, biz, skus):
    r = rnd.random()
    if r < 0.003:
        # 전송 중에 잘린 줄
        return "%d,%s,ST01" % (order_id, biz.strftime("%Y-%m-%d 10:00"))

    store = rnd.choice(STORES) if rnd.random() > 0.01 else "ST09"
    when = pick_time(rnd, biz)
    fmt = "%Y/%m/%d %H:%M" if store in OLD_POS else "%Y-%m-%d %H:%M"
    pay = rnd.choices(["CARD", "CASH", "POINT"], weights=[60, 25, 15])[0]
    sku = rnd.choice(skus) if rnd.random() > 0.01 else "Z-999"
    qty = str(rnd.randint(1, 5))
    if rnd.random() < 0.01:
        qty = " " + qty  # 손으로 고친 줄
    price = rnd.randrange(100, 3001) * 10
    price_text = str(price)
    if rnd.random() < 0.005:
        price_text = '"{:,}"'.format(price)  # 엑셀로 저장한 줄
    status = rnd.choices(["OK", "RTN", "CXL"], weights=[88, 7, 5])[0]

    m = rnd.random()
    if m < 0.80:
        memo = ""
    elif m < 0.84:
        memo = rnd.choice(["test", "TEST 주문", "테스트용 test"])
    elif m < 0.86:
        memo = '"문앞, 부재시 경비실"'
    else:
        memo = rnd.choice(MEMOS)

    return ",".join([str(order_id), when.strftime(fmt), store, pay, sku, qty, price_text, status, memo])


def pick_time(rnd, biz):
    r = rnd.random()
    if r < 0.80:
        day, hour = biz, rnd.randint(8, 22)
    elif r < 0.85:
        day, hour = biz - dt.timedelta(days=1), 23  # 전날 23시 이후는 다음 영업일
    elif r < 0.90:
        day, hour = biz, 23
    elif r < 0.95:
        day, hour = biz + dt.timedelta(days=1), rnd.randint(8, 22)
    else:
        day, hour = biz - dt.timedelta(days=1), rnd.randint(8, 22)
    return day.replace(hour=hour, minute=rnd.randint(0, 59))


if __name__ == "__main__":
    main()
