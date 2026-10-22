# 견본: billing 오류율을 물었을 때 받은 답

> 2026-10-17에 Claude Code(헤드리스, 모델 claude-opus-5-5)로 실제로 보낸 말에 Claude가 한 답이에요. 고치지 않았어요. 같은 말을 보내도 표 모양과 말투는 조금씩 달라요.

보낸 말은 [prompts.md](prompts.md)의 실습 A '3. 말로 묻기' 문장이에요. 권한 카드에서 MCP 도구 두 개(`get_services`, `query_events`)를 허락했어요.

````markdown
billing 서비스의 오류율은 **66.7%(3건 중 2건)**입니다. 상태 코드가 5xx인 이벤트를 오류로 계산했습니다.

| id | status | latency_ms | 오류 여부 |
|---|---|---|---|
| evt-001 | 200 | 120 | 정상 |
| evt-002 | 500 | 500 | 오류 |
| evt-003 | 503 | 900 | 오류 |

`total`이 3이고 `next_offset`이 `null`이라 billing 이벤트는 이 3건이 전부입니다. 다만 표본이 3건뿐이라 이 비율은 크게 믿을 만한 수치는 아닙니다. 이 데이터는 교육용 가상 데이터입니다(`synthetic: true`).

**도구 호출 내역 (총 3회)**
| 도구 | 횟수 | 용도 |
|---|---|---|
| `ToolSearch` | 1 | MCP 도구 두 개의 스키마 불러오기 |
| `mcp__dbinc-training-events__get_services` | 1 | 서비스 목록 확인 (billing, catalog, identity) |
| `mcp__dbinc-training-events__query_events` | 1 | `service=billing`, `limit=100`, `offset=0`으로 이벤트 조회 |

파일은 만들거나 고치지 않았습니다.
````

확인할 것: billing은 3건 중 2건이 상태 500 이상이에요. Claude가 66.7%나 66.67%로 말하면 맞아요.
