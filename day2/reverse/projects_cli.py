"""연습 서버 화면 뒤의 JSON API(/api/projects)를 부르는 작은 CLI입니다.

Chrome 개발자 도구의 Network 탭에서 찾은 요청을 그대로 감쌌어요. 공개 API 문서가 없는
화면이라도 브라우저가 실제로 주고받는 요청을 찾으면 이렇게 프로그램으로 부를 수 있어요.
내 PC(127.0.0.1, localhost)의 교육용 연습 서버만 부르고, 표준 라이브러리만 씁니다.

사용법 (실습 폴더 맨 위에서)
  python reverse/projects_cli.py page 1     # 1쪽 응답 보기
  python reverse/projects_cli.py all        # 모든 쪽을 읽고 id가 겹치는 항목 빼기

연습 서버 주소는 PRACTICE_BASE_URL 환경 변수나 --base-url로 바꿀 수 있어요.
기본값은 http://127.0.0.1:8765 입니다.
"""
import argparse
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

DEFAULT_BASE_URL = "http://127.0.0.1:8765"
RETRYABLE = {429, 500, 502, 503, 504}
MAX_PAGES = 10
MAX_WAIT_SECONDS = 5
FIELDS = ("id", "title", "category", "updatedAt")


class NoRedirect(HTTPRedirectHandler):
    """다른 주소로 넘기는 응답을 따라가지 않아요. 연습 서버는 넘기지 않습니다."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


OPENER = build_opener(NoRedirect)


def log(message):
    # MCP 서버로 쓸 때 표준 출력은 MCP 통신에 쓰이므로, 안내는 표준 오류로만 내보내요.
    print(message, file=sys.stderr, flush=True)


def base_url(value=None):
    url = (value or os.environ.get("PRACTICE_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    parts = urlsplit(url)
    if parts.scheme != "http" or parts.hostname not in ("127.0.0.1", "localhost") or parts.username or parts.password:
        raise ValueError(f"이 예시는 내 PC의 연습 서버(http://127.0.0.1 또는 localhost)만 부릅니다: {url}")
    return url


def fetch_page(page=1, base=None, attempts=3, sleep=time.sleep):
    """한 쪽을 읽어서 {synthetic, page, items, next_page, source_url}로 돌려줘요."""
    if type(page) is not int or page < 1:
        raise ValueError("page는 1 이상의 정수여야 합니다")
    url = f"{base_url(base)}/api/projects?page={page}"
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "DBIncTrainingCLI/1.0"})
    for attempt in range(1, attempts + 1):
        try:
            with OPENER.open(request, timeout=5) as response:
                data = json.loads(response.read(1_000_000).decode("utf-8"))
            break
        except HTTPError as error:
            body = error.read(4096).decode("utf-8", errors="replace")
            retry_after = error.headers.get("Retry-After", "")
            error.close()
            if error.code not in RETRYABLE or attempt == attempts:
                raise RuntimeError(f"{error.code} 응답: {url} {body}".strip()) from None
            wait = float(retry_after) if retry_after.isdigit() else 0.2 * 2 ** (attempt - 1)
            if wait > MAX_WAIT_SECONDS:
                raise RuntimeError(f"{error.code} 응답: {wait}초를 기다리라고 해서 멈춥니다") from None
            log(f"{error.code} 응답: {wait:g}초 기다렸다가 다시 요청해요 ({attempt}/{attempts}) {url}")
            sleep(wait)
        except (URLError, OSError) as error:
            raise RuntimeError(f"연습 서버에 연결하지 못했어요: {base_url(base)} ({getattr(error, 'reason', error)}). "
                               "연습 서버를 켰는지 확인하세요.") from None
    if data.get("synthetic") is not True or not isinstance(data.get("items"), list):
        raise ValueError("교육용 연습 서버의 응답 모양이 아닙니다")
    items = []
    for item in data["items"]:
        if not isinstance(item, dict) or any(not isinstance(item.get(key), str) for key in FIELDS):
            raise ValueError("항목에 id, title, category, updatedAt 글자가 필요합니다")
        items.append({key: item[key] for key in FIELDS})
    following = data.get("nextPage")
    if following is not None and (type(following) is not int or following <= page):
        raise ValueError(f"nextPage 값이 이상합니다: {following!r}")
    return {"synthetic": True, "page": page, "items": items, "next_page": following, "source_url": url}


def fetch_all(base=None, sleep=time.sleep):
    """next_page가 없을 때까지 읽고, id가 겹치는 항목은 처음 본 것만 남겨요."""
    page, pages, seen, items, duplicates = 1, 0, set(), [], []
    while page is not None:
        if pages >= MAX_PAGES:
            raise ValueError(f"{MAX_PAGES}쪽을 넘어서 멈춥니다")
        result = fetch_page(page, base, sleep=sleep)
        pages += 1
        for item in result["items"]:
            if item["id"] in seen:
                duplicates.append(item["id"])
                continue
            seen.add(item["id"])
            items.append(item)
        page = result["next_page"]
    return {"synthetic": True, "pages": pages, "items": items, "duplicates": duplicates,
            "source": f"{base_url(base)}/api/projects"}


def main(argv=None):
    parser = argparse.ArgumentParser(description="연습 서버의 /api/projects를 부르는 CLI")
    parser.add_argument("--base-url", help=f"연습 서버 주소 (기본 {DEFAULT_BASE_URL})")
    commands = parser.add_subparsers(dest="command", required=True)
    one = commands.add_parser("page", help="한 쪽만 읽어요")
    one.add_argument("number", type=int)
    commands.add_parser("all", help="모든 쪽을 읽고 중복을 빼요")
    args = parser.parse_args(argv)
    try:
        result = fetch_page(args.number, args.base_url) if args.command == "page" else fetch_all(args.base_url)
    except (ValueError, RuntimeError) as error:
        parser.exit(1, f"멈췄어요: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
