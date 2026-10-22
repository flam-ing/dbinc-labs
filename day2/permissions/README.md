# 권한 규칙 연습 · 쓰기·삭제 도구 막기

수업 뒤에 혼자 해 보는 자료예요. 2일차 5교시 [사내 시스템 연동](../../../docs/day2-integration.md)의 실습 3에서 권한 규칙을 한 줄 걸어 봤어요. 사내 시스템의 MCP 서버에는 조회 도구뿐 아니라 고치고 지우는 도구도 들어 있는 경우가 많아요. 여기서는 삭제 도구가 있는 가상 운영 도구를 Claude Code에 붙이고, `.claude/settings.json`의 권한 규칙으로 그 도구를 막아 봐요.

| 파일 | 하는 일 |
| --- | --- |
| `admin_server.py` | 교육용 운영 도구 MCP 서버예요. 도구는 `count_events`(읽기)와 `delete_event`(삭제) 두 개예요. 지우는 대상은 `work/admin/events.json`(원본 `fixtures/events.json`의 사본) 하나뿐이에요. |
| `settings.example.json` | 이 실습의 권한 규칙 예시예요. 삭제 도구와 원본·사본 파일 편집은 `deny`, `git push`는 `ask`, 읽기 도구는 `allow`에 넣었어요. |
| `apply_rules.py` | 위 규칙을 실습 폴더의 `.claude/settings.json`에 더해요. 파일이 이미 있으면 다른 설정은 그대로 두고 빠진 규칙만 더해요. `--remove`를 붙이면 이 예시의 규칙만 빼요. |

## 켜는 법

`labs/day2` 맨 위에서 가상환경을 켜고 실행해요. 가상환경 만드는 법은 [labs/day2 README](../README.md)에 있어요.

```bash
python permissions/admin_server.py --reset
python permissions/admin_server.py --status
```

실행 결과:

```text
되돌렸어요: work/admin/events.json 8건
work/admin/events.json: 8건 (evt-001, evt-002, evt-003, evt-004, evt-005, evt-006, evt-007, evt-008)
```

옵션 없이 `python permissions/admin_server.py`만 치면 입력을 기다리며 멈춘 것처럼 보여요. stdio 서버라서 정상이에요. `Ctrl+C`로 꺼요.

MCP 서버로 등록할 때는 Code 탭에서 Claude에게 "permissions/admin_server.py를 .mcp.json에 dbinc-training-admin이라는 이름으로 더해 줘. command에는 .venv 안 python의 절대 경로를 넣어 줘"라고 부탁해요. 새 서버는 같은 폴더로 새 세션을 열어야 보여요.

권한 규칙을 더해요.

```bash
python permissions/apply_rules.py
```

실행 결과(처음 만들 때):

```text
.claude/settings.json: 7개 바꿨어요
+ deny: mcp__dbinc-training-admin__delete_event
+ deny: Edit(./fixtures/**)
+ deny: Edit(./work/admin/**)
+ ask: Bash(git push *)
+ allow: mcp__dbinc-training-events__get_services
+ allow: mcp__dbinc-training-events__query_events
+ allow: mcp__dbinc-training-admin__count_events
```

Claude Code는 설정 파일이 바뀌면 다시 읽어요. 터미널의 Claude Code에서는 `/permissions`로 규칙과 그 규칙이 적힌 파일을 확인해요. 데스크톱 Code 탭에서는 `/permissions`가 열리지 않으니 `.claude/settings.json`을 열어 보거나 Claude에게 보여 달라고 해요. 실습이 끝나면 `python permissions/admin_server.py --reset`으로 사본을 되돌려요.

## 확인 명령

```bash
python tools/smoke_admin.py
```

마지막 줄이 `PASS 운영 도구 MCP:`로 시작하면 돼요. 그 앞의 `Tool 'delete_event' failed: ... 없는 이벤트입니다: evt-008` 한 줄은 이미 지운 이벤트를 다시 지워 보는 검사라서 정상이에요. 이 검사는 임시 파일만 쓰고, `work/admin/events.json`과 `.claude/settings.json`은 건드리지 않아요.

권한 규칙은 Claude Code가 지키는 규칙이에요. 이 검사는 서버와 도우미 스크립트만 확인해요. Claude Code 세션에서 실제로 막히는지는 직접 확인해요.
