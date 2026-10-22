# 프로젝트 지침과 스킬 예제

2일차 3교시 [프로젝트 지침, 스킬, TDD와 훅](../../docs/day2-rules.md)에서 쓰는 자료예요.

## 수업에서 쓰는 것

수업은 `~/legacy/cafe-points`에서 해요. 이 폴더의 파일을 복사하지 않아요.

| 파일 | 무엇 |
| --- | --- |
| [`examples/prompts-30min.md`](examples/prompts-30min.md) | 실습 1(규칙 세 줄), 실습 2(스킬 하나), 실습 3(테스트 먼저), 실습 4(훅 하나)에서 보내는 문장 |
| [`examples/made-by-claude/cafe-points/`](examples/made-by-claude/cafe-points/) | 강사 사본에서 Claude가 만든 파일. `CLAUDE.md.diff`, `run-check` 스킬, 테스트, 훅 설정이 있어요 |

## 수업 뒤에 해 볼 것

방명록으로 지침 비교와 스킬 세 개를 더 해 볼 수 있어요. 문장은 [`examples/prompts.md`](examples/prompts.md)에 있어요.

| 파일 | 무엇 |
| --- | --- |
| [`CLAUDE.md`](CLAUDE.md) | 방명록 작업 지침 |
| [`.claude/skills/check-change/SKILL.md`](.claude/skills/check-change/SKILL.md) | 방명록 변경 검토. `/check-change`로 불러요. 파일은 고치지 않아요 |
| [`.claude/skills/polish-ko/SKILL.md`](.claude/skills/polish-ko/SKILL.md) | 한국어 글을 쉬운 해요체로 다듬어요. Claude가 알아서 불러오기도 해요 |
| [`.claude/skills/readme-for-people/SKILL.md`](.claude/skills/readme-for-people/SKILL.md) | README를 동료가 읽는 안내문 `README.people.md`로 다시 써요 |
| [`.claude/commands/review-change.md`](.claude/commands/review-change.md) | `check-change`를 예전 명령 파일 형식으로 쓴 것이에요. 지금도 동작해요 |
| [`examples/run-checks/SKILL.md`](examples/run-checks/SKILL.md) | 사람이 쓴 내 스킬 예시예요 |
| [`examples/made-by-claude/`](examples/made-by-claude/) | Claude가 실제로 만든 결과. 검토 답, `README.people.md`, `run-checks` 스킬이 있어요 |

`check-change`와 `readme-for-people`에는 `disable-model-invocation: true`가 있어요. 그래서 사람이 `/이름`을 쳐야 돌아요.

## 막히면

| 증상 | 해결 |
| --- | --- |
| 스킬이 `/` 목록에 없어요 | `.claude`가 폴더 맨 위에 있는지 보고 새 세션을 열어요 |
| `/review`를 쳤더니 다른 리뷰가 돌아요 | `/review`는 내장 명령이에요. `/check-change`를 쳐요 |
| Windows에서 `python3`가 없어요 | 문장 끝에 "py로 돌려 줘"를 붙여요 |

공식 안내: [스킬](https://code.claude.com/docs/en/skills), [CLAUDE.md와 메모리](https://code.claude.com/docs/en/memory)
