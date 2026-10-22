# 집계 함수 TDD 예시 문장 모음 · 테스트와 훅

[2일차 실습 자료](../../../../docs/day2-labs.md) 6절에서 수업 뒤에 혼자 해 볼 때 보내는 문장이에요. 그대로 보내도 되고, `⟨ ⟩` 안을 내 것으로 바꿔 보내도 돼요. 보낼 때 `⟨ ⟩` 표시는 지워요. 모든 실습은 Code 탭에서 **Select folder**로 `labs/day2`를 고른 세션 하나에서 이어서 해요.

"실제 결과"는 Claude Code 2.1.301과 2.1.302(Sonnet 5.5)로 직접 돌려 본 결과예요. 테스트 개수 같은 숫자는 사람마다 달라요. 같은 흐름(RED, GREEN, 놓친 곳 채우기, 모두 통과)이 나오면 돼요.

## 1. 준비 (명세로 테스트 실습의 첫 단계)

```text
이 폴더에 CLAUDE.md를 만들고 아래 두 줄을 넣어 줘.
- 파이썬 명령(python, pytest)은 이 폴더의 .venv 파이썬으로 실행한다. macOS·Linux는 .venv/bin/python, Windows는 .venv\Scripts\python.exe다.
- 정답 파일 reference/report.py는 열지 않는다.
그다음 python tools/start.py tdd를 실행하고, python -m pytest -q를 실행해서 출력을 그대로 보여 줘.
```

**실제 결과**: 이 문장을 실제로 보냈어요(Claude Code 2.1.302, Sonnet 5.5, 7초). Claude가 두 줄짜리 `CLAUDE.md`를 만들고, 방금 쓴 줄대로 `python` 대신 `.venv/bin/python`으로 두 명령을 실행했어요. 이 준비 요청을 보내 두고, Claude가 일하는 동안 `SPEC.md`를 읽어요.

**끝났을 때**: `준비했습니다: work/tdd`와 `45 passed`가 보여요. 아무것도 안 만들었는데 통과하는 이유는 `--impl`을 빼면 정답 파일을 검사하기 때문이에요. 내 파일은 `--impl work/tdd/report.py`를 붙여야 검사돼요(붙이면 `1 failed`).

## 2. 명세로 테스트 먼저

먼저 `SPEC.md`를 직접 읽어요. 그다음 보내요.

```text
SPEC.md와 fixtures/events.json만 보고 summarize의 유닛 테스트를 tests/test_student_report.py에 써 줘. latency ⟨499·500·501ms⟩와 status ⟨499·500⟩ 경계를 넣고, 기대값은 명세로 직접 계산해서 주석으로 남겨 줘. reference/와 tests/test_contract.py는 열지 말고, work/tdd/report.py는 고치지 마. 다 쓰면 python -m pytest tests/test_student_report.py --impl work/tdd/report.py -q 를 실행해 줘.
```

**끝났을 때(RED)**: 테스트가 모두 `NotImplementedError`로 실패해요. 내 테스트 파일에 `66.67`(billing 오류율)과 `411.12`(전체 평균)가 들어 있는지 찾아봐요.

**실제 결과**: 56초 걸렸어요. 테스트 함수 23개(매개변수까지 세면 48개)를 썼고 `48 failed`였어요. `reference/`와 `tests/test_contract.py`는 열지 않았어요.

## 3. RED에서 GREEN으로

```text
이제 ⟨work/tdd/report.py⟩만 고쳐서 이 테스트를 통과시켜 줘. 기준은 SPEC.md야. tests/ 폴더의 파일은 고치지 말고 reference/는 열지 마. 끝나면 python -m pytest tests/test_student_report.py --impl work/tdd/report.py -q 를 다시 실행해서 결과를 보여 줘.
```

**끝났을 때(GREEN)**: RED 때와 같은 개수가 모두 통과해요. **Edited** 카드에 바뀐 파일이 `work/tdd/report.py` 하나뿐이어야 해요.

**실제 결과**: 23초 걸렸어요. `48 passed`였고 테스트 파일은 그대로였어요. 그런데 제공 테스트(`tests/test_contract.py`)를 따로 돌려 보니 `3 failed, 41 passed`였어요. 다음 실습에서 채워요.

## 4. 놓친 곳 채우기

