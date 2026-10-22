#!/usr/bin/env python3
"""상담 티켓 분류 검사 도구

원본 CLI나 내가 고친 프로그램을 expected/cases.json의 사례대로 실행하고,
표준 출력을 expected/에 기록된 결과(원본 CLI를 실제로 실행해서 남긴 것)와 비교해요.

  python3 verify.py                                   원본(node cli/triage.js)을 검사해요
  python3 verify.py --cmd "node cli/triage.js"        실행 명령을 직접 줘요
  python3 verify.py --cmd "node adapters/cli.js"      구조를 바꾼 프로그램도 같은 사례로 검사해요
  python3 verify.py --cmd "python3 port/triage.py"    다른 언어로 옮긴 프로그램도 검사해요
  python3 verify.py --case basic                      사례 하나만 실행해요(여러 번 줄 수 있어요)
  python3 verify.py --list                            사례 목록과 인자만 보여 줘요

- 명령은 이 폴더(verify.py가 있는 곳)에서 실행돼요. 명령 뒤에 사례의 인자가 붙어요.
- 표준 출력이 .json으로 기록된 사례는 JSON 내용으로 비교해요. 키 순서와 들여쓰기는 보지 않고, 배열 순서는 봐요.
- 글로 기록된 사례는 줄 단위로 비교해요. 줄바꿈(CRLF, LF), 줄 끝 공백, 맨 끝 빈 줄 차이는 무시해요.
- 종료 코드도 비교해요. 오류 메시지(stderr)는 비교하지 않아요.
- 웹 화면(web/)은 검사하지 않아요. 브라우저로 열어서 봐요.
- Windows에서는 python3 대신 python이나 py로 실행해요.

파이썬 표준 라이브러리만 써요.
"""
import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
EXPECTED = LAB / "expected"
INPUTS = LAB / "data"
OUT_ROOT = LAB / ".verify-out"
DEFAULT_CMD = "node cli/triage.js"
RUNTIME = "node"
RUNTIME_HINT = "Node 18 이상을 설치하고 새 터미널에서 node --version이 되는지 확인해요."
ID_KEYS = ("id", "category", "urgency")
TIMEOUT = 60


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="expected/에 기록된 원본의 결과와 비교해요.")
    parser.add_argument("--cmd", help=f'실행 명령(기본 "{DEFAULT_CMD}"). 이 폴더에서 실행돼요.')
    parser.add_argument("--case", action="append", help="이 사례만 실행해요(여러 번 줄 수 있어요).")
    parser.add_argument("--list", action="store_true", help="사례 목록과 인자만 보여 줘요.")
    parser.add_argument("--keep", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    manifest = json.loads((EXPECTED / "cases.json").read_text(encoding="utf-8"))
    if args.list:
        for case in manifest["cases"]:
            print(f"{case['name']:<16} {' '.join(case['args']) or '(인자 없음)'}")
            if case.get("note"):
                print(f"{'':<16} {case['note']}")
        return

    command = args.cmd or DEFAULT_CMD
    if not args.cmd and shutil.which(RUNTIME) is None:
        stop(f"{RUNTIME} 명령을 찾지 못했어요. {RUNTIME_HINT}")

    cases = manifest["cases"]
    if args.case:
        names = [c["name"] for c in cases]
        unknown = [n for n in args.case if n not in names]
        if unknown:
            stop(f"없는 사례예요: {', '.join(unknown)}. 있는 사례: {', '.join(names)}")
        cases = [c for c in cases if c["name"] in args.case]

    print(f"실행 명령: {command}  (이 폴더에서 실행해요: {LAB})")
    before = hash_inputs()
    passed = 0
    try:
        for case in cases:
            if run_case(command, case):
                passed += 1
    finally:
        if not args.keep:
            shutil.rmtree(OUT_ROOT, ignore_errors=True)

    if hash_inputs() != before:
        print("FAIL 입력 파일(data/)이 바뀌었어요. 프로그램이 입력을 고치면 안 돼요.")
        passed = min(passed, len(cases) - 1)
    print(f"통과 {passed}/{len(cases)}")
    sys.exit(0 if passed == len(cases) else 1)


def stop(message):
    print(f"verify.py: {message}")
    sys.exit(2)


def quote(arg):
    if os.name == "nt":
        return subprocess.list2cmdline([arg])
    return shlex.quote(arg)


def run_case(command, case):
    name = case["name"]
    out_dir = OUT_ROOT / name
    shutil.rmtree(out_dir, ignore_errors=True)
    if any("{out}" in a for a in case["args"]) or case.get("files") or case.get("absent"):
        out_dir.mkdir(parents=True)
    out_rel = out_dir.relative_to(LAB).as_posix()
    case_args = [a.replace("{out}", out_rel) for a in case["args"]]
    full = command + "".join(" " + quote(a) for a in case_args)
    try:
        result = subprocess.run(full, shell=True, cwd=LAB, capture_output=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        print(f"FAIL {name}: {TIMEOUT}초 안에 끝나지 않았어요.")
        return False

    problems = []
    if result.returncode != case["exit"]:
        problems.append(f"종료 코드가 달라요. 기대 {case['exit']}, 실제 {result.returncode}")
    if case.get("stdout"):
        problems += compare_output("표준 출력", result.stdout, EXPECTED / case["stdout"])
    for produced, recorded in case.get("files", {}).items():
        target = out_dir / produced
        if not target.is_file():
            problems.append(f"{produced} 파일이 생기지 않았어요.")
            continue
        problems += compare_output(produced, target.read_bytes(), EXPECTED / recorded)
    for produced in case.get("absent", []):
        if (out_dir / produced).exists():
            problems.append(f"{produced} 파일이 생기면 안 되는데 생겼어요.")

    if not problems:
        print(f"OK   {name}")
        return True
    print(f"FAIL {name}  ({case.get('note', '')})")
    print(f"  실행한 명령: {full}")
    for line in problems:
        print("  " + line.replace("\n", "\n  "))
    show_stderr(result)
    return False


def compare_output(label, actual_bytes, expected_path):
    expected_text = decode(expected_path.read_bytes())
    actual_text = decode(actual_bytes)
    if expected_path.suffix == ".json":
        return compare_json(label, expected_text, actual_text)
    return compare_text(label, expected_text, actual_text)


def decode(raw):
    text = raw.decode("utf-8", errors="replace")
    if text.startswith("\ufeff"):
        text = text[1:]
    return text.replace("\r\n", "\n")


def compare_text(label, expected, actual):
    exp_lines = [line.rstrip() for line in expected.rstrip().split("\n")]
    act_lines = [line.rstrip() for line in actual.rstrip().split("\n")]
    for number, (e, a) in enumerate(zip(exp_lines, act_lines), 1):
        if e != a:
            return [f"{label}: {number}번째 줄이 처음으로 달라요.\n  기대 | {e}\n  실제 | {a}"]
    if len(exp_lines) != len(act_lines):
        number = min(len(exp_lines), len(act_lines)) + 1
        extra = exp_lines[number - 1] if len(exp_lines) > len(act_lines) else act_lines[number - 1]
        who = "기대에만" if len(exp_lines) > len(act_lines) else "실제에만"
        return [f"{label}: 줄 수가 달라요. 기대 {len(exp_lines)}줄, 실제 {len(act_lines)}줄.\n"
                f"  {number}번째 줄은 {who} 있어요 | {extra}"]
    return []


def compare_json(label, expected, actual):
    try:
        exp = json.loads(expected)
    except ValueError as error:
        return [f"{label}: expected 파일이 JSON이 아니에요({error}). expected/를 고쳤는지 확인해요."]
    try:
        act = json.loads(actual)
    except ValueError as error:
        first = actual.strip().split("\n")[0][:120] if actual.strip() else "(비어 있음)"
        return [f"{label}: JSON으로 읽을 수 없어요({error}).\n  실제 첫 줄 | {first}"]
    diff = first_json_diff(exp, act, "")
    if diff is None:
        return []
    path, e, a = diff
    lines = [f"{label}: {path or '(맨 위)'} 에서 처음으로 달라요."]
    hint = element_hint(exp, path)
    if hint:
        lines.append(f"  (기대 쪽 그 항목: {hint})")
    if isinstance(e, str) and isinstance(a, str) and max(len(e), len(a)) > 60:
        lines += string_diff(e, a)
    else:
        lines.append(f"  기대 | {show(e)}")
        lines.append(f"  실제 | {show(a)}")
    return ["\n".join(lines)]


def kind(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    return "object"


class _Missing:
    """배열 항목이나 키가 한쪽에만 있을 때 쓰는 표시예요."""

    def __repr__(self):
        return "(없음)"


MISSING = _Missing()


def first_json_diff(exp, act, path):
    if kind(exp) != kind(act):
        return path, exp, act
    if isinstance(exp, list):
        for i, (e, a) in enumerate(zip(exp, act)):
            found = first_json_diff(e, a, f"{path}[{i}]")
            if found:
                return found
        if len(exp) > len(act):
            return f"{path}[{len(act)}]", exp[len(act)], MISSING
        if len(act) > len(exp):
            return f"{path}[{len(exp)}]", MISSING, act[len(exp)]
        return None
    if isinstance(exp, dict):
        for key in exp:
            if key not in act:
                return f"{path}.{key}", exp[key], MISSING
            found = first_json_diff(exp[key], act[key], f"{path}.{key}")
            if found:
                return found
        for key in act:
            if key not in exp:
                return f"{path}.{key}", MISSING, act[key]
        return None
    return None if exp == act else (path, exp, act)


def element_hint(exp, path):
    """[12].sendAt 처럼 배열 안 항목이 다르면, 그 항목을 알아볼 수 있는 값을 보여 줘요."""
    if not path.startswith("[") or not isinstance(exp, list):
        return ""
    index = int(path[1:path.index("]")])
    if index >= len(exp) or not isinstance(exp[index], dict):
        return ""
    item = exp[index]
    return ", ".join(f"{k}={item[k]}" for k in ID_KEYS if k in item)


def string_diff(e, a):
    i = 0
    while i < min(len(e), len(a)) and e[i] == a[i]:
        i += 1
    start = max(0, i - 25)
    count = f"  글자 수: 기대 {len(e)}자, 실제 {len(a)}자."
    if utf16_len(e) != len(e) or utf16_len(a) != len(a):
        count += f" (자바스크립트 length로 세면 기대 {utf16_len(e)}, 실제 {utf16_len(a)}. 이모지는 2로 세요.)"
    return [f"{count} {i + 1}번째 글자부터 달라요.",
            f"  기대 | {'…' if start else ''}{show(e[start:i + 40])}",
            f"  실제 | {'…' if start else ''}{show(a[start:i + 40])}"]


def utf16_len(text):
    return len(text.encode("utf-16-le", errors="surrogatepass")) // 2


def show(value):
    if value is MISSING:
        return "(없음)"
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 200 else text[:200] + " …"


def show_stderr(result):
    """오류 메시지(stderr)를 보여 줘요. Node는 앞쪽에, 파이썬은 맨 끝에 진짜 오류가 있어서 둘 다 보여 줘요."""
    text = result.stderr.decode("utf-8", errors="replace").strip()
    if not text:
        return
    lines = text.splitlines()
    shown = lines if len(lines) <= 7 else lines[:5] + ["…"] + lines[-2:]
    print("  stderr:")
    for line in shown:
        print("    " + line[:200])


def hash_inputs():
    return {p.relative_to(LAB).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(INPUTS.rglob("*")) if p.is_file()}


if __name__ == "__main__":
    main()
