"""Claude 설정을 바꾸지 않고 실제 stdio 통신을 검증합니다."""
import asyncio
from hashlib import sha256
from pathlib import Path
import sys
from mcp import Client, StdioServerParameters
ROOT = Path(__file__).resolve().parents[1]

async def check():
    data = ROOT / "fixtures/events.json"
    before = sha256(data.read_bytes()).hexdigest()
    server = StdioServerParameters(command=sys.executable, args=[str(ROOT / "server.py")])
    async with Client(server) as client:
        listed = await client.list_tools()
        assert {tool.name for tool in listed.tools} == {"get_services", "query_events"}
        assert all(tool.annotations.read_only_hint for tool in listed.tools)
        services = await client.call_tool("get_services", {})
        assert not services.is_error
        assert services.structured_content == {"synthetic":True, "services":["billing","catalog","identity"]}
        first = await client.call_tool("query_events", {"service":"billing","offset":0,"limit":2})
        assert first.structured_content["total"] == 3
        assert len(first.structured_content["events"]) == 2
        assert first.structured_content["next_offset"] == 2
        second = await client.call_tool("query_events", {"service":"billing","offset":2,"limit":2})
        assert len(second.structured_content["events"]) == 1
        assert second.structured_content["next_offset"] is None
        missing = await client.call_tool("query_events", {"service":"unknown"})
        assert missing.structured_content["events"] == []
        invalid = await client.call_tool("query_events", {"limit":0})
        assert invalid.is_error
    assert sha256(data.read_bytes()).hexdigest() == before
    print("PASS stdio MCP: 도구 목록·서비스·필터·페이지·빈 결과·입력 오류·원본 파일 불변")

if __name__ == "__main__":
    asyncio.run(check())
