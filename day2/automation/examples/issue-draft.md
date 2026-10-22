# 이슈 초안 받기 (실제 답)

예전 판 2일차 디버깅 교시의 "버그 이슈 쓰기" 실습에서 Claude에게 이슈 초안을 맡긴 실제 결과예요. 저장소가 준비된 사람은 이 초안을 GitHub의 **New issue**에 옮기고, 준비가 안 된 사람은 이 파일을 그대로 두고 강사 저장소의 이슈와 견줘요.

## 보낸 말

Code 탭의 `labs/day2` 세션(Manual)에서 보냈어요. `prompts.md` 2번과 같아요. 바꿀 곳은 `billing 오류율`이에요(다른 증상: catalog의 404와 500ms, 없는 서비스). 공백이 붙은 이름은 재현 스크립트가 검사하지 않아서, 그 증상은 `../bug-issue-example.md`의 공백 명령과 기대 문장을 옮겨 써요.

```text
automation/repo/github/ISSUE_TEMPLATE/bug.md 양식으로 billing 오류율 버그 이슈를 써서 artifacts/issue-draft.md에 저장해 줘. python tools/reproduce.py --impl buggy/report.py를 실행해서 실제 칸에는 출력을 고치지 말고 그대로 넣고, 기대 칸에는 SPEC.md의 근거 문장을 넣어 줘. 입력 칸 명령은 양식 그대로 두고, 제목은 증상 한 줄로 써 줘.
```

## 어떻게 돌렸나

- 2026-10-17, `labs/day2`의 사본, Claude Code 2.1.302, 모델 Sonnet 5.5
- 걸린 시간 17초, 주고받은 횟수 5번
- Claude가 한 일: 양식 `bug.md`를 읽고, `.venv` 파이썬으로 재현 스크립트를 실행하고, `SPEC.md`를 읽은 다음 파일을 썼어요. `bug-issue-example.md`나 `examples/`는 열지 않았어요.
- 헤드리스 실행이라 파일을 쓰는 카드가 없었어요. 수업의 Manual 모드에서는 파일을 쓰기 전에 카드가 떠요. 바뀌는 파일이 `artifacts/issue-draft.md` 하나인지 보고 **Accept**를 눌러요.

## Claude가 쓴 파일 `artifacts/issue-draft.md`

````markdown
---
name: 버그 신고
about: 입력, 기대, 실제 세 칸으로 버그를 알려 주세요.
title: "[버그] billing 오류율이 66.67이 아니라 25.0으로 나옴"
labels: bug
---

## 입력

무엇을 넣고 어떻게 실행했나요? 명령을 그대로 붙여 주세요.

```bash
python tools/reproduce.py
```

## 기대

명세(`SPEC.md`)대로라면 무엇이 나와야 하나요? 근거가 되는 명세 문장도 함께 적어 주세요.

billing만 집계하면 `(error_count, error_rate_pct, slow_count)`가 `(2, 66.67, 2)`여야 합니다.

근거 (`SPEC.md`):

- "`error_rate_pct`: `round(error_count / total * 100, 2)`"
- "`total`: 필터를 적용한 이벤트 수"
- "`error_count`: HTTP 상태가 **500 이상**인 이벤트 수"
- "`slow_count`: 응답 시간이 **slow_ms 이상**인 이벤트 수"
- "위 결과는 `fixtures/events.json`에서 billing만 골랐을 때입니다." (`total` 3, `error_count` 2, `error_rate_pct` 66.67, `slow_count` 2)

## 실제

실제로 무엇이 나왔나요? 출력이나 오류 메시지를 고치지 말고 그대로 붙여 주세요.

`python tools/reproduce.py --impl buggy/report.py` 실행 결과입니다.

```text
ERROR 없는 서비스: ZeroDivisionError: division by zero
FAIL 오류 비율의 분모: actual=(2, 25.0, 1) expected=(2, 66.67, 2)
FAIL 404와 500ms 경계: actual=(1, 12.5, 0) expected=(0, 0.0, 1)
재현 실패 사례: 3/3
```

## 자동 처리

