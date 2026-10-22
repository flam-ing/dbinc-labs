"""가공 담당: 검증된 집계 함수를 받아 서비스별 표를 만듭니다."""

def build_summaries(events, summarize):
    services = sorted({event["service"].strip() for event in events})
    return [summarize(events)] + [summarize(events, service=name) for name in services]
