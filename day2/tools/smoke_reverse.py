"""reverse/의 CLI와 MCP 감싸기가 연습 서버와 실제로 주고받는지 확인합니다.

연습 서버(강의 저장소의 demos/revision/crawler/server.py)를 먼저 켜 두어야 해요.
  python tools/smoke_reverse.py                       # 기본 http://127.0.0.1:8765
  python tools/smoke_reverse.py --base-url http://127.0.0.1:18765
Claude 설정은 바꾸지 않아요.
"""
import argparse
import asyncio
from pathlib import Path
import sys
from mcp import Client, StdioServerParameters

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reverse"))
import projects_cli  # noqa: E402

EXPECTED_IDS = [f"proj-00{n}" for n in range(1, 8)]


async def check_mcp(base):
    server = StdioServerParameters(command=sys.executable, args=[str(ROOT / "reverse/projects_mcp.py")],
                                   env={"PRACTICE_BASE_URL": base})
    async with Client(server) as client:
        listed = await client.list_tools()
        assert {tool.name for tool in listed.tools} == {"list_projects", "list_all_projects"}
        assert all(tool.annotations.read_only_hint for tool in listed.tools)
        first = await client.call_tool("list_projects", {"page": 1})
        assert not first.is_error, first.content
        assert [item["id"] for item in first.structured_content["items"]] == EXPECTED_IDS[:3]
        assert first.structured_content["next_page"] == 2
        everything = await client.call_tool("list_all_projects", {})
        assert [item["id"] for item in everything.structured_content["items"]] == EXPECTED_IDS
        assert everything.structured_content["duplicates"] == ["proj-003", "proj-005"]
        missing = await client.call_tool("list_projects", {"page": 4})
        assert missing.is_error


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    base = parser.parse_args().base_url
    try:
        projects_cli.fetch_page(1, base, attempts=1)
    except RuntimeError as error:
        parser.exit(1, f"연습 서버를 먼저 켜세요: {error}\n")
    result = projects_cli.fetch_all(base)
    assert result["pages"] == 3, result
    assert [item["id"] for item in result["items"]] == EXPECTED_IDS
    assert result["duplicates"] == ["proj-003", "proj-005"]
    for outside in ("https://example.com", "http://user:pw@127.0.0.1:8765", "file:///etc/hosts"):
        try:
            projects_cli.base_url(outside)
        except ValueError:
            continue
        raise AssertionError(f"연습 서버 밖 주소를 막지 않았어요: {outside}")
    asyncio.run(check_mcp(base))
    print("PASS 리버스 엔지니어링: CLI 3쪽·7건·중복 2건 / MCP 도구 2개·읽기 전용·없는 쪽 오류 / 외부 주소 차단")


if __name__ == "__main__":
    main()
