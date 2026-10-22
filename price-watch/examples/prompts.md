# 가격 추적 예시 요청

2일차 4교시 연습몰 실습에서 Code 탭에 보낼 말의 예시예요. 작업 폴더는 `~/dbinc-price-watch`(`labs/price-watch/starter` 사본)예요.
이 파일은 작업 폴더에 복사하지 않아요. 저장소(`~/dbinc-ai-course/labs/price-watch/examples/`)나 교안 사이트에서 열어 둔 채로 보면서 해요.
그대로 써도 되지만 `<꺾쇠>` 안은 내 것으로 바꿔요. 내 말로 바꿔 써도 되고, 핵심 단어만 지키면 돼요.
앞쪽은 90분 수업의 필수 실습이고, "선택 심화" 아래는 부록(수업 뒤나 일찍 끝났을 때)이에요. "실제로 돌려 봤어요" 표시가 있는 문장은 2026-10-17에 학생 자리에서 그대로 보내 본 문장이에요. 그때 나온 결과는 [results.md](results.md)에 있어요. 표시가 없는 문장과 "더 해 보기" 요청은 실행해 보지 않은 예시예요.

## 작업 폴더 첫 요청 (같이 하기 · 6분)

```text
이 폴더에서 git init을 하고, 지금 상태를 "가격 추적 시작 상태"로 첫 커밋해 줘. 그다음 python3 -m unittest discover -s tests를 실행해서 마지막 줄만 보여 줘. 파일은 고치지 마.
```

- 끝나면: 마지막 줄이 `OK`예요(테스트 19개).
- 이어서 Terminal 창(Ctrl과 백틱 키)에 직접 쳐요: `python3 tools/run_days.py 1 7` → 마지막 줄 `가격 기록 kb/prices.csv: 70행`.

## 8일 구조 변경 고치기 (각자 · 10분) · 실제로 돌려 봤어요

먼저 Terminal 창에서 `python3 tools/run_days.py 8`로 멈추는 것을 봐요(종료 코드 2). 시작한 시각을 적어 둬요.
아래는 실제로 돌려 본 문장 그대로예요. 내 말로 바꿀 때는 핵심 다섯 가지(스냅숏 먼저, 새 파서는 맨 앞, 새 테스트 파일, 할인 상품의 판매가와 정가, 테스트 통과 뒤 기록)를 지켜요.

```text
python3 tools/run_days.py 8 이 종료 코드 2로 멈췄어. price-watch-rules 스킬을 지켜서 고쳐 줘.
1. kb/wiki/selector-changes.md와 .runtime/snapshots/products-2026-11-08.html을 먼저 읽어.
2. collect.py에 새 구조를 읽는 파서를 PARSERS 맨 앞에 더해. 예전 파서와 기존 테스트는 고치지 마.
3. 스냅숏을 tests/fixtures/로 복사하고 tests/test_layout_b.py를 새로 만들어. 할인 상품의 판매가와 정가를 꼭 확인해.
4. python3 -m unittest discover -s tests 가 모두 통과하면 selector-changes.md에 파일 첫머리 형식대로 기록을 더해.
연습몰에는 요청하지 말고, 날짜도 바꾸지 마. 끝나면 git diff --stat을 보여 줘.
```

덧붙이면 좋은 한 줄이에요. 처음 돌렸을 때 Claude가 걸린 시간을 지어서 적었어요. 그래서 이 줄을 더했고, 넣고 다시 돌려 보니 기록에 "걸린 시간: 12분"이 그대로 적혔어요. `<12분>`은 내가 잰 시간으로 바꿔요.

```text
기록의 "걸린 시간"은 <12분>으로 적어.
```

- 끝나면: 테스트가 모두 `OK`예요(수는 사람마다 달라요. 실제로는 24개였어요). `selector-changes.md` 맨 아래에 `## 2026-11-08 ·`로 시작하는 기록이 생겨요.
- 이어서 Terminal 창: `python3 tools/run_days.py 8 14` → `가격 기록 kb/prices.csv: 140행`.
- 걸린 시간을 알려 주지 않았더니 Claude가 실제로는 1분 걸린 일을 "약 10분"이라고 적었어요. 끝난 뒤 기록을 꼭 읽어 봐요.
- 막히면: 정답 수집기와 정답 테스트를 같이 가져와요. Terminal 창에서 `cp ~/dbinc-ai-course/labs/price-watch/reference/collect.py collect.py`와 `cp -R ~/dbinc-ai-course/labs/price-watch/reference/tests/. tests/`를 쳐요. 수집기만 가져오면 내 Claude가 만든 테스트가 실패해요.

