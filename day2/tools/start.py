"""새 작업 폴더만 만듭니다. 기존 작업을 덮어쓰지 않습니다."""
import argparse
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("lesson", choices=["tdd", "debug", "integration"])
args = parser.parse_args()
target = ROOT / "work" / args.lesson
if target.exists():
    parser.exit(1, f"이미 있습니다: {target}. 기존 작업을 보존합니다. 새 이름으로 복사해 이어가세요.\n")
source = ROOT / {"tdd":"starter", "debug":"buggy", "integration":"integration/starter"}[args.lesson]
shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
print(f"준비했습니다: work/{args.lesson}")
