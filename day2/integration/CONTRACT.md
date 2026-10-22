# 조회·가공·보고서 연결 약속

데이터는 `fixtures/events.json`의 교육용 가상 이벤트 8건입니다. 서버는 파일을 읽는 도구 2개만 제공합니다. API 키나 실제 사내 시스템은 필요하지 않습니다.

## MCP 도구

| 도구 | 입력 | 결과 |
| --- | --- | --- |
| `get_services` | 없음 | `synthetic: true`, `services: ["billing","catalog","identity"]` |
| `query_events` | `service=None`, `offset=0`, `limit=100` | `synthetic`, `events`, `total`, `next_offset` |

`offset`은 0 이상, `limit`은 1~100입니다. `next_offset=null`이면 마지막 페이지입니다. `total`은 필터 결과 전체 수로, 해당 페이지의 개수가 아닙니다. 정렬은 제공 JSON 순서를 유지합니다. 없는 서비스는 `events=[]`, `total=0`, `next_offset=null`입니다.

SDK가 도구 응답의 `structured_content`에 이 객체를 넣습니다. 호출 오류는 `is_error`로 확인합니다. 도구 이름 앞에 붙는 호스트 접두사와 Python 함수 이름을 구분하세요.

## 세 사람이 동시에 작업할 파일

| 역할 | 수정할 파일 | 읽을 자료 | 반환값 |
| --- | --- | --- | --- |
| 조회 | `work/integration/query.py` | 이 문서, `server.py` | `async fetch_events(server_path)` → 이벤트 전체 리스트 |
| 가공 | `work/integration/process.py` | 이 문서, `SPEC.md` | `build_summaries(events, summarize)` → 전체·서비스별 집계 리스트 |
| 보고서 | `work/integration/report.py` | 이 문서의 출력 예시 | `render_report(summaries)` → Markdown 문자열 |
| 통합 담당 | 실행 명령, Git, 최종 문서 | 세 결과와 테스트 로그 | 실행 가능한 ZIP |

조회 담당은 각 페이지를 `limit=3`으로 호출해 8건을 모두 가져옵니다. ID가 중복되면 통합 검증에서 실패합니다. 가공 담당은 2일차 실습 자료 6·7절에서 테스트로 검사한 `summarize` 함수를 인자로 받아 재사용합니다. 첫 행은 전체, 그다음은 서비스 이름 오름차순입니다. 보고서 담당은 결과값을 다시 계산하지 않습니다.

보고서에는 교육용 가상 데이터라는 안내, 조회한 자료의 출처(`fixtures/events.json` · MCP `query_events`), 서비스·요청·오류·오류율·500ms 이상·평균 응답 시간 표가 필요합니다. 비율과 평균은 소수 둘째 자리까지 표시합니다. 서비스 이름에 `|` 또는 줄바꿈이 들어가도 표가 깨지지 않게 처리합니다.

```json
[
  {"service":"all","total":8,"error_count":3,"error_rate_pct":37.5,"slow_count":4,"average_ms":411.12},
  {"service":"billing","total":3,"error_count":2,"error_rate_pct":66.67,"slow_count":2,"average_ms":506.67},
  {"service":"catalog","total":3,"error_count":0,"error_rate_pct":0.0,"slow_count":1,"average_ms":363.0},
  {"service":"identity","total":2,"error_count":1,"error_rate_pct":50.0,"slow_count":1,"average_ms":340.0}
]
```

조회 결과를 기다리면서 가공·보고서 담당이 멈출 필요는 없습니다. 이 계약과 fixture/위 예시를 입력으로 각자 구현한 뒤 실제 조회 결과로 합쳐 확인합니다. 예시 데이터를 실제 MCP 호출 결과처럼 설명하지 않습니다.

## 통합 테스트가 확인하는 것

`integration/tests/test_pipeline.py`와 `tools/run_report.py`는 아래 내용을 그대로 확인합니다. 모양이 조금만 달라도 실패합니다.

### 가공 `process.py`

- 받은 `events` 리스트를 걸러 내거나 복사하지 않고 같은 객체 그대로 `summarize`에 넘깁니다. 테스트는 `rows is events`로 같은 객체인지 봅니다.
- 호출 순서는 전체 집계 한 번(`service`를 넘기지 않거나 `None`), 그다음 서비스 이름 오름차순입니다. 서비스가 `"z"`, `"a"`이면 호출은 `[None, "a", "z"]` 순서이고, 결과 리스트도 같은 순서입니다.
- 이벤트가 0건이면 전체 집계 한 줄만 돌려줍니다. 받은 이벤트는 바꾸지 않습니다.
- 서비스 이름은 `summarize(events, service=name)`처럼 키워드로 넘기기를 권장합니다. `summarize(events, name)`처럼 위치로 넘겨도 테스트는 통과하지만, 키워드로 쓰면 어느 인자에 무엇을 넣었는지 바로 보입니다.

### 보고서 `report.py`

- billing 행은 정확히 `| billing | 3 | 2 | 66.67% | 2 | 506.67 |` 모양입니다. 열 순서는 서비스, 요청, 오류, 오류율, 500ms 이상, 평균 응답(ms)입니다. 오류율은 소수 둘째 자리 뒤에 `%`를 붙이고, 평균은 소수 둘째 자리까지 씁니다. 칸 경계 `|` 양옆에는 공백을 한 칸씩 둡니다.
- 서비스 이름 안의 `|`는 앞에 역슬래시를 붙여 `\|`로, 줄바꿈은 공백 한 칸으로 바꿉니다. 이름 `"a|b\nc"`는 표에 `a\|b c`로 들어갑니다.
- 본문에 `교육용`, `fixtures/events.json`, `query_events`가 들어 있습니다. 받은 집계 결과는 바꾸지 않습니다.

### 조회와 전체 흐름 `tools/run_report.py`

- 이벤트가 8건이고 ID가 겹치지 않습니다.
- 가공 결과의 서비스 순서가 `all`, `billing`, `catalog`, `identity`입니다.
- 첫 행이 위 JSON의 `all` 행과 같습니다.

## 충돌을 피하는 방법

담당 파일 외에는 읽기만 합니다. `SPEC.md`, `conftest.py`, 제공 검사, fixture, `server.py`는 통합 담당과 합의하기 전 수정하지 않습니다. 함수 이름·인자·출력 키를 바꿔야 한다면 먼저 통합 담당에게 이유와 영향을 알립니다. 여러 에이전트가 동시에 `git add`나 `git commit`을 실행하지 않습니다.

파일 소유권은 작업 약속입니다. 보안 샌드박스로 강제하는 기능은 아니므로 통합 담당이 diff로 확인합니다.
