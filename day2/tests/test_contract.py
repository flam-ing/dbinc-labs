"""수강생 구현을 검증하는 독립 검사. 구현과 함께 정답을 바꾸지 마세요."""
from copy import deepcopy
import pytest

def test_mixed_events(report_module, events):
    assert report_module.summarize(events) == {
        "service":"all", "total":3, "error_count":1,
        "error_rate_pct":33.33, "slow_count":2, "average_ms":500.0,
    }

def test_filtered_denominator(report_module, events):
    assert report_module.summarize(events, service="billing") == {
        "service":"billing", "total":2, "error_count":1,
        "error_rate_pct":50.0, "slow_count":1, "average_ms":300.0,
    }

@pytest.mark.parametrize("service", [None, "unknown"])
def test_empty(report_module, service):
    result = report_module.summarize([], service=service)
    assert result == {"service":service or "all", "total":0, "error_count":0,
                      "error_rate_pct":0.0, "slow_count":0, "average_ms":0.0}

def test_unknown_service(report_module, events):
    assert report_module.summarize(events, service="no-such-service")["total"] == 0

@pytest.mark.parametrize("status,expected", [(100,0),(399,0),(400,0),(499,0),(500,1),(599,1)])
def test_error_boundary(report_module, status, expected):
    assert report_module.summarize([{"service":"a","status":status,"latency_ms":0}])["error_count"] == expected

@pytest.mark.parametrize("latency,expected", [(0,0),(499,0),(500,1),(501,1)])
def test_slow_boundary(report_module, latency, expected):
    assert report_module.summarize([{"service":"a","status":200,"latency_ms":latency}])["slow_count"] == expected

def test_custom_threshold(report_module, events):
    assert report_module.summarize(events, slow_ms=0)["slow_count"] == 3

def test_input_unchanged(report_module, events):
    old = deepcopy(events)
    report_module.summarize(events, service="billing")
    assert events == old

def test_trimmed_service(report_module):
    rows = [{"service":" billing ","status":200,"latency_ms":1}]
    assert report_module.summarize(rows, service=" billing ")["total"] == 1

@pytest.mark.parametrize("field,value", [
    ("service",""),("service"," "),("service",None),
    ("status",99),("status",600),("status",True),("status","500"),
    ("latency_ms",-1),("latency_ms",True),("latency_ms",1.5),("latency_ms",None),
])
def test_bad_event(report_module, field, value):
    row = {"service":"billing","status":200,"latency_ms":20}
    row[field] = value
    with pytest.raises(ValueError):
        report_module.summarize([row])

@pytest.mark.parametrize("events", [None, {}, "events", [None], [{}]])
def test_invalid_shape(report_module, events):
    with pytest.raises(ValueError):
        report_module.summarize(events)

@pytest.mark.parametrize("threshold", [-1, True, 0.5, "500", None])
def test_invalid_threshold(report_module, threshold):
    with pytest.raises(ValueError):
        report_module.summarize([], slow_ms=threshold)

@pytest.mark.parametrize("service", ["", " ", 1, False])
def test_invalid_service_filter(report_module, service):
    with pytest.raises(ValueError):
        report_module.summarize([], service=service)

def test_validate_before_filter(report_module):
    with pytest.raises(ValueError):
        report_module.summarize([{"service":"other","status":700,"latency_ms":1}], service="billing")