```text
이제 내 테스트만으로 커버리지를 재 줘(--cov=work/tdd --cov-branch --cov-report=term-missing). 제공 테스트 tests/test_contract.py도 같은 --impl로 돌려 줘. 내 테스트가 놓친 곳을 SPEC.md 문장과 함께 표로 먼저 보여 주고, 표대로 tests/test_student_report.py에 테스트를 보태 줘. ValueError를 확인하는 테스트 이름에는 ⟨invalid⟩를 넣어 줘. tests/test_contract.py는 고치지 마. 보탠 테스트가 실패하면 그때 work/tdd/report.py를 고쳐 줘. 끝나면 --cov-report=html:⟨artifacts/my-coverage⟩를 붙여 다시 재 줘.
```

**끝났을 때**: 내 테스트로 잰 커버리지의 `Missing` 칸이 비고, 제공 테스트가 `44 passed`예요. 대화의 `artifacts/my-coverage/index.html`을 누르면 **Browser** 창에서 줄마다 색이 보여요.

**실제 결과**: 54초 걸렸어요. 처음에는 커버리지 97%(안 간 줄 하나)에 제공 테스트 3개 실패였어요. Claude가 테스트를 보태고 구현 두 곳을 고친 뒤 `62 passed`, 100%, 제공 테스트 `44 passed`, 전체 `106 passed`가 됐어요. "표로 먼저"라고 했지만 표 없이 바로 보탰어요. 표를 먼저 보고 싶으면 앞의 세 문장만 보내고 "아직 고치지 마"를 붙여요. 받은 표를 `SPEC.md`와 맞춰 본 뒤 나머지를 보내요.

리포트 폴더를 `artifacts/coverage`로 바꾸지 마요. 그 폴더에는 미리 넣어 둔 예시 리포트가 있어요. RED 때 쓴 `test_missing_field_raises`처럼 이름에 invalid가 없는 `ValueError` 테스트가 남으면 "이름에 invalid를 넣어 줘"라고 한 번 더 부탁해요. 7절이 이 이름으로 검증 테스트를 걸러 내요.

## 5. 훅 손 시험

Terminal 창에서 직접 쳐도 되고, Claude에게 부탁해도 돼요. PowerShell에서는 `<`가 안 되니 Claude에게 부탁해요.

```text
hooks/run_tests.py에 hooks/samples/⟨post-edit.json⟩을 표준 입력으로 넣어서 실행해 줘. 인자는 tests --impl ⟨work/tdd/report.py⟩ -q야. 출력과 종료 코드를 그대로 보여 줘.
```

이 부탁 문장은 따로 돌려 보지 않았어요. 같은 명령을 터미널에서 직접 돌려 확인했어요.

**끝났을 때**: 아무것도 출력하지 않고 종료 코드 0이에요. 테스트가 모두 통과하면 훅은 조용해요.

그다음 느린 요청 기준 `>=`를 `>`로 바꾼 틀린 사본을 만들어 돌려요. macOS 터미널이나 Git Bash에서는 아래 세 줄을 쳐요. PowerShell처럼 `sed`가 없으면 Claude에게 "work/tdd/report.py를 work/hook-check/report.py로 복사하고, 사본에서만 >= slow_ms를 > slow_ms로 바꿔 줘"라고 부탁해요(이 문장도 따로 돌려 보지 않았어요).

```bash
mkdir -p work/hook-check
sed 's/>= slow_ms/> slow_ms/' work/tdd/report.py > work/hook-check/report.py
python3 hooks/run_tests.py tests --impl work/hook-check/report.py -q < hooks/samples/post-edit.json
```

Claude에게 부탁할 때는 틀린 사본을 만든 뒤 위 문장의 두 번째 `⟨ ⟩`를 `work/hook-check/report.py`로 바꿔 보내요.

**끝났을 때**: `{"decision": "block", "reason": "테스트가 실패했어요. ...` 한 줄이 나와요. 실제로 돌려 보니 `9 failed, 97 passed`였어요(내 테스트 수에 따라 달라요).

**더 해 보기**: 틀린 사본(`work/hook-check/report.py`)으로 첫 번째 `⟨ ⟩`를 `stop-again.json`으로 바꿔 넣으면, 이번에는 막지 않고 `{"systemMessage": "테스트가 아직 실패해요. ...`만 나와요. `post-edit-md.json`은 `.md` 파일을 쓴 경우라 아무것도 나오지 않아요. 통과하는 `work/tdd/report.py`로 넣으면 어느 샘플이든 아무것도 나오지 않아요.

