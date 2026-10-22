"""지식베이스와 예측 결과로 리포트(out/report.md)를 만들어요.

  python3 tools/report.py

리포트의 숫자는 모두 이 스크립트가 kb/ 파일에서 계산한 값이에요. 같은 kb/로 다시 돌리면 같은 리포트가 나와요.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import forecast  # noqa: E402
from curate import discount_runs, list_price_changes  # noqa: E402
from kbtools import KB, ROOT, load_news, load_prices, load_runs, pct, series, won  # noqa: E402

LOOKBACK_DAYS = 7


def related_news(news: list[dict], category: str, when: str, days: int = LOOKBACK_DAYS) -> list[dict]:
    """when 날짜 앞 days일 안에 나온 소식 중 태그에 이 분류가 있는 것만 골라요."""
    end = date.fromisoformat(when)
    start = (end - timedelta(days=days)).isoformat()
    return [n for n in news if start <= n["date"] < when and category in n.get("tags", [])]


def cite(items: list[dict]) -> str:
    return "; ".join(f"{n['id']} {n['date'][5:]} {n['title']}" for n in items) or "없음"


def build(kb: Path = KB) -> tuple[str, dict]:
    rows, news, runs = load_prices(kb), load_news(kb), load_runs(kb)
    groups = series(rows)
    fc = forecast.run(kb)
    dates = sorted({r["date"] for r in rows})
    out = [
        "# 연습몰 가격 추적 리포트",
        "",
        "교육용 가상 데이터예요. 실제 상품과 가격이 아니에요.",
        "",
        f"- 기준일: {fc['base_date']}",
        f"- 관측: {dates[0]} ~ {dates[-1]} ({len(dates)}일), 상품 {len(groups)}개, 가격 기록 {len(rows)}행, 소식 {len(news)}건",
        f"- 수집 실패: {sum(1 for r in runs if r.get('status') != 'ok')}번 (자세한 내용은 kb/wiki/selector-changes.md)",
        "",
        "## 상품별 요약",
        "",
        "| 상품 | 이름 | 오늘 판매가 | 7일 평균 | 14일 추세(원/일) | 추세선 7일 뒤 | 주의 |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for p in fc["products"]:
        out.append(f"| {p['sku']} | {p['name']} | {won(p['today'])} | {won(p['ma7'])} | {p['slope_per_day']:+,.1f} | "
                   f"{won(p['linear'][-1])} | {', '.join(p['warnings']) or '-'} |")
    out += ["", "## 정가가 바뀐 날과 그 앞 7일의 관련 소식", "",
            "| 날짜 | 상품 | 정가 변화 | 앞 7일 관련 소식 |", "| --- | --- | --- | --- |"]
    for sku, points in groups.items():
        category = points[-1]["category"]
        for when, before, after in list_price_changes(points):
            out.append(f"| {when} | {sku} | {won(before)} → {won(after)} ({pct(before, after):+.1f}%) | "
                       f"{cite(related_news(news, category, when))} |")
    out += ["", "## 사흘 이상 이어진 할인과 그 앞 7일의 관련 소식", "",
            "| 기간 | 상품 | 할인율 | 앞 7일 관련 소식 |", "| --- | --- | ---: | --- |"]
    for sku, points in groups.items():
        category = points[-1]["category"]
        for start, end, rate in discount_runs(points):
            length = (date.fromisoformat(end) - date.fromisoformat(start)).days + 1
            if length >= 3:
                out.append(f"| {start} ~ {end} | {sku} | {rate}% | {cite(related_news(news, category, start))} |")
    b = fc["backtest"]
    out += ["", "## 예측 방법과 되돌아보기", "",
            "세 방법 모두 판매가만 써요. 소식은 계산에 넣지 않고, 행사 예고 기간이 겹치면 \"주의\"에 적어요.", ""]
    if b:
        out += [f"{b['hidden'][0]} ~ {b['hidden'][1]}을 가리고 그 앞 기록만으로 맞혀 본 평균 오차율이에요.", "",
                "| 방법 | 평균 오차율 |", "| --- | ---: |",
                f"| 그대로(마지막 값) | {b['naive']}% |", f"| 7일 평균 | {b['ma7']}% |", f"| 14일 추세선 | {b['linear']}% |", ""]
        flagged = [p for p in fc["products"] if p.get("backtest_warnings")]
        if flagged:
            out.append("가린 기간에 행사가 겹친 상품: " + ", ".join(
                f"{p['sku']}({', '.join(p['backtest_warnings'])})" for p in flagged))
            out.append("")
    out += ["## 이 리포트가 말하지 않는 것", "",
            "- 소식과 가격이 같은 시기에 움직인 것을 나란히 보여 줄 뿐, 소식 때문에 가격이 바뀌었다고 증명하지 않아요.",
            "- 추세선은 지난 14일이 그대로 이어진다고 가정해요. 행사, 신제품, 품절은 미리 알 수 없어요.",
            "- 오차율은 지난 7일 한 번으로 잰 값이에요. 기간이 바뀌면 순위도 바뀔 수 있어요.",
            ""]
    return "\n".join(out), fc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--kb", type=Path, default=KB)
    parser.add_argument("--out", type=Path, default=ROOT / "out")
    args = parser.parse_args(argv)
    text, fc = build(args.kb)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "report.md").write_text(text, encoding="utf-8")
    (args.out / "forecast.json").write_text(json.dumps(fc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"리포트를 만들었어요: out/report.md · 기준일 {fc['base_date']} · 상품 {len(fc['products'])}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
