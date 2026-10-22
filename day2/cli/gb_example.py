"""방명록 CLI 예시. 화면(index.html, app.js)이 막던 것을 보내기 전에 똑같이 막아요.

사용법
  python gb.py list                     최신 글 10개
  python gb.py list --json              JSON으로
  python gb.py write 이름 내용 --yes      글 남기기(--yes가 있어야 보내요)

주소는 GB_URL 환경 변수나 --url로 바꿔요. 기본값은 http://127.0.0.1:8000 이에요.
파이썬 표준 라이브러리만 써요.
"""
import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_URL = "http://127.0.0.1:8000"
RULES = {"name": ("이름", 40), "message": ("내용", 500)}  # 화면의 maxlength, required와 같아요


def check(name, message):
    """화면이 막던 규칙을 서버에 보내기 전에 검사해요. 문제가 있으면 이유를 돌려줘요."""
    for key, value in (("name", name), ("message", message)):
        label, limit = RULES[key]
        text = value.strip()
        if not text:
            return f"{label}을 입력해 주세요."
        if len(text) > limit:
            return f"{label}은 {limit}자 이내로 입력해 주세요. (지금 {len(text)}자)"
    return None


def read_json(raw):
    try:
        return json.loads(raw.decode("utf-8") or "{}")
    except ValueError:
        return {"error": "JSON이 아닌 응답이에요. 주소가 API 주소인지 확인해요."}


def call(url, method="GET", body=None):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    request = Request(url, data=data, method=method,
                      headers={"Content-Type": "application/json", "User-Agent": "gb-cli/1.0"})
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, read_json(response.read())
    except HTTPError as error:
        return error.code, read_json(error.read())


def main(argv=None):
    parser = argparse.ArgumentParser(description="방명록 CLI 예시")
    parser.add_argument("--url", default=os.environ.get("GB_URL", DEFAULT_URL))
    commands = parser.add_subparsers(dest="command", required=True)
    show = commands.add_parser("list", help="최신 글 보기")
    show.add_argument("--limit", type=int, default=10)
    show.add_argument("--json", action="store_true", help="JSON으로 출력")
    write = commands.add_parser("write", help="글 남기기")
    write.add_argument("name")
    write.add_argument("message")
    write.add_argument("--yes", action="store_true", help="확인 없이 보내기")
    write.add_argument("--json", action="store_true", help="JSON으로 출력")
    args = parser.parse_args(argv)
    api = args.url.rstrip("/") + "/api/entries"
    try:
        if args.command == "list":
            status, data = call(api)
            if status != 200:
                print(f"목록을 받지 못했어요: {status} {data.get('error', '')}", file=sys.stderr)
                return 2
            if "entries" not in data:
                print(f"목록을 받지 못했어요: {data.get('error', '응답 모양이 달라요')}", file=sys.stderr)
                return 2
            entries = data["entries"][: args.limit]
            if args.json:
                print(json.dumps(entries, ensure_ascii=False, indent=2))
            else:
                for entry in entries:
                    print(f"#{entry['id']} {entry['name']}: {entry['message']}")
                print(f"{len(entries)}개 (전체 {len(data['entries'])}개)")
            return 0
        problem = check(args.name, args.message)
        if problem:
            print(f"보내지 않았어요: {problem}", file=sys.stderr)
            return 1
        if not args.yes:
            print("보내지 않았어요: 확인이 필요해요. 보내려면 --yes를 붙여요.", file=sys.stderr)
            return 1
        status, data = call(api, "POST", {"name": args.name.strip(), "message": args.message.strip()})
        if status != 201:
            print(f"서버가 거절했어요: {status} {data.get('error', '')}", file=sys.stderr)
            return 2
        entry = data["entry"]
        print(json.dumps(entry, ensure_ascii=False) if args.json else f"저장했어요: #{entry['id']} {entry['name']}")
        return 0
    except (URLError, OSError) as error:
        print(f"방명록 서버에 연결하지 못했어요: {args.url} ({getattr(error, 'reason', error)})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
