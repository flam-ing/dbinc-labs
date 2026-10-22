"""업비트 KRW-BTC 일봉 2년치 + 공포·탐욕 지수를 날짜로 합쳐 data/btc.csv로 저장한다."""
import csv
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

UPBIT_URL = "https://api.upbit.com/v1/candles/days"
FNG_URL = "https://api.alternative.me/fng/"
MARKET = "KRW-BTC"
DAYS = 730
PAGE = 200  # 업비트 일봉 요청 1회 최대 개수
SLEEP = 0.5

OUT_DIR = Path(__file__).resolve().parent / "data"


def get_json(url, params):
    req = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fetch_upbit(first_day, last_day):
    """first_day~last_day(UTC 날짜, 완결된 봉만) 범위의 {날짜: (종가, 거래대금)}."""
    rows = {}
    to = None
    while True:
        params = {"market": MARKET, "count": PAGE}
        if to:
            params["to"] = to
        page = get_json(UPBIT_URL, params)
        time.sleep(SLEEP)
        if not page:
            break
        for c in page:
            d = datetime.strptime(c["candle_date_time_utc"], "%Y-%m-%dT%H:%M:%S").date()
            if first_day <= d <= last_day:
                rows[d] = (c["trade_price"], c["candle_acc_trade_price"])
        oldest = min(c["candle_date_time_utc"] for c in page)
        if datetime.strptime(oldest, "%Y-%m-%dT%H:%M:%S").date() <= first_day:
            break
        to = oldest + "Z"
    return rows


def fetch_fng(first_day, last_day):
    # limit=0 은 전체 이력. 범위는 아래에서 직접 자른다.
    data = get_json(FNG_URL, {"limit": 0, "format": "json"})["data"]
    time.sleep(SLEEP)
    out = {}
    for r in data:
        d = datetime.fromtimestamp(int(r["timestamp"]), timezone.utc).date()
        if first_day <= d <= last_day:
            out[d] = int(r["value"])
    return out


def main():
    fetched_at = datetime.now(timezone.utc)
    today = fetched_at.date()  # 업비트 일봉은 00:00 UTC(09:00 KST) 기준, 오늘 봉은 미완결
    last_day = today - timedelta(days=1)
    first_day = last_day - timedelta(days=DAYS - 1)

    prices = fetch_upbit(first_day, last_day)
    fng = fetch_fng(first_day, last_day)

    days = sorted(prices.keys() & fng.keys())
    OUT_DIR.mkdir(exist_ok=True)
    with open(OUT_DIR / "btc.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["날짜", "종가", "거래대금", "공포탐욕지수"])
        for d in days:
            close, value = prices[d]
            w.writerow([d.isoformat(), f"{close:.0f}", f"{value:.0f}", fng[d]])

    local = fetched_at.astimezone()
    (OUT_DIR / "SOURCE.md").write_text(
        "# 데이터 출처\n\n"
        f"- 받은 시각: {fetched_at:%Y-%m-%d %H:%M:%S} UTC ({local:%Y-%m-%d %H:%M:%S %z})\n"
        f"- 기간: {days[0]} ~ {days[-1]} (UTC 날짜 기준, 오늘 {today} 봉은 미완결이라 제외), {len(days)}행\n"
        f"- 종가·거래대금: 업비트 공개 API `{UPBIT_URL}?market={MARKET}` "
        "(trade_price, candle_acc_trade_price; 원화, 일봉은 09:00 KST 시작)\n"
        f"- 공포·탐욕 지수: alternative.me `{FNG_URL}`\n"
        "- 합치기: 날짜(UTC)로 inner join. 한쪽에만 있는 날은 제외\n"
        "- 생성: fetch.py\n",
        encoding="utf-8",
    )
    print(f"upbit {len(prices)}일, fng {len(fng)}일, 저장 {len(days)}행")


if __name__ == "__main__":
    main()
