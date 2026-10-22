"""원격 수집 연습의 하네스 훅이에요. Claude Code가 도구를 쓰기 전에(PreToolUse) 이 스크립트를 불러요.

막는 것(종료 코드 2, 이유는 Claude에게 전달돼요)
- Bash로 test-server와 내 PC(127.0.0.1, localhost) 말고 다른 주소에 요청하기
- 관리자 주소(/admin, /api/admin)와 검증 주소(/api/turnstile) 부르기
- 이름(User-Agent) 없이 curl로 부르기, WebFetch로 부르기(우리 이름과 간격을 지킬 수 없어요)
- data/live-prices.csv를 Edit·Write로 고치기(polite_fetch.py만 덧붙여요)
- 아래 EXTRA_BLOCKS에 우리가 더한 Bash 명령
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ALLOWED_HOSTS = {"test-server-8az.pages.dev", "127.0.0.1", "localhost"}
URL = re.compile(r"https?://([^/\s:'\"]+)(?::\d+)?([^\s'\"]*)", re.I)
FORBIDDEN = ("/admin", "/api/admin", "/api/turnstile")
PROTECTED = {"data/live-prices.csv"}
ROOT = Path(__file__).resolve().parents[2]

# 해 보기: 꼭 막고 싶은 Bash 명령을 (찾을 글자, 이유) 한 줄로 더해요.
EXTRA_BLOCKS = [
    # ("while true", "하네스: 끝없이 반복해서 부르지 않아요. 횟수를 정하고 1분 넘게 띄워요."),
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


def decide(event: dict) -> int:
    tool = event.get("tool_name", "")
    data = event.get("tool_input") or {}
    cwd = event.get("cwd") or "."
    if tool == "WebFetch":
        return block("하네스: 값을 모을 때는 python3 polite_fetch.py를 써요. 우리 이름과 1분 간격을 지키려는 거예요.")
    if tool == "Bash":
        text = data.get("command", "")
        urls = URL.findall(text)
        for host, path in urls:
            if host.lower() not in ALLOWED_HOSTS:
                return block(f"하네스: test-server와 내 PC 말고 다른 주소({host})에는 요청하지 않아요.")
            if any(word in path for word in FORBIDDEN):
                return block("하네스: 관리자 주소와 검증 주소는 부르지 않아요. 관리자 화면은 강사만 다뤄요.")
        if urls and re.search(r"\bcurl\b", text) and not re.search(r"(\s-A\s|--user-agent|user-agent:)", text, re.I):
            return block("하네스: curl로 부를 때도 -A \"DBInc-3jo/1.0\"처럼 우리 이름을 밝혀요.")
        for words, reason in EXTRA_BLOCKS:
            if words in text:
                return block(reason)
    if tool in ("Edit", "Write"):
        if relative(data.get("file_path", ""), cwd) in PROTECTED:
            return block("하네스: data/live-prices.csv는 polite_fetch.py만 덧붙이는 기록이에요. 잘못된 줄은 data/incidents.md에 적어요.")
    return 0


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    return decide(event)


if __name__ == "__main__":
    sys.exit(main())
