"""Claude Code 훅에서 부르는 테스트 검사 스크립트예요.

Claude가 파이썬 파일을 고친 뒤(PostToolUse)와 답을 마치기 전(Stop)에 pytest를 돌려요.
테스트가 실패하면 {"decision": "block", "reason": "..."}을 출력해서
실패한 테스트 이름을 Claude에게 돌려줘요. 통과하면 아무것도 출력하지 않아요.

쓰는 법 (실습 폴더 맨 위에서):
    python3 hooks/run_tests.py tests --impl work/tdd/report.py -q < hooks/samples/post-edit.json

- 뒤에 붙인 인자는 그대로 pytest에 넘겨요. 인자가 없으면 "tests -q"를 써요.
- 훅 정보(JSON)는 표준 입력으로 받아요. Claude Code가 훅을 부를 때 넣어 줘요.
- 실습 폴더에 .venv가 있으면 그 Python으로 pytest를 돌려요.
- 표준 라이브러리만 써요. jq가 없는 Windows에서도 같은 파일을 써요.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # 이 파일이 든 hooks 폴더의 한 단계 위(실습 폴더)
DEFAULT_ARGS = ["tests", "-q"]
MAX_LINES = 15


def find_python():
    """실습 폴더의 가상환경 Python을 먼저 찾고, 없으면 지금 Python을 써요."""
    for relative in (".venv/bin/python", ".venv/Scripts/python.exe"):
        candidate = ROOT / relative
        if candidate.exists():
            return str(candidate)
    return sys.executable


def run_pytest(args):
    command = [find_python(), "-m", "pytest", *args, "--tb=line"]
    try:
        done = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=110,
        )
    except subprocess.TimeoutExpired:
        return None, "pytest가 110초 안에 끝나지 않았어요."
    return done.returncode, done.stdout + done.stderr


def failure_lines(output):
    """실패한 테스트 이름과 마지막 요약 줄만 골라요."""
    lines = [line for line in output.splitlines() if line.strip()]
    picked = [line for line in lines if line.startswith(("FAILED", "ERROR"))]
    if not picked:
        picked = lines[-MAX_LINES:]
    elif lines and lines[-1] not in picked:
        picked.append(lines[-1])
    return picked[:MAX_LINES]


def emit(payload):
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        print("훅 입력이 JSON이 아니에요. Claude Code가 부르거나 samples 파일을 넣어 실행하세요.", file=sys.stderr)
        return 1

    event = data.get("hook_event_name", "")
    if event == "PostToolUse":
        changed = (data.get("tool_input") or {}).get("file_path", "")
        if not changed.endswith(".py"):
            return 0  # 파이썬 파일이 아니면(예: 메모 .md) 검사하지 않아요

    args = sys.argv[1:] or DEFAULT_ARGS
    shown = "python -m pytest " + " ".join(args)
    code, output = run_pytest(args)
    if code == 0:
        return 0

    if "No module named pytest" in output:
        # 환경 문제는 Claude가 코드로 고칠 일이 아니라서 막지 않고 사람에게만 알려요.
        print("pytest를 찾지 못했어요. 실습 폴더에 .venv를 만들고 requirements.txt를 설치하세요.", file=sys.stderr)
        return 1

    detail = "\n".join(failure_lines(output))
    if event == "Stop" and data.get("stop_hook_active"):
        # 이미 한 번 막아서 Claude가 다시 일했는데도 실패예요. 무한 반복을 피하려고 이번에는 멈추게 두고 사람에게 알려요.
        emit({"systemMessage": f"테스트가 아직 실패해요. 직접 확인하세요: {shown}\n{detail}"})
        return 0

    reason = (
        f"테스트가 실패했어요. 확인 명령: {shown}\n"
        f"{detail}\n"
        "방금 바꾼 코드가 SPEC.md나 기존 테스트와 어긋나는지 보고 코드를 고치세요. "
        "테스트 파일을 고쳐서 통과시키지 마세요. 요청이 명세와 부딪히면 사용자에게 물어보세요."
    )
    emit({"decision": "block", "reason": reason})
    return 0


if __name__ == "__main__":
    sys.exit(main())
