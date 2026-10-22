# 버그 네 개 방명록

2일차 4교시 [버그 원인 분석과 디버깅](../../docs/day2-debugging.md)에서 쓰는 폴더예요. 1일차 방명록에 버그를 일부러 네 개 넣었어요. 화면, 서버, DB, 실행 환경에 하나씩 있고, 고칠 곳은 모두 코드 한 줄이에요.

처음에는 이슈가 하나도 없어요. 수업 중에 강사가 강사 저장소에 이슈를 하나씩 올려요. 그래서 이 폴더에는 이슈 글이 들어 있지 않아요.

| 도착 | 이슈 | 영역 | 쓰는 곳 |
| --- | --- | --- | --- |
| 10:35 | #1 이름을 딱 40자로 쓰면 거절돼요 | 서버 | 강사 시연 |
| 10:42쯤 | #2 내용에 작은따옴표(')가 있으면 저장이 안 돼요 | DB | 실습 2 |
| 10:51 | #3 글을 남겨도 목록에 바로 안 나와요 | 화면 | 실습 4 |
| 10:51 | #4 새로 배포하면 글이 다 사라져요 | 실행 환경 | 실습 4 |

## 받고 켜기

강사 저장소를 `~/dbinc-debug`로 받아요. Claude에게 "이 저장소 주소를 ~/dbinc-debug로 clone해 줘"라고 해도 되고, GitHub의 Code 단추에서 Download ZIP으로 받아도 돼요. GitHub가 막힌 회사라면 강의 저장소의 `labs/debug` 폴더를 복사해요. 내용은 같아요.

받은 폴더로 Code 탭 새 세션을 열고 "서버를 켜고 테스트를 돌려 줘"라고 보내요. Windows는 "py로 돌려 줘"를 붙여요. 테스트 3개가 통과하면 준비가 끝났어요. 버그를 잡는 테스트가 아직 없어서 통과해요.

직접 켤 때는 폴더 맨 위에서 아래 명령을 한 줄씩 쳐요. Windows는 `python3` 대신 `py`를 써요.

```text
python3 app.py
python3 -m unittest
```

서버 주소는 http://127.0.0.1:8000 이에요. 설치할 패키지는 없어요.

## 폴더

| 파일·폴더 | 내용 |
| --- | --- |
| `app.py`, `static/` | 서버와 화면 |
| `tests/test_guestbook.py` | 지금 있는 테스트 3개 |
| `CLAUDE.md` | 작업 지침이에요. 재현 먼저, 그 줄만 고치기, 회귀 테스트는 `tests/test_bugs.py`에 넣기 |
| `Dockerfile`, `compose.yaml` | 컨테이너로 띄울 때 쓰는 파일 |
| `github/workflows/claude.yml` | 온콜 워크플로예요. 이슈에 `autofix` 라벨이 붙으면 GitHub Actions가 Claude Code를 깨워요 |
| `github/ISSUE_TEMPLATE/bug.md` | 버그 신고 양식(재현 순서, 기대, 실제) |
| `routine-prompt.md` | 루틴에 붙여 넣는 요청문(강사 시연) |
| `tools/make_repo.py` | 강사 저장소 폴더를 만드는 스크립트 |
| `examples/` | 실습에서 보내는 문장([prompts.md](examples/prompts.md)), 강사 사본에서 받은 실제 결과, 강사용 정답(`answers.md`) |
| `_reference/` | 강사용이에요. 이슈 글 네 장, 이슈를 올리는 `post_issue.py`, 연습용 PR이 있어요. 학생용 ZIP과 사이트에는 없어요 |

`github/`와 `gitignore`는 저장소를 만들 때 `.github/`와 `.gitignore`로 이름이 바뀌어 들어가요.

## 강사 저장소 준비

강의용 맥북에서 수업 전에 해요.

1. `labs/debug` 폴더에서 `python3 tools/make_repo.py ~/guestbook-oncall`을 실행해요. 예시 답과 강사용 기록은 들어가지 않아요.
2. 그 폴더를 공개 저장소로 올려요. 이슈는 0개로 둬요.
3. 저장소에 Claude GitHub App을 설치하고, Actions 비밀값 `CLAUDE_CODE_OAUTH_TOKEN`을 넣고, `autofix` 라벨을 만들어요.
4. 이슈 하나로 온콜을 끝까지 돌려 봐요. 확인이 끝나면 저장소를 지우고 새로 만들어요. 그래야 수업 중 이슈 번호가 #1부터 맞아요.

수업 중에는 `_reference/post_issue.py`로 이슈를 올려요. 10:35에 `1`, 10:42에 `2`, 10:51에 `3 4`를 넘겨요. 4교시가 끝나면 루틴과 온콜 워크플로를 꺼요.
