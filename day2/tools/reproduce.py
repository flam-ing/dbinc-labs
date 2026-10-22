"""제공 버그를 재현합니다. 정상 구현이면 모든 사례가 통과합니다."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("--impl", default="work/debug/report.py")
args = p.parse_args()
spec = importlib.util.spec_from_file_location("repro_report", Path(args.impl).resolve())
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
events = json.loads((ROOT / "fixtures/events.json").read_text())
checks = [("없는 서비스", "unknown", 0, 0.0, 0),
          ("오류 비율의 분모", "billing", 2, 66.67, 2),
          ("404와 500ms 경계", "catalog", 0, 0.0, 1)]
failures = 0
for label, service, count, rate, slow in checks:
    try:
        value = module.summarize(events, service=service)
        got = (value["error_count"], value["error_rate_pct"], value["slow_count"])
        expected = (count, rate, slow)
        if got != expected:
            failures += 1
            print(f"FAIL {label}: actual={got} expected={expected}")
        else:
            print(f"PASS {label}")
    except Exception as error:
        failures += 1
        print(f"ERROR {label}: {type(error).__name__}: {error}")
print(f"재현 실패 사례: {failures}/{len(checks)}")
sys.exit(1 if failures else 0)
