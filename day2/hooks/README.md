# 테스트를 강제하는 훅

수업 뒤에 혼자 해 보는 자료예요. 수업 중 훅은 2일차 3교시 [프로젝트 지침, 스킬, TDD와 훅](../../../docs/day2-rules.md)에서 다뤄요.

훅(hook)은 Claude Code가 정해진 순간마다 내 명령을 반드시 실행하게 하는 설정이에요. 여기서는 두 순간에 pytest를 돌려요.

| 순간 | 훅 이벤트 | 실패하면 |
| --- | --- | --- |
| Claude가 파일을 고친 직후(`Edit`, `Write`) | `PostToolUse` | 실패한 테스트 이름을 Claude에게 돌려줘요. 이미 고친 파일을 되돌리지는 못해요 |
| Claude가 답을 마치려 할 때 | `Stop` | 끝내지 못하게 막고 이유를 돌려줘요. 두 번째부터는 막지 않고 사람에게 알려요 |

## 들어 있는 파일

| 파일 | 무엇 |
| --- | --- |
| [run_tests.py](run_tests.py) | 훅이 부르는 검사 스크립트. 실패하면 `{"decision": "block", "reason": ...}`을 출력해요. 표준 라이브러리만 써요 |
| [settings.json](settings.json) | macOS용 훅 설정 |
| [settings.windows.json](settings.windows.json) | Windows용 훅 설정. `python3` 대신 `python`을 불러요 |
| [samples/](samples/) | 손으로 훅을 시험할 가짜 입력 4개 |
| [examples/kb_guard.py](examples/kb_guard.py), [examples/kb-settings.example.json](examples/kb-settings.example.json) | 레거시에 거는 kb 훅 예시. 코드만 바뀌고 `docs/kb/`가 그대로면 Stop에서 한 번 막아요 |

`run_tests.py`는 `.venv`가 있으면 그 Python으로 pytest를 돌려요. pytest를 찾지 못하면 막지 않고 사람에게만 알려요.

## 1. 손으로 돌려 보기

`labs/day2` 맨 위에서 가상환경을 켜고 해요. 테스트 먼저 연습을 마쳐서 `work/tdd/report.py`가 테스트를 모두 통과한다고 가정해요. PowerShell에서는 `<`로 파일을 넘길 수 없어요. Git Bash에서 하거나 Claude에게 실행을 부탁해요.

```bash
python3 hooks/run_tests.py tests --impl work/tdd/report.py -q < hooks/samples/post-edit.json
echo "exit=$?"
```

테스트가 모두 통과하면 아무것도 출력하지 않고 `exit=0`이 나와요. 일부러 틀린 사본으로 검사하면 `decision: block`과 실패 목록이 나와요.

```bash
mkdir -p work/hook-check
sed 's/>= slow_ms/> slow_ms/' work/tdd/report.py > work/hook-check/report.py
python3 hooks/run_tests.py tests --impl work/hook-check/report.py -q < hooks/samples/post-edit.json
```

| 샘플 | 상황 | 틀린 사본에서 나오는 것 |
| --- | --- | --- |
| `post-edit.json` | `.py` 파일을 고친 직후 | `decision: block`과 실패 목록 |
| `post-edit-md.json` | `.md` 메모를 쓴 직후 | 아무것도 없음. 파이썬 파일이 아니면 검사하지 않아요 |
| `stop.json` | 답을 마치려 할 때 | `decision: block`과 실패 목록 |
| `stop-again.json` | 한 번 막힌 뒤 다시 마치려 할 때 | `systemMessage`만. 무한 반복을 피하려고 사람에게 알려요 |

## 2. Claude Code에 걸기

macOS 터미널에서는 이렇게 복사해요.

```bash
mkdir -p .claude
cp hooks/settings.json .claude/settings.json
```

Windows PowerShell에서는 이렇게 복사해요.

```powershell
New-Item -ItemType Directory -Force .claude
Copy-Item hooks\settings.windows.json .claude\settings.json
```

설정의 명령은 `$CLAUDE_PROJECT_DIR/hooks/run_tests.py`를 불러요. 그래서 Code 탭에서 꼭 `labs/day2` 폴더로 세션을 열어요. 복사한 뒤 새 세션을 열고, 일부러 틀린 요청을 넣어 막히는지 봐요.

## 3. 다 쓰면 끄기

설정 파일 이름을 바꾸면 훅이 꺼지고 파일은 남아요. macOS는 이렇게 해요.

```bash
mv .claude/settings.json .claude/settings.hooks-off.json
rm -r work/hook-check
```

Windows PowerShell은 이렇게 해요.

```powershell
Rename-Item .claude\settings.json settings.hooks-off.json
Remove-Item -Recurse work\hook-check
```

공식 안내: [훅 가이드](https://code.claude.com/docs/en/hooks-guide), [훅 레퍼런스](https://code.claude.com/docs/en/hooks)
