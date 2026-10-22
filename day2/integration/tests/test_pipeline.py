from copy import deepcopy

def test_service_order_and_aggregate_reuse(integration_modules):
    events = [{"service":"z"},{"service":"a"}]
    calls = []
    def aggregate(rows, service=None):
        assert rows is events
        calls.append(service)
        return {"service":service or "all"}
    result = integration_modules["process"].build_summaries(events, aggregate)
    assert calls == [None, "a", "z"]
    assert result == [{"service":"all"},{"service":"a"},{"service":"z"}]

def test_empty_uses_aggregate(integration_modules):
    assert integration_modules["process"].build_summaries([], lambda rows, service=None: {"service":"all","total":0}) == [{"service":"all","total":0}]

def test_event_input_unchanged(integration_modules, report_module, events):
    before = deepcopy(events)
    integration_modules["process"].build_summaries(events, report_module.summarize)
    assert events == before

def test_report_values_and_synthetic_label(integration_modules):
    summary = {"service":"billing","total":3,"error_count":2,"error_rate_pct":66.67,"slow_count":2,"average_ms":506.67}
    before = deepcopy(summary)
    text = integration_modules["report"].render_report([summary])
    assert "교육용" in text
    assert "fixtures/events.json" in text and "query_events" in text
    assert "| billing | 3 | 2 | 66.67% | 2 | 506.67 |" in text
    assert summary == before

def test_report_escapes_table_text(integration_modules):
    row = {"service":"a|b\nc","total":0,"error_count":0,"error_rate_pct":0.0,"slow_count":0,"average_ms":0.0}
    text = integration_modules["report"].render_report([row])
    assert "a\\|b c" in text
