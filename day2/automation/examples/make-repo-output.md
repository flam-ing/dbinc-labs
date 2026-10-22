# make_repo.py 실제 출력

2026-10-17에 `labs/day2`에서 `python3 automation/make_repo.py <폴더>`를 실행했을 때 찍힌 글이에요. 첫 줄의 폴더 경로만 `/Users/me/dbinc-auto`로 바꿨어요. 버그가 든 상태라 재현이 3/3 실패인 것이 정상이에요.

```text
만들었습니다: /Users/me/dbinc-auto
  .github/ISSUE_TEMPLATE/bug.md
  .github/workflows/claude.yml
  .gitignore
  CLAUDE.md
  README.md
  SPEC.md
  conftest.py
  fixtures/events.json
  report.py
  requirements.txt
  tests/test_contract.py
  tools/reproduce.py

재현 결과 (버그가 든 상태라 실패가 정상이에요):
ERROR 없는 서비스: ZeroDivisionError: division by zero
FAIL 오류 비율의 분모: actual=(2, 25.0, 1) expected=(2, 66.67, 2)
FAIL 404와 500ms 경계: actual=(1, 12.5, 0) expected=(0, 0.0, 1)
재현 실패 사례: 3/3

다음 할 일: 이 폴더로 이동해서 git init, 첫 커밋, GitHub 비공개 저장소에 push 해요.
```

만든 폴더에서 `python -m pytest -q`를 돌리면 `8 failed, 36 passed`가 나와요(같은 날 확인).
