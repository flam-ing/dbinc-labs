# 내 폴더의 하네스 부품 · 지도

실습 2에서 써요. 오전에 쓴 `~/legacy/cafe-points`(없으면 `labs/rules`)를 Code 탭에서 열고, Claude에게 부품을 찾아 달라고 한 뒤 아래 빈 지도를 채워요. 칸 이름은 발표의 "하네스가 일하는 순서" 그림과 같아요.

## 빈 지도

| 그림의 칸 | 부품 | 내 폴더의 파일 | 있어요? | 언제 작동해요 |
| --- | --- | --- | --- | --- |
| 입력 | 지침 | `CLAUDE.md` | | |
| 입력 | 스킬 | `.claude/skills/<이름>/SKILL.md` | | |
| 입력 | 명령(예전 방식) | `.claude/commands/<이름>.md` | | |
| 확인 | 훅 | `.claude/settings.json`의 `hooks` | | |
| 확인 | 권한 규칙 | `.claude/settings.json`의 `permissions` | | |
| 도구 | MCP 연결 | `.mcp.json` | | |
| 도구 | 서브에이전트 | `.claude/agents/<이름>.md` | | |
| 도구 | 기본 도구 | (파일이 없어요. Claude에게 물어봐요) | | |

다 채웠으면 "있어요?" 칸이 빈 줄을 하나 골라, 그 칸을 채우면 무엇이 달라질지 한 줄로 적어요.

## 실제로 찾아 본 예

방명록 완성본에 `labs/rules`의 `CLAUDE.md`와 `.claude`를 넣은 폴더를 만들어서 2026-10-17에 Manual 모드, Sonnet 5.5로 돌렸어요. 원문은 [made-by-claude/03-parts.md](made-by-claude/03-parts.md)에 있어요.

| 그림의 칸 | 부품 | 내 폴더의 파일 | 있어요? | 언제 작동해요 |
| --- | --- | --- | --- | --- |
| 입력 | 지침 | `CLAUDE.md` | 있음 | 세션을 시작할 때 자동으로 읽어요 |
| 입력 | 스킬 | `polish-ko`, `check-change`, `run-checks`, `readme-for-people` | 있음(4개) | `/이름`으로 부를 때. `polish-ko`만 Claude가 스스로 부르기도 해요 |
| 입력 | 명령(예전 방식) | `review-change.md` | 있음 | `/review-change`로 부를 때 |
| 확인 | 훅 | 없음 | 없음 | 해당 없음 |
| 확인 | 권한 규칙 | 없음 | 없음 | 그때그때 권한 모드(Manual)가 정해요 |
| 도구 | MCP 연결 | 없음 | 없음 | 해당 없음 |
| 도구 | 서브에이전트 | 없음 | 없음 | 해당 없음 |
| 도구 | 기본 도구 | Agent, Bash, Edit, Read, Skill, Write 들 | 있음 | Claude가 필요할 때 골라 써요 |

Claude가 덧붙인 말 가운데 가장 중요한 한 줄이에요. "실제로 막는 장치는 훅과 권한 설정인데, 둘 다 없어요." 이 폴더의 지침과 스킬은 모두 부탁이고, 강제로 막는 장치는 아직 없다는 뜻이에요. 3교시에 `~/legacy/cafe-points`에 훅을 걸었다면 그 폴더에서는 훅 칸이 "있음"으로 나와요.

실행 중에 Claude가 `ls`와 `find`로 목록을 보려고 했는데, Manual 모드라 승인 없이는 돌지 않았어요. Claude는 그다음 Read 도구로 파일을 하나씩 열어서 찾았어요. 수업에서는 승인 카드가 뜨고, 목록만 보는 명령이라 **Allow once**를 눌러도 돼요.
