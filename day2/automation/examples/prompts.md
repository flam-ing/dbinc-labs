# 이슈 자동 처리 연습 문장

수업 뒤에 혼자 해 보는 [이슈 자동 처리 연습](../README.md)에서 보내는 문장이에요. 그대로 써도 되지만 `<…>`로 표시한 곳은 내 것으로 바꿔요.

| 순서 | 할 일 | 어디서 | 문장 |
| --- | --- | --- | --- |
| 1 | 저장소 만들고 올리기, 라벨 만들기 | Code 탭 `labs/day2` 세션, Manual | 1번, 3번 |
| 2 | 버그 이슈 쓰기 | Code 탭 `labs/day2` 세션, 그다음 github.com | 2번 |
| 3 | 루틴 만들고 돌리기 | claude.ai/code/routines 또는 앱 왼쪽 Routines | 4번 |
| 4 | GitHub Actions로 부르기 | 이슈 댓글 | 5번 |
| 5 | PR 검토 | GitHub PR 화면, `~/dbinc-auto` 세션 | 7번, 8번 |
| 더 해 보기 | 내 루틴 설계 | 아무 세션 | 6번 |

## 1. 저장소 만들고 비공개로 올리기 (Manual)

```text
python3 automation/make_repo.py <~/dbinc-auto>를 실행해 줘.
그다음 <~/dbinc-auto>를 git 저장소로 만들고(기본 브랜치 main) "이벤트 집계 실습 시작 상태"로 첫 커밋을 해 줘.
gh가 있으면 gh repo create <dbinc-auto> --private --source . --push로 내 GitHub에 비공개 저장소를 만들어 올려 줘.
gh가 없거나 로그인이 안 돼 있으면 멈추고 알려 줘.
```

- 바꿀 곳: 폴더 이름과 저장소 이름. 이미 있으면 `~/dbinc-auto-2`처럼 바꿔요.
- 카드에서 볼 곳: `gh repo create` 줄에 `--private`가 있는지 보고 **Allow once**를 눌러요.
- `make_repo.py`가 실제로 찍는 출력은 `make-repo-output.md`에 있어요.
- gh가 없으면: github.com에서 **New repository**로 Private 저장소를 만들고 `이 주소를 origin으로 더하고 main을 push해 줘: <저장소 주소>`라고 부탁해요.

## 2. 이슈 초안 받기 (Manual)

`labs/day2` 세션에서 보내요.

```text
automation/repo/github/ISSUE_TEMPLATE/bug.md 양식으로 <billing 오류율> 버그 이슈를 써서 artifacts/issue-draft.md에 저장해 줘. python tools/reproduce.py --impl buggy/report.py를 실행해서 실제 칸에는 출력을 고치지 말고 그대로 넣고, 기대 칸에는 SPEC.md의 근거 문장을 넣어 줘. 입력 칸 명령은 양식 그대로 두고, 제목은 증상 한 줄로 써 줘.
```

- 바꿀 곳: `<billing 오류율>`을 `catalog의 404와 500ms`, `없는 서비스`로 바꿔도 돼요. 공백이 붙은 서비스 이름은 재현 스크립트가 검사하지 않는 사례라, 그 증상으로 쓸 때는 `../bug-issue-example.md`의 공백 명령(`python -c …`)과 기대 문장을 옮겨 써요.
- 카드에서 볼 곳: 바뀌는 파일이 `artifacts/issue-draft.md` 하나인지 보고 **Accept**를 눌러요.
- 이렇게 나오면 돼요: 2026-10-17에 실제로 보냈더니 17초 만에 제목, 기대(명세 문장 다섯 줄), 실제(출력 네 줄)가 채워졌어요. 전문은 `issue-draft.md`에 있어요.
- 저장소가 준비된 사람: 초안의 `## 입력`부터 `## 실제`까지를 GitHub **New issue**의 버그 신고 템플릿에 옮기고 `auto-fix` 라벨을 붙여요. 입력 칸 명령은 양식 그대로(`python tools/reproduce.py`) 둬요. 실습 저장소에서는 `report.py` 자체가 버그가 든 파일이라 그게 맞아요. 실제 칸 위의 "`… --impl buggy/report.py` 실행 결과입니다." 한 줄은 지워요.
- 이 이슈로 루틴이 만든 PR: billing만 적은 이슈라서, 루틴은 재현에 나온 원인 넷을 고치고 공백 이름은 "별도 이슈가 필요합니다"라고 남겼어요(`pr-example.md` 끝). 그 증상은 이슈를 하나 더 써서 맡겨요.
- 실습 저장소 폴더 `~/dbinc-auto`에서 직접 재현 출력만 보고 싶으면 그 폴더로 새 세션을 열고 `python3 tools/reproduce.py를 실행해서 출력을 그대로 보여 줘.`라고 보내요.

