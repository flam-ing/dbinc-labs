"""교육용 고정 JSON만 읽는 로컬 stdio MCP 서버."""
import json
from typing import Any
from typing_extensions import TypedDict
from pathlib import Path
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "fixtures/events.json"
mcp = MCPServer("DB Inc training events")
READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False,
                            idempotent_hint=True, open_world_hint=False)

class ServicesResult(TypedDict):
    synthetic: bool
    services: list[str]

class EventsResult(TypedDict):
    synthetic: bool
    events: list[dict[str, Any]]
    total: int
    next_offset: int | None

def load_events():
    return json.loads(DATA.read_text(encoding="utf-8"))

@mcp.tool(annotations=READ_ONLY)
def get_services() -> ServicesResult:
    """교육용 가상 데이터에 있는 서비스 이름을 조회합니다. 사내 데이터가 아닙니다."""
    return {"synthetic": True, "services": sorted({event["service"] for event in load_events()})}

@mcp.tool(annotations=READ_ONLY)
def query_events(service: str | None = None, offset: int = 0, limit: int = 100) -> EventsResult:
    """고정 교육용 이벤트를 읽습니다. 이름 필터와 페이지 조회만 지원하며 파일을 수정하지 않습니다."""
    if type(offset) is not int or offset < 0:
        raise ToolError("offset must be a non-negative integer")
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ToolError("limit must be from 1 to 100")
    if service is not None and (not isinstance(service, str) or not service.strip()):
        raise ToolError("service must be non-empty")
    events = load_events()
    if service is not None:
        events = [event for event in events if event["service"] == service.strip()]
    rows = events[offset:offset + limit]
    following = offset + len(rows)
    return {"synthetic": True, "events": rows, "total": len(events),
            "next_offset": following if following < len(events) else None}

if __name__ == "__main__":
    mcp.run(transport="stdio")
