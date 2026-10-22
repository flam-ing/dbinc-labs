# 방명록 CLI 결과 견본을 만든 문장

2일차 5교시 따라 하기 C, 실습 2, 실습 3에서 보내는 짧은 문장은 [integration/examples/prompts.md](../../integration/examples/prompts.md)에 있어요. 이 파일에는 강사가 결과 견본을 만들 때 보낸 긴 문장을 모았어요. 2026-10-17에 참고 방명록(`labs/guestbook`)을 복사한 폴더에서 실제로 보냈어요.

| 파일 | 무엇 |
| --- | --- |
| [plan-answer.md](plan-answer.md) | 1번 문장을 Plan 모드로 보냈을 때 받은 답. 발표의 따라 하기 C 결과 장면이 이 답이에요 |
| [claude-made-gb.py](claude-made-gb.py) | 그 계획대로 Claude가 만든 `tools/gb.py` 그대로 |
| [check-output.txt](check-output.txt) | 2번 문장으로 그 CLI를 켜 둔 방명록에 돌린 출력. 발표의 실습 2 결과 장면이 이 출력이에요 |

## 1. 계획 받기 (Plan)

```text
이 폴더의 방명록 화면 코드를 읽고 표 두 개로 정리해 줘.
1) 화면이 부르는 API: 주소, 방법, 보내는 값, 받는 값
2) 화면이 막는 것: 글자 수, 빈 칸, 버튼 잠금, 확인 창, 횟수 제한, 금지어 중 실제로 있는 것과 그 코드 위치
그다음 같은 규칙을 지키는 CLI를 tools/gb.py로 만드는 계획을 세워 줘.
- 명령: list(최신 글 보기), write(글 남기기)
- 화면이 막는 것은 서버에 보내기 전에 CLI도 막고, 막은 까닭을 한국어로 알려 줘.
- write는 --yes가 없으면 보내지 않아.
- API 주소는 --url이나 GB_URL 환경 변수로 바꿀 수 있게 해 줘.
- 파이썬 표준 라이브러리만 써. 화면과 서버 코드는 고치지 마.
```

1분쯤 걸렸어요. Claude가 "공백만 넣은 값은 화면이 막지 않는데 CLI에서 막을까요?"라고 물었어요.

## 2. 만들고 확인하기 (Accept edits)

```text
공백만 넣은 값도 CLI에서 막아 줘. 나머지는 계획대로 만들어 줘.
다 만들면 켜 둔 방명록(127.0.0.1:8000)에 tools/gb.py로 아래를 차례로 실행하고 결과를 표로 보여 줘.
1) list
2) 이름을 41자로 해서 write --yes (막혀야 해)
3) 이름을 공백만으로 해서 write --yes (막혀야 해)
4) 정상적인 이름과 내용으로 write (--yes 없이, 막혀야 해)
5) 같은 값으로 write --yes
6) list
막힌 경우에 서버로 요청이 갔는지도 확인해 줘.
```

만들고 확인하는 데 1분 9초 걸렸어요. 틀린 값 세 번은 서버로 가지 않았고, 맞는 값만 저장됐어요. 이때 답은 영어로 왔어요. 그럴 때는 "한국어로 다시 정리해 줘"라고 보내요.

## 3. 권한 규칙 (Accept edits)

```text
이 폴더에 .claude/settings.json을 만들어 줘. tools/gb.py의 list는 묻지 않고 실행하게(allow), write는 매번 묻게(ask) 해 줘. python3와 python으로 부르는 두 모양을 다 적어 줘. 다른 파일은 고치지 마.
```

Accept edits 모드여도 `.claude/settings.json` 쓰기는 카드가 떠요. Claude는 `allow`에 `list` 줄 네 개, `ask`에 `write` 줄 네 개를 적었어요. 같은 모양의 예시는 [../settings.example.json](../settings.example.json)이에요. 규칙의 명령 모양은 Claude가 실제로 실행한 명령과 같아야 해요. 권한 카드에 보인 명령을 그대로 옮겨 적는 것이 가장 확실해요.

`--url`을 `list` 앞에 붙여 부르면 규칙과 모양이 달라져서 목록도 매번 물어요.

## 수업 뒤에 해 볼 것

```text
tools/gb.py를 언제, 어떻게 쓰는지 .claude/skills/guestbook-cli/SKILL.md로 정리해 줘. description에는 '방명록 글을 읽거나 남길 때'를 넣어 줘.
```

그다음 새 세션에서 "방명록에 오늘 회의 끝났다고 남겨 줘"라고 해 보고, Claude가 이 CLI를 쓰는지 봐요.

```text
tools/gb.py의 규칙 검사에 테스트 3개를 써 줘. 41자 이름, 빈 내용, 정상 입력이야.
```
