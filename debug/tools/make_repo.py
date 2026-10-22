"""2교시 강사 저장소(온콜 시연용) 폴더를 만들어요.

쓰는 법 (labs/debug 폴더에서):
    python3 tools/make_repo.py ~/guestbook-oncall

버그 네 개가 든 방명록, 작업 지침(CLAUDE.md), 테스트, 이슈 템플릿,
GitHub Actions 워크플로가 들어가요. 예시 답(examples/)과 강사용 기록(_reference/)은
넣지 않아요. 이미 있는 폴더는 덮어쓰지 않아요.
"""
import argparse
import re
from pathlib import Path
import shutil
import subprocess
import sys

LAB = Path(__file__).resolve().parents[1]
SKIP = {"examples", "_reference", "data", "__pycache__", "tools", "routine-prompt.md", "README.md"}
RENAME = {"github": ".github", "gitignore": ".gitignore"}


def main():
    parser = argparse.ArgumentParser(description="강사 저장소 폴더를 만들어요.")
    parser.add_argument("target", help="새로 만들 폴더 (예: ~/guestbook-oncall)")
    target = Path(parser.parse_args().target).expanduser().resolve()
    if target.exists():
        parser.exit(1, f"이미 있습니다: {target}. 기존 폴더를 지키려고 멈췄어요. 다른 이름을 쓰세요.\n")

    target.mkdir(parents=True)
    for item in sorted(LAB.iterdir()):
        if item.name in SKIP:
            continue
        dest = target / RENAME.get(item.name, item.name)
        if item.is_dir():
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copyfile(item, dest)

    print(f"만들었습니다: {target}")
    for path in sorted(p for p in target.rglob("*") if p.is_file()):
        print("  " + path.relative_to(target).as_posix())

    # 지금 테스트는 통과해요. 이슈 네 개의 버그를 아직 아무 테스트도 잡지 못해서예요.
    result = subprocess.run([sys.executable, "-m", "unittest"], cwd=target,
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    print("\n지금 테스트 결과 (버그가 있어도 통과해요. 버그를 잡는 테스트가 아직 없어서예요):")
    for line in result.stderr.splitlines():
        if line.startswith(("Ran ", "OK", "FAILED")):
            print(re.sub(r" in [0-9.]+s$", "", line))
    print("\n다음 할 일: 이 폴더로 이동해서 git init, 첫 커밋, GitHub 저장소에 push 해요. 이슈는 수업 중에 _reference/post_issue.py로 하나씩 올려요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
