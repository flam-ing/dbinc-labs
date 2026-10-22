"""디버깅 실습용 고의 버그. 운영 코드가 아닙니다."""

def summarize(events, service=None, slow_ms=500):
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
