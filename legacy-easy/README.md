# 쉬운 레거시

여러 교시에서 같은 카페 포인트 폴더를 이어서 써요. 코드가 작아서 화면에 다 띄워 놓고 같이 읽을 수 있어요. Python 3 하나만 있으면 돼요.

| 시간 | 교안 | 쓰는 폴더 |
| --- | --- | --- |
| 1일차 5교시 | [레거시 분석과 Claude Code 잘 쓰는 법](../../docs/day1-legacy.md) | `cafe-points/`, `cafe-points-wiki/`(실습 6) |
| 2일차 1교시 | [레거시 리팩토링](../../docs/day1-refactoring.md) | 어제 만든 `~/legacy/cafe-points` |
| 2일차 2교시 | [지식베이스, LLM 위키, 옵시디언](../../docs/day1-kb.md) | 어제 만든 `~/legacy/cafe-points`, `cafe-points-wiki/`의 메신저 한 장 |
| 2일차 3교시 | [프로젝트 지침, 스킬, TDD와 훅](../../docs/day2-rules.md) | 같은 `~/legacy/cafe-points` |
| 2일차 번외 | [모델·하네스·에이전트](../../docs/bonus-harness-runbook.md) | 같은 폴더에서 하네스 부품을 찾아요(실습 2). 파일은 고치지 않아요 |
| 2일차 7교시 | [AX에 대한 고찰](../../docs/day2-ax.md) | 같은 폴더에서 팀 저장소에 남길 파일을 골라요(실습 1). 파일은 고치지 않아요 |

## 들어 있는 것

| 폴더 | 무엇 |
| --- | --- |
| [`cafe-points/`](cafe-points/README.md) | 동네카페 포인트 마감 프로그램(`cafe.py`)과 키오스크 화면(`web/src/`)이에요. 정책 카드 `issues/CAFE-1~5`도 있어요 |
| [`cafe-points-wiki/`](cafe-points-wiki/README.md) | 위키, 메신저, 회의록, 고객 문의, 메일 다섯 장이에요. 코드에 없는 이유가 적혀 있어요 |
| [`kakao-sample/`](kakao-sample/README.md) | 카페 사장님, 점장, 알바가 나눈 지어낸 카톡 대화 두 개예요. 수업 실습에서는 쓰지 않아요. 재미로 해 볼 때 써요 |
| [`hamurabi/`](hamurabi/README.md) | 1978년 BASIC 게임이에요. 수업에서는 쓰지 않아요. 더 오래된 코드를 읽어 보고 싶을 때 써요 |
| [`examples/`](examples/README.md) | 실습마다 보내는 말과 강사가 실제로 받은 답이에요 |
| `_reference/` | 강사용 원본 기록이에요. 학생용 ZIP에는 들어가지 않아요 |

## 복사하기

홈 폴더에 `legacy` 폴더를 만들고, 탐색기나 Finder로 `cafe-points` 폴더를 그 안에 복사해요. `examples/`와 `_reference/`는 복사하지 않아요. 같은 폴더에 있으면 Claude가 견본까지 읽어서 내 답에 섞여요.

`cafe-points-wiki`는 1일차 5교시 실습 6에서 폴더째 `~/legacy/cafe-points` 안에 복사해요. 2일차 2교시에는 메신저 한 장만 따로 복사해요.

## 돌려 보기

`~/legacy/cafe-points` 폴더에서 `python3 cafe.py`를 쳐요. Windows는 `py cafe.py`로 쳐요. Code 탭에서 Claude에게 돌려 달라고 해도 돼요.

영수증 여섯 장이 찍히고 `out/members.csv`, `out/report.txt`가 생겨요. 끝나기 전에 1초쯤 멈춰요. 마감 보고는 주문 6건, 매출 36,800원, 적립 703점, VIP 2명이에요.

## 일부러 넣은 것

1일차 5교시에 찾고 2일차 1교시에 고칠 이상한 코드를 일부러 넣었어요.

- 아무도 부르지 않는 함수 `run2()`, `load_members()`, `reset_points()`와 주석으로 남긴 옛 적립 코드가 있어요.
- 한글 발음 이름(`maechul`, `hoewon_bulleogi`, `gyeolje`)과 뜻이 안 보이는 이름(`tmp`, `a`)이 섞여 있어요.
- 적립률(0.01, 0.03), VIP 기준(100000), 쿠폰 금액(3000)이 이름 없이 여러 곳에 있어요.
- 생일 쿠폰 쪽과 일반 쪽에 같은 적립 계산이 두 벌 있어요.
- 관리자 비밀번호 `cafe1234`가 `cafe.py`와 키오스크 화면 `App.tsx`에 그대로 적혀 있어요.
- 저장을 `except: pass`로 감싸서 실패해도 아무 말이 없어요.
- `time.sleep(1)`에 "지우지 마시오!!! (왜인지는 모름)" 주석이 있어요. 이유는 `cafe-points-wiki`의 메신저 대화에 있어요.
- 생일 쿠폰을 쓴 날은 할인 전 금액으로 적립하는 버그가 있어요(CAFE-5). 버그 고치기는 리팩토링이 아니라서 수업에서는 그대로 둬요.

데이터, 이름, 금액, 비밀번호는 모두 지어낸 것이에요.