- 루틴에 맡기려면 이슈를 만든 뒤 `auto-fix` 라벨을 붙여요.
- GitHub Actions에 맡기려면 이슈를 만든 뒤 댓글로 Claude를 불러요. 부르는 말은 README의 '자동 처리' 절에 있어요.
````

## Claude가 마지막에 한 말 (원문 그대로)

```text
이슈 초안을 `artifacts/issue-draft.md`에 저장했습니다.

- **제목:** `[버그] billing 오류율이 66.67이 아니라 25.0으로 나옴`
- **입력:** 양식의 `python tools/reproduce.py`를 그대로 뒀습니다. 이 명령은 `--impl buggy/report.py` 없이 적힌 상태입니다. 그래서 이슈만 보고 실행하면 buggy 구현이 아니라 기본 구현이 돌아갑니다. 옵션을 넣을지는 정해 주세요.
- **기대:** `(2, 66.67, 2)`라고 쓰고, 근거로 SPEC.md의 `error_rate_pct`, `total`, `error_count`, `slow_count` 정의와 billing 예시 문장을 인용했습니다.
- **실제:** `.venv/bin/python tools/reproduce.py --impl buggy/report.py`를 실행한 출력 4줄을 고치지 않고 넣었습니다. 이 출력에는 billing 오류율 외에 두 가지가 더 있습니다.
  - 없는 서비스에서 `ZeroDivisionError`가 납니다.
  - 404와 500ms 경계 처리가 어긋납니다.

   이슈 제목은 요청대로 billing 증상 하나만 다뤘습니다. 나머지 두 가지는 따로 이슈로 나누거나 본문에 더할 수 있습니다.
```

## 볼 점

- **입력 칸의 명령을 사람에게 물었어요.** `labs/day2`에서는 버그가 든 파일이 `buggy/report.py`라서 `--impl`을 붙여야 해요. 이슈를 올릴 실습 저장소 `dbinc-auto`에서는 `report.py` 자체가 버그가 든 파일이라 양식 그대로 `python tools/reproduce.py`가 맞아요. 그래서 고치지 않고 그대로 올려요.
- **실제 칸은 출력 그대로예요.** 숫자를 옮겨 적다가 틀리는 일이 없어요.
- **증상 하나에 이슈 하나예요.** Claude도 나머지 두 증상은 따로 이슈로 나누자고 했어요. 루틴은 이슈와 테스트에 드러난 것까지만 고쳐요. 이 초안을 그대로 이슈로 넣고 루틴 요청문을 돌려 보니(GitHub 단계만 빼고, 48초), 재현에 나온 원인 넷은 고쳤지만 공백이 붙은 이름은 "이슈 범위 밖이라 고치지 않았습니다. 별도 이슈가 필요합니다"라고 PR 설명에 남겼어요. 그 줄을 보면 공백 문제로 이슈를 하나 더 써요. 입력 칸에는 `../bug-issue-example.md`의 공백 명령(`python -c …`)을 옮겨 써요.

## GitHub에 옮기기 (저장소가 준비된 사람)

1. 내 저장소의 **Issues**에서 **New issue**를 누르고 **버그 신고** 템플릿을 골라요.
2. 제목 칸에는 `title:` 줄의 따옴표 안 글을 붙여요.
3. 본문은 템플릿 글을 지우고 초안의 `## 입력`부터 `## 실제`의 출력 상자까지 붙여요. 맨 위 `---` 사이의 머리말은 붙이지 않아요. 실제 칸 위의 "`python tools/reproduce.py --impl buggy/report.py` 실행 결과입니다." 한 줄은 지워요. 실습 저장소에는 `buggy/report.py`가 없고, `python tools/reproduce.py`가 같은 네 줄을 내요. 지우지 않으면 루틴이 "없는 경로라 실행하지 못했다"고 PR에 적어요.
4. 오른쪽 **Labels**에서 `auto-fix`를 붙이고 이슈를 만들어요. 라벨이 없으면 **Issues** 탭의 **Labels**에서 **New label**로 먼저 만들어요. 만드는 단추의 글자는 GitHub 화면에서 확인해요.

준비가 안 된 사람은 여기까지 파일로 두면 돼요. 강사 저장소에 올라간 이슈와 내 초안의 세 칸이 같은지 견줘 봐요.
