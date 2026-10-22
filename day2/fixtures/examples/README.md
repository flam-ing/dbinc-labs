# 디버깅 실습 예시

수업 뒤에 혼자 해 보는 디버깅 연습의 예시 모음이에요. `labs/day2`의 집계 함수에 든 버그를 재현하고 한 줄씩 고쳐요. 무엇을 보내면 되는지 막힐 때 열어 봐요. 작업 폴더는 `labs/day2` 맨 위에서 `tools/start.py debug`로 만들어요(Windows는 `py tools/start.py debug`).

| 파일 | 무엇 | 언제 |
| --- | --- | --- |
| [prompts.md](prompts.md) | Claude에게 보낼 말의 예시 6개와 바꿀 곳 | 실습마다 |
| [three-cells.md](three-cells.md) | 버그 신고를 입력, 기대, 실제 세 칸으로 나눈 견본 | 실습 · 재현하기 |
| [01-plan-answer.md](01-plan-answer.md) | Plan 모드로 받은 사실, 가설, 단계별 계획(실제 답) | 실습 · 사실과 가설 |
| [02-step-answers.md](02-step-answers.md) | 한 단계씩 고칠 때 Claude가 말한 값의 변화(실제 답) | 실습 · 하나씩 고치기 |
| [03-regression-test.md](03-regression-test.md) | 회귀 테스트를 만든 답과 실제 테스트 파일 | 실습 · 회귀 테스트와 기록 |
| [04-debug-note.md](04-debug-note.md) | 다섯 번째 원인을 고친 답과 실제 디버깅 기록 | 실습 · 회귀 테스트와 기록 |
| [05-legacy-inv80.md](05-legacy-inv80.md) | 레거시의 열린 버그(inventory-py INV-80)로 재현하고 계획을 받은 실제 답 | 레거시로 할 때 |

`01`~`05`는 2026-10-17에 이 폴더의 사본에서 `prompts.md`의 문장을 Claude Code(Sonnet 5.5)에 실제로 보내서 받은 답이에요. Claude가 한 말은 고치지 않았어요. 같은 문장을 보내도 답의 모양과 고치는 순서는 조금씩 달라요. 내 답이 달라도 틀린 게 아니에요. 값이 기대대로 바뀌었는지로 봐요.

> **주의** 이 폴더에는 답이 들어 있어요. Claude에게 원인 분석을 맡길 때는 `reference/`와 함께 `examples/`도 읽지 말라고 해요. 예시 문장에 이미 들어 있어요.
