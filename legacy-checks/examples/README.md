# 6교시 예시와 결과 견본

6교시(레거시 리팩토링과 문서) 실습에서 쓰는 예시 문장과, 그 문장을 실제로 보냈을 때 나온 결과 견본이에요. 내 레거시 폴더로 복사하지 않아요. 옆에 열어 두고 보면서 따라 해요.

| 파일 | 내용 | 쓰는 때 |
| --- | --- | --- |
| [prompts.md](prompts.md) | 실습마다 보내는 예시 문장, 바꿀 곳, 레거시 열 개의 첫 문장 | 실습 내내 |
| [results/1-find-expense-py.md](results/1-find-expense-py.md) | 나쁜 곳 찾기 답(③ 칸, 한 함수에 다 넣기) | 2부 끝 실습 |
| [results/1-find-inventory-py.md](results/1-find-inventory-py.md) | 나쁜 곳 찾기 답(② 칸, 같은 검사 복사) | 2부 끝 실습 |
| [results/1-find-payroll-java.md](results/1-find-payroll-java.md) | 나쁜 곳 찾기 답(④ 칸, 사람마다 다른 스타일) | 2부 끝 실습 |
| [results/2-safety-net-expense-py.md](results/2-safety-net-expense-py.md) | 안전망을 만들어 달라고 했을 때 답 | 3부 실습 |
| [results/3-plan-expense-py.md](results/3-plan-expense-py.md) | Plan 모드로 받은 첫 단계 계획 | 실습 1판 |
| [results/4-step-expense-py.md](results/4-step-expense-py.md), [results/4-step-expense-py.diff](results/4-step-expense-py.diff) | 첫 단계만 고친 결과와 바뀐 줄 | 실습 1판 |
| [results/5-plan-triage-js.md](results/5-plan-triage-js.md) | 다른 레거시에서 미리 만든 안전망으로 받은 계획 | 실습 2판 |
| [results/6-decisions-expense-py.md](results/6-decisions-expense-py.md) | Claude가 쓴 결정 기록 | 6부 문서 |

- 견본은 2026-10-17에 Claude Code(claude-opus-5-5)로 실제로 돌린 결과예요. Claude가 한 말과 만든 파일은 고치지 않았어요.
- 같은 문장을 보내도 답의 모양, 걸린 시간, 파일 이름은 그때그때 달라요. 견본은 "다 되면 대략 이런 모양"을 보는 용도예요.
- 견본 1~4와 6은 출장비 정산(`expense-py`), 견본 5는 고객 문의 분류(`triage-js`)예요. 나쁜 곳 찾기는 칸마다 말이 달라서 재고·발주(`inventory-py`)와 급여 계산(`payroll-java`) 견본을 더 두었어요. 발표 4부의 강사 시연은 회의실 예약(`room-java`)이에요.
