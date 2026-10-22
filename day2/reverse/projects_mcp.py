"""projects_cli.py를 MCP 도구로 내놓는 로컬 stdio MCP 서버입니다.

실습 폴더의 server.py와 같은 방식(MCPServer, 읽기 전용 표시, ToolError)으로 만들었어요.
CLI가 하던 일을 그대로 부르기만 해서, 에이전트가 화면 없이 연습 서버의 목록을 읽게 돼요.
내 PC의 교육용 연습 서버(기본 http://127.0.0.1:8765)만 부릅니다.
"""
from typing import Any
from typing_extensions import TypedDict
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
import projects_cli

mcp = MCPServer("DB Inc practice projects")
READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False,
                            idempotent_hint=True, open_world_hint=False)


class PageResult(TypedDict):
    synthetic: bool
    page: int
    items: list[dict[str, Any]]
    next_page: int | None
    source_url: str


class AllResult(TypedDict):
    synthetic: bool
    pages: int
    items: list[dict[str, Any]]
    duplicates: list[str]
    source: str


@mcp.tool(annotations=READ_ONLY)
def list_projects(page: int = 1) -> PageResult:
    """교육용 연습 서버의 가상 프로젝트 목록을 한 쪽 읽습니다. next_page가 null이면 마지막 쪽입니다. 사내 데이터가 아닙니다."""
    try:
        return projects_cli.fetch_page(page)
    except (ValueError, RuntimeError) as error:
        raise ToolError(str(error)) from None


@mcp.tool(annotations=READ_ONLY)
def list_all_projects() -> AllResult:
    """교육용 연습 서버의 모든 쪽을 차례로 읽고, id가 겹치는 항목은 처음 본 것만 돌려줍니다."""
    try:
        return projects_cli.fetch_all()
    except (ValueError, RuntimeError) as error:
        raise ToolError(str(error)) from None


if __name__ == "__main__":
    mcp.run(transport="stdio")
