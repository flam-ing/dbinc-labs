# 6. 확인하고 커밋하기: 실제로 나온 답

#1과 #2를 고친 사본(커밋 전)에서 새 세션을 열고 실습 3의 문장을 보낸 실제 답이에요.

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-10-23 |
| Claude Code | 2.1.309 |
| 모델 | Sonnet 5.5 |
| 모드 | Auto |
| 걸린 시간 | 32초 |

## 보낸 말

```text
바꾼 파일과 줄을 git diff로 보여 주고, 테스트를 다시 돌려 줘. 모두 통과하면 고친 이슈마다 커밋을 하나씩 만들어 줘. 커밋 메시지에 이슈 번호를 넣어. push는 하지 마.
```

## Claude의 답 (그대로)

이슈마다 커밋을 하나씩 만들었고, push는 하지 않았습니다. 커밋 전 `python3 -m unittest`는 5개 테스트가 모두 통과했습니다.

#### 변경 내용 (`git diff`)
- **`cafe.py:33`**, 이슈 #2: `if grade == "vip":`을 `if grade == "VIP":`으로 바꿨습니다. 명부에는 등급이 `VIP`로 저장되는데 비교는 소문자로 하고 있어서 VIP에게 3%가 적용되지 않았습니다.
- **`cafe.py:75`**, 이슈 #1: `> VIP_GIJUN`을 `>= VIP_GIJUN`으로 바꿨습니다. 누적이 딱 100,000원이어도 VIP가 되어야 합니다.
- **`tests/test_bugs.py`**(새 파일): 이슈 입력을 그대로 쓴 회귀 테스트 2개를 넣었습니다. #1은 M001이 5,000원을 결제하는 경우이고, #2는 M002(VIP)가 12,000원 주문에 2,000점을 쓰는 경우입니다.

#### 커밋
| 커밋 | 메시지 | 포함 내용 |
|---|---|---|
| `89fbca9` | fix: 누적 결제 100,000원이면 VIP가 되도록 수정 (#1) | `cafe.py` 1줄, `Issue1Test` |
| `a6440d0` | fix: VIP 적립률 3%가 적용되도록 등급 비교 수정 (#2) | `cafe.py` 1줄, `Issue2Test` |

- **테스트 실행:** 첫 커밋만 적용한 상태에서는 4개(기존 3개와 `Issue1Test`)가 통과했습니다. 두 번째 커밋까지 적용한 최종 상태에서는 5개가 모두 통과했습니다.
- **커밋 메시지:** 각 메시지 끝에 Co-Authored-By 줄을 붙였습니다.
- **이슈 번호:** 지금까지 받은 내용에는 번호를 확인할 근거가 없어서 `tests/test_bugs.py`에 적힌 #1, #2를 그대로 썼습니다. 실제 GitHub 이슈 번호와 다르면 알려 주세요.
- **확인하지 못한 것:** 고치기 전 코드에서 회귀 테스트가 실패하는지는 이번 턴에 다시 돌려 보지 않았습니다. 필요하면 확인하겠습니다.

## 생긴 커밋 (`git log --stat`)

```text
--- a6440d0 fix: VIP 적립률 3%가 적용되도록 등급 비교 수정 (#2)
grade == "vip" 를 "VIP" 로 바꾼다. 회귀 테스트 추가.

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>


 cafe.py            | 2 +-
 tests/test_bugs.py | 9 +++++++++
 2 files changed, 10 insertions(+), 1 deletion(-)
--- 89fbca9 fix: 누적 결제 100,000원이면 VIP가 되도록 수정 (#1)
VIP 승급 비교를 > 에서 >= 로 바꾼다. 회귀 테스트 추가.

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>


 cafe.py            |  2 +-
 tests/test_bugs.py | 18 ++++++++++++++++++
 2 files changed, 19 insertions(+), 1 deletion(-)
--- 49829f6 첫 커밋


 .github/ISSUE_TEMPLATE/bug.md |  25 ++++++++++
 .github/workflows/claude.yml  |  48 +++++++++++++++++++
 .gitignore                    |   2 +
 CLAUDE.md                     |  25 ++++++++++
 README.md                     |  52 +++++++++++++++++++++
 cafe.py                       | 105 ++++++++++++++++++++++++++++++++++++++++++
 data/members.csv              |   5 ++
 data/orders.csv               |   7 +++
 tests/__init__.py             |   0
 tests/cafe_runner.py          |  49 ++++++++++++++++++++
 tests/test_cafe.py            |  27 +++++++++++
 11 files changed, 345 insertions(+)
```

## 볼 곳

- 두 이슈가 한 작업 폴더에 섞여 있었는데, 이슈마다 커밋을 하나씩 나눴어요. 커밋 메시지 끝에 이슈 번호가 들어갔어요.
- 고치기 전에 테스트가 실패하는지는 이번에 다시 보지 않았다고 밝혔어요. 그 확인은 앞 단계(03, 05)에서 했어요.
