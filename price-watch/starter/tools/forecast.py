"""쌓인 판매가로 앞으로 7일의 추이를 계산해요. 추이를 읽는 연습용이에요.

  python3 tools/forecast.py          # 표를 보여 주고 out/forecast.json을 써요

쓰는 방법은 셋이고, 모두 손으로 다시 계산할 수 있어요.
- 그대로: 마지막 판매가가 이어진다고 봐요.
- 7일 평균: 최근 7일 판매가의 평균이 이어진다고 봐요.
- 추세선: 최근 14일 판매가에 직선 하나를 맞추고(최소제곱법) 그 선을 7일 더 그어요.

되돌아보기(백테스트): 마지막 7일을 가린 채 같은 방법으로 맞혀 보고, 실제와 몇 % 차이 났는지 봐요.
소식에 "OO월 OO~OO일 ... 예고"가 있고 그 기간이 앞으로 7일과 겹치면 주의 표시를 붙여요.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kbtools import KB, ROOT, load_news, load_prices, series  # noqa: E402

HORIZON = 7
WINDOW = 14
PROMO_RANGE = re.compile(r"(\d{1,2})월 (\d{1,2})~(\d{1,2})일")


def moving_average(values: list[float], n: int = 7) -> float:
    tail = values[-n:]
    return sum(tail) / len(tail)


def linear_fit(values: list[float]) -> tuple[float, float]:
    """x = 0, 1, 2, ... 에 대한 최소제곱 직선의 (기울기, 절편)."""
    n = len(values)
    if n < 2:
        return 0.0, float(values[0])
    mean_x = (n - 1) / 2
    mean_y = sum(values) / n
    sxx = sum((x - mean_x) ** 2 for x in range(n))
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in enumerate(values))
    slope = sxy / sxx
    return slope, mean_y - slope * mean_x


def predict(values: list[float], method: str, horizon: int = HORIZON, window: int = WINDOW) -> list[float]:
    if method == "naive":
        return [float(values[-1])] * horizon
    if method == "ma7":
        return [moving_average(values, 7)] * horizon
    if method == "linear":
        tail = values[-window:]
        slope, intercept = linear_fit(tail)
        return [intercept + slope * (len(tail) - 1 + h) for h in range(1, horizon + 1)]
    raise ValueError(method)


def mape(actual: list[float], predicted: list[float]) -> float:
    """평균 절대 오차율(%): 날마다 |실제-예측|/실제를 구해 평균 내요."""
    return sum(abs(a - p) / a for a, p in zip(actual, predicted)) / len(actual) * 100


def promo_windows(news: list[dict], year: int) -> list[dict]:
    """경쟁사 행사 예고 소식에서 기간과 분류를 꺼내요. 제목의 "12월 3~5일" 같은 글자를 읽어요."""
    out = []
    for n in news:
        if "경쟁사행사" not in n.get("tags", []):
            continue
        m = PROMO_RANGE.search(n["title"])
        if not m:
            continue
        month, first, last = map(int, m.groups())
        out.append({"news_id": n["id"], "title": n["title"],
                    "start": date(year, month, first).isoformat(), "end": date(year, month, last).isoformat(),
                    "categories": [t for t in n["tags"] if t != "경쟁사행사"]})
    return out


def overlaps(window: dict, first: str, last: str, category: str) -> bool:
    return category in window["categories"] and not (window["end"] < first or window["start"] > last)


def run(kb: Path = KB, horizon: int = HORIZON) -> dict:
    rows = load_prices(kb)
    if not rows:
        raise SystemExit("가격 기록이 없어요. 먼저 python3 collect.py로 모아요.")
    groups = series(rows)
    base = max(r["date"] for r in rows)
    base_day = date.fromisoformat(base)
    first = (base_day + timedelta(days=1)).isoformat()
    last = (base_day + timedelta(days=horizon)).isoformat()
    windows = promo_windows(load_news(kb), base_day.year)
    products, totals = [], {"naive": [], "ma7": [], "linear": []}
    for sku, points in groups.items():
        values = [p["price"] for p in points]
        info = points[-1]
        slope, _ = linear_fit(values[-WINDOW:])
        item = {
            "sku": sku, "name": info["name"], "category": info["category"],
            "observed": len(values), "today": values[-1],
            "ma7": round(moving_average(values, 7)),
            "slope_per_day": round(slope, 1),
            "linear": [round(v) for v in predict(values, "linear", horizon)],
            "warnings": [f"{w['start'][5:]}~{w['end'][5:]} 행사 예고({w['news_id']})"
                         for w in windows if overlaps(w, first, last, info["category"])],
        }
        if len(values) >= horizon + 7:
            train, actual = values[:-horizon], values[-horizon:]
            back = {m: round(mape(actual, predict(train, m, horizon)), 2) for m in totals}
            for m in totals:
                totals[m].append(back[m])
            cut_first = points[-horizon]["date"]
            item["backtest"] = back
            item["backtest_warnings"] = [f"{w['start'][5:]}~{w['end'][5:]} 행사({w['news_id']})"
                                         for w in windows if overlaps(w, cut_first, base, info["category"])]
        products.append(item)
    backtest = None
    if totals["naive"]:
        backtest = {
            "hidden": [groups[next(iter(groups))][-horizon]["date"], base],
            **{m: round(sum(v) / len(v), 2) for m, v in totals.items()},
        }
    return {"synthetic": True, "base_date": base, "horizon": [first, last], "window": WINDOW,
            "products": products, "backtest": backtest}


def show(result: dict) -> str:
    lines = [f"기준일 {result['base_date']} · 앞으로 7일 {result['horizon'][0]} ~ {result['horizon'][1]}",
             "상품   | 오늘 판매가 | 7일 평균 | 추세(원/일) | 추세선 7일 뒤 | 주의"]
    for p in result["products"]:
        lines.append(f"{p['sku']} | {p['today']:>10,} | {p['ma7']:>8,} | {p['slope_per_day']:>+10,.1f} | "
                     f"{p['linear'][-1]:>12,} | " + (", ".join(p["warnings"]) or "-"))
    b = result["backtest"]
    if b:
        lines.append(f"되돌아보기({b['hidden'][0]}~{b['hidden'][1]}을 가리고 맞혀 보기) 평균 오차율: "
                     f"그대로 {b['naive']}% · 7일 평균 {b['ma7']}% · 추세선 {b['linear']}%")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--kb", type=Path, default=KB)
    parser.add_argument("--out", type=Path, default=ROOT / "out" / "forecast.json")
    args = parser.parse_args(argv)
    result = run(args.kb)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(show(result))
    print(f"저장: {args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
