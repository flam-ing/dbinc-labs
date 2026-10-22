"""조회 담당: stdio MCP에서 모든 페이지를 읽어 이벤트 목록을 반환합니다."""
from pathlib import Path
import sys
from mcp import Client, StdioServerParameters

async def fetch_events(server_path):
    server = StdioServerParameters(command=sys.executable, args=[str(Path(server_path).resolve())])
    events, offset = [], 0
    async with Client(server) as client:
        while True:
            result = await client.call_tool("query_events", {"offset": offset, "limit": 3})
            if result.is_error:
                raise RuntimeError(f"query_events failed: {result.content}")
            payload = result.structured_content
            if payload.get("synthetic") is not True:
                raise ValueError("교육용 데이터 여부를 확인할 수 없습니다")
            events.extend(payload["events"])
            following = payload["next_offset"]
            if following is None:
                break
            if following <= offset:
                raise ValueError("페이지 위치가 앞으로 진행하지 않습니다")
            offset = following
    return events
