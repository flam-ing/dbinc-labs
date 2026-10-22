# 1교시 실습 자료 · ChatBot과 Agent

1일차 1교시 [ChatBot과 Agent의 차이](../../docs/day1-agent.md)에서 쓰는 가상 자료예요. 모두 수업을 위해 만든 것이라 챗봇에 올려도 돼요. 회사 자료는 올리지 않아요.

| 파일 | 무엇 | 쓰는 실습 |
| --- | --- | --- |
| `orders.csv` | 가상 주문 5건. 금액 열을 모두 더하면 89,000원이에요. 엑셀에서 한글이 깨지지 않게 UTF-8 BOM으로 저장했어요 | 실습 2, 실습 3, 강사 Code 탭 시연 |
| `examples/prompts.md` | 실습마다 예시 문장과 바꿀 곳, 실제로 돌려 본 결과 요약 | 모든 실습 |
| `examples/expenses.csv` | 가상 출장비 5건(합계 310,500원). `orders.csv` 대신 바꿔 볼 파일이에요 | 실습 2 |
| `examples/meeting-notes.txt` | 가상 주간 회의 메모. 할 일만 뽑아 보는 데 써요 | 실습 2 |
| `examples/rules.md` | 보고 메일 검토 규칙 다섯 줄 | 실습 4 |
| `examples/draft-mail.txt` | 규칙을 일부러 어긴 메일 초안 | 실습 4 |
| `examples/agent-compare.md` | 비교 결과 템플릿 | 실습 5 |
| `examples/results/` | 실제로 돌려서 나온 결과 견본(챗봇의 답, Code 탭이 만든 `total.md`, `NOTES.md`, 이어 하기 답, 규칙 검토 답, 채운 비교 표, `expenses.csv`로 바꿔 본 부서별 합계 답, `meeting-notes.txt`로 바꿔 본 할 일 답) | 끝났을 때 비교 |

실습은 모두 바탕화면의 `dbinc-notes` 폴더에 결과를 모아요. 실습 3에서 이 폴더를 만들고 `NOTES.md`를, 실습 5에서 `agent-compare.md`를 저장해요.

`_reference/claude-runs/`는 강사가 실습을 실제로 돌려 본 원문 기록이에요. 강사용이라 학생용 ZIP과 교안 사이트에는 들어 있지 않아요.
