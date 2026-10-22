"""서비스 이벤트 집계. 계약은 SPEC.md를 따릅니다.

교육용 실습 파일이에요. 버그 신고가 들어온 상태 그대로 두었어요. 운영 코드가 아니에요.
"""


def _check_event(event):
    if not isinstance(event, dict):
        raise ValueError("이벤트는 딕셔너리여야 합니다")
    name = event.get("service")
    status = event.get("status")
    latency = event.get("latency_ms")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("service 값이 비어 있습니다")
    if type(status) is not int or not 100 <= status <= 599:
        raise ValueError("status는 100~599 정수여야 합니다")
    if type(latency) is not int or latency < 0:
        raise ValueError("latency_ms는 0 이상 정수여야 합니다")


def summarize(events, service=None, slow_ms=500):
    if type(slow_ms) is not int or slow_ms < 0:
        raise ValueError("slow_ms는 0 이상 정수여야 합니다")
    if service is not None and (not isinstance(service, str) or not service.strip()):
        raise ValueError("service 필터가 비어 있습니다")
    if not isinstance(events, list):
        raise ValueError("events는 리스트여야 합니다")
    for event in events:
        _check_event(event)

    rows = events
    if service:
        rows = [event for event in events if event["service"] == service]
    total = len(rows)
    errors = sum(event["status"] >= 400 for event in rows)
    slow = sum(event["latency_ms"] > slow_ms for event in rows)
    average = sum(event["latency_ms"] for event in rows) / total
    return {
        "service": service or "all",
        "total": total,
        "error_count": errors,
        "error_rate_pct": round(errors / len(events) * 100, 2),
        "slow_count": slow,
        "average_ms": round(average, 2),
    }
