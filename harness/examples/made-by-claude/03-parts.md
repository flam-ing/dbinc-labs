# 2. 내 폴더의 하네스 부품

- 폴더: 방명록 완성본에 `labs/rules`의 `CLAUDE.md`와 `.claude`를 넣은 폴더(예전 지침 비교 사본 `compare-with-rules`와 같아요)
- 모드 · 모델: Manual · Sonnet 5.5 · effort High
- 걸린 시간: 20.9초 · 주고받은 횟수(턴) 10번 · API 값으로 환산한 금액 $0.086
- 날짜: 2026-10-17 · Claude Code 2.1.301 · 대화 없이 한 번 실행(`claude -p`)

## 보낸 말

```text
이 폴더에 있는 하네스 부품을 찾아 표로 정리해 줘. 칸은 부품, 파일, 하는 일 한 줄, 언제 작동하는지예요. CLAUDE.md, .claude/skills, .claude/commands, .claude/settings*.json(훅과 권한), .claude/agents, .mcp.json을 보고 없는 것은 '없음'으로 적어 줘. 표 아래에 지금 네가 쓸 수 있는 도구 이름을 한 줄로 적어 줘. 파일은 고치지 마.
```

## Claude의 답 (고치지 않았어요)

| 부품 | 파일 | 하는 일 | 언제 작동하는지 |
|---|---|---|---|
| CLAUDE.md | `CLAUDE.md` | 프로젝트 사실, 코딩 컨벤션, 금지 패턴, 작업 순서, 리뷰 기준을 알려 줘요. | 세션을 시작할 때 자동으로 불러와요. |
| 스킬 | `.claude/skills/polish-ko/SKILL.md` | 한국어 글을 쉬운 해요체로 다듬고 "바꾼 곳" 표를 붙여요. 원본 파일은 고치지 않아요. | 한국어 문서를 쓰거나 고칠 때 모델이 스스로 쓰거나, `/polish-ko`로 불러요. |
| 스킬 | `.claude/skills/check-change/SKILL.md` | 변경을 검토하고 `smoke_test.py`를 실행해요. 파일 수정이나 커밋은 하지 않아요. | `/check-change`로 부를 때만 써요. (`disable-model-invocation: true`) |
| 스킬 | `.claude/skills/run-checks/SKILL.md` | `smoke_test.py`만 실행하고 통과·실패 수를 짧게 보고해요. | `/run-checks`로 부를 때만 써요. (`disable-model-invocation: true`) |
| 스킬 | `.claude/skills/readme-for-people/SKILL.md` | README를 동료용 안내문으로 다시 써서 `README.people.md`를 새로 만들어요. | `/readme-for-people`로 부를 때만 써요. (`disable-model-invocation: true`) |
| 명령 | `.claude/commands/review-change.md` | 요구사항, git diff, 코드, 검사 결과를 보고 변경을 검토해요. 검토 중에는 파일을 고치지 않아요. | `/review-change`로 부를 때만 써요. (`disable-model-invocation: true`) |
| 설정 (훅·권한) | 없음 | `.claude/settings*.json` 파일이 없어서 프로젝트 훅과 권한 규칙이 없어요. | 해당 없음 |
| 에이전트 | 없음 | `.claude/agents` 폴더가 없어요. | 해당 없음 |
| MCP | 없음 | `.mcp.json` 파일이 없어요. | 해당 없음 |

- 이 폴더에 `.claude/settings*.json`이 없으니, 도구 사용 허용 여부는 프로젝트 설정이 아니라 지금 세션의 권한 모드가 정해요.
- 사용자 전역 설정(`~/.claude`)은 보지 않았어요. 요청하신 범위가 이 폴더였어요.
- CLAUDE.md 끝에 "이 파일은 작업 지침이며 실행 권한이나 보안 경계를 대신하지 않는다"라고 적혀 있어요. 실제로 막는 장치는 훅과 권한 설정인데, 둘 다 없어요.
- 파일은 고치지 않았어요.

**지금 쓸 수 있는 도구:** Agent, Bash, Edit, ListAgents, Read, ReportFindings, ScheduleWakeup, Skill, ToolSearch, Workflow, Write (ToolSearch로 불러 쓰는 도구: CronCreate, CronDelete, CronList, DesignSync, EnterWorktree, ExitWorktree, Monitor, NotebookEdit, PushNotification, RemoteTrigger, SendMessage, TaskStop, WebFetch, WebSearch)
