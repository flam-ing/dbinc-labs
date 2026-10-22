# 견본 3: 실습 1판 첫 단계 계획 (expense-py)

6교시 실습 1판의 첫 예시 문장을 Plan 모드로 실제로 보낸 결과예요. 좋은 계획에는 첫 단계 하나, 그대로 지킬 것, 안 할 것, 확인 방법이 들어 있어요.

- 폴더: `labs/legacy/expense-py`를 복사하고, 5교시에 만든 `CLAUDE.md`와 인수인계 보고서를 넣은 폴더예요. 5교시를 마친 학생 폴더와 같은 모양이에요.
- 모드: Plan. 견본 2의 안전망을 만든 세션에서 이어서 보냈어요.
- 걸린 시간: 46초

## 보낸 말

```text
한 함수가 다 하는 코드를 가운데(계산 규칙)와 바깥(파일, 메일, 화면)으로 조금씩 나누고 싶어. 먼저 메일을 만드는 부분을 바깥으로 떼어 내는 첫 단계를 계획해 줘. 동작은 그대로여야 하고, 안전망으로 확인해.
```

## Claude가 세운 계획

Plan 모드가 남긴 계획 원문이에요. 고치지 않았어요.

````markdown
# 1단계: 메일 만들기를 process() 밖으로 떼어 내기

## Context
`src/expense_batch.py`의 `process()` 한 함수가 계산 규칙(검사·일비·한도·결재선)과 바깥 일(파일 읽기, 메일, 감사 로그, 화면)을 모두 해요.
가운데(계산)와 바깥(입출력)을 조금씩 나누는 첫 단계로, **8. 메일** 블록(현재 HTML 조립 + `mailer.send()` 호출)을 `mailer.py`로 옮겨요.
동작은 바이트 단위로 그대로여야 하고, 안전망은 `tools/golden.py check`예요(시나리오 10개, outbox HTML 포함).

## 지금 메일 블록이 쓰는 값 (8단계)
`name, req_id, trip_k, city, dep, ret, status, st, reason, per_diem, hotel_ok, trans, etc, no_rcpt_ok, ok_amt, ng_amt, line, req.get('memo'), emp_no`,
그리고 `mailer.HEAD/TAIL`, `util.won`, `CONFIG['finance_cc']`.

## 동작을 지키려고 그대로 둘 것
- **호출 위치와 순서**: 7단계(결과 줄) 뒤, 9단계(감사 로그) 앞. 메일 쪽에서 예외가 나면 감사 로그 줄이 안 써지는 지금 동작까지 그대로예요.
- **값은 가공하지 않고 그대로 넘겨요**: `dep`/`ret`는 date 객체(또는 `None` → `str()`으로 `'None'`), `city`·`name`·`memo`는 원래 값 그대로. `str()`을 미리 씌우면 지금은 TypeError로 죽는 입력이 살아나는 식으로 동작이 바뀌어요.
- `etc + no_rcpt_ok`를 "기타" 한 칸에 합치기, `line.replace('>', ' &gt; ')`, 메모는 HTML 이스케이프 없이(CLAUDE.md: BT-2019-0111), `if req.get('memo'):` 참 판정.
- 받는 사람 `emp_no.lower() + '@nuri.example'`, 참조 `[CONFIG['finance_cc']]`, 제목 `'[출장비] ' + req_id + ' ' + st`.
- `send()`가 쓰는 머리 5줄+빈 줄 형식(외부 메일 에이전트가 읽음)은 손대지 않아요.
- 금액 계산은 한 줄도 안 건드려요(FIN-187).

## 순서 (각 단계 뒤에 check)
0. **기준 확인**: `python3 tools/golden.py check`가 지금 통과하는지 봐요. 기록과 같은 Python(3.14.6)으로 돌려요. `golden/`, `tools/`는 아직 커밋 전이라 리팩토링 전에 먼저 커밋해 두길 권해요(사용자 확인 후).
1. **같은 파일 안에서 함수로 빼기** — `expense_batch.py`에 `result_mail_html(r)`를 만들고 8단계의 `html` 조립 줄들을 그대로 옮겨요. `r`은 위 값들을 담은 dict예요(나중에 계산 결과를 돌려줄 모양의 씨앗). `process()`에서는 dict를 만들어 호출하고, 제목과 `mailer.send(...)`는 그대로 둬요. → `check`
2. **mailer.py로 옮기기** — `result_mail_html(r)`를 `src/mailer.py`로 옮기고 `send_result(r)`을 더해요. `send_result`는 제목과 받는 사람을 만들어 기존 `send()`를 불러요. `mailer.py`에 `from util import won`을 추가해요(util은 의존이 없어서 순환 import가 안 생겨요). `process()`의 8단계는 `mailer.send_result(r)` 한 줄이 돼요. → `check`
3. 정리: `process()`에서 이제 안 쓰는 지역 변수가 생겼는지 확인만 해요(지우는 건 계산 단계를 나눌 다음 단계에서). 모듈 맨 위 변경 이력 주석에 한 줄을 더해요.

