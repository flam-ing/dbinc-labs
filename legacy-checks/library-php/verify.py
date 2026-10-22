#!/usr/bin/env python3
"""사내 도서 대여의 일괄 처리와 연체 보고가 지금 동작(expected/)과 똑같이 도는지 검사해요.

쓰는 법 (이 파일이 있는 폴더에서 실행해요)
  python3 verify.py
      src/ 폴더의 PHP를 실행해서 expected/와 비교해요. PHP 8 이상이 필요해요.
      받은 그대로면 모두 통과해요. src/를 고칠 때마다 다시 돌려서 결과가 그대로인지 봐요.
  python3 verify.py --src 폴더
      다른 폴더에 새로 만든 PHP를 검사해요. 그 폴더에 batch.php와 overdue_report.php가 있어야 해요.
  python3 verify.py --cmd "명령"
      다른 언어로 옮긴 프로그램을 같은 사례로 비교해요.
      명령에 {script}를 쓰면 사례마다 batch 또는 overdue_report로 바뀌어요.
      {script}가 없으면 명령 뒤에 batch나 overdue_report를 첫 인자로 붙여요.
      예) python3 verify.py --cmd "php -n new/{script}.php"
          python3 verify.py --cmd "python3 port/library.py"
  python3 verify.py --case batch-1226
      사례 하나만 봐요. 여러 번 줄 수 있어요.
  python3 verify.py --list
      사례 목록과 인자만 보여 줘요.

사례마다 하는 일
  1. data/store를 임시 폴더에 새로 복사해요. 인자의 {store}는 이 임시 폴더 경로로 바뀌어요.
     그래서 프로그램이 저장소 파일을 고쳐도 data/는 그대로예요.
  2. 이 폴더에서 명령을 실행해요. 명령 안의 경로도 이 폴더를 기준으로 적어요.
  3. 표준 출력, 종료 코드, 그리고 사례에 적힌 저장소 파일(books.csv 등)을 expected/와 비교해요.
     바이트로 받아 UTF-8로 풀고, 줄바꿈(CRLF와 LF) 차이는 무시해요.
     표준 오류(stderr)는 비교하지 않아요. 내용이 있으면 첫 줄만 참고로 보여 줘요.

마지막 줄은 "통과 N/N"이에요. 모두 통과하면 종료 코드 0, 하나라도 다르면 1이에요.
PHP는 PHP_BIN 환경 변수가 있으면 그것을, 없으면 PATH의 php를 써요.
파이썬 표준 라이브러리만 써요.
"""
import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LAB = Path(__file__).resolve().parent
EXPECTED = LAB / "expected"
DATA = LAB / "data"
STORE = DATA / "store"
TIMEOUT = 120


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(
        description="일괄 처리와 연체 보고를 expected/에 기록된 원본 결과와 비교해요.")
    parser.add_argument("--cmd", help="내 프로그램 실행 명령({script} 자리에 batch나 overdue_report가 들어가요)")
    parser.add_argument("--src", metavar="폴더", help="batch.php와 overdue_report.php가 있는 폴더(기본 src)")
    parser.add_argument("--case", action="append", help="이 사례만 실행해요(여러 번 줄 수 있어요)")
    parser.add_argument("--list", action="store_true", help="사례 목록만 보여 줘요")
    args = parser.parse_args()

    manifest = json.loads((EXPECTED / "cases.json").read_text(encoding="utf-8"))
    cases = manifest["cases"]
    if args.list:
        for case in cases:
            print(f"{case['name']:<16} {case['script']} {' '.join(case['args']) or '(인자 없음)'}")
            print(f"{'':<16} {case['note']}")
        return
    if args.case:
        names = [c["name"] for c in cases]
        unknown = [n for n in args.case if n not in names]
        if unknown:
            setup_error(f"없는 사례예요: {', '.join(unknown)}. 있는 사례: {', '.join(names)}")
        cases = [c for c in cases if c["name"] in args.case]
    SELECTED.extend(cases)
    if args.cmd and args.src:
        setup_error("--cmd와 --src 중 하나만 써요.")

    if args.cmd:
        base = args.cmd
    else:
        src = Path(args.src) if args.src else Path("src")
        for script in ("batch", "overdue_report"):
            if not (LAB / src / f"{script}.php").is_file():
                setup_error(f"{src / (script + '.php')} 파일이 없어요.")
        base = php_command() + " " + quote(f"{src.as_posix()}/{{script}}.php")
    print(f"검사할 명령: {base}")

    before = hash_inputs()
    passed = sum(1 for case in cases if run_case(base, case))
    changed = hash_inputs() != before

    total = len(cases)
    if changed:
        print("FAIL 입력 파일: data/ 폴더의 파일이 바뀌었어요. 저장소는 {store} 인자로 받은 폴더에만 써야 해요.")
    print(f"통과 {passed}/{total}")
    sys.exit(0 if passed == total and not changed else 1)


SELECTED = []


def setup_error(message, code=2):
    """검사를 시작하지 못할 때예요. 실행 도구가 없으면(code 3) 마지막 줄을 통과 0/N으로 맞춰요."""
    print(f"verify.py: {message}")
    if code == 3 and SELECTED:
        print(f"통과 0/{len(SELECTED)}")
    sys.exit(code)


