"""가격 추적 작업의 하네스 훅이에요. Claude Code가 도구를 쓰기 전에(PreToolUse) 이 스크립트를 불러요.

막는 것(종료 코드 2, 이유는 stderr로 Claude에게 전달돼요)
- Bash, WebFetch로 127.0.0.1·localhost가 아닌 주소에 요청하기
- Bash로 연습몰의 /admin 주소를 직접 부르기(날짜는 tools/sim_day.py, tools/run_days.py로만 바꿔요)
- kb/prices.csv, kb/news.jsonl, kb/runs.jsonl을 Edit·Write로 고치기(collect.py만 덧붙여요)
- tests/ 안의 커밋된 테스트(와 처음부터 있던 테스트 두 개)를 Edit·Write로 고치기
  (새로 만든 테스트 파일은 커밋하기 전까지 고칠 수 있어요)
- 아래 EXTRA_BLOCKS에 우리 팀이 더한 Bash 명령
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

LOCAL_HOSTS = {"127.0.0.1", "localhost"}
URL = re.compile(r"https?://([^/\s:'\"]+)", re.I)
PROTECTED = {"kb/prices.csv", "kb/news.jsonl", "kb/runs.jsonl"}
BASE_TESTS = {"tests/test_collect.py", "tests/test_tools.py"}
ROOT = Path(__file__).resolve().parents[2]

# 해 보기(교안 8절): 꼭 막고 싶은 Bash 명령을 (찾을 글자, 이유) 한 줄로 더해요.
# 예시 줄 맨 앞의 # 을 지우면 price-watch-rules 12번(git push 하지 않기)이 부탁에서 강제로 바뀌어요.
EXTRA_BLOCKS = [
    # ("git push", "하네스: git push는 사람이 확인하고 직접 해요. (price-watch-rules 12번)"),
]


def block(reason: str) -> int:
    print(reason, file=sys.stderr)
    return 2


def relative(path: str, cwd: str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = Path(cwd) / p
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def committed(rel: str) -> bool:
    """git이 이미 추적하는(커밋한) 파일인지 봐요. git이 없으면 아니라고 봐요."""
    try:
        done = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", "--", rel],
                              capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0


def decide(event: dict) -> int:
    tool = event.get("tool_name", "")
    data = event.get("tool_input") or {}
    cwd = event.get("cwd") or "."
    if tool in ("Bash", "WebFetch"):
        text = data.get("command", "") if tool == "Bash" else data.get("url", "")
        for host in URL.findall(text):
            if host.lower() not in LOCAL_HOSTS:
                return block(f"하네스: 연습몰(127.0.0.1:8766) 말고 다른 주소({host})에는 요청하지 않아요.")
        if tool == "Bash" and "/admin" in text and URL.search(text):
            return block("하네스: /admin은 수업 진행용 주소예요. 날짜는 python3 tools/sim_day.py로 바꿔요.")
        if tool == "Bash":
            for words, reason in EXTRA_BLOCKS:
                if words in text:
                    return block(reason)
    if tool in ("Edit", "Write"):
        path = data.get("file_path", "")
        rel = relative(path, cwd)
        if rel in PROTECTED:
            return block(f"하네스: {rel}은 collect.py만 덧붙이는 기록이에요. 잘못된 행은 kb/wiki/incidents.md에 적고 사람에게 알려요.")
        if rel.startswith("tests/") and rel.endswith(".py") and (rel in BASE_TESTS or committed(rel)):
            return block(f"하네스: 커밋된 테스트({rel})는 고치지 않아요. 새 구조는 새 테스트 파일로 더해요.")
    return 0


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    return decide(event)


if __name__ == "__main__":
    sys.exit(main())