더 해 보기:

```text
/code-review
```

## 위키 숫자 채우기 (같이 하기 · 2분)

Terminal 창에서 쳐요.

```bash
python3 tools/curate.py
```

- 끝나면: `위키를 고쳤어요: 상품 페이지 10개, quality.md · 가격 140행 · 14일 · …`가 나오고, `kb/wiki/products/PW-101.md`에 숫자 칸(`curate:start`~`curate:end`)과 메모 칸(`## 메모`)이 생겨요.

## 15~22일은 준비된 수집기로 (Terminal 창)

Claude에게 보내는 말이 아니라 Terminal 창에 붙여 넣는 명령이에요. 15일과 23일 구조를 이미 읽는 정답 수집기로 바꿔서 22일까지 모아요. 15일을 직접 고치고 싶으면 이걸 치기 전에 아래 "선택 심화"의 셋에게 맡기기로 가요.

```bash
cp ~/dbinc-ai-course/labs/price-watch/reference/collect.py collect.py
cp -R ~/dbinc-ai-course/labs/price-watch/reference/tests/. tests/
python3 -m unittest discover -s tests
python3 tools/run_days.py 15 22
git add collect.py tests kb
git commit -m "정답 수집기로 15~22일"
```

- 끝나면: 테스트 24개 `OK`, 마지막 줄 `가격 기록 kb/prices.csv: 220행`(실제로 15초 걸렸어요).
- 정답 테스트를 빼먹으면 8일에 내 Claude가 만든 테스트가 `has no attribute`로 실패해요.

## 22일 · 서브에이전트 하나에게 맡기기 (각자 · 8분) · 실제로 돌려 봤어요

먼저 `.claude/agents/`의 세 파일을 열어 누가 무엇을 맡는지 봐요. 모드는 **Accept edits**예요. curator와 reporter 중 하나를 골라 그 문장을 보내요. 둘은 맡기는 일이 달라서 이름만 바꾸지 말고 문장을 통째로 골라요.

curator를 고르면(상품 페이지 메모):

```text
curator 서브에이전트에게 맡겨 줘. 1~22일 기록으로 python3 tools/curate.py를 돌리고, 사흘 이상 이어진 할인과 정가가 바뀐 날마다 관련 소식을 찾아 상품 페이지 메모에 적게 해. git add와 commit은 하지 마.
끝나면 세 가지를 보여 줘. 서브에이전트 셋이 맡는 일과 고칠 수 있는 파일 한 줄씩, git status --short 그대로, 메모에 적힌 소식 id 개수(파일에서 직접 센 것).
```

- 끝나면: 역할 한 줄씩, `git status`에 `kb/wiki/` 파일만, 소식 id 8번(서로 다른 id 3개)이 와요. 실제로 1분 52초 걸렸어요.
- 보고받을 것은 문장 끝에 모아요. "먼저 역할을 알려 주고 그다음 맡겨 줘"처럼 앞에 두었더니 역할 줄을 빠뜨렸어요.
- 메모의 숫자는 파일로 한 번 더 봐요. 메모의 비율(+1.0% 같은 것)은 숫자 칸에 `curate.py`가 쓴 값과 같아야 해요.

reporter를 고르면(22일 요약 다섯 줄):

```text
reporter 서브에이전트에게 맡겨 줘. 1~22일 기록으로 python3 tools/report.py를 돌리고 out/summary.md를 쓰게 해. git add와 commit은 하지 마.
끝나면 세 가지를 보여 줘. 서브에이전트 셋이 맡는 일과 고칠 수 있는 파일 한 줄씩, git status --short 그대로, out/summary.md 전문.
```

- 끝나면: 역할 한 줄씩과 "기준일 2026-11-22"로 시작하는 다섯 줄 요약이 와요. 실제로 44초 걸렸어요.
- 실제로 해 보니 reporter가 `out/summary.md`를 새로 쓰는 것은 막혔고, 이번에는 메인도 "허락해 주시면 저장할게요"라고 묻고 멈췄어요. `out/summary.md`가 없으면 "그 요약을 바꾸지 않고 out/summary.md에 저장해 줘"라고 한 번 더 보내요(이 한 줄은 보내 보지 않았어요).
- 요약의 숫자는 `out/report.md`와 한 번 더 봐요. 실제로 맞춰 보니 모두 같았어요.

