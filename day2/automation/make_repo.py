"""이슈 자동 처리 실습에 쓸 작은 저장소 폴더를 만들어요.

쓰는 법 (labs/day2 폴더 맨 위에서):
    python automation/make_repo.py ~/dbinc-auto

만드는 폴더에는 버그가 든 report.py, 명세, 계약 테스트, 재현 스크립트,
작업 지침(CLAUDE.md), 이슈 템플릿, GitHub Actions 워크플로가 들어가요.
정답 구현(reference/)은 넣지 않아요. 이미 있는 폴더는 덮어쓰지 않아요.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

DAY2 = Path(__file__).resolve().parents[1]
TEMPLATE = Path(__file__).resolve().parent / "repo"

# (원본 경로, 새 저장소 안의 경로)
COPIES = [
    (DAY2 / "SPEC.md", "SPEC.md"),
    (DAY2 / "fixtures" / "events.json", "fixtures/events.json"),
    (DAY2 / "tests" / "test_contract.py", "tests/test_contract.py"),
    (TEMPLATE / "report.py", "report.py"),
    (TEMPLATE / "CLAUDE.md", "CLAUDE.md"),
    (TEMPLATE / "README.md", "README.md"),
    (TEMPLATE / "requirements.txt", "requirements.txt"),
    (TEMPLATE / "gitignore", ".gitignore"),
    (TEMPLATE / "github" / "ISSUE_TEMPLATE" / "bug.md", ".github/ISSUE_TEMPLATE/bug.md"),
    (TEMPLATE / "github" / "workflows" / "claude.yml", ".github/workflows/claude.yml"),
]

# 원본 파일에서 실습 폴더 전용 기본값만 바꿔서 옮겨요. 바꿀 글자가 없으면 멈춰요.
REWRITES = [
    (DAY2 / "conftest.py", "conftest.py", [
        ('default="reference/report.py"', 'default="report.py"'),
        ("tools/start.py로 작업 폴더를 준비하세요.", "--impl 경로를 확인하세요."),
    ]),
    (DAY2 / "tools" / "reproduce.py", "tools/reproduce.py", [
        ('default="work/debug/report.py"', 'default="report.py"'),
    ]),
]


def main():
    parser = argparse.ArgumentParser(description="이슈 자동 처리 실습 저장소 폴더를 만들어요.")
    parser.add_argument("target", help="새로 만들 폴더 (예: ~/dbinc-auto)")
    args = parser.parse_args()
    target = Path(args.target).expanduser().resolve()
    if target.exists():
        parser.exit(1, f"이미 있습니다: {target}. 기존 폴더를 지키려고 멈췄어요. 다른 이름을 쓰세요.\n")

    for source, relative in COPIES:
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)

    for source, relative, pairs in REWRITES:
        text = source.read_text(encoding="utf-8")
        for old, new in pairs:
            if old not in text:
                shutil.rmtree(target)
                parser.exit(1, f"{source.name}에서 '{old}'를 찾지 못했어요. 원본이 바뀌었는지 확인하세요.\n")
            text = text.replace(old, new)
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")

    print(f"만들었습니다: {target}")
    for path in sorted(p for p in target.rglob("*") if p.is_file()):
        print("  " + path.relative_to(target).as_posix())

    # 지금 상태를 한 번 보여 줘요. 버그가 든 상태라 재현은 실패해야 정상이에요.
    result = subprocess.run([sys.executable, "tools/reproduce.py"], cwd=target,
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("\n재현 결과 (버그가 든 상태라 실패가 정상이에요):")
    print(result.stdout.rstrip())
    print("\n다음 할 일: 이 폴더로 이동해서 git init, 첫 커밋, GitHub 비공개 저장소에 push 해요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
