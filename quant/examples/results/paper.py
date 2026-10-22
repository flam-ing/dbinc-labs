"""전략 B(공포·탐욕 25 미만 매수, 75 초과 매도)로 가상 계좌 모의 주문을 하루 한 줄 기록한다.
공개 시세 조회(GET)만 쓰고, 주문 API·API 키는 쓰지 않는다."""
import csv
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UPBIT_URL = "https://api.upbit.com/v1/candles/days"
FNG_URL = "https://api.alternative.me/fng/"
MARKET = "KRW-BTC"
INITIAL = 10_000_000
FEE = 0.0005
BUY_BELOW, SELL_ABOVE = 25, 75
SLEEP = 0.5

LEDGER = Path(__file__).resolve().parent / "paper" / "ledger.csv"
HEADER = ["날짜", "판단", "가격", "수량", "현금", "평가금액"]


def get_json(url, params):
    req = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def latest_closed_candle(today):
    """오늘(UTC) 봉은 미완결이라 빼고, 가장 최근 완결 일봉 (날짜, 종가)."""
    candles = get_json(UPBIT_URL, {"market": MARKET, "count": 3})
    done = []
    for c in candles:
        d = datetime.strptime(c["candle_date_time_utc"], "%Y-%m-%dT%H:%M:%S").date()
        if d < today:
            done.append((d, c["trade_price"]))
    return max(done)


def fng_on(day):
    for r in get_json(FNG_URL, {"limit": 5, "format": "json"})["data"]:
        if datetime.fromtimestamp(int(r["timestamp"]), timezone.utc).date() == day:
            return int(r["value"])
    return None


def read_ledger():
    if not LEDGER.exists():
        return []
    with open(LEDGER, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    today = datetime.now(timezone.utc).date()
    day, price = latest_closed_candle(today)
    time.sleep(SLEEP)
    value = fng_on(day)
    if value is None:
        raise SystemExit(f"{day} 공포·탐욕 지수를 받지 못해 기록하지 않음")

    rows = read_ledger()
    if any(r["날짜"] == day.isoformat() for r in rows):
        print(f"{day}는 이미 기록됨, 다시 적지 않음")
        return

    cash, qty = (float(rows[-1]["현금"]), float(rows[-1]["수량"])) if rows else (float(INITIAL), 0.0)
    if value < BUY_BELOW and cash > 0:
        decision = "매수"
        qty, cash = cash * (1 - FEE) / price, 0.0
    elif value > SELL_ABOVE and qty > 0:
        decision = "매도"
        cash, qty = qty * price * (1 - FEE), 0.0
    else:
        decision = "쉼"

    equity = cash + qty * price
    LEDGER.parent.mkdir(exist_ok=True)
    new = not LEDGER.exists()
    with open(LEDGER, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(HEADER)
        w.writerow([day.isoformat(), decision, f"{price:.0f}", f"{qty:.8f}", f"{cash:.2f}", f"{equity:.2f}"])
    print(f"{day} 공포·탐욕 {value} → {decision} | 가격 {price:,.0f} 수량 {qty:.8f} 현금 {cash:,.0f} 평가금액 {equity:,.0f}")


if __name__ == "__main__":
    main()