- 이어서: `git add kb out`과 `git commit -m "22일까지 위키 메모"`(reporter였다면 `"22일까지 요약"`).

## 23일 · 하루치를 스킬로 (각자 · 6분) · 실제로 돌려 봤어요

Terminal 창에서 `python3 tools/sim_day.py 23`으로 날짜만 넘기고, Code 탭 입력창에 아래 한 줄을 보내요.

```text
/price-watch-daily
```

- 정답 수집기로 바꿨다면 collector를 부르지 않고 15초쯤에 끝나요. 15일을 직접 고쳐 온 폴더라면 23일 구조 변경으로 collector가 불려서 2분쯤 걸려요.
- 기다리는 동안 하네스에 내 규칙을 한 줄 더해요. `.claude/skills/price-watch-rules/SKILL.md`의 "하지 않는 것" 끝에 13번으로 적어요. 고를 만한 규칙은 [team-rules.md](team-rules.md)에 있어요. 훅으로 강제하는 것은 선택 심화예요.
- 끝나면: 다섯 줄 보고(날짜, 저장한 행 수, 실패와 대응, 리포트 경로, 확인하지 않은 것)가 와요.
- 이어서 Terminal 창: `python3 tools/run_days.py 23 30` → `300행`.

## 30일 · 요약과 묶기 (각자 · 5분) · 실제로 돌려 봤어요

먼저 Terminal 창에서 `python3 tools/curate.py`를 쳐서 위키 숫자를 30일로 바꿔요. 그다음 보내요.

```text
reporter 서브에이전트에게 30일 기준으로 out/summary.md를 다시 쓰게 해 줘. 그다음 python3 tools/package.py를 실행해서 마지막 줄을 그대로 보여 줘. git add와 commit은 하지 마.
```

- 끝나면: `검사를 통과한 결과를 묶었어요: dist/price-watch.zip (파일 51개)`, 그리고 "기준일 2026-11-30"으로 시작하는 다섯 줄 요약이 와요. 실제로 46초 걸렸어요.
- 실제로 해 보니 reporter가 `out/summary.md`를 새로 쓰는 것은 거부되고 메인이 숫자를 맞춰 본 뒤 대신 저장했어요. 그래도 괜찮아요. 메인이 저장하지 않고 허락을 물으면(22일에 그랬어요) "그 요약을 바꾸지 않고 out/summary.md에 저장해 줘"라고 한 번 더 보내요.
- Claude 없이 하려면 Terminal 창에서 `python3 tools/package.py`만 쳐요.

# 선택 심화

여기부터는 90분 수업에서 하지 않는 것이에요. 일찍 끝났거나 수업 뒤에 해요.

## 훅 시험 (선택 심화 · 2분)

Claude에게 보내는 말이 아니라 Terminal 창에 붙여 넣는 명령이에요. 가짜 도구 호출을 훅(`guard.py`)에 넣어 봐요.

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"curl -s https://test-server-8az.pages.dev/api/price"},"cwd":"."}' | python3 .claude/hooks/guard.py; echo $?
echo '{"tool_name":"Edit","tool_input":{"file_path":"'$PWD'/tests/test_collect.py"},"cwd":"."}' | python3 .claude/hooks/guard.py; echo $?
```

- 끝나면: 두 번 모두 "하네스: …"로 시작하는 이유와 `2`가 나와요(실제로 해 봤어요).
- 더 해 보기: 주소를 `http://127.0.0.1:8766/products`로 바꾸면 `0`(통과), `http://127.0.0.1:8766/admin/day`로 바꾸면 `2`예요.
- Windows PowerShell은 따옴표와 `echo $?`가 달라요. Git Bash에서 하면 그대로 돼요.

## 15일 · 셋에게 맡기는 계획 (선택 심화 · 11분) · 실제로 돌려 봤어요

정답 수집기로 바꾸기 전에만 할 수 있어요. 이미 바꿨다면 `starter`를 새 폴더에 다시 복사해서 8일까지 다시 해요.


