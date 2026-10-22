from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import pytest

ROOT = Path(__file__).parent

def pytest_addoption(parser):
    parser.addoption("--impl", default="reference/report.py", help="검사할 summarize 구현 파일")
    parser.addoption("--modules", default="integration/reference", help="조회·가공·보고서 모듈 폴더")

@pytest.fixture(scope="session")
def report_module(request):
    path = Path(request.config.getoption("--impl")).resolve()
    if not path.is_file():
        pytest.fail(f"구현 파일이 없습니다: {path}. tools/start.py로 작업 폴더를 준비하세요.")
    spec = spec_from_file_location("student_report", path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

@pytest.fixture
def events():
    return [
        {"id":"a", "service":"billing", "status":200, "latency_ms":100},
        {"id":"b", "service":"billing", "status":500, "latency_ms":500},
        {"id":"c", "service":"catalog", "status":404, "latency_ms":900},
    ]

@pytest.fixture(scope="session")
def integration_modules(request):
    path = Path(request.config.getoption("--modules")).resolve()
    loaded = {}
    for name in ("process", "report"):
        spec = spec_from_file_location(f"integration_{name}", path / f"{name}.py")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        loaded[name] = module
    return loaded
