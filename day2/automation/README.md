# 이슈 자동 처리 연습

수업 뒤에 혼자 해 보는 자료예요. 2일차 4교시 [버그 원인 분석과 디버깅](../../../docs/day2-debugging.md)에서는 루틴과 온콜을 강사 시연으로 봤어요. 여기서는 내 비공개 저장소에 같은 흐름을 직접 만들어요. 버그 이슈를 올리면 Claude Code가 재현하고, 고치고, 테스트를 돌린 뒤 PR을 올려요.

| 방식 | 언제 돌아요 | 무엇이 필요해요 |
| --- | --- | --- |
| 루틴 | 매시간 한 번 돌면서 `auto-fix` 라벨이 붙은 열린 이슈를 찾아요 | Claude Pro·Max·Team·Enterprise 요금제, 저장소에 Claude GitHub App |
| GitHub Actions | 이슈 댓글에 `@claude`를 쓰는 순간 돌아요 | Claude GitHub App, 저장소 비밀값에 토큰이나 API 키 |

루틴의 GitHub 트리거는 PR과 릴리스 이벤트만 받아요. 그래서 루틴은 매시간 예약으로 이슈를 확인하게 만들어요.

## 들어 있는 파일

| 파일 | 무엇 |
| --- | --- |
| [make_repo.py](make_repo.py) | 연습 저장소 폴더를 만드는 스크립트. 정답 구현은 넣지 않아요 |
| [repo/](repo/) | 새 저장소에 들어갈 파일 원본. `github/`는 `.github/`로, `gitignore`는 `.gitignore`로 바뀌어 복사돼요 |
| [routine-prompt.md](routine-prompt.md) | 루틴에 붙여 넣을 요청문과 만들기 화면에서 고를 값 |
| [bug-issue-example.md](bug-issue-example.md) | 사람이 쓴 버그 이슈 견본 |
| [examples/](examples/README.md) | 보내는 문장과 실제로 받은 답, 루틴 요청문으로 만든 PR 견본 |

## 1. 저장소 만들기

`labs/day2` 맨 위에서 실행해요. Windows는 `python3` 대신 `py`를 써요.

```text
python3 automation/make_repo.py ~/dbinc-auto
```

끝에 `재현 실패 사례: 3/3`이 나오면 돼요. 버그가 든 상태라 실패가 정상이에요. 실제 출력은 [examples/make-repo-output.md](examples/make-repo-output.md)에 있어요.

만든 폴더를 개인 GitHub 계정의 **비공개** 저장소로 올려요. 회사 저장소나 회사 조직에는 승인 없이 만들지 않아요. Claude에게 맡기는 문장은 [examples/prompts.md](examples/prompts.md) 1번이에요. 승인 카드에서 `--private`를 꼭 확인해요.

## 2. 버그 이슈 쓰기

저장소의 Issues에서 New issue를 누르고 버그 신고 양식을 골라요. 입력, 기대, 실제를 채워요. Claude에게 초안을 맡기는 문장은 [examples/prompts.md](examples/prompts.md) 2번이에요. 루틴을 쓸 거면 `auto-fix` 라벨도 만들어 붙여요.

## 3. 루틴으로 처리하기

1. https://github.com/apps/claude 에서 Claude GitHub App을 설치해요. Only select repositories로 `dbinc-auto` 하나만 골라요.
2. claude.ai/code/routines나 데스크톱 앱 왼쪽 Routines에서 New routine을 눌러요. 앱에서 만들 때는 클라우드에서 도는 쪽을 골라요.
3. [routine-prompt.md](routine-prompt.md)의 요청문을 붙여 넣고, 저장소, 환경, 트리거, 커넥터를 표대로 골라요.
4. Create 다음 상세 화면에서 Run now를 눌러요.
5. 실행 기록을 열어 Claude가 무엇을 했는지 읽어요. 초록 표시는 세션이 오류 없이 끝났다는 뜻일 뿐이에요.
6. Pull requests에서 `claude/`로 시작하는 브랜치의 PR을 열어 검토해요.

PR 모양은 [examples/pr-example.md](examples/pr-example.md)에서 미리 볼 수 있어요. 다 쓰면 루틴을 끄거나 지워요. 켜 두면 매시간 돌면서 사용량을 써요.

## 4. GitHub Actions로 처리하기

1. Claude GitHub App을 설치해요.
2. 저장소 Settings의 Secrets and variables, Actions에서 비밀값을 넣어요. 구독을 쓰면 `claude setup-token`으로 만든 토큰을 `CLAUDE_CODE_OAUTH_TOKEN`으로 넣어요. API 키를 쓰면 `ANTHROPIC_API_KEY`로 넣고 워크플로의 주석대로 한 줄을 바꿔요.
3. 워크플로 파일은 `make_repo.py`가 이미 넣어 두었어요.
4. 이슈 댓글에 [examples/prompts.md](examples/prompts.md) 5번 문장을 써요.
5. Actions 탭에서 실행 기록을 보고, Claude가 만든 PR을 검토해요.

## 5. PR 검토하기

- 바뀐 파일이 `report.py`와 `tests/test_regression.py`뿐인지 봐요. `tests/test_contract.py`, `SPEC.md`, `fixtures/`가 바뀌었으면 머지하지 않아요.
- PR 본문에 재현 결과(`재현 실패 사례: 0/3`)와 테스트 결과가 있는지 봐요.
- 내 PC에서 PR 브랜치를 받아 직접 돌려 봐요. 문장은 [examples/prompts.md](examples/prompts.md) 7번이에요.
- `except Exception`처럼 오류를 숨기는 코드가 없는지 봐요.

## 주의

- 토큰과 API 키는 저장소 비밀값에만 넣어요. 워크플로 파일, 이슈, 커밋, 채팅에 붙여 넣지 않아요.
- 연습은 비공개 저장소에서 해요. 공개 저장소에서는 누구나 이슈를 쓸 수 있어서, 루틴이 남이 쓴 글을 일감으로 읽을 수 있어요.
- 회사 저장소에 걸 때는 보안 담당과 저장소 관리자의 승인을 먼저 받아요.
- 이 폴더의 워크플로와 요청문은 GitHub에서 끝까지 돌려 보지 않았어요. GitHub 단계만 뺀 같은 요청문을 로컬에서 돌렸을 때는 46초 만에 `재현 실패 사례: 0/3`, `48 passed`가 나왔어요.

공식 안내: [루틴](https://code.claude.com/docs/en/routines), [GitHub Actions](https://code.claude.com/docs/en/github-actions)
