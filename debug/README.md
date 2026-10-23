# 버그 네 개 카페 포인트

2일차 4교시 버그 원인 분석과 디버깅에서 쓰는 저장소예요. 오전 1~3교시에 고친 `~/legacy/cafe-points`와 같은 카페 프로그램이에요. 이번 판은 버그 넷을 일부러 넣어 따로 만든 판이고, 고칠 곳은 모두 `cafe.py`의 한 줄이에요. 오전 폴더는 그대로 두고, 새 폴더 `~/cafe-points-oncall`로 받아요. 오전에 만든 훅과 규칙은 새 폴더에 없어요. 회원 명부도 조금 달라서, 오전 폴더에서는 이슈가 재현되지 않아요.

처음에는 이슈가 하나도 없어요. 수업 중에 강사가 이 저장소의 Issues에 버그 신고를 하나씩 올려요.

| 도착 | 이슈 | 영역 | 쓰는 곳 |
| --- | --- | --- | --- |
| 10:35 | #1 누적 결제가 딱 100,000원이 됐는데 VIP가 안 돼요 | 등급 | 강사 시연 |
| 10:42쯤 | #2 VIP인데 포인트가 1%만 쌓여요 | 적립 | 실습 2 |
| 10:51 | #3 생일 쿠폰이 한 달에 두 번 나와요 | 쿠폰 | 실습 4 |
| 10:51 | #4 포인트 칸이 비어 있으면 마감이 멈춰요 | 마감 | 실습 4 |

## 받고 돌려 보기

강사 저장소(`flam-ing/cafe-points-oncall`)를 `~/cafe-points-oncall`로 받아요. Claude에게 "https://github.com/flam-ing/cafe-points-oncall 을 ~/cafe-points-oncall로 clone해 줘"라고 해도 되고, GitHub의 초록 Code 단추에서 Download ZIP으로 받아도 돼요. ZIP을 풀면 폴더 이름이 `cafe-points-oncall-main`이 돼요. 끝의 `-main`을 지워 `cafe-points-oncall`로 바꿔요.

GitHub가 막힌 회사라면 강의 자료의 `labs/debug` 폴더에서 `py tools/make_repo.py`를 실행해요(Mac은 `python3`). `~/cafe-points-oncall`이 생기고, 예시 답은 들어가지 않아요. `labs/debug` 폴더를 통째로 복사하지는 않아요. 예시 답까지 들어가서 Claude가 읽을 수 있어요.

ZIP이나 `make_repo.py`로 받았으면 git 저장소가 아니에요. 받자마자 Claude에게 "git init하고 첫 커밋을 해 줘"라고 보내요. 그래야 실습 3에서 이슈마다 커밋을 나눌 수 있어요.

받은 폴더로 Code 탭 새 세션을 열고 "마감을 한 번 돌리고 테스트도 돌려 줘"라고 보내요. Windows는 "py로 돌려 줘"를 붙여요. 영수증이 나오고 테스트 3개가 통과하면 준비가 끝났어요. 버그를 잡는 테스트가 아직 없어서 통과해요.

직접 돌릴 때는 폴더 맨 위에서 아래 명령을 한 줄씩 쳐요.

```text
py cafe.py
py -m unittest
```

Mac은 `py` 대신 `python3`를 써요. 설치할 패키지는 없어요. Windows에서 영수증 한글이 깨져 보이면 `py -X utf8 cafe.py`처럼 `-X utf8`을 붙여요.

## 폴더

| 파일·폴더 | 내용 |
| --- | --- |
| `cafe.py` | 마감 프로그램이에요. 주문을 읽고 영수증을 찍고 포인트와 등급을 바꿔요 |
| `data/members.csv` | 회원 명부(회원 넷) |
| `data/orders.csv` | 오늘 주문 여섯 건 |
| `out/` | 마감을 돌리면 생겨요. `members.csv`와 `report.txt`(마감 보고) |
| `tests/test_cafe.py` | 지금 있는 테스트 3개 |
| `tests/cafe_runner.py` | 테스트에서 임시 폴더로 마감을 돌려 주는 도우미 |
| `CLAUDE.md` | 작업 지침이에요. 재현 먼저, 그 줄만 고치기, 회귀 테스트는 `tests/test_bugs.py`에 넣기 |
| `.github/workflows/claude.yml` | 온콜 워크플로예요. 이슈에 `autofix` 라벨이 붙으면 GitHub Actions가 Claude Code를 깨워요 |
| `.github/ISSUE_TEMPLATE/bug.md` | 버그 신고 양식(재현 순서, 기대, 실제) |

강의 자료의 `labs/debug` 폴더에서는 `github/`와 `gitignore`가 점 없이 들어 있어요. 저장소를 만들 때 `.github/`와 `.gitignore`로 이름이 바뀌어요.

## 규칙

- 결제 금액의 1%를 포인트로 쌓아요. VIP는 3%예요. 1점 미만은 버려요.
- 누적 결제가 100,000원 이상이면 VIP가 돼요. 딱 100,000원도 VIP예요.
- 생일이 있는 달 첫 주문이 5,000원 이상이면 3,000원을 깎아 줘요.
- 포인트는 1,000점부터 쓸 수 있어요.

교육용 가상 자료예요. 회원 이름과 주문은 지어낸 거예요.

강사용 안내(강사 저장소 만들기, 이슈 올리기)는 강의 자료의 `labs/debug/_reference/README.md`에 있어요.