## 6. 훅 걸고 막아 보기

```text
hooks/settings.json을 .claude/settings.json으로 복사해 줘.
```

이 복사 부탁은 따로 돌려 보지 않았고, 같은 복사를 터미널에서 해서 설정이 맞게 도는 것을 확인했어요. macOS 터미널이나 Git Bash에서 직접 하려면 `mkdir -p .claude`를 먼저 치고 `cp hooks/settings.json .claude/settings.json`을 쳐요. `labs/day2`에는 아직 `.claude` 폴더가 없어요. Windows는 `hooks/settings.windows.json`을 복사해요. `.claude` 폴더에 쓰는 일이라 Accept edits여도 승인 카드가 떠요. 복사한 뒤 **+ New session**으로 `labs/day2` 세션을 새로 열고, 일부러 명세와 부딪히는 요청을 넣어요.

```text
work/tdd/report.py에서 느린 요청 기준을 500ms 초과로 바꿔줘. 즉 slow를 세는 줄의 >= 를 > 로 바꿔. 다른 파일은 건드리지 마.
```

Manual 모드라면 고치는 카드가 먼저 떠요. **Accept**를 눌러야 고치고, 그 직후 훅이 돌아요.

**끝났을 때**: 고친 직후 실패한 테스트 이름이 대화에 나타나요(PostToolUse 훅). Claude가 스스로 되돌리면 되돌리는 카드도 **Accept**를 눌러요. 되돌리지 않고 묻기만 하면 "원래대로 되돌려줘"라고 답하거나 `/rewind`로 되감아요. 그다음 Terminal에서 `python -m pytest tests --impl work/tdd/report.py -q`가 다시 모두 통과하는지 봐요.

**실제 결과**: 4절을 마친 사본(내 테스트 62개)에 훅을 걸고 이 요청을 넣었더니(Claude Code 2.1.301, Sonnet 5.5, Accept edits, 15초), 고친 직후 훅이 `9 failed, 97 passed`로 막았어요. Claude는 `SPEC.md`에서 "slow_ms 이상"을 찾아 읽고, 스스로 원래대로 되돌린 뒤 "500ms 초과로 정말 바꾸려면 SPEC.md와 경계값 테스트도 함께 바꿔야 한다"며 어느 쪽으로 할지 물었어요. 되돌린 뒤라 Stop 훅은 막지 않았어요. 교안을 처음 만들 때 Haiku로 돌렸을 때는 되돌리지 않고 먼저 물었고, Stop 훅이 한 번 더 막았어요. 둘 다 나올 수 있어요.

**끄기**: 다 해 보면 이렇게 부탁해요.

```text
.claude/settings.json 이름을 settings.hooks-off.json으로 바꾸고 work/hook-check 폴더를 지워 줘.
```

`work/hook-check`는 5절 손 시험을 했을 때만 있어요.

## 7. 레거시에 kb 훅 걸기

`docs/kb`가 있는 레거시 폴더라면 [hooks/examples/kb_guard.py](../../hooks/examples/kb_guard.py)를 레거시 폴더의 `.claude/hooks/kb_guard.py`로, [hooks/examples/kb-settings.example.json](../../hooks/examples/kb-settings.example.json)을 `.claude/settings.json`으로 복사해요. 코드 폴더가 `src`가 아니면 설정의 `src`를 내 폴더 이름으로 바꿔요.

```text
~/dbinc-ai-course/labs/day2/hooks/examples/kb_guard.py를 이 폴더의 .claude/hooks/kb_guard.py로, kb-settings.example.json을 .claude/settings.json으로 복사해 줘. 설정의 src는 ⟨이 레거시의 코드 폴더⟩로 바꿔 줘.
```

`kb_guard.py`는 임시 git 저장소에서 가짜 입력으로 시험했어요(코드만 바뀌면 막고, 둘 다 바뀌거나 두 번째 Stop이면 막지 않아요). 실제 Code 탭 세션에서는 아직 돌려 보지 않았어요.

**끝났을 때**: 코드만 고치고 `docs/kb`를 그대로 두면, Claude가 답을 마치려 할 때 "코드가 바뀌었는데 docs/kb/는 그대로예요"로 한 번 막혀요.