먼저 Terminal 창에서 `python3 tools/run_days.py 15`로 멈추는 것을 봐요. 앞의 `/plan `은 Plan 모드로 들어가는 말이에요(모드 선택기에서 Plan을 골라도 같아요). 바꿀 곳은 `<세 서브에이전트에게>`예요. 시간이 모자라면 "collector에게만"으로 바꾸고 아래 collector 줄만 남겨요.

```text
/plan <세 서브에이전트에게> 동시에 맡기는 계획을 세워 줘.
- collector: python3 tools/run_days.py 15 가 종료 코드 2로 멈췄어. .runtime/snapshots/products-2026-11-15.html과 kb/wiki/selector-changes.md를 읽고 고쳐. 새 테스트 파일은 tests/test_layout_c.py야. 이번에는 collect.py를 실행하지 마. 테스트 통과와 기록까지만 해.
- curator: 1~14일 기록으로 python3 tools/curate.py를 돌리고, 사흘 이상 이어진 할인과 정가가 바뀐 날마다 관련 소식을 찾아 상품 페이지 메모에 적어.
- reporter: 1~14일 기록으로 python3 tools/report.py를 돌리고 out/summary.md를 써.
각자 정의 파일에 적힌 파일만 고치고, git add와 commit은 하지 마.
셋이 끝나면 git status --short와 python3 -m unittest discover -s tests 결과를 그대로 보여 줘.
```

- 계획이 나오면 읽고 승인해요. 승인한 다음 모드 선택기에서 **Accept edits**를 골라요.
- 실제로 해 보니 Claude가 계획에서 "incidents.md는 collector와 curator가 둘 다 고칠 수 있어서 동시에 쓰면 덮어써요"를 먼저 짚었어요.
- 끝나면: 테스트 `OK`, `tests/test_layout_c.py`가 새로 생기고, 상품 페이지 메모에 소식 id(예: N-0904)와 "관계는 추정이에요"가 적혀요.
- 이어서 Terminal 창: `python3 tools/run_days.py 15 22` → `220행`.

더 해 보기:

```text
reporter가 쓴 out/summary.md를 <우리 팀 주간 보고> 말투로 다시 써 줘. 숫자는 바꾸지 마.
```

## 손 계산 부탁 (선택 심화 · 2분) · 실제로 돌려 봤어요

계산은 내가 해요. Claude에게는 숫자만 보여 달라고 해요. 바꿀 곳은 `<PW-103>`이에요.

```text
kb/prices.csv에서 <PW-103>의 마지막 7일 판매가만 보여 줘. 계산은 하지 마.
```

- 끝나면: 날짜와 판매가 일곱 줄이 표로 와요. 실제로 보내 보니 4초 만에 표만 보여 주고 합이나 평균은 말하지 않았어요.

Terminal 창에서 직접 봐도 돼요(Windows는 Git Bash): `grep PW-103 kb/prices.csv | tail -7 | cut -d, -f1,5`. 일곱 값을 더하면 235,100, 7로 나누면 33,585.7이에요.

## GUIDE.md 고치기 (선택 심화 · 7분) · 실제로 돌려 봤어요

```text
GUIDE.md를 이 폴더를 처음 받은 사람 기준으로 다시 읽고, 오늘 실제로 실행한 명령과 출력에 맞지 않는 곳만 고쳐 줘. "확인하지 않은 것"에는 내가 확인하지 않은 것을 더해. 실행하지 않은 명령은 넣지 마.
```

- 끝나면: GUIDE.md에서 몇 줄이 바뀌고 "확인하지 않은 것"이 늘어요. 바뀐 줄은 **Changes**에서 읽어요.
- 이어서 Terminal 창: `python3 tools/package.py` → 다른 폴더에 풀고 `diff`로 "리포트 같음"을 확인해요. 필수 경로로 만든 ZIP으로도 실제로 해 보니 "리포트 같음"이 나왔어요.

## 풀린 폴더로 새 세션 (선택 심화)

`~/price-watch-unzip/price-watch`를 Code 탭 새 세션으로 열고 물어봐요.

```text
이 폴더로 무엇을 할 수 있어? 먼저 읽어야 할 파일과 하면 안 되는 일도 알려 줘.
```

- 대화 기록은 ZIP에 없지만 CLAUDE.md, 위키, 스킬은 들어 있어서 하지 말 일까지 답하는지 봐요.
- 이 질문은 실제로 보내 보지 않은 예시예요.
