"""교육용 '운영 도구' MCP 서버입니다. 권한 규칙으로 쓰기·삭제를 막는 연습에 써요.

사내 시스템의 MCP 서버에는 조회 도구만 있는 게 아니라 고치고 지우는 도구도 있어요.
이 서버는 일부러 삭제 도구(delete_event)를 하나 넣어 두었어요. 지우는 대상은
work/admin/events.json(fixtures/events.json의 사본) 하나뿐이고, 원본 fixture는 건드리지 않아요.

사람이 터미널에서 쓰는 명령 (실습 폴더 맨 위에서)
  python permissions/admin_server.py --status   # 사본에 남은 이벤트 보기
  python permissions/admin_server.py --reset    # 사본을 원본 8건으로 되돌리기
옵션 없이 실행하면 stdio MCP 서버로 입력을 기다려요. Claude Code가 띄우는 방식이에요.
"""
import argparse
import json
import os
import shutil
from pathlib import Path
from typing_extensions import TypedDict
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "fixtures/events.json"
mcp = MCPServer("DB Inc training admin")
READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False,
                            idempotent_hint=True, open_world_hint=False)
DESTRUCTIVE = ToolAnnotations(read_only_hint=False, destructive_hint=True,
                              idempotent_hint=False, open_world_hint=False)


class CountResult(TypedDict):
    synthetic: bool
    file: str
    total: int
    ids: list[str]


class DeleteResult(TypedDict):
    synthetic: bool
    file: str
    deleted: str
    remaining: int


def data_file():
    # 검사 스크립트는 ADMIN_EVENTS_FILE로 임시 파일을 쓰게 해서 실습 사본을 건드리지 않아요.
    return Path(os.environ.get("ADMIN_EVENTS_FILE") or ROOT / "work/admin/events.json")


def shown(path):
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def reset():
    path = data_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, path)
    return path


def load():
    path = data_file()
    if not path.exists():
        reset()
    return path, json.loads(path.read_text(encoding="utf-8"))


@mcp.tool(annotations=READ_ONLY)
def count_events() -> CountResult:
    """운영 사본(work/admin/events.json)에 남은 교육용 이벤트 수와 id를 조회합니다. 파일을 바꾸지 않습니다."""
    path, events = load()
    return {"synthetic": True, "file": shown(path), "total": len(events), "ids": [e["id"] for e in events]}


@mcp.tool(annotations=DESTRUCTIVE)
def delete_event(event_id: str) -> DeleteResult:
    """운영 사본(work/admin/events.json)에서 이벤트 하나를 지웁니다. 되돌리는 도구는 없습니다."""
    if not isinstance(event_id, str) or not event_id.strip():
        raise ToolError("event_id must be non-empty")
    path, events = load()
    kept = [e for e in events if e["id"] != event_id.strip()]
    if len(kept) == len(events):
        raise ToolError(f"없는 이벤트입니다: {event_id}")
    path.write_text(json.dumps(kept, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"synthetic": True, "file": shown(path), "deleted": event_id.strip(), "remaining": len(kept)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="교육용 운영 도구 MCP 서버")
    parser.add_argument("--status", action="store_true", help="사본에 남은 이벤트를 보여 줘요")
    parser.add_argument("--reset", action="store_true", help="사본을 원본 8건으로 되돌려요")
    args = parser.parse_args()
    if args.reset:
        restored = reset()
        print(f"되돌렸어요: {shown(restored)} {len(json.loads(restored.read_text(encoding='utf-8')))}건")
    elif args.status:
        info = count_events()
        print(f"{info['file']}: {info['total']}건 ({', '.join(info['ids'])})")
    else:
        mcp.run(transport="stdio")
