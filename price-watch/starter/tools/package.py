"""검사를 모두 통과했을 때만 작업 폴더를 ZIP 하나로 묶어요.

  python3 tools/package.py            # dist/price-watch.zip

순서: 예전 ZIP 지우기 → 테스트 → 데이터 점검(curate --check) → 리포트 다시 만들기 → 묶기.
하나라도 실패하면 멈추고 ZIP을 만들지 않아요.
내 PC 전용 파일(.claude/settings.local.json)과 임시 파일(.runtime/, 캐시)은 넣지 않아요.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".runtime", "dist", "__pycache__", ".git", ".venv", ".pytest_cache"}
SKIP_FILES = {"settings.local.json", ".DS_Store"}
REQUIRED = ["GUIDE.md", "CLAUDE.md", "collect.py", "kb/prices.csv", "kb/news.jsonl", "kb/wiki/selector-changes.md",
            "out/report.md", ".claude/skills/price-watch-rules/SKILL.md", "routine/daily-prompt.md"]


def step(title: str, args: list[str]) -> None:
    print(f"== {title}", flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def files_to_pack() -> list[Path]:
    out = []
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if path.is_dir() or SKIP_DIRS & set(rel.parts) or path.name in SKIP_FILES:
            continue
        out.append(path)
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "price-watch.zip")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    output.unlink(missing_ok=True)
    try:
        step("테스트", [sys.executable, "-m", "unittest", "discover", "-s", "tests"])
        step("데이터 점검", [sys.executable, "tools/curate.py", "--check"])
        step("리포트", [sys.executable, "tools/report.py"])
    except subprocess.CalledProcessError as error:
        print(f"검사가 실패해서 묶지 않았어요: {' '.join(error.cmd[1:])}", file=sys.stderr)
        return 1
    missing = [name for name in REQUIRED if not (ROOT / name).exists()]
    if missing:
        print(f"꼭 있어야 할 파일이 없어서 묶지 않았어요: {', '.join(missing)}", file=sys.stderr)
        return 1
    files = files_to_pack()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, Path("price-watch") / path.relative_to(ROOT))
    shown = output.relative_to(ROOT) if output.is_relative_to(ROOT) else output
    print(f"검사를 통과한 결과를 묶었어요: {shown} (파일 {len(files)}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
