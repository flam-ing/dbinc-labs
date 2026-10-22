"""MCP 파이썬 SDK로 server.py에 연결해 서비스별 요청 수와 오류율을 출력합니다."""
import argparse
import asyncio
from collections import Counter
from pathlib import Path
import sys
from mcp import Client, StdioServerParameters
ROOT = Path(__file__).resolve().parents[1]

async def fetch_all_events(client, limit):
    events, offset, pages = [], 0, 0
    while offset is not None:
        result = await client.call_tool("query_events", {"offset": offset, "limit": limit})
        if result.is_error:
            raise RuntimeError(f"query_events 실패 (offset={offset})")
        page = result.structured_content
        events.extend(page["events"])
        offset = page["next_offset"]
        pages += 1
    if len(events) != page["total"]:
        raise RuntimeError(f"이벤트 수 불일치: {len(events)} != total {page['total']}")
    return events, pages

def print_table(events):
    requests = Counter(event["service"] for event in events)
    errors = Counter(event["service"] for event in events if event["status"] >= 500)
    print(f"{'service':<10} {'requests':>8} {'errors':>6} {'error_rate':>10}")
    print("-" * 37)
    for service in sorted(requests):
        rate = errors[service] / requests[service]
        print(f"{service:<10} {requests[service]:>8} {errors[service]:>6} {rate:>10.1%}")
    print("-" * 37)
    total_errors = sum(errors.values())
    print(f"{'TOTAL':<10} {len(events):>8} {total_errors:>6} {total_errors / len(events):>10.1%}")

async def main(limit):
    server = StdioServerParameters(command=sys.executable, args=[str(ROOT / "server.py")])
    async with Client(server) as client:
        events, pages = await fetch_all_events(client, limit)
    print(f"query_events {pages}페이지(limit={limit})로 이벤트 {len(events)}건 수집 · 오류 기준: status >= 500\n")
    print_table(events)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=100, help="페이지 크기 (1~100)")
    asyncio.run(main(parser.parse_args().limit))