## 3. auto-fix 라벨 만들기 (Manual, gh가 있을 때)

```text
이 저장소에 auto-fix 라벨을 만들어 줘. 설명은 "루틴이 자동으로 처리할 이슈", 색은 F97316.
```

- gh가 없으면 github.com의 **Issues** 탭, **Labels**, **New label**로 만들어요.
- 이슈 본문 예시: `../bug-issue-example.md`(billing), `issue-catalog.md`(catalog, 하나 더 쓸 때)

## 4. 루틴 요청문

`../routine-prompt.md`의 "요청문" 상자를 통째로 붙여 넣어요. 바꿀 곳은 첫 줄과 1번 줄의 `<내 저장소>` 두 군데예요(예: `my-id/dbinc-auto`).

- 만들기 화면에서 고를 것: 저장소 하나, 환경 Default, Schedule 매시간, Connectors 모두 빼기
- **Create** 다음 상세 화면에서 **Run now**
- 루틴이 만든 PR 견본: `pr-example.md`

## 5. 이슈 댓글로 부르기 (GitHub Actions)

```text
@claude 이 이슈를 CLAUDE.md 규칙대로 재현하고 고쳐줘. 고칠 때마다 python tools/reproduce.py와 python -m pytest -q를 다시 돌리고, 회귀 테스트를 tests/test_regression.py에 더해줘.
```

## 6. 내 루틴 설계 초안 받기

`my-routine-example.md`의 표를 내 일로 채운 다음 보내요.

```text
my-routine.md의 표를 읽고 루틴 요청문 초안을 써 줘. 할 일이 없으면 "처리할 일 없음" 한 줄만 남기고 끝내는 줄, 한 번에 하나만 처리하는 줄, 사람이 정할 일은 남겨 두는 줄을 꼭 넣어 줘. 루틴은 아직 만들지 마.
```

- 이렇게 나오면 돼요: 실제로 보낸 답은 `my-routine-draft.md`에 있어요. 11초 만에 [할 일], [할 일이 없을 때], [한 번에 하나만], [사람이 정할 일] 네 칸으로 된 초안이 나왔어요.

## 7. PR 브랜치를 내 PC에서 돌려 보기 (Manual, PR 검토의 더 해 보기)

`~/dbinc-auto` 폴더로 새 세션을 열고 보내요. 브랜치 이름은 PR 화면에서 복사해요.

```text
origin을 가져와서 PR 브랜치 <claude/issue-1>로 바꾸고, python3 tools/reproduce.py와 python3 -m pytest -q를 실행해서 출력을 그대로 보여 줘.
pytest가 없으면 <~/dbinc-ai-course/labs/day2/.venv>의 파이썬으로 실행해 줘.
```

- 이렇게 나오면 돼요: `재현 실패 사례: 0/3`이고 pytest에 failed가 없어요. 2026-10-17에 견본 PR 브랜치로 이 문장을 실제로 보내 봤을 때 `48 passed`가 나왔어요. passed 숫자는 회귀 테스트 수에 따라 달라요(초안 이슈로 만든 PR은 `47 passed`). 시스템 파이썬에 pytest가 없어서 Claude가 `.venv`의 파이썬으로 다시 돌렸어요.
- 카드에서 볼 곳: 같은 실행에서 Claude가 처음에 `git checkout -b claude/issue-1`로 main에서 같은 이름의 새 브랜치를 만들었다가, origin의 커밋과 다른 것을 보고 스스로 다시 맞췄어요. 카드에 `git checkout -b`가 보이거나 결과가 `3/3`으로 나오면 PR이 아니라 main을 검사한 거예요. 그때는 `origin의 <claude/issue-1>을 그대로 받아서 마지막 커밋을 보여 줘`라고 다시 부탁해요.

## 8. 두 번째 눈으로 보기 (더 해 보기)

같은 세션에서 입력창에 `/code-review`를 쳐요. 또는 이렇게 물어요.

```text
main과 <claude/issue-1>의 차이를 읽고 SPEC.md와 다른 곳, 오류를 숨기는 코드, 테스트가 못 잡는 입력이 있는지 봐 줘. 고치지는 마.
```
