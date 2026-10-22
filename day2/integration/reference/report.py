"""보고서 담당: 집계 결과를 Markdown 표로 표현합니다."""

def render_report(summaries):
    lines = ["# 서비스 이벤트 보고서", "", "교육용 가상 데이터입니다. 실제 DB Inc 운영 지표가 아닙니다.", "",
             "자료: fixtures/events.json · MCP query_events로 전체 페이지 조회", "",
             "| 서비스 | 요청 | 오류 | 오류율 | 500ms 이상 | 평균 응답(ms) |",
             "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in summaries:
        name = str(row["service"]).replace("|", "\\|").replace("\n", " ")
        lines.append(f'| {name} | {row["total"]} | {row["error_count"]} | {row["error_rate_pct"]:.2f}% | {row["slow_count"]} | {row["average_ms"]:.2f} |')
    lines.extend(["", "오류는 HTTP 500 이상, 느린 요청은 500ms 이상으로 집계했습니다.", ""])
    return "\n".join(lines)
