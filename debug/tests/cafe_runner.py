"""테스트에서 마감(cafe.py)을 임시 폴더에서 돌려 주는 도우미예요.

data/ 원본은 건드리지 않아요. 임시 폴더에 회원 명부와 주문을 만들고
그 폴더에서 cafe.py를 실행해요. 회귀 테스트(tests/test_bugs.py)에서도 이걸 쓰면 돼요.

    from tests.cafe_runner import run_cafe
    result = run_cafe(["2026-10-17,M001,5000,0"])
    result.code      # 0이면 마감이 끝까지 돌았어요
    result.output    # 영수증과 오류 글
    result.members   # out/members.csv를 읽은 dict (회원번호 → 한 줄)
    result.report    # out/report.txt 글
"""
from pathlib import Path
import csv
import os
import subprocess
import sys
import tempfile
from types import SimpleNamespace

CAFE = Path(__file__).resolve().parent.parent / "cafe.py"

MEMBERS = [
    "M001,김하늘,1990-03-03,95000,2400,일반",
    "M002,이바다,1985-04-21,152000,5100,VIP",
    "M003,박노을,1999-10-28,23000,800,일반",
    "M004,최구름,1978-12-09,61000,1500,일반",
]


def run_cafe(orders, members=None):
    """orders: 주문 줄 목록("날짜,회원번호,금액,사용 포인트"). members를 주지 않으면 기본 회원 넷을 써요."""
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        (folder / "data").mkdir()
        (folder / "data" / "members.csv").write_text(
            "id,name,birth,total,points,grade\n" + "\n".join(members or MEMBERS) + "\n", encoding="utf-8")
        (folder / "data" / "orders.csv").write_text(
            "date,member_id,amount,use_points\n" + "\n".join(orders) + "\n", encoding="utf-8")
        # Windows에서도 영수증 글자가 깨지지 않게 출력을 UTF-8로 받아요.
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        done = subprocess.run([sys.executable, str(CAFE)], cwd=folder, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", env=env)
        out_members = {}
        if (folder / "out" / "members.csv").exists():
            with open(folder / "out" / "members.csv", encoding="utf-8") as f:
                out_members = {row["id"]: row for row in csv.DictReader(f)}
        report = ""
        if (folder / "out" / "report.txt").exists():
            report = (folder / "out" / "report.txt").read_text(encoding="utf-8")
        return SimpleNamespace(code=done.returncode, output=done.stdout + done.stderr,
                               members=out_members, report=report)
