"""permissions/의 운영 도구 MCP 서버와 권한 규칙 도우미를 임시 파일로 확인합니다.

실습 사본(work/admin/events.json)과 .claude/settings.json은 건드리지 않아요. Claude 설정도 바꾸지 않아요.
  python tools/smoke_admin.py
"""
import asyncio
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from mcp import Client, StdioServerParameters

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "fixtures/events.json"


async def check_server(data):
    server = StdioServerParameters(command=sys.executable, args=[str(ROOT / "permissions/admin_server.py")],
                                   env={"ADMIN_EVENTS_FILE": str(data)})
    async with Client(server) as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}
        assert set(tools) == {"count_events", "delete_event"}
        assert tools["count_events"].annotations.read_only_hint
        assert tools["delete_event"].annotations.destructive_hint
        before = await client.call_tool("count_events", {})
        assert before.structured_content["total"] == 8
        deleted = await client.call_tool("delete_event", {"event_id": "evt-008"})
        assert not deleted.is_error and deleted.structured_content["remaining"] == 7
        again = await client.call_tool("delete_event", {"event_id": "evt-008"})
        assert again.is_error
    assert len(json.loads(data.read_text(encoding="utf-8"))) == 7


def check_rules(target):
    run = lambda *extra: subprocess.run([sys.executable, str(ROOT / "permissions/apply_rules.py"), "--target", str(target), *extra],
                                        check=True, capture_output=True, text=True).stdout
    target.write_text(json.dumps({"hooks": {"Stop": []}, "permissions": {"deny": ["Read(./.env)"]}}), encoding="utf-8")
    run()
    run()  # 두 번 실행해도 같은 규칙이 두 번 들어가지 않아요.
    merged = json.loads(target.read_text(encoding="utf-8"))
    assert merged["hooks"] == {"Stop": []}, "다른 설정은 그대로 두어야 해요"
    assert merged["permissions"]["deny"] == ["Read(./.env)", "mcp__dbinc-training-admin__delete_event",
                                             "Edit(./fixtures/**)", "Edit(./work/admin/**)"]
    assert "mcp__dbinc-training-admin__count_events" in merged["permissions"]["allow"]
    run("--remove")
    assert json.loads(target.read_text(encoding="utf-8")) == {"hooks": {"Stop": []}, "permissions": {"deny": ["Read(./.env)"]}}


def main():
    fixture = sha256(SOURCE.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="dbinc-admin-") as temp:
        data = Path(temp) / "events.json"
        asyncio.run(check_server(data))
        status = subprocess.run([sys.executable, str(ROOT / "permissions/admin_server.py"), "--reset"],
                                env={**os.environ, "ADMIN_EVENTS_FILE": str(data)}, check=True, capture_output=True, text=True)
        assert "8건" in status.stdout and len(json.loads(data.read_text(encoding="utf-8"))) == 8
        check_rules(Path(temp) / "settings.json")
    assert sha256(SOURCE.read_bytes()).hexdigest() == fixture, "원본 fixture가 바뀌었어요"
    print("PASS 운영 도구 MCP: 도구 2개(읽기·삭제 표시)·삭제·없는 id 오류·되돌리기·원본 불변 / 권한 규칙 더하기·빼기")


if __name__ == "__main__":
    main()
