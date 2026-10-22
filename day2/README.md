# 2일차 연습 폴더 · labs/day2

가상 서비스의 이벤트 기록을 집계하는 작은 Python 프로그램이에요. 이벤트는 모두 수업을 위해 만든 가상 데이터예요.

2일차 수업은 대부분 다른 폴더로 해요. 이 폴더에서 수업 중에 보는 것은 5교시 [사내 시스템 연동](../../docs/day2-integration.md)의 CLI 결과 견본([cli/](cli/README.md))뿐이에요. 나머지는 수업 뒤에 혼자 해 보는 연습이에요.

| 교시 | 쓰는 폴더 |
| --- | --- |
| 1~2교시 레거시 리팩토링, 지식베이스 | [labs/legacy-easy](../legacy-easy/README.md) |
| 3교시 지침, 스킬, TDD와 훅 | [labs/rules](../rules/README.md) |
| 4교시 디버깅 | [labs/debug](../debug/README.md) |
| 번외 모델·하네스·에이전트 | [labs/harness](../harness/README.md) |
| 5교시 사내 시스템 연동 | 어제 만든 방명록 폴더나 [labs/guestbook](../guestbook/README.md). 문장은 [integration/examples/prompts.md](integration/examples/prompts.md) |
| 6교시 크롤링, 퀀트 | [labs/crawl-once](../crawl-once/README.md), [labs/quant](../quant/README.md) |

환경 만들기, 명령마다 나오는 출력, 막혔을 때 볼 표는 [2일차 실습 자료](../../docs/day2-labs.md)에 자세히 있어요.

## 폴더

| 파일·폴더 | 무엇 |
| --- | --- |
| `SPEC.md` | 집계 함수 `summarize`의 명세 |
| `fixtures/` | 가상 이벤트 8건(`events.json`)과 버그 재현 출력(`debug.log`) |
| `starter/`, `buggy/`, `reference/` | 테스트 먼저 연습의 시작 파일, 버그가 든 파일, 정답이에요. 원본이라 고치지 않아요. 정답은 연습 중에 열지 않아요 |
| `tests/` | 계약 테스트 44개(`test_contract.py`)와 내가 테스트를 더하는 파일 |
| `server.py` | 가상 사내 시스템 MCP 서버. 읽기 도구 2개 |
| `cli/` | 방명록 CLI 예시와 5교시 결과 견본 |
| `integration/` | MCP와 SDK 연습의 예시 문장과 실제 답, 연결 약속(`CONTRACT.md`) |
| `hooks/` | 테스트를 강제하는 훅 예시 |
| `fixtures/examples/` | 집계 함수 버그를 재현하고 고치는 연습의 예시 |
| `automation/` | 이슈를 루틴과 GitHub Actions로 처리하는 연습 |
| `reverse/`, `permissions/` | 화면 뒤 API를 감싸는 연습, 삭제 도구를 막는 권한 규칙 연습 |
| `config/` | MCP 설정 예시, 에이전트 정의 3개, `CLAUDE.md` 예시 |
| `tools/` | 작업 폴더 만들기, 재현, 검사 스크립트 |
| `work/` | `tools/start.py`가 만드는 내 작업 폴더 |

> **주의** `examples/`에는 답이 들어 있어요. Claude에게 원인 분석이나 구현을 맡길 때는 `reference/`와 함께 `examples/`도 읽지 말라고 해요.

## 수업 뒤에 해 볼 것

먼저 이 폴더에 가상환경을 만들어요. Python 3.12를 써요. Code 탭에서 이 폴더를 열고 Claude에게 맡겨도 돼요.

```text
이 폴더에 .venv 가상환경을 만들고 requirements.txt를 설치해 줘.
```

직접 할 때는 한 줄씩 쳐요. macOS는 이렇게 해요.

```text
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell은 이렇게 해요. `Activate.ps1`이 막히면 `.venv\Scripts\python.exe`를 직접 불러요.

```text
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

그다음 해 볼 만한 연습이에요.

- 가상 사내 시스템을 MCP로 붙이고 SDK로 다시 읽기: [integration/examples/prompts.md](integration/examples/prompts.md)의 "수업 뒤에 해 볼 것"
- 집계 함수 버그를 재현하고 한 줄씩 고치기: [fixtures/examples/prompts.md](fixtures/examples/prompts.md)
- 파일을 고칠 때마다 테스트를 돌리는 훅: [hooks/README.md](hooks/README.md)
- 이슈를 루틴과 GitHub Actions로 처리하기: [automation/README.md](automation/README.md)
- 화면 뒤 API를 CLI와 MCP로 감싸기: [reverse/README.md](reverse/README.md)
- 삭제 도구를 권한 규칙으로 막기: [permissions/README.md](permissions/README.md)
