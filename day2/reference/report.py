"""교육용 가상 서비스 이벤트 집계. 외부 시스템에 접속하지 않습니다."""

def summarize(events, service=None, slow_ms=500):
    """SPEC.md의 입력과 출력 계약에 따라 집계합니다. 입력은 수정하지 않습니다."""
    if type(slow_ms) is not int or slow_ms < 0:
        raise ValueError("slow_ms must be a non-negative integer")
    if service is not None:
        if not isinstance(service, str) or not service.strip():
            raise ValueError("service must be a non-empty string or None")
        service = service.strip()
    if not isinstance(events, list):
        raise ValueError("events must be a list")
    selected = []
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("each event must be an object")
        name = event.get("service")
        status = event.get("status")
        latency = event.get("latency_ms")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("event.service must be a non-empty string")
        if type(status) is not int or not 100 <= status <= 599:
            raise ValueError("event.status must be an integer from 100 to 599")
        if type(latency) is not int or latency < 0:
            raise ValueError("event.latency_ms must be a non-negative integer")
        if service is None or name.strip() == service:
            selected.append(event)
    total = len(selected)
    errors = sum(event["status"] >= 500 for event in selected)
    slow = sum(event["latency_ms"] >= slow_ms for event in selected)
    average = sum(event["latency_ms"] for event in selected) / total if total else 0.0
    rate = errors / total * 100 if total else 0.0
    return {
        "service": service if service is not None else "all",
        "total": total,
        "error_count": errors,
        "error_rate_pct": round(rate, 2),
        "slow_count": slow,
        "average_ms": round(average, 2),
    }
