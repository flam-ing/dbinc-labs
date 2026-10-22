"""지식베이스를 점검하고, LLM 위키(kb/wiki/)의 "숫자" 부분을 다시 써요.

  python3 tools/curate.py           # 점검하고 위키 숫자 갱신
  python3 tools/curate.py --check   # 점검만. 중복이나 이상한 행이 있으면 종료 코드 1

위키 페이지에서 <!-- curate:start -->와 <!-- curate:end --> 사이만 이 스크립트가 다시 써요.
그 밖의 부분(메모)은 사람과 Claude가 쓰는 곳이라 건드리지 않아요.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kbtools import KB, load_news, load_prices, load_runs, pct, series, won  # noqa: E402

START, END = "<!-- curate:start -->", "<!-- curate:end -->"


def check(rows: list[dict], runs: list[dict]) -> dict:
    keys = Counter((r["date"], r["sku"]) for r in rows)
    duplicates = sorted(k for k, n in keys.items() if n > 1)
    bad = [r for r in rows if r["price"] <= 0 or r["list_price"] < r["price"]]
    dates = sorted({r["date"] for r in rows})
    missing = []
    if dates:
        d, last = date.fromisoformat(dates[0]), date.fromisoformat(dates[-1])
        while d <= last:
            if d.isoformat() not in dates:
                missing.append(d.isoformat())
            d += timedelta(days=1)
    failures = [r for r in runs if r.get("status") != "ok"]
    return {"rows": len(rows), "dates": dates, "duplicates": duplicates, "bad": bad,
            "missing": missing, "failures": failures}


def list_price_changes(points: list[dict]) -> list[tuple]:
    out = []
    for prev, cur in zip(points, points[1:]):
        if cur["list_price"] != prev["list_price"]:
            out.append((cur["date"], prev["list_price"], cur["list_price"]))
    return out


def discount_runs(points: list[dict]) -> list[tuple]:
    """판매가가 정가보다 낮았던 날을 이어진 기간으로 묶어요. (시작, 끝, 할인율)"""
    out = []
    for p in points:
        if p["price"] >= p["list_price"]:
            continue
        rate = round(-pct(p["list_price"], p["price"]))
        if out and out[-1][2] == rate and date.fromisoformat(p["date"]) - date.fromisoformat(out[-1][1]) == timedelta(days=1):
            out[-1] = (out[-1][0], p["date"], rate)
        else:
            out.append((p["date"], p["date"], rate))
    return out


def product_numbers(points: list[dict]) -> str:
    first, last = points[0], points[-1]
    low = min(points, key=lambda p: (p["price"], p["date"]))
    high = min(points, key=lambda p: (-p["price"], p["date"]))
    lines = [
        "| 항목 | 값 |",
        "| --- | --- |",
        f"| 관측 기간 | {first['date']} ~ {last['date']} ({len(points)}일) |",
        f"| 마지막 판매가 | {won(last['price'])} (정가 {won(last['list_price'])}) |",
        f"| 판매가 최저 | {won(low['price'])} ({low['date']}) |",
        f"| 판매가 최고 | {won(high['price'])} ({high['date']}) |",
        "",
        "정가가 바뀐 날",
    ]
    changes = list_price_changes(points)
    lines += [f"- {d}: {won(a)} → {won(b)} ({pct(a, b):+.1f}%)" for d, a, b in changes] or ["- 없어요"]
    lines += ["", "정가보다 싸게 판 날(할인율)"]
    runs = discount_runs(points)
    lines += [f"- {s}{'' if s == e else ' ~ ' + e}: {r}%" for s, e, r in runs] or ["- 없어요"]
    return "\n".join(lines)


def replace_block(text: str, block: str) -> str:
    if START in text and END in text:
        head, rest = text.split(START, 1)
        _, tail = rest.split(END, 1)
        return f"{head}{START}\n{block}\n{END}{tail}"
    return text.rstrip() + f"\n\n{START}\n{block}\n{END}\n"


def product_page(path: Path, sku: str, name: str, category: str, block: str) -> None:
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = (f"# {sku} {name}\n\n분류: {category}\n\n"
                "\"숫자\" 부분은 tools/curate.py가 다시 써요. \"메모\" 부분은 사람과 Claude가 써요.\n\n"
                f"## 숫자\n\n{START}\n{END}\n\n"
                "## 메모\n\n"
                "아직 없어요. 가격이 크게 바뀐 날의 까닭을 근거(소식 id, 날짜)와 함께 적어요.\n")
    path.write_text(replace_block(text, block), encoding="utf-8")


def quality_page(result: dict, news_count: int) -> str:
    dates = result["dates"]
    span = f"{dates[0]} ~ {dates[-1]} ({len(dates)}일)" if dates else "기록 없음"
    lines = [
        "# 데이터 점검 결과",
        "",
        "이 파일은 tools/curate.py가 통째로 다시 써요. 손으로 고치지 않아요.",
        "",
        "| 항목 | 값 |",
        "| --- | --- |",
        f"| 가격 기록 | {result['rows']}행 |",
        f"| 관측 기간 | {span} |",
        f"| 소식 | {news_count}건 |",
        f"| 같은 날 같은 상품이 두 번 | {len(result['duplicates'])}건 |",
        f"| 판매가가 0 이하이거나 정가보다 비싼 행 | {len(result['bad'])}건 |",
        f"| 빠진 날 | {len(result['missing'])}일 |",
        f"| 수집 실패 기록 | {len(result['failures'])}번 |",
        "",
        "수집 실패 기록",
    ]
    for r in result["failures"]:
        lines.append(f"- {r.get('date') or '날짜 모름'} · {r.get('kind', 'error')} · {r.get('error', '')}")
    if not result["failures"]:
        lines.append("- 없어요")
    if result["missing"]:
        lines += ["", "빠진 날", *[f"- {d}" for d in result["missing"]]]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--kb", type=Path, default=KB)
    parser.add_argument("--check", action="store_true", help="점검만 하고 위키는 고치지 않아요")
    args = parser.parse_args(argv)
    rows, news, runs = load_prices(args.kb), load_news(args.kb), load_runs(args.kb)
    result = check(rows, runs)
    problems = len(result["duplicates"]) + len(result["bad"])
    summary = (f"가격 {result['rows']}행 · {len(result['dates'])}일 · 소식 {len(news)}건 · 중복 {len(result['duplicates'])}"
               f" · 이상한 행 {len(result['bad'])} · 빠진 날 {len(result['missing'])} · 수집 실패 {len(result['failures'])}번")
    if args.check:
        print(("점검 통과: " if not problems else "점검 실패: ") + summary)
        return 1 if problems else 0
    if not rows:
        print("가격 기록이 없어요. 먼저 python3 collect.py로 모아요.")
        return 1
    wiki = args.kb / "wiki"
    (wiki / "products").mkdir(parents=True, exist_ok=True)
    groups = series(rows)
    for sku, points in groups.items():
        last = points[-1]
        product_page(wiki / "products" / f"{sku}.md", sku, last["name"], last["category"], product_numbers(points))
    (wiki / "quality.md").write_text(quality_page(result, len(news)), encoding="utf-8")
    index = wiki / "index.md"
    if index.exists():
        table = ["| 상품 | 이름 | 분류 | 마지막 판매가 |", "| --- | --- | --- | ---: |"]
        for sku, points in groups.items():
            last = points[-1]
            table.append(f"| [{sku}](products/{sku}.md) | {last['name']} | {last['category']} | {won(last['price'])} |")
        index.write_text(replace_block(index.read_text(encoding="utf-8"), "\n".join(table)), encoding="utf-8")
    print(f"위키를 고쳤어요: 상품 페이지 {len(groups)}개, quality.md · {summary}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
