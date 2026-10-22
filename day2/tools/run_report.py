"""조회·가공·보고서 모듈을 연결하고 실습 계약을 확인합니다."""
import argparse
import asyncio
import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

async def run(args):
    modules = Path(args.modules).resolve()
    # --query를 주면 조회 모듈만 그 파일로 바꾸고, 가공·보고서는 --modules 폴더의 것을 써요.
    query = load("lab_query", Path(args.query).resolve() if args.query else modules / "query.py")
    process = load("lab_process", modules / "process.py")
    report = load("lab_render", modules / "report.py")
    aggregate = load("lab_aggregate", Path(args.impl).resolve())
    events = await query.fetch_events(ROOT / "server.py")
    assert len(events) == 8, "페이지를 끝까지 읽으면 이벤트는 8건입니다"
    assert len({event["id"] for event in events}) == 8, "이벤트가 중복되었습니다"
    summaries = process.build_summaries(events, aggregate.summarize)
    assert [row["service"] for row in summaries] == ["all", "billing", "catalog", "identity"]
    assert summaries[0] == {"service":"all","total":8,"error_count":3,"error_rate_pct":37.5,"slow_count":4,"average_ms":411.12}
    text = report.render_report(summaries)
    assert "교육용" in text and "|" in text and "billing" in text, "교육용 안내와 서비스 표가 필요합니다"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(f"PASS 조회→가공→보고서: 8건 / 오류 3건 / 500ms 이상 4건")
    print(f"보고서: {output}")
    if args.query:
        print(f"조회 모듈: {args.query}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--modules", default="integration/reference")
    parser.add_argument("--impl", default="reference/report.py")
    parser.add_argument("--output", default="artifacts/day2-report.md")
    parser.add_argument("--query", help="조회 모듈(fetch_events) 파일만 따로 지정 (예: work/integration/query.py)")
    asyncio.run(run(parser.parse_args()))
