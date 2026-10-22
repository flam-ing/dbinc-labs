import json
import subprocess
import sys

event = json.load(sys.stdin)
path = event.get("tool_input", {}).get("file_path", "")
if not path.endswith(".py"):
    sys.exit(0)

result = subprocess.run(
    ["python3", "-m", "unittest", "-q"],
    cwd=event.get("cwd") or None,
    capture_output=True,
    text=True,
)
if result.returncode != 0:
    sys.stderr.write(result.stderr or result.stdout)
    sys.exit(2)
