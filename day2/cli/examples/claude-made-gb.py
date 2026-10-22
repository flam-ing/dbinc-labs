"""DB Inc 교육용 방명록 CLI. 화면(static/)과 같은 규칙을 지킨다. Python 표준 라이브러리만 사용한다."""

import argparse
from datetime import datetime
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

DEFAULT_URL = "http://127.0.0.1:8000"
TIMEOUT = 10
LIMITS = [("name", 40, "이름"), ("message", 500, "내용")]

EXIT_OK, EXIT_SERVER, EXIT_BLOCKED, EXIT_NOT_SENT = 0, 1, 2, 3


class CliError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


def utf16_length(text):
    """브라우저 maxlength와 같은 방식(UTF-16 코드 단위)으로 센다."""
    return len(text.encode("utf-16-le")) // 2


def validate(name, message):
    """서버에 보내기 전에 막을 까닭을 한국어 목록으로 돌려준다. 비어 있으면 통과."""
    reasons = []
    values = {"name": name, "message": message}
    for key, maximum, label in LIMITS:
        value = values[key]
        if value == "":
            reasons.append(f"{label}을 입력해 주세요.")
            continue
        if not value.strip():
            reasons.append(f"{label}이 공백뿐입니다. 글자를 입력해 주세요.")
            continue
        length = utf16_length(value)
        if length > maximum:
            reasons.append(f"{label}은 {maximum}자 이내로 입력해 주세요. (지금 {length}자)")
    if "\n" in name or "\r" in name:
        reasons.append("이름에는 줄바꿈을 넣을 수 없습니다.")
    return reasons


def entries_url(base):
    parts = urlsplit(base)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise CliError(f"API 주소가 올바르지 않습니다: {base} (예: {DEFAULT_URL})", EXIT_BLOCKED)
    return base.rstrip("/") + "/api/entries"


def request(url, payload=None):
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    try:
        with urlopen(Request(url, data=data, headers=headers), timeout=TIMEOUT) as response:
            return decode(response.read(), response.status)
    except HTTPError as error:
        body = decode(error.read(), error.code, strict=False)
        reason = body.get("error") if isinstance(body, dict) else None
        raise CliError(f"서버가 거절했습니다({error.code}): {reason or '설명 없음'}", EXIT_SERVER)
    except (URLError, TimeoutError, OSError) as error:
        reason = getattr(error, "reason", error)
        raise CliError(f"서버에 연결하지 못했습니다: {url} ({reason})", EXIT_SERVER)


def decode(raw, status, strict=True):
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        if not strict:
            return None
        raise CliError(f"서버 응답이 JSON이 아닙니다(상태 {status}).", EXIT_SERVER)


def local_time(value):
    try:
        return datetime.fromisoformat(value).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return str(value)


def command_list(args, url):
    data = request(url)
    entries = data.get("entries") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        raise CliError("서버 응답에 entries 목록이 없습니다.", EXIT_SERVER)
    if not entries:
        print("아직 기록이 없습니다.")
        return EXIT_OK
    shown = entries[: args.limit]
    for entry in shown:
        print(f"#{entry.get('id')} {entry.get('name')} · {local_time(entry.get('created_at'))}")
        for line in str(entry.get("message", "")).splitlines() or [""]:
            print(f"  {line}")
    print(f"({len(shown)}개 표시 / 받은 기록 {len(entries)}개)")
    return EXIT_OK


def command_write(args, url):
    reasons = validate(args.name, args.message)
    if reasons:
        print("보내지 않았습니다. 화면과 같은 규칙에 걸렸습니다:", file=sys.stderr)
        for reason in reasons:
            print(f"- {reason}", file=sys.stderr)
        return EXIT_BLOCKED
    payload = {"name": args.name, "message": args.message}
    if not args.yes:
        print(f"보낼 주소: POST {url}")
        print(f"보낼 내용: {json.dumps(payload, ensure_ascii=False)}")
        print("보내지 않았습니다. 보내려면 --yes를 붙이세요.")
        return EXIT_NOT_SENT
    data = request(url, payload)
    entry = data.get("entry") if isinstance(data, dict) else None
    if not isinstance(entry, dict):
        raise CliError("서버 응답에 entry가 없습니다.", EXIT_SERVER)
    print(f"저장했습니다. 기록 번호 #{entry.get('id')}")
    return EXIT_OK


def limit_type(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("숫자로 입력해 주세요.")
    if not 1 <= number <= 200:
        raise argparse.ArgumentTypeError("1~200 사이로 입력해 주세요.")
    return number


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=None, help=f"API 주소 (기본: GB_URL 환경 변수, 없으면 {DEFAULT_URL})")
    commands = parser.add_subparsers(dest="command", required=True)
    list_parser = commands.add_parser("list", help="최신 글 보기")
    list_parser.add_argument("--limit", type=limit_type, default=20, help="보여 줄 개수 1~200 (기본 20)")
    write_parser = commands.add_parser("write", help="글 남기기")
    write_parser.add_argument("--name", required=True, help="이름 (1~40자)")
    write_parser.add_argument("--message", required=True, help="내용 (1~500자)")
    write_parser.add_argument("--yes", action="store_true", help="이 옵션이 있어야 실제로 보냅니다")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        url = entries_url(args.url or os.environ.get("GB_URL") or DEFAULT_URL)
        handler = command_list if args.command == "list" else command_write
        return handler(args, url)
    except CliError as error:
        print(error, file=sys.stderr)
        return error.code


if __name__ == "__main__":
    sys.exit(main())