def quote(arg):
    """셸 명령에 넣을 인자를 감싸요. Windows(cmd.exe)는 큰따옴표를 써요."""
    if os.name == "nt":
        if arg and not re.search(r'[\s"&|<>^()%!]', arg):
            return arg
        return '"' + arg.replace('"', '\\"') + '"'
    return shlex.quote(arg)


def php_command():
    """php.ini 설정에 흔들리지 않게 -n으로 실행하고, PHP 경고는 stderr로 보내요."""
    php = os.environ.get("PHP_BIN") or shutil.which("php")
    if not php:
        setup_error("php를 찾지 못했어요. PHP 8 이상을 설치하고 새 터미널에서 `php -v`가 되는지 "
                    "확인해요. PHP 없이 다른 언어로 옮긴 프로그램만 검사하려면 --cmd를 써요.", code=3)
    try:
        result = subprocess.run([php, "-n", "-v"], capture_output=True, timeout=60)
    except OSError as error:
        setup_error(f"php를 실행하지 못했어요: {error}", code=3)
    first = result.stdout.decode("utf-8", errors="replace").strip().splitlines()[:1]
    match = re.match(r"PHP (\d+)\.", first[0]) if first else None
    if result.returncode != 0 or not match:
        setup_error(f"php가 동작하지 않아요. php가 남긴 말: {first[0] if first else '(출력 없음)'}", code=3)
    if int(match.group(1)) < 8:
        print(f"주의: {first[0]}이에요. expected/는 PHP 8로 기록했어요.")
    return " ".join(quote(p) for p in [php, "-n", "-d", "display_errors=stderr"])


def build_command(base, case, store):
    args = [a.replace("{store}", str(store)) for a in case["args"]]
    if "{script}" in base:
        command = base.replace("{script}", case["script"])
    else:
        command = base + " " + case["script"]
    return command + "".join(" " + quote(a) for a in args)


def run_case(base, case):
    name = case["name"]
    with tempfile.TemporaryDirectory(prefix="verify-") as tmp:
        store = Path(tmp) / "store"
        shutil.copytree(STORE, store)
        command = build_command(base, case, store)
        try:
            result = subprocess.run(command, shell=True, cwd=LAB, capture_output=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            print(f"FAIL {name}: {TIMEOUT}초 안에 끝나지 않았어요.")
            return False

        problems = []
        expected = normalize((EXPECTED / case["stdout"]).read_bytes())
        actual = normalize(result.stdout)
        if expected != actual:
            problems.append(("표준 출력", f"expected/{case['stdout']}", expected, actual))
        for stored, want in case.get("files", {}).items():
            path = store / stored
            got = normalize(path.read_bytes()) if path.is_file() else None
            want_text = normalize((EXPECTED / want).read_bytes())
            if got != want_text:
                problems.append((f"저장소 파일 {stored}", f"expected/{want}", want_text, got))
        same_exit = result.returncode == case["exit"]

    if not problems and same_exit:
        print(f"OK   {name}")
        return True

    print(f"FAIL {name}  ({case['note']})")
    print(f"  실행한 명령: {command}")
    if not same_exit:
        print(f"  종료 코드: 기대 {case['exit']}, 실제 {result.returncode}")
    for what, label, want, got in problems:
        if got is None:
            print(f"  다른 곳: {what}. 파일이 없어요. 저장소 폴더 인자로 받은 곳에 같은 이름으로 저장해야 해요.")
            continue
        print(f"  다른 곳: {what}")
        show_first_difference(want, got, label)
    stderr = result.stderr.decode("utf-8", errors="replace").strip()
    if stderr:
        print(f"  참고(stderr 첫 줄): {stderr.splitlines()[0][:160]}")
    return False


def normalize(raw):
    text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")
    return text[1:] if text.startswith("﻿") else text


def show_first_difference(expected, actual, label):
    exp_lines = expected.split("\n")
    act_lines = actual.split("\n")
    for number, (e, a) in enumerate(zip(exp_lines, act_lines), 1):
        if e != a:
            print(f"    처음 다른 줄: {label}의 {number}번째 줄")
            print(f"      기대 | {e}")
            print(f"      실제 | {a}")
            if e.rstrip() == a.rstrip():
                print("      (줄 끝 공백만 달라요)")
            return
    if exp_lines[len(act_lines):] == [""] or act_lines[len(exp_lines):] == [""]:
        print("    마지막 줄바꿈 하나만 달라요.")
    elif len(exp_lines) > len(act_lines):
        print(f"    실제 결과가 {len(act_lines)}번째 줄에서 끝났어요. "
              f"기대하는 다음 줄: {exp_lines[len(act_lines)]}")
    else:
        print(f"    실제 결과에 줄이 더 있어요. "
              f"첫 번째 남는 줄({len(exp_lines) + 1}번째): {act_lines[len(exp_lines)]}")


def hash_inputs():
    return {str(p.relative_to(LAB)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(DATA.rglob("*")) if p.is_file()}


if __name__ == "__main__":
    main()
