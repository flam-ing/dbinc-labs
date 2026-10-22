# 방명록 CLI 예시

2일차 5교시 [사내 시스템 연동](../../../docs/day2-integration.md)의 실습 2(방명록을 CLI로)와 실습 3(권한 규칙 걸기)에서 보는 자료예요. 실습은 내 방명록 폴더에서 Claude와 함께 해요. 이 폴더의 파일은 결과 견본과 막혔을 때 쓰는 자료예요.

| 파일 | 하는 일 |
| --- | --- |
| [examples/prompts.md](examples/prompts.md) | 강사가 결과 견본을 만들 때 보낸 긴 문장 |
| [examples/plan-answer.md](examples/plan-answer.md) | Plan 모드로 화면 코드를 읽게 했을 때 받은 답 |
| [examples/claude-made-gb.py](examples/claude-made-gb.py) | 그 계획대로 Claude가 만든 `tools/gb.py` 그대로 |
| [examples/check-output.txt](examples/check-output.txt) | 그 CLI를 켜 둔 방명록에 돌린 출력. 발표의 실습 2 결과 장면이 이 출력이에요 |
| [gb_example.py](gb_example.py) | 막혔을 때 복사해서 시작하는 강사 예시 CLI. 파이썬 표준 라이브러리만 써요 |
| [settings.example.json](settings.example.json) | 권한 규칙 예시. 목록은 묻지 않고, 쓰기는 매번 물어요 |
| `_reference/` | 강사용 실행 기록. 실습 3 기록은 `claude-runs/c0-rules-file.md`예요. 학생용 ZIP과 사이트에는 없어요 |

## 강사 예시 CLI 써 보기

참고 방명록을 켜고, 켠 터미널은 그대로 둬요. Windows는 `python3` 대신 `py`를 써요.

```text
python3 ~/dbinc-ai-course/labs/guestbook/app.py
```

다른 터미널에서 이 폴더로 와서 한 줄씩 쳐요.

```text
python3 gb_example.py write "실습자" "CLI로 남긴 첫 기록"
python3 gb_example.py write "실습자" "CLI로 남긴 첫 기록" --yes
python3 gb_example.py write "  " "공백 이름" --yes
python3 gb_example.py list
```

첫째 줄은 `--yes`가 없어서 보내지 않아요. 둘째 줄은 저장하고, 셋째 줄은 이름이 비어서 막아요. 서버 터미널에는 `POST /api/entries`가 한 줄만 찍혀요. 막은 요청은 서버로 가지 않았다는 뜻이에요.

Claude가 실습에서 만드는 CLI는 쓰는 법이 다를 수 있어요. 틀린 값을 보내기 전에 막기만 하면 어느 모양이든 괜찮아요. 방명록 API 주소가 다르면 `--url`을 붙이거나 `GB_URL` 환경 변수를 정해요. Spring 방명록이면 `--url http://127.0.0.1:8080`이에요.

Claude가 만든 CLI가 계속 실패하면 이렇게 부탁해요. "~/dbinc-ai-course/labs/day2/cli/gb_example.py를 이 폴더의 tools/gb.py로 복사하고, 이 방명록 규칙에 맞게 고쳐 줘."