## 바뀌는 파일
- `src/expense_batch.py` — 8단계 블록 → dict 만들기 + `mailer.send_result(r)`
- `src/mailer.py` — `result_mail_html(r)`, `send_result(r)` 추가, `won` import

## Verification
- 단계마다 `python3 tools/golden.py check` → "같음: 10개 시나리오" + 종료 코드 0.
- golden이 메일 쪽에서 다루는 경우: 정산완료/반려 메일, 불인정 줄 있음(0102, 0112), 임원 결재(0106), 특수문자 메모(0111), 중복 반려(0109), 다시 돌리기(덮어쓰기). 다르면 diff가 HTML 줄 단위로 나와요.
- golden이 못 다루는 경우(이름·도시가 문자열이 아닌 입력 등)는 "값을 그대로 넘긴다" 원칙으로 지켜요. 코드 리뷰로 `str()` 등이 새로 끼어들지 않았는지 확인해요.
- 마지막에 `git diff`로 `settings.py`, `fx.py`, `util.py`와 계산 단계(2~7)가 그대로인지 확인해요.
````

데스크톱 앱에서는 계획 아래에 승인 단추가 떠요. 답 끝의 "승인을 요청하는 도구가 이 환경에 없어서"는 화면 없이 돌려서 나온 말이에요. 오늘 실습에서는 승인하지 않고 계획을 더 다듬는 쪽(터미널판 문구 No, keep planning)을 고른 뒤 모드를 Accept edits로 바꿔요. 승인하면 이 계획의 세 걸음을 한꺼번에 고쳐서, 한 걸음씩 비교할 수 없어요.

## Claude의 답

Claude가 마지막에 한 말 원문이에요. 강사 PC의 홈 폴더 경로만 `~`로 줄였고, 나머지는 고치지 않았어요.

````markdown
메일 부분을 떼어 내는 첫 단계 계획을 `~/.claude/plans/replicated-shimmying-spark.md`에 적어 뒀어요. 계획 모드라서 코드는 아직 바꾸지 않았어요. 승인을 요청하는 도구가 이 환경에 없어서 여기에 요약할게요.

**목표**
`process()`의 8단계(메일 HTML 조립과 `mailer.send()` 호출)를 `src/mailer.py`로 옮겨요. 결과는 바이트 단위로 그대로여야 해요.

**순서 (단계마다 `python3 tools/golden.py check`)**
0. **기준 확인:** 지금 상태에서 check가 통과하는지 먼저 봐요. 기록할 때와 같은 Python 3.14.6으로 돌려요. `golden/`과 `tools/`는 리팩토링 전에 커밋해 두길 권해요.
1. **같은 파일 안에서 빼기:** `expense_batch.py` 안에 `result_mail_html(r)` 함수를 만들어요. `r`은 메일에 필요한 값을 담은 dict예요. HTML을 만드는 줄은 고치지 않고 그대로 옮겨요.
2. **`mailer.py`로 옮기기:** `result_mail_html(r)`과 `send_result(r)`을 `mailer.py`로 옮기고, `won`을 import해요. 그러면 `process()`의 8단계는 `mailer.send_result(r)` 한 줄이 돼요.
3. **정리:** 이제 안 쓰는 지역 변수가 있는지 확인만 하고, 지우지는 않아요. 파일 맨 위 변경 이력에 한 줄을 더해요.

**동작을 지키려고 그대로 둘 것**
- **호출 위치:** 결과 줄 뒤, 감사 로그 앞이에요. 메일을 만들다 예외가 나면 감사 로그 줄이 안 남는 지금 동작도 그대로 유지돼요.
- **값을 바꾸지 않고 넘기기:** `dep`/`ret`, `city`, `name`, `memo`를 원래 값 그대로 넘겨요. 미리 `str()`을 씌우면 지금은 오류로 멈추는 입력이 통과하게 돼서 동작이 달라져요.
- **메일 내용:** 메모는 HTML 이스케이프를 하지 않아요. "기타" 칸은 지금처럼 `etc + no_rcpt_ok`로 합쳐요. 받는 사람, 참조, 제목 형식과 `send()`가 쓰는 머리 다섯 줄도 그대로예요.
- **금액 계산:** 2~7단계 계산은 건드리지 않아요(FIN-187).

**확인 범위**
- **golden이 확인하는 것:** 정산완료 메일, 반려 메일, 불인정 줄(0102, 0112), 임원 결재(0106), 특수문자 메모(0111), 중복 반려(0109), 같은 폴더에 다시 돌리기.
- **golden이 확인하지 못하는 것:** 이름이나 도시가 문자열이 아닌 입력은 시험 자료에 없어요. 이 경우는 diff를 읽어서 값을 가공하는 코드가 새로 들어가지 않았는지 직접 확인해요.

이대로 진행할지, 아니면 바꿀 곳이 있는지 알려 주세요.
````
