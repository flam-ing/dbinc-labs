# 견본: SDK 길로 스크립트를 만들게 했을 때 받은 답

> 2026-10-17에 Claude Code(헤드리스, 모델 claude-opus-5-5)로 실제로 보낸 말에 Claude가 한 답이에요. 고치지 않았어요. 같은 말을 보내도 표 모양과 말투는 조금씩 달라요.

보낸 말은 [prompts.md](prompts.md)의 "SDK 길"이에요. 이때 Claude가 만든 파일은 [sdk_report.py](sdk_report.py)예요(고치지 않았어요).

````markdown
`work/sdk_report.py`를 만들고 `.venv/bin/python`으로 실행했습니다. 기본 실행과 `--limit 3` 실행 모두 같은 결과가 나왔습니다.

```
query_events 3페이지(limit=3)로 이벤트 8건 수집 · 오류 기준: status >= 500

service    requests errors error_rate
-------------------------------------
billing           3      2      66.7%
catalog           3      0       0.0%
identity          2      1      50.0%
-------------------------------------
TOTAL             8      3      37.5%
```

- **연결:** `tools/smoke_mcp.py`와 같은 방식으로 `Client`와 `StdioServerParameters`를 써서 `server.py`를 stdio로 띄워 연결합니다.
- **페이지 읽기:** `query_events`를 `next_offset`이 `null`이 될 때까지 반복 호출합니다. 다 모은 건수가 서버가 알려 준 `total`과 다르거나 도구 호출이 오류를 내면 바로 멈춥니다.
- **오류 기준:** 상태 500 이상만 오류로 셉니다. 그래서 catalog의 404와 identity의 401은 오류율에 들어가지 않습니다.
- **페이지 크기:** 데이터가 8건뿐이라 기본값(`limit=100`)으로는 한 페이지에 다 들어옵니다. 여러 페이지를 넘기는 부분이 실제로 동작하는지 보려고 `--limit 3`으로 한 번 더 돌렸고, 3페이지에 걸쳐 같은 결과가 나왔습니다.

`integration/`과 `reference/` 폴더는 열지 않았습니다. 실행 후 `git status`에 아무것도 나오지 않아서, `work/` 폴더가 `.gitignore`에 들어 있는 것으로 보입니다.
````

확인할 것: billing 3건 중 2건(66.7%), catalog 3건 중 0건(0.0%), identity 2건 중 1건(50.0%), 모두 8건 중 3건(37.5%)이에요. `integration/CONTRACT.md`에 같은 값이 있어요.
