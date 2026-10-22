"""설정 예시만 출력합니다. .mcp.json이나 사용자 설정에 쓰지 않습니다.

  python tools/mcp_config.py         # 이벤트 조회 서버(dbinc-training-events) 하나
  python tools/mcp_config.py --all   # 혼자 더 해 보기까지 서버 세 개 (이벤트 조회, 연습 서버 감싸기, 운영 도구)
"""
import argparse
import json
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description="실습용 .mcp.json 내용을 화면에 출력합니다")
parser.add_argument("--all", action="store_true", help="연습 서버 감싸기와 운영 도구 서버도 함께 출력")
args = parser.parse_args()
servers = {"dbinc-training-events": "server.py"}
if args.all:
    servers.update({"practice-projects": "reverse/projects_mcp.py", "dbinc-training-admin": "permissions/admin_server.py"})
print(json.dumps({"mcpServers": {name: {
    "type": "stdio", "command": sys.executable,
    "args": [str(root / script)]
} for name, script in servers.items()}}, ensure_ascii=False, indent=2))
