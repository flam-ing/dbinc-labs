#!/usr/bin/env python3
"""급여 계산 배치가 지금 동작(expected/)과 똑같이 도는지 검사해요.

쓰는 법 (이 파일이 있는 폴더에서 실행해요)
  python3 verify.py
      src/ 폴더의 Java 코드를 컴파일하고 실행해서 expected/와 비교해요. JDK 17 이상이 필요해요.
      받은 그대로면 모두 통과해요. src/를 고칠 때마다 다시 돌려서 출력이 그대로인지 봐요.
  python3 verify.py --cmd "명령"
      다른 구조나 다른 언어로 옮긴 프로그램을 같은 사례로 비교해요.
      verify.py가 명령 뒤에 사례의 인자(직원 파일, 근태 파일, 대상월)를 붙여서 실행해요.
      예) python3 verify.py --cmd "java -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 -cp out nuri.pay.PayMain"
          python3 verify.py --cmd "python3 port/payroll.py"
  python3 verify.py --java 폴더
      그 폴더 아래의 .java 파일을 모두 컴파일하고, main 메서드가 있는 클래스를 찾아 실행해요.
      main이 여러 개면 --main 패키지.클래스 로 골라요.
  python3 verify.py --case oct
      사례 하나만 봐요. 여러 번 줄 수 있어요.
  python3 verify.py --list
      사례 목록과 인자만 보여 줘요.

비교하는 것
  - 표준 출력. 바이트로 받아 UTF-8로 풀고, 줄바꿈(CRLF와 LF) 차이는 무시해요.
  - 종료 코드.
  - 표준 오류(stderr)는 비교하지 않아요. 내용이 있으면 첫 줄만 참고로 보여 줘요.
  - data/ 폴더의 입력 파일이 바뀌면 실패로 봐요.

명령은 이 폴더에서 실행해요. 그래서 명령 안의 경로도 이 폴더를 기준으로 적어요.
마지막 줄은 "통과 N/N"이에요. 모두 통과하면 종료 코드 0, 하나라도 다르면 1이에요.
JDK는 JAVA_HOME이 있으면 그 안의 것을, 없으면 PATH의 javac와 java를 써요.
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
ORIGINAL_SRC = LAB / "src"
ORIGINAL_MAIN = "nuri.pay.PayMain"
JAVA_OPTS = ["-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8"]
TIMEOUT = 120


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(
        description="급여 계산 배치를 expected/에 기록된 원본 출력과 비교해요.")
    parser.add_argument("--cmd", help="내 프로그램 실행 명령(사례 인자는 verify.py가 뒤에 붙여요)")
    parser.add_argument("--java", metavar="폴더", help="이 폴더의 .java를 컴파일해서 검사해요")
    parser.add_argument("--main", help="--java에서 main 클래스를 직접 고를 때(예: nuri.payroll.PayrollApp)")
    parser.add_argument("--case", action="append", help="이 사례만 실행해요(여러 번 줄 수 있어요)")
    parser.add_argument("--list", action="store_true", help="사례 목록만 보여 줘요")
    args = parser.parse_args()

    manifest = json.loads((EXPECTED / "cases.json").read_text(encoding="utf-8"))
    cases = manifest["cases"]
    if args.list:
        for case in cases:
            print(f"{case['name']:<12} {' '.join(case['args']) or '(인자 없음)'}")
            print(f"{'':<12} {case['note']}")
        return
    if args.case:
        names = [c["name"] for c in cases]
        unknown = [n for n in args.case if n not in names]
        if unknown:
            setup_error(f"없는 사례예요: {', '.join(unknown)}. 있는 사례: {', '.join(names)}")
        cases = [c for c in cases if c["name"] in args.case]
    SELECTED.extend(cases)
    if args.cmd and args.java:
        setup_error("--cmd와 --java 중 하나만 써요.")

    with tempfile.TemporaryDirectory(prefix="verify-") as tmp:
        try:
            if args.cmd:
                base = args.cmd
            elif args.java:
                base = build_java(Path(args.java).resolve(), Path(tmp), args.main)
            else:
                base = build_java(ORIGINAL_SRC, Path(tmp), ORIGINAL_MAIN)
        except CompileError:
            print(f"통과 0/{len(cases)}")
            sys.exit(1)
        print(f"검사할 명령: {base}")
        before = hash_inputs()
        passed = sum(1 for case in cases if run_case(base, case))
        changed = hash_inputs() != before

    total = len(cases)
    if changed:
        print("FAIL 입력 파일: data/ 폴더의 파일이 바뀌었어요. 입력 파일은 고치지 않아요.")
    print(f"통과 {passed}/{total}")
    sys.exit(0 if passed == total and not changed else 1)


class CompileError(Exception):
    pass


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


def find_jdk():
    suffix = ".exe" if os.name == "nt" else ""
    home = os.environ.get("JAVA_HOME")
    if home:
        javac = Path(home) / "bin" / f"javac{suffix}"
        java = Path(home) / "bin" / f"java{suffix}"
        if javac.exists() and java.exists():
            return str(javac), str(java)
    javac, java = shutil.which("javac"), shutil.which("java")
    if not javac or not java:
        setup_error("javac나 java를 찾지 못했어요. JDK 17 이상을 설치하고 새 터미널에서 "
                    "`javac -version`이 되는지 확인해요. 원본 없이 내 프로그램만 검사하려면 "
                    "--cmd를 써요.", code=3)
    return javac, java


def check_javac(javac):
    """macOS에는 JDK가 없어도 /usr/bin/javac가 있어서, 실제로 실행해 봐야 알 수 있어요."""
    try:
        result = subprocess.run([javac, "-version"], capture_output=True, timeout=60)
    except OSError as error:
        setup_error(f"javac를 실행하지 못했어요: {error}", code=3)
    text = (result.stdout + result.stderr).decode("utf-8", errors="replace").strip()
    match = re.search(r"javac (\d+)", text)
    if result.returncode != 0 or not match:
        first = text.splitlines()[0] if text else "(출력 없음)"
        setup_error(f"javac가 동작하지 않아요. JDK 17 이상을 설치해요. javac가 남긴 말: {first}", code=3)
    if int(match.group(1)) < 17:
        print(f"주의: {text.splitlines()[0]}이에요. 원본은 record와 switch 식을 써서 JDK 17 이상이 필요해요.")


def build_java(src_dir, tmp, main_class):
    if not src_dir.is_dir():
        setup_error(f"폴더가 없어요: {src_dir}")
    sources = sorted(src_dir.rglob("*.java"))
    if not sources:
        setup_error(f".java 파일이 없어요: {src_dir}")
    javac, java = find_jdk()
    check_javac(javac)
    classes = tmp / "classes"
    command = [javac, "-encoding", "UTF-8", "-nowarn", "-d", str(classes)] + [str(p) for p in sources]
    result = subprocess.run(command, capture_output=True)
    if result.returncode != 0:
        print("FAIL 컴파일: javac가 남긴 내용이에요.")
        for line in result.stderr.decode("utf-8", errors="replace").splitlines()[:30]:
            print(f"    {line}")
        raise CompileError()
    main_class = main_class or find_main_class(sources)
    parts = [java] + JAVA_OPTS + ["-cp", str(classes), main_class]
    return " ".join(quote(p) for p in parts)


def find_main_class(sources):
    found = []
    for path in sources:
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"static\s+void\s+main\s*\(", text):
            package = re.search(r"^\s*package\s+([\w.]+)\s*;", text, re.MULTILINE)
            found.append(f"{package.group(1)}.{path.stem}" if package else path.stem)
    if len(found) == 1:
        return found[0]
    if not found:
        setup_error("main 메서드가 있는 클래스를 찾지 못했어요. --main 으로 알려 줘요.")
    setup_error(f"main이 여러 개예요: {', '.join(found)}. --main 으로 하나를 골라요.")


def run_case(base, case):
    name = case["name"]
    command = base + "".join(" " + quote(a) for a in case["args"])
    try:
        result = subprocess.run(command, shell=True, cwd=LAB, capture_output=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        print(f"FAIL {name}: {TIMEOUT}초 안에 끝나지 않았어요.")
        return False

    expected = normalize((EXPECTED / case["stdout"]).read_bytes())
    actual = normalize(result.stdout)
    same_exit = result.returncode == case["exit"]
    if expected == actual and same_exit:
        print(f"OK   {name}")
        return True

    print(f"FAIL {name}  ({case['note']})")
    print(f"  실행한 명령: {command}")
    if not same_exit:
        print(f"  종료 코드: 기대 {case['exit']}, 실제 {result.returncode}")
    if expected != actual:
        show_first_difference(expected, actual, case["stdout"])
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
            print(f"  처음 다른 줄: expected/{label}의 {number}번째 줄")
            print(f"    기대 | {e}")
            print(f"    실제 | {a}")
            if e.rstrip() == a.rstrip():
                print("    (줄 끝 공백만 달라요)")
            return
    if exp_lines[len(act_lines):] == [""] or act_lines[len(exp_lines):] == [""]:
        print("  마지막 줄바꿈 하나만 달라요.")
    elif len(exp_lines) > len(act_lines):
        print(f"  실제 출력이 {len(act_lines)}번째 줄에서 끝났어요. "
              f"기대하는 다음 줄: {exp_lines[len(act_lines)]}")
    else:
        print(f"  실제 출력에 줄이 더 있어요. "
              f"첫 번째 남는 줄({len(exp_lines) + 1}번째): {act_lines[len(exp_lines)]}")


def hash_inputs():
    return {str(p.relative_to(LAB)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(DATA.rglob("*")) if p.is_file()}


if __name__ == "__main__":
    main()
