"""선택한 구현을 먼저 검증한 뒤 로컬 실행 가능한 ZIP을 만듭니다."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("--impl", default="reference/report.py")
p.add_argument("--modules", default="integration/reference")
p.add_argument("--output", default="dist/dbinc-day2-report.zip")
a = p.parse_args()
impl = Path(a.impl).resolve()
modules = Path(a.modules).resolve()
output = Path(a.output).resolve()
# 검사가 실패했을 때 예전 ZIP이 남아 성공처럼 보이지 않게 먼저 지웁니다.
output.unlink(missing_ok=True)
subprocess.run([sys.executable, "-m", "pytest", "tests/test_contract.py", "--impl", str(impl), "-q"], cwd=ROOT, check=True)
subprocess.run([sys.executable, "-m", "pytest", "integration/tests", "--impl", str(impl), "--modules", str(modules), "-q"], cwd=ROOT, check=True)
subprocess.run([sys.executable, str(ROOT / "tools/run_report.py"), "--impl", str(impl), "--modules", str(modules)], cwd=ROOT, check=True)
output.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="dbinc-training-package-") as temp:
    bundle = Path(temp) / "dbinc-day2-report"
    # settings.local.json은 이 PC에서 허용한 권한과 MCP 승인이 담긴 개인 파일이라 넣지 않습니다.
    shutil.copytree(ROOT, bundle, ignore=shutil.ignore_patterns(".venv", "work", "dist", "artifacts", "__pycache__", ".pytest_cache", ".coverage", ".git", ".mcp.json", "settings.local.json"))
    shutil.copy2(impl, bundle / "reference/report.py")
    for filename in ("query.py", "process.py", "report.py"):
        shutil.copy2(modules / filename, bundle / "integration/reference" / filename)
    (bundle / "artifacts").mkdir()
    shutil.copy2(ROOT / "artifacts/day2-report.md", bundle / "artifacts/day2-report.md")
    # 2교시 디버깅 기록이 있으면 함께 넣습니다.
    debug_note = ROOT / "artifacts/debug-note.md"
    if debug_note.is_file():
        shutil.copy2(debug_note, bundle / "artifacts/debug-note.md")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(bundle.rglob("*")):
            if file.is_file():
                archive.write(file, file.relative_to(Path(temp)))
print(f"검증한 구현을 묶었습니다: {output}")
