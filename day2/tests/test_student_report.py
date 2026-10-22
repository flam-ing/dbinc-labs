"""여기부터 명세를 읽고 테스트를 추가하세요. reference/는 보지 않고 시작합니다."""

def test_empty_result(report_module):
    result = report_module.summarize([])
    assert result == {
        "service": "all", "total": 0, "error_count": 0,
        "error_rate_pct": 0.0, "slow_count": 0, "average_ms": 0.0,
    }
