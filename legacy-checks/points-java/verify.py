"""원본 프로그램과 같은 결과가 나오는지 검사해요(골든 마스터 비교).

  python3 verify.py                           src/의 Java 코드를 컴파일해서 검사해요
  python3 verify.py --java 다른폴더            다른 폴더의 Java 코드를 컴파일해서 검사해요
  python3 verify.py --cmd "python3 port/main.py"   다른 언어로 옮긴 프로그램을 검사해요
  python3 verify.py --case <사례 이름>        사례 하나만 검사해요(여러 번 줄 수 있어요)
  python3 verify.py --list                    사례 목록과 인자만 보여 줘요

하는 일
  1. expected/cases.json에 적힌 사례마다 프로그램을 이 폴더에서 실행해요.
     --cmd를 주면 "<명령> <사례 인자들>"을 셸에서 실행해요.
     인자 안의 {out}은 그 사례의 출력 폴더(actual/<사례>/out)로 바꿔서 넘겨요.
  2. 표준 출력, 종료 코드, 사례에 적힌 출력 파일을 expected/(원본을 실제로 실행해서 기록한 결과)와 비교해요.
     줄바꿈(\\r\\n과 \\n), 맨 끝 빈 줄, 맨 앞 BOM은 같게 봐요. 표준 오류(stderr)는 비교하지 않아요.
  3. 사례마다 OK나 FAIL을 찍고, 다르면 처음 다른 줄을 보여 줘요. 내 결과는 actual/<사례>/에 남아요.
  4. data/의 입력 파일이 바뀌지 않았는지도 확인해요.
  마지막 줄은 '통과 N/N'이에요. 모두 통과하면 종료 코드 0, 하나라도 다르면 1, 검사를 못 하면 2예요.

파이썬 3.10 이상, 표준 라이브러리만 써요. --cmd 없이 쓰면 JDK 17 이상(javac, java)이 필요해요.
JAVA_HOME이 있으면 그 안의 javac와 java를, 없으면 PATH에 있는 것을 써요.
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
ACTUAL = LAB / "actual"
DATA = LAB / "data"
TIMEOUT = 120
JAVA_FLAGS = ["-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8"]


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    parser = argparse.ArgumentParser(description="원본과 같은 결과가 나오는지 expected/와 비교해요.")
    how = parser.add_mutually_exclusive_group()
    how.add_argument("--cmd", help='내 프로그램을 실행하는 명령(예: --cmd "python3 port/main.py")')
    how.add_argument("--java", metavar="폴더", help="이 폴더의 .java를 컴파일해서 검사해요(기본 src)")
    parser.add_argument("--main", help="Java로 검사할 때 main이 있는 클래스 이름(보통은 저절로 찾아요)")
    parser.add_argument("--case", action="append", metavar="이름", help="이 사례만 검사해요")
    parser.add_argument("--list", action="store_true", help="사례 목록과 인자만 보여 줘요")
    args = parser.parse_args()

    manifest = json.loads((EXPECTED / "cases.json").read_text(encoding="utf-8"))
    if args.list:
        for case in manifest["cases"]:
            print(f"{case['name']:<16} {' '.join(case['args']) or '(인자 없음)'}")
            if case.get("note"):
                print(f"{'':<16} {case['note']}")
        return
    cases = pick_cases(manifest["cases"], args.case)
    before = hash_inputs()

    total = len(cases)
    with tempfile.TemporaryDirectory(prefix="verify-") as build:
        if args.cmd:
            print(f"검사 대상: 명령 {args.cmd}")
            runner = shell_runner(args.cmd)
        else:
            runner = java_runner(find_folder(args.java or "src"), args.main, manifest.get("java_main"), build)
            if runner is None:
                print(f"통과 0/{total}")
                sys.exit(1)
        passed = sum(1 for case in cases if run_case(case, runner))

    if hash_inputs() != before:
        print("FAIL data/ 안의 입력 파일이 바뀌었어요. 입력 파일은 고치지 않아요.")
        passed = min(passed, total - 1)
    print(f"통과 {passed}/{total}")
    sys.exit(0 if passed == total else 1)


def find_folder(name):
    """지금 위치 기준으로 먼저 찾고, 없으면 이 파일이 있는 폴더 기준으로 찾아요."""
    path = Path(name)
    if path.is_absolute() or (Path.cwd() / path).is_dir():
        return path.resolve()
    return (LAB / path).resolve()


def pick_cases(cases, names):
    if not names:
        return cases
    known = [c["name"] for c in cases]
    unknown = [n for n in names if n not in known]
    if unknown:
        stop(f"없는 사례예요: {', '.join(unknown)}. 있는 사례: {', '.join(known)}")
    return [c for c in cases if c["name"] in names]


def stop(message):
    print(f"verify.py: {message}")
    sys.exit(2)


# ---------------------------------------------------------------- 실행 방법 두 가지

def shell_runner(cmd):
    def run(args):
        joined = subprocess.list2cmdline(args) if os.name == "nt" else shlex.join(args)
        return subprocess.run(f"{cmd} {joined}".strip(), shell=True, cwd=LAB,
                              capture_output=True, timeout=TIMEOUT)
    return run


def java_runner(src, wanted_main, default_main, build):
    if not src.is_dir():
        stop(f"폴더가 없어요: {src}")
    sources = sorted(src.rglob("*.java"))
    if not sources:
        stop(f".java 파일이 없어요: {src}")
    javac, java = find_jdk()
    main_class = find_main_class(sources, wanted_main, default_main)
    command = [javac, "-encoding", "UTF-8", "-nowarn", "-d", build] + [str(p) for p in sources]
    result = subprocess.run(command, capture_output=True)
    if result.returncode != 0:
        print("FAIL 컴파일하지 못했어요. javac가 남긴 내용이에요.")
        for line in decode(result.stderr + result.stdout).splitlines()[:30]:
            print(f"     {line}")
        return None
    shown = src.relative_to(LAB).as_posix() if src.is_relative_to(LAB) else str(src)
    print(f"검사 대상: {shown} 폴더의 Java (시작 클래스 {main_class})")

    def run(args):
        return subprocess.run([java] + JAVA_FLAGS + ["-cp", build, main_class] + args, cwd=LAB,
                              capture_output=True, timeout=TIMEOUT)
    return run


def find_jdk():
    suffix = ".exe" if os.name == "nt" else ""
    home = os.environ.get("JAVA_HOME")
    if home:
        javac, java = Path(home) / "bin" / f"javac{suffix}", Path(home) / "bin" / f"java{suffix}"
        if javac.exists() and java.exists():
            return check_jdk(str(javac)), str(java)
    javac, java = shutil.which("javac"), shutil.which("java")
    if not javac or not java:
        stop("javac나 java를 찾지 못했어요. JDK 17 이상을 설치하고 새 터미널에서 `javac -version`을 확인해요.\n"
             "  JDK가 없으면 다른 언어로 옮긴 뒤 --cmd로 검사할 수 있어요.")
    return check_jdk(javac), java


def check_jdk(javac):
    """macOS에는 JDK가 없어도 /usr/bin/javac가 있어서, 실제로 실행해 봐야 알 수 있어요."""
    try:
        result = subprocess.run([javac, "-version"], capture_output=True, timeout=60)
    except OSError as error:
        stop(f"javac를 실행하지 못했어요: {error}")
    text = decode(result.stdout + result.stderr).strip()
    match = re.search(r"javac (\d+)", text)
    if result.returncode != 0 or not match:
        stop("javac가 동작하지 않아요. JDK 17 이상을 설치해요.\n  javac가 남긴 말: "
             + (text.splitlines()[0] if text else "(없음)"))
    if int(match.group(1)) < 17:
        print(f"주의: {text.splitlines()[0]}이에요. 이 예제는 JDK 17 이상을 기준으로 해요.")
    return javac


def find_main_class(sources, wanted, default):
    found = []
    for path in sources:
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"static\s+void\s+main\s*\(", text):
            package = re.search(r"^\s*package\s+([\w.]+)\s*;", text, re.MULTILINE)
            found.append((package.group(1) + "." if package else "") + path.stem)
    if wanted:
        if "." in wanted:
            return wanted
        matches = [name for name in found if name.split(".")[-1] == wanted]
        if len(matches) == 1:
            return matches[0]
        stop(f"main이 있는 클래스 {wanted}를 찾지 못했어요. 찾은 것: {', '.join(found) or '(없음)'}")
    if default in found:
        return default
    if len(found) == 1:
        return found[0]
    if not found:
        stop("main 메서드가 있는 클래스를 찾지 못했어요.")
    stop(f"main이 있는 클래스가 여러 개예요({', '.join(found)}). --main으로 하나를 골라요.")


# ---------------------------------------------------------------- 사례 하나 실행하고 비교

def run_case(case, runner):
    name = case["name"]
    workdir = ACTUAL / name
    shutil.rmtree(workdir, ignore_errors=True)
    (workdir / "out").mkdir(parents=True, exist_ok=True)
    out_arg = f"actual/{name}/out"
    args = [arg.replace("{out}", out_arg) for arg in case["args"]]
    try:
        result = runner(args)
    except subprocess.TimeoutExpired:
        print(f"FAIL {name}: {TIMEOUT}초 안에 끝나지 않았어요.")
        return False
    (workdir / "stdout.txt").write_bytes(result.stdout)
    if result.stderr:
        (workdir / "stderr.txt").write_bytes(result.stderr)

    problems = []
    if result.returncode != case["exit"]:
        problems.append(f"종료 코드가 달라요. 원본 {case['exit']}, 내 것 {result.returncode}")
    diff = first_difference((EXPECTED / case["stdout"]).read_bytes(), result.stdout)
    if diff:
        problems.append("표준 출력 " + diff)
    if case.get("files"):
        problems.extend(compare_tree(EXPECTED / case["files"], workdir / "out"))

    if not problems:
        print(f"OK   {name}")
        return True
    print(f"FAIL {name}  ({case.get('note', '')})")
    print(f"     실행 인자: {' '.join(args) or '(없음)'}")
    for problem in problems:
        for line in problem.splitlines():
            print(f"     {line}")
    errors = decode(result.stderr).strip().splitlines()
    if errors:
        print("     참고, 표준 오류(stderr)의 앞부분이에요:")
        for line in errors[:5]:
            print(f"       {line[:200]}")
    print(f"     내 결과 전체: actual/{name}/")
    return False


def compare_tree(expected_dir, actual_dir):
    want = files_under(expected_dir)
    got = files_under(actual_dir)
    problems = [f"파일이 없어요: {path}" for path in sorted(set(want) - set(got))]
    problems += [f"원본에는 없는 파일이 생겼어요: {path}" for path in sorted(set(got) - set(want))]
    for path in sorted(set(want) & set(got)):
        diff = first_difference(want[path].read_bytes(), got[path].read_bytes())
        if diff:
            problems.append(f"파일 {path} {diff}")
    return problems


def files_under(folder):
    if not folder.is_dir():
        return {}
    return {p.relative_to(folder).as_posix(): p for p in sorted(folder.rglob("*")) if p.is_file()}


def first_difference(expected_raw, actual_raw):
    """같으면 None, 다르면 처음 다른 줄을 설명하는 글을 돌려줘요."""
    want, got = normalize(expected_raw), normalize(actual_raw)
    if want == got:
        return None
    want_lines, got_lines = want.split("\n"), got.split("\n")
    for number, (w, g) in enumerate(zip(want_lines, got_lines), 1):
        if w != g:
            if w.split() == g.split():
                return (f"{number}번째 줄이 달라요. 글자는 같고 띄어쓰기만 달라요(·는 띄어쓰기 한 칸).\n"
                        f"  원본: {show(w, dots=True)}\n  내 것: {show(g, dots=True)}")
            return f"{number}번째 줄이 달라요.\n  원본: {show(w)}\n  내 것: {show(g)}"
    if len(want_lines) > len(got_lines):
        return (f"줄 수가 달라요. 원본은 {len(want_lines)}줄, 내 것은 {len(got_lines)}줄이에요.\n"
                f"  내 것에 없는 첫 줄({len(got_lines) + 1}번째): {show(want_lines[len(got_lines)])}")
    return (f"줄 수가 달라요. 원본은 {len(want_lines)}줄, 내 것은 {len(got_lines)}줄이에요.\n"
            f"  원본에 없는 첫 줄({len(want_lines) + 1}번째): {show(got_lines[len(want_lines)])}")


def show(line, dots=False):
    if dots:
        line = line.replace(" ", "·")
    if line == "":
        return "(빈 줄)"
    return line if len(line) <= 200 else line[:200] + "…"


def normalize(raw):
    text = decode(raw).replace("\r\n", "\n").replace("\r", "\n")
    if text.startswith("﻿"):
        text = text[1:]
    return text.rstrip("\n")


def decode(raw):
    return raw.decode("utf-8", errors="replace")


def hash_inputs():
    if not DATA.is_dir():
        return {}
    return {p.relative_to(LAB).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(DATA.rglob("*")) if p.is_file()}


if __name__ == "__main__":
    main()
