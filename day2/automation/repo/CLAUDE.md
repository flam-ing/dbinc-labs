# 이벤트 집계 저장소 작업 지침

## 프로젝트 사실

- `report.py`의 `summarize` 함수 하나를 다루는 교육용 저장소다. 이벤트는 모두 가상 데이터다.
- 명세는 `SPEC.md`, 입력 데이터는 `fixtures/events.json`, 테스트는 `tests/`, 버그 재현은 `tools/reproduce.py`다.
- 의존성은 `requirements.txt`의 pytest 하나다. 설치는 `python -m pip install -r requirements.txt`다.
- 테스트: `python -m pytest -q`
- 재현: `python tools/reproduce.py`

## 버그를 고칠 때

- 먼저 재현하고 입력, 기대, 실제를 적는다. 재현되지 않으면 고치지 않는다.
- 원인은 한 번에 하나씩 고친다. 고칠 때마다 재현과 테스트를 다시 돌린다.
- `tests/test_contract.py`, `SPEC.md`, `fixtures/`는 고치지 않는다. 테스트가 명세와 다르다고 판단되면 고치지 말고 PR 설명에 적는다.
- 고친 버그마다 이슈의 입력을 그대로 쓴 회귀 테스트를 `tests/test_regression.py`에 더한다.
- 예외를 잡아서 0을 돌려주는 식으로 오류를 숨기지 않는다. 0을 돌려주는 경우는 명세가 정한 "필터 결과가 0건일 때"뿐이다.
- 새 패키지를 추가하지 않는다.

## PR 규칙

- 브랜치 이름은 `claude/`로 시작한다. 기본 브랜치에 직접 push하지 않는다.
- PR 제목은 `fix: <이슈 제목> (#이슈번호)`로 쓴다. 본문 첫 줄에 `Closes #이슈번호`를 쓴다.
- PR 본문에는 원인, 바꾼 줄, 실행한 명령과 결과(재현, 테스트), 확인하지 못한 것을 순서대로 적는다.
- 실행하지 않은 테스트를 통과했다고 쓰지 않는다.
