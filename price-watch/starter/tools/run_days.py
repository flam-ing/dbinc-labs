"""연습몰 날짜를 하루씩 넘기면서 collect.py로 모아요. 30일을 짧은 시간에 돌려 보는 시뮬레이션 도구예요.

  python3 tools/run_days.py 1 7      # 1일차부터 7일차까지
  python3 tools/run_days.py 8        # 8일차 하루만

어느 날 수집이 실패하면 거기서 멈추고 collect.py의 종료 코드(구조 변경이면 2)로 끝나요.
collect.py가 마지막 요청 시각을 .runtime/last-request.txt에 적어 두어서, 날짜가 바뀌어도 1초 간격을 지켜요.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from sim_day import BASE_URL, admin  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("first", type=int)
    parser.add_argument("last", type=int, nargs="?")
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args(argv)
    last = args.last or args.first
    if not 1 <= args.first <= last <= 30:
        parser.error("날짜는 1~30 사이이고, 처음 날이 마지막 날보다 크면 안 돼요.")
    for day in range(args.first, last + 1):
        admin(args.base_url, {"day": day})
        print(f"[{day}일차] ", end="", flush=True)
        result = subprocess.run([sys.executable, str(ROOT / "collect.py"), "--base-url", args.base_url], cwd=ROOT)
        if result.returncode != 0:
            again = f"{day}" if day == last else f"{day} {last}"
            print(f"{day}일차에서 멈췄어요. 고친 다음 python3 tools/run_days.py {again} 로 이어 가요.")
            return result.returncode
    rows = sum(1 for _ in (ROOT / "kb" / "prices.csv").open(encoding="utf-8")) - 1
    print(f"{args.first}~{last}일차를 모았어요. 가격 기록 kb/prices.csv: {rows}행")
    return 0


if __name__ == "__main__":
    sys.exit(main())
