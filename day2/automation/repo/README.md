# 이벤트 집계 실습 저장소

가상 서비스의 이벤트 기록을 집계하는 `summarize` 함수 하나가 든 교육용 저장소예요. 버그 신고가 들어온 상태로 시작해요. 이슈를 쓰면 Claude Code 루틴이나 GitHub Actions가 고쳐서 PR을 올리는 흐름을 연습해요. 데이터는 모두 가상이에요.

## 켜는 법

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell에서는 둘째 줄 대신 `.venv\Scripts\Activate.ps1`을 실행해요.

## 확인하는 법

```bash
python tools/reproduce.py
python -m pytest -q
```

처음 받은 상태에서는 재현이 `재현 실패 사례: 3/3`, 테스트가 `8 failed, 36 passed`로 끝나요. 버그를 다 고치면 `재현 실패 사례: 0/3`과 `failed` 없는 결과가 나와요.

## 자동 처리

| 방식 | 맡기는 법 | 결과가 보이는 곳 |
| --- | --- | --- |
| 루틴 | 이슈에 `auto-fix` 라벨을 붙여요. 매시간 도는 루틴이 라벨 붙은 이슈를 찾아요 | claude.ai/code의 실행 세션, 이 저장소의 PR |
| GitHub Actions | 이슈 댓글에 `@claude 이 이슈를 CLAUDE.md 규칙대로 고치고 PR을 만들어줘`라고 써요 | 이슈 댓글, Actions 실행 기록 |

작업 규칙은 [CLAUDE.md](CLAUDE.md)에 있어요. 사람이 PR을 읽고 머지해요.
