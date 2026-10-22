#!/usr/bin/env python3
"""지금 동작을 기록한 expected/와 프로그램의 결과를 비교해요.

쓰는 법
  python3 verify.py                  src/의 프로그램을 실행해서 비교해요(받은 그대로라면 모두 통과해요).
  python3 verify.py --cmd "명령"     고치거나 다른 언어로 옮긴 프로그램을 같은 사례로 비교해요.
                                     예) --cmd "python3 new/reorder.py"
                                         --cmd "java -cp out Main"
  python3 verify.py --case basic     사례 하나만 실행해요(여러 번 써도 돼요).
  python3 verify.py --list           사례 목록만 보여 줘요.

Windows에서는 python3 대신 python이나 py를 써요.

하는 일
  1. expected/cases.json에 적힌 사례마다 프로그램을 실행해요. 실행 위치는 이 파일이 있는 폴더예요.
     명령 뒤에 사례의 인자를 붙여요. 인자 속 {out}은 verify-out/<사례 이름>으로 바꿔요.
     verify가 그 폴더를 비워서 미리 만들어 둬요.
  2. 종료 코드, 화면 출력(stdout), {out} 폴더에 생긴 파일을 expected/와 비교해요.
     줄바꿈(CRLF와 LF) 차이와 파일 끝 빈 줄은 같게 봐요. 나머지는 한 글자도 같아야 해요.
     stderr는 비교하지 않고, 실패했을 때 마지막 줄만 보여 줘요.
  3. data/의 입력 파일이 기록할 때와 다르거나 실행 중에 바뀌면 그 사례는 FAIL이에요.
  4. 사례마다 OK나 FAIL을 찍고, 다르면 처음 다른 줄을 보여 줘요. 마지막 줄은 "통과 N/N"이에요.
     모두 통과하면 종료 코드 0, 하나라도 다르면 1이에요.

파이썬 3.8 이상의 표준 라이브러리만 써요.
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

HERE = Path(__file__).resolve().parent
EXPECTED = HERE / "expected"
DATA = HERE / "data"
OUT_ROOT = HERE / "verify-out"
TIMEOUT = 60
OS_JUNK = {".DS_Store", "Thumbs.db", "desktop.ini"}   # 운영체제가 몰래 만드는 파일은 보지 않아요.


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(description="expected/에 기록한 지금 동작과 비교해요.")
    parser.add_argument("--cmd", help='검사할 프로그램을 실행하는 명령. 없으면 src/의 원본을 실행해요.')
    parser.add_argument("--case", action="append", metavar="NAME", help="이 사례만 실행해요(여러 번 써도 돼요).")
    parser.add_argument("--list", action="store_true", help="사례 목록만 보여 줘요.")
    args = parser.parse_args()

    manifest = load_manifest()
    cases = manifest["cases"]
    if args.list:
        for case in cases:
            print(f"{case['name']:<16} {case.get('note', '')}")
        return
    if args.case:
        names = [c["name"] for c in cases]
        unknown = [n for n in args.case if n not in names]
        if unknown:
            stop(f"없는 사례예요: {', '.join(unknown)}. 있는 사례: {', '.join(names)}")
        cases = [c for c in cases if c["name"] in args.case]

    if args.cmd:
        print(f"검사 대상: {args.cmd}")
    else:
        print(f"검사 대상: 원본 ({' '.join(manifest['original'])})")

    changed = changed_inputs(manifest.get("data_sha256", {}))
    passed = 0
    for case in cases:
        if run_case(case, args.cmd, manifest["original"], changed):
            passed += 1
    print(f"통과 {passed}/{len(cases)}")
    sys.exit(0 if passed == len(cases) else 1)


def load_manifest():
    path = EXPECTED / "cases.json"
    if not path.is_file():
        stop(f"{path.relative_to(HERE)}이 없어요. verify.py는 expected/ 폴더와 같은 곳에 있어야 해요.")
    return json.loads(path.read_text(encoding="utf-8"))


def stop(message):
    print(f"verify.py: {message}")
    sys.exit(2)


def changed_inputs(recorded):
    changed = set()
    for rel, digest in recorded.items():
        path = HERE / rel
        if not path.is_file() or file_digest(path) != digest:
            changed.add(rel)
    return changed


def run_case(case, cmd, original, changed):
    name = case["name"]
    out_dir = OUT_ROOT / name
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    case_args = [a.replace("{out}", f"verify-out/{name}") for a in case["args"]]

    env = dict(os.environ)
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    before = snapshot(DATA)
    try:
        if cmd:
            line = cmd + (" " + join_args(case_args) if case_args else "")
            proc = subprocess.run(line, shell=True, cwd=HERE, env=env,
                                  capture_output=True, timeout=TIMEOUT)
        else:
            proc = subprocess.run([sys.executable] + original + case_args, cwd=HERE, env=env,
                                  capture_output=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        print(f"FAIL {name}  ({case.get('note', '')})")
        print(f"     {TIMEOUT}초 안에 끝나지 않았어요.")
        return False

    problems = []
    if proc.returncode != case["exit"]:
        problems.append([f"종료 코드가 달라요. 기대 {case['exit']}, 실제 {proc.returncode}"])
    expected_out = read_text((EXPECTED / case["stdout"]).read_bytes())
    found = first_difference("화면 출력(stdout)", expected_out, read_text(proc.stdout))
    if found:
        problems.append(found)

    expected_files = case.get("files", [])
    for rel in expected_files:
        made = out_dir / rel
        if not made.is_file():
            problems.append([f"파일이 생기지 않았어요: {rel}"])
            continue
        want = read_text((EXPECTED / name / "files" / rel).read_bytes())
        found = first_difference(f"파일 {rel}", want, read_text(made.read_bytes()))
        if found:
            problems.append(found)
    extra = sorted(p.relative_to(out_dir).as_posix() for p in out_dir.rglob("*")
                   if p.is_file() and p.name not in OS_JUNK
                   and p.relative_to(out_dir).as_posix() not in expected_files)
    if extra:
        problems.append([f"기대에 없는 파일이 생겼어요: {', '.join(extra)}"])
    roots = [i.rstrip("/") for i in case.get("inputs", [])]
    touched = sorted(p for p in changed if any(p == r or p.startswith(r + "/") for r in roots))
    if touched:
        problems.append([f"입력 파일이 기록할 때와 달라요: {', '.join(touched)}. 입력 파일은 고치지 않아요."])
    if snapshot(DATA) != before:
        problems.append(["실행하는 동안 data/의 입력 파일이 바뀌었어요. 입력 파일은 고치지 않아요."])

    if not problems:
        print(f"OK   {name}")
        return True
    print(f"FAIL {name}  ({case.get('note', '')})")
    for lines in problems:
        for text in lines:
            print(f"     {text}")
    last = last_line(proc.stderr)
    if last:
        print(f"     stderr 마지막 줄: {last}")
    print(f"     실행한 인자: {' '.join(case_args) or '(없음)'}")
    if expected_files or extra:
        print(f"     만든 파일은 verify-out/{name}/에 남아 있어요.")
    return False


def read_text(raw):
    text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")
    return text.rstrip("\n")


def first_difference(label, expected, actual):
    if expected == actual:
        return None
    exp_lines, act_lines = expected.split("\n"), actual.split("\n")
    for number in range(max(len(exp_lines), len(act_lines))):
        want = exp_lines[number] if number < len(exp_lines) else None
        got = act_lines[number] if number < len(act_lines) else None
        if want != got:
            break
    lines = [f"{label} {number + 1}번째 줄부터 달라요. (기대 {len(exp_lines)}줄, 실제 {len(act_lines)}줄)"]
    if want is not None and got is not None and looks_same(want, got):
        lines.append("  눈에 안 보이는 글자가 달라서 그대로 보여 줘요(\\ufeff는 BOM, \\t는 탭).")
        want, got = repr(want), repr(got)
    lines.append(f"  기대 | {want if want is not None else '(줄 없음)'}")
    lines.append(f"  실제 | {got if got is not None else '(줄 없음)'}")
    return lines


def looks_same(a, b):
    def visible(s):
        return "".join(ch for ch in s if ch.isprintable()).strip()
    return visible(a) == visible(b)


def last_line(raw):
    text = raw.decode("utf-8", errors="replace").strip()
    return text.splitlines()[-1][:200] if text else ""


def join_args(items):
    if os.name == "nt":
        return subprocess.list2cmdline(items)
    return " ".join(shlex.quote(item) for item in items)


def file_digest(path):
    # 윈도우에서 git이 줄바꿈을 CRLF로 바꿔 받아도 같은 파일로 봐요.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def snapshot(folder):
    return {p.relative_to(folder).as_posix(): file_digest(p)
            for p in sorted(folder.rglob("*")) if p.is_file() and p.name not in OS_JUNK}


if __name__ == "__main__":
    main()
