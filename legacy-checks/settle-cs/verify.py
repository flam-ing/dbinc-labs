r"""옮기거나 고친 프로그램이 원본 C#과 같은 결과를 내는지 검사해요.

  python3 verify.py                       src/의 C# 코드를 실행해서 expected/와 비교해요(.NET 8 SDK 필요).
  python3 verify.py --cmd "<실행 명령>"    아무 언어로 옮긴 프로그램을 같은 사례로 비교해요.
  python3 verify.py --java <폴더>         (편의) 폴더 안의 .java를 모두 컴파일해서 비교해요(JDK 17 이상).
  python3 verify.py --case basic          사례 하나만 봐요(여러 번 줄 수 있어요).
  python3 verify.py --list                사례 목록과 인자만 보여 줘요.

--cmd 예
  python3 verify.py --cmd "java -cp out DailySettle"
  python3 verify.py --cmd "python3 port/daily_settle.py"
  python3 verify.py --cmd "node port/dailySettle.js"

하는 일
  1. expected/cases.json의 사례마다 프로그램을 실행해요. 실행 위치는 이 파일이 있는 폴더예요.
     사례의 인자(args)를 명령 뒤에 붙여요. 입력 파일 경로(data/...)도 이 폴더를 기준으로 해요.
  2. 표준 출력과 종료 코드를 expected/(원본을 실제로 실행해서 기록한 결과)와 비교해요.
     줄바꿈 \r\n과 \n, 맨 끝 줄바꿈이 있고 없음은 같게 봐요. 표준 오류는 비교하지 않아요.
  3. 사례마다 OK나 FAIL을 찍어요. 다르면 처음 다른 줄을 보여 줘요. 마지막 줄은 "통과 N/N"이에요.
  4. data/의 입력 파일이 바뀌지 않았는지도 확인해요.

종료 코드: 0 모두 통과, 1 실패한 사례가 있음, 2 실행 준비 실패(런타임 없음, 컴파일 실패 등).
파이썬 3.10 이상, 표준 라이브러리만 써요.
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
SRC = LAB / "src"
PROJECT = "DailySettle"        # 원본 프로젝트: src/DailySettle.csproj
MAIN_CLASS = "DailySettle"     # --java에서 찾는 main 클래스 이름
TIMEOUT = 120
QUIET_DOTNET = {"DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1",
                "DOTNET_SKIP_FIRST_TIME_EXPERIENCE": "1"}


class SetupError(Exception):
    """프로그램을 실행할 준비가 안 됐을 때(런타임 없음, 컴파일 실패)."""


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(
        description="옮기거나 고친 프로그램을 원본 C#의 기록된 출력(expected/)과 비교해요.",
        epilog='예: python3 verify.py --cmd "java -cp out DailySettle"')
    how = parser.add_mutually_exclusive_group()
    how.add_argument("--cmd", metavar="명령",
                     help="검사할 프로그램의 실행 명령. 사례의 인자를 뒤에 붙여서 이 폴더에서 실행해요.")
    how.add_argument("--java", metavar="폴더",
                     help="(편의) 이 폴더의 .java를 모두 컴파일해서 검사해요. JDK 17 이상이 필요해요.")
    how.add_argument("--list", action="store_true", help="사례 목록만 보여 줘요.")
    parser.add_argument("--main", default=MAIN_CLASS,
                        help=f"--java에서 main 메서드가 있는 클래스 이름(기본 {MAIN_CLASS}).")
    parser.add_argument("--case", action="append", metavar="이름",
                        help="이 사례만 실행해요. 여러 번 줄 수 있어요.")
    args = parser.parse_args()

    cases = load_cases(args.case)
    if args.list:
        for case in cases:
            print(f"{case['name']:<16} 인자: {' '.join(case['args']) or '(없음)'}")
            print(f"{'':<16} 기대 출력: expected/{case['stdout']}, 종료 코드 {case['exit']}. {case['note']}")
        return

    before = hash_inputs()
    passed = 0
    with tempfile.TemporaryDirectory(prefix="verify-") as tmp:
        try:
            if args.cmd:
                label, run = f"내 프로그램 ({args.cmd})", shell_runner(args.cmd)
            elif args.java:
                label, run = java_runner(Path(args.java), args.main, Path(tmp))
            else:
                label, run = dotnet_runner(Path(tmp))
        except SetupError as error:
            print(f"준비 실패: {error}")
            print(f"통과 0/{len(cases)}")
            sys.exit(2)
        print(f"검사 대상: {label}")
        for case in cases:
            if run_case(run, case):
                passed += 1

    inputs_ok = hash_inputs() == before
    if not inputs_ok:
        print("FAIL data/의 입력 파일이 바뀌었어요. 입력은 고치지 않아요. 원래대로 되돌리고 다시 검사해요.")
    print(f"통과 {passed}/{len(cases)}")
    sys.exit(0 if passed == len(cases) and inputs_ok else 1)


def load_cases(names):
    manifest = json.loads((EXPECTED / "cases.json").read_text(encoding="utf-8"))
    cases = manifest["cases"]
    if names:
        known = [c["name"] for c in cases]
        unknown = [n for n in names if n not in known]
        if unknown:
            print(f"없는 사례예요: {', '.join(unknown)}. 있는 사례: {', '.join(known)}")
            sys.exit(2)
        cases = [c for c in cases if c["name"] in names]
    return cases


# ---------------------------------------------------------------- 실행 방법 세 가지

def shell_runner(command):
    """--cmd: 명령 뒤에 사례의 인자를 붙여서 셸로 실행해요."""
    def run(case_args):
        line = command + "".join(" " + quote_arg(a) for a in case_args)
        return subprocess.run(line, shell=True, cwd=LAB, capture_output=True, timeout=TIMEOUT)
    return run


def quote_arg(text):
    if os.name == "nt":
        return subprocess.list2cmdline([text])
    return shlex.quote(text)


def dotnet_runner(tmp):
    """기본: src/를 임시 폴더에 복사해서 빌드한 뒤 실행해요. src/ 안에는 bin/, obj/가 생기지 않아요."""
    dotnet, version = find_dotnet()
    if not (SRC / f"{PROJECT}.csproj").is_file():
        raise SetupError(f"src/{PROJECT}.csproj가 없어요.")
    build_dir = tmp / "src"
    shutil.copytree(SRC, build_dir, ignore=shutil.ignore_patterns("bin", "obj"))
    out_dir = tmp / "bin"
    env = dict(os.environ, **QUIET_DOTNET)
    result = subprocess.run([dotnet, "build", str(build_dir / f"{PROJECT}.csproj"), "-c", "Release",
                             "-o", str(out_dir), "--nologo"],
                            capture_output=True, env=env, timeout=900)
    if result.returncode != 0:
        lines = decode(result.stdout + result.stderr).splitlines()
        errors = [line.strip() for line in lines if re.search(r"error|오류", line, re.IGNORECASE)]
        raise SetupError("src/의 C# 코드를 빌드하지 못했어요. dotnet build가 남긴 말이에요.\n"
                         + indent(errors[:15] or lines[-15:]))
    dll = out_dir / f"{PROJECT}.dll"

    def run(case_args):
        return subprocess.run([dotnet, str(dll)] + case_args, cwd=LAB, capture_output=True,
                              timeout=TIMEOUT, env=env)
    return f"src/의 C# 코드 (.NET SDK {version})", run


def find_dotnet():
    """DOTNET_ROOT가 있으면 그 안의 dotnet을, 없으면 PATH에서 찾아요. SDK 8 이상이 있어야 해요."""
    exe = "dotnet.exe" if os.name == "nt" else "dotnet"
    candidates = []
    if os.environ.get("DOTNET_ROOT"):
        candidates.append(Path(os.environ["DOTNET_ROOT"]) / exe)
    if shutil.which("dotnet"):
        candidates.append(Path(shutil.which("dotnet")))
    for path in candidates:
        if not path.is_file():
            continue
        try:
            listed = subprocess.run([str(path), "--list-sdks"], capture_output=True, timeout=60,
                                    env=dict(os.environ, **QUIET_DOTNET))
        except OSError:
            continue
        versions = re.findall(r"^(\d+)\.(\d+)\.(\d+)", decode(listed.stdout), re.MULTILINE)
        good = [v for v in versions if int(v[0]) >= 8]
        if good:
            return str(path), ".".join(good[-1])
    raise SetupError(".NET 8 SDK를 찾지 못했어요. 원본을 직접 실행할 때만 필요해요. "
                     "원본 결과는 expected/에 이미 있으니, 옮긴 프로그램은 --cmd나 --java로 검사해요.")


def java_runner(folder, main_name, tmp):
    """--java: 폴더의 .java를 모두 컴파일하고 main 클래스를 실행해요."""
    folder = folder.resolve()
    if not folder.is_dir():
        raise SetupError(f"폴더가 없어요: {folder}")
    sources = sorted(folder.rglob("*.java"))
    if not sources:
        raise SetupError(f".java 파일이 없어요: {folder}")
    javac, java = find_jdk()
    classes = tmp / "classes"
    result = subprocess.run([javac, "-encoding", "UTF-8", "-d", str(classes)] + [str(p) for p in sources],
                            capture_output=True)
    if result.returncode != 0:
        raise SetupError("컴파일하지 못했어요. javac가 남긴 말이에요.\n"
                         + indent(decode(result.stderr or result.stdout).splitlines()[:30]))
    main_class = find_main_class(sources, main_name)

    def run(case_args):
        command = [java, "-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8", "-cp", str(classes), main_class]
        return subprocess.run(command + case_args, cwd=LAB, capture_output=True, timeout=TIMEOUT)
    return f"{folder}의 Java 코드 (main 클래스 {main_class})", run


def find_jdk():
    """JAVA_HOME이 있으면 그 안의 javac와 java를, 없으면 PATH에서 찾아요."""
    suffix = ".exe" if os.name == "nt" else ""
    home = os.environ.get("JAVA_HOME")
    if home:
        javac, java = Path(home) / "bin" / f"javac{suffix}", Path(home) / "bin" / f"java{suffix}"
        if javac.is_file() and java.is_file():
            check_jdk_version(str(javac))
            return str(javac), str(java)
    javac, java = shutil.which("javac"), shutil.which("java")
    if not javac or not java:
        raise SetupError("javac나 java를 찾지 못했어요. JDK 17 이상을 설치하고 새 터미널에서 "
                         "`javac -version`이 되는지 확인해요.")
    check_jdk_version(javac)
    return javac, java


def check_jdk_version(javac):
    """macOS에는 JDK가 없어도 /usr/bin/javac가 있어서, 실제로 실행해 봐야 알 수 있어요."""
    try:
        result = subprocess.run([javac, "-version"], capture_output=True, timeout=60)
    except OSError as error:
        raise SetupError(f"javac를 실행하지 못했어요: {error}")
    text = decode(result.stdout + result.stderr).strip()
    match = re.search(r"javac (\d+)", text)
    if result.returncode != 0 or not match:
        first = text.splitlines()[0] if text else "(출력 없음)"
        raise SetupError(f"javac가 동작하지 않아요. JDK 17 이상을 설치해요. javac가 남긴 말: {first}")
    if int(match.group(1)) < 17:
        print(f"주의: {text.splitlines()[0]}이에요. 이 실습은 JDK 17 이상을 기준으로 해요.")


def find_main_class(sources, name):
    if "." in name:
        return name
    for path in sources:
        if path.stem == name:
            text = path.read_text(encoding="utf-8", errors="replace")
            match = re.search(r"^\s*package\s+([\w.]+)\s*;", text, re.MULTILINE)
            return f"{match.group(1)}.{name}" if match else name
    raise SetupError(f"{name}.java를 찾지 못했어요. main 메서드가 있는 클래스 이름을 --main으로 알려 줘요.")


# ---------------------------------------------------------------- 비교

def run_case(run, case):
    name = case["name"]
    try:
        result = run(case["args"])
    except subprocess.TimeoutExpired:
        print(f"FAIL {name}  ({case['note']})")
        print(f"     {TIMEOUT}초 안에 끝나지 않았어요.")
        return False

    expected = clean((EXPECTED / case["stdout"]).read_bytes())
    actual = clean(result.stdout)
    exit_ok = result.returncode == case["exit"]
    if expected == actual and exit_ok:
        print(f"OK   {name}")
        return True

    print(f"FAIL {name}  ({case['note']})")
    print(f"     인자: {' '.join(case['args']) or '(없음)'}")
    if not exit_ok:
        print(f"     종료 코드: 기대 {case['exit']}, 실제 {result.returncode}")
    if expected != actual:
        show_first_difference(expected, actual)
    stderr = decode(result.stderr).strip()
    if stderr:
        print(f"     표준 오류 첫 줄(비교하지는 않아요): {stderr.splitlines()[0][:160]}")
    return False


def show_first_difference(expected, actual):
    exp_lines, act_lines = expected.split("\n"), actual.split("\n")
    pairs = list(zip(exp_lines, act_lines))
    differing = sum(1 for e, a in pairs if e != a) + abs(len(exp_lines) - len(act_lines))
    for number, (e, a) in enumerate(pairs, 1):
        if e != a:
            column = next((i for i, (x, y) in enumerate(zip(e, a)) if x != y), min(len(e), len(a))) + 1
            print(f"     처음 다른 줄: {number}번째 줄, {column}번째 글자부터 (다른 줄 모두 {differing}개)")
            print(f"       기대 | {e}")
            print(f"       실제 | {a}")
            if e.rstrip() == a.rstrip():
                print("       줄 끝의 공백만 달라요.")
            return
    shorter = len(pairs)
    print(f"     줄 수가 달라요: 기대 {len(exp_lines)}줄, 실제 {len(act_lines)}줄. 앞의 {shorter}줄은 같아요.")
    if len(exp_lines) > shorter:
        print(f"       기대에만 있는 {shorter + 1}번째 줄 | {exp_lines[shorter]}")
    else:
        print(f"       실제에만 있는 {shorter + 1}번째 줄 | {act_lines[shorter]}")


def clean(raw):
    text = decode(raw)
    if text.startswith("﻿"):
        text = text[1:]
    return text.replace("\r\n", "\n").rstrip("\n")


def decode(raw):
    return raw.decode("utf-8", errors="replace")


def indent(lines):
    return "\n".join("    " + line for line in lines)


def hash_inputs():
    return {str(p.relative_to(LAB)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(DATA.rglob("*")) if p.is_file()}


if __name__ == "__main__":
    main()
