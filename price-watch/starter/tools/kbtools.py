"""지식베이스(kb/) 파일을 읽는 공용 함수예요. curate.py, forecast.py, report.py가 같이 써요."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "kb"


def load_prices(kb: Path = KB) -> list[dict]:
    path = kb / "prices.csv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["price"] = int(r["price"])
        r["list_price"] = int(r["list_price"])
    return rows


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_news(kb: Path = KB) -> list[dict]:
    return sorted(load_jsonl(kb / "news.jsonl"), key=lambda n: (n["date"], n["id"]))


def load_runs(kb: Path = KB) -> list[dict]:
    return load_jsonl(kb / "runs.jsonl")


def series(rows: list[dict]) -> dict[str, list[dict]]:
    """상품 코드별로 날짜순 기록을 모아요. 같은 날 기록이 둘이면 먼저 들어온 것을 써요."""
    out: dict[str, dict[str, dict]] = {}
    for r in rows:
        out.setdefault(r["sku"], {}).setdefault(r["date"], r)
    return {sku: [days[d] for d in sorted(days)] for sku, days in sorted(out.items())}


def won(value: float) -> str:
    return f"{int(round(value)):,}원"


def pct(before: float, after: float) -> float:
    return (after - before) / before * 100 if before else 0.0
