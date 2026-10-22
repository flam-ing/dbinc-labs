"""permissions/settings.example.json의 권한 규칙을 실습 폴더의 .claude/settings.json에 더합니다.

.claude/settings.json이 이미 있으면 다른 설정(hooks 등)은 그대로 두고, 빠진 규칙만 목록에 더해요.
JSON을 손으로 고치다가 쉼표 하나로 파일이 깨지는 일을 막으려고 만든 도우미예요.

  python permissions/apply_rules.py            # 규칙 더하기
  python permissions/apply_rules.py --remove   # 이 예시가 더한 규칙만 빼기
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = Path(__file__).resolve().parent / "settings.example.json"
LISTS = ("deny", "ask", "allow")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--remove", action="store_true", help="예시의 규칙만 빼요")
    parser.add_argument("--target", type=Path, default=ROOT / ".claude/settings.json")
    args = parser.parse_args()
    rules = json.loads(EXAMPLE.read_text(encoding="utf-8"))["permissions"]
    target = args.target
    try:
        settings = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
    except json.JSONDecodeError as error:
        parser.exit(1, f"{target}가 올바른 JSON이 아니라서 멈춰요: {error}\n")
    permissions = settings.setdefault("permissions", {})
    changed = []
    for name in LISTS:
        current = permissions.setdefault(name, [])
        for rule in rules.get(name, []):
            if args.remove and rule in current:
                current.remove(rule)
                changed.append(f"- {name}: {rule}")
            elif not args.remove and rule not in current:
                current.append(rule)
                changed.append(f"+ {name}: {rule}")
        if not current:
            del permissions[name]
    if not permissions:
        del settings["permissions"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shown = target.relative_to(ROOT) if target.is_relative_to(ROOT) else target
    print(f"{shown}: {'바뀐 규칙이 없어요' if not changed else f'{len(changed)}개 바꿨어요'}")
    for line in changed:
        print(line)


if __name__ == "__main__":
    main()
