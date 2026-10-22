"""코드가 바뀌었는데 kb 문서가 그대로면, Claude가 답을 마치기 전에 한 번 막는 Stop 훅이에요.

쓰는 법: python3 kb_guard.py <코드 폴더> <kb 폴더>   (예: python3 kb_guard.py src docs/kb)
훅 정보(JSON)는 표준 입력으로 받아요. 표준 라이브러리만 써요.
"""
import json
import os
import subprocess
import sys


def git_lines(args, cwd):
    try:
        done = subprocess.run(["git", "-c", "core.quotepath=false", *args],
                              cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return []  # git이 없으면 아무것도 하지 않아요.
    return done.stdout.splitlines() if done.returncode == 0 else []


def main():
    code_dir = (sys.argv[1] if len(sys.argv) > 1 else "src").rstrip("/") + "/"
    kb_dir = (sys.argv[2] if len(sys.argv) > 2 else "docs/kb").rstrip("/") + "/"
    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
    if data.get("stop_hook_active"):
        return 0  # 한 번 막았으면 두 번째는 막지 않아요. 같은 일을 되풀이하지 않게 하려는 거예요.
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or "."
    changed = git_lines(["diff", "--name-only", "--relative", "HEAD"], cwd)
    changed += git_lines(["ls-files", "--others", "--exclude-standard"], cwd)
    code = [p for p in changed if p.startswith(code_dir)]
    kb = [p for p in changed if p.startswith(kb_dir)]
    if code and not kb:
        reason = (
            f"코드가 바뀌었는데 {kb_dir}는 그대로예요. 바뀐 파일: {', '.join(code[:5])}. "
            f"바뀐 동작이 {kb_dir}의 문서에 닿는지 보고 함께 고쳐 주세요. "
            "고칠 것이 없으면 그 이유를 답에 한 줄로 적어 주세요."
        )
        sys.stdout.reconfigure(encoding="utf-8")
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
