"""연습몰의 시뮬레이션 날짜를 보거나 바꿔요. 수업 진행용 도구예요.

  python3 tools/sim_day.py           # 지금 날짜 보기
  python3 tools/sim_day.py 8         # 8일차(2026-11-08)로 바꾸기
  python3 tools/sim_day.py next      # 하루 넘기기

실제 사이트에는 이런 기능이 없어요. 수집기(collect.py)는 이 주소(/admin)를 부르지 않아요.
"""
from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:8766"


def admin(base_url: str, payload: dict | None = None) -> dict:
    url = base_url.rstrip("/") + "/admin/day"
    if not url.startswith(("http://127.0.0.1", "http://localhost")):
        raise SystemExit("연습몰(127.0.0.1)에만 써요.")
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(url, data=data, method="POST" if data else "GET",
                      headers={"Content-Type": "application/json", "User-Agent": "price-watch-sim/1.0"})
    try:
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read())
    except HTTPError as error:
        raise SystemExit(f"날짜를 바꾸지 못했어요: {error.read().decode('utf-8', 'replace')}")
    except URLError as error:
        raise SystemExit(f"연습몰에 연결하지 못했어요({error.reason}). 서버를 켰는지 확인해요.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("day", nargs="?", help="바꿀 날(1~30) 또는 next")
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args(argv)
    if args.day is None:
        info = admin(args.base_url)
    elif args.day == "next":
        info = admin(args.base_url, {"next": True})
    else:
        info = admin(args.base_url, {"day": int(args.day)})
    print(f"연습몰 날짜: {info['date']} ({info['day']}일차)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
