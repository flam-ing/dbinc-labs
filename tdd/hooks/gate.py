"""Claude Code 훅에서 부르는 '테스트 관문' 스크립트예요.

빌드 도구가 실패한 테스트로 jar나 dist를 막듯이, 이 스크립트는 같은 테스트로 Claude를 막아요.
테스트가 실패하면 {"decision": "block", "reason": "..."}을 출력해서 Claude가 그냥 끝내지 못하게 해요.
통과하면 아무것도 출력하지 않아요. 언어와 상관없이 테스트 명령만 바꿔 쓰면 돼요.

쓰는 법 (실습 폴더 맨 위에서):
    python3 hooks/gate.py --cwd api -- ./gradlew test -q < hooks/samples/stop.json

- --cwd 뒤에는 테스트를 돌릴 폴더를 써요. 실습 폴더(hooks의 한 단계 위) 기준이에요.
- -- 뒤에 쓴 것이 그대로 테스트 명령이 돼요.
- 훅 정보(JSON)는 표준 입력으로 받아요. Claude Code가 훅을 부를 때 넣어 줘요.
- 표준 라이브러리만 써요. Windows에서도 같은 파일을 써요.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # hooks 폴더의 한 단계 위(실습 폴더)
CODE_FILES = (".java", ".gradle", ".js", ".jsx", ".ts", ".tsx", ".py")
KEYWORDS = ("fail", "×", "error", "expected", "received", "but was")
MAX_LINES = 15


def emit(payload):
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))


def failure_lines(output):
    """실패를 알리는 줄만 골라요. 고를 줄이 없으면 마지막 줄들을 써요."""
    lines = [line.rstrip() for line in output.splitlines() if line.strip()]
    picked = [line for line in lines if any(word in line.lower() for word in KEYWORDS)]
    return (picked or lines[-MAX_LINES:])[:MAX_LINES]


def main():
    args = sys.argv[1:]
    if "--cwd" not in args or "--" not in args:
        print("쓰는 법: gate.py --cwd <폴더> -- <테스트 명령>", file=sys.stderr)
        return 1
    workdir = ROOT / args[args.index("--cwd") + 1]
    command = args[args.index("--") + 1:]

    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
    event = data.get("hook_event_name", "")
    if event == "PostToolUse":
        changed = (data.get("tool_input") or {}).get("file_path", "")
        if not changed.endswith(CODE_FILES):
            return 0  # 코드가 아닌 파일(예: 메모 .md)을 고쳤으면 검사하지 않아요

    # gradlew처럼 폴더 안에 있는 파일을 먼저 찾고, 없으면 npm처럼 설치된 명령을 찾아요.
    first = command[0]
    found = str(workdir / first) if (workdir / first).exists() else shutil.which(first)
    if not found:
        print(f"테스트 명령을 찾지 못했어요: {first} (JDK, Node, Python 설치를 확인하세요)", file=sys.stderr)
        return 1  # 환경 문제는 Claude가 코드로 고칠 일이 아니라서 막지 않아요

    shown = f"cd {args[args.index('--cwd') + 1]} && " + " ".join(command)
    try:
        done = subprocess.run([found, *command[1:]], cwd=workdir, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=280)
    except subprocess.TimeoutExpired:
        print(f"테스트가 280초 안에 끝나지 않았어요. 직접 돌려 보세요: {shown}", file=sys.stderr)
        return 1
    if done.returncode == 0:
        return 0
    output = done.stdout + done.stderr
    if "command not found" in output or "is not recognized" in output:
        print(f"테스트 도구가 설치되지 않았어요(npm install 등을 먼저 하세요): {shown}", file=sys.stderr)
        return 1

    detail = "\n".join(failure_lines(output))
    if event == "Stop" and data.get("stop_hook_active"):
        # 이미 한 번 막았는데도 실패예요. 무한 반복을 피하려고 멈추게 두고 사람에게만 알려요.
        emit({"systemMessage": f"테스트가 아직 실패해요. 직접 확인하세요: {shown}\n{detail}"})
        return 0

    reason = (
        f"테스트가 실패해서 끝낼 수 없어요. 확인 명령: {shown}\n"
        f"{detail}\n"
        "테스트를 고치거나 지워서 통과시키지 말고 코드를 고치세요. "
        "규칙(RULES.md)과 요청이 부딪히면 사용자에게 물어보세요."
    )
    emit({"decision": "block", "reason": reason})
    return 0


if __name__ == "__main__":
    sys.exit(main())
