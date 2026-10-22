# 최고 점수 표시 (게임 오버 / 클리어 화면)

## Context
게임 오버·클리어 화면에 최고 점수를 보여주고, 새로고침해도 남게 이 브라우저(localStorage)에만 저장한다. 새 기록이면 "새 기록" 글자를 적는다. 점수 계산, 속도, 목숨 규칙(`RULES`), 미디어 파일(`assets/`)은 건드리지 않는다.

## 바꿀 파일
- `index.html` (게임 전체가 이 한 파일)
- `deploy/index.html` — `index.html`과 지금 내용이 완전히 같은 복사본이라, 같은 수정을 똑같이 넣어 둘을 동기화한다. (확인: `diff`가 차이 없음)

둘 다 약 +25줄, 삭제 거의 없음. 정확한 줄 수는 `git diff --stat`으로 보고한다.

## 변경 내용 (`index.html`)
1. **HTML**: 게임 오버(`#over`)와 클리어(`#clear`) 오버레이에 각각
   `<p class="best" id="over-best"></p>` / `<p class="best" id="clear-best"></p>` 추가.
   새 기록이면 같은 줄에 `새 기록` 글자를 넣는다.
2. **CSS**: `.best`(작은 굵은 글씨) 한 줄, 클리어 화면(어두운 배경)에서는 기존 `.clear-screen p { color:#fff }`가 적용되므로 추가 색 규칙 불필요.
3. **JS**
   - `const BEST_KEY = 'rabbit-carrot-best';`
   - `loadBest()` / `saveBest(n)`: `localStorage`를 `try/catch`로 감싼다 (저장이 막힌 브라우저에서도 게임은 정상 동작, 그땐 이번 판 기록만 표시).
   - `endGame(kind)` 안, 화면을 보이기 직전에 `showBest(kind)` 호출:
     - `final = Math.floor(score)`, `prev = loadBest()`
     - `final > prev`이면 `saveBest(final)`, 문구 `최고 점수 N점 · 새 기록`
     - 아니면 `최고 점수 prev점`
   - `score`를 읽기만 하고 바꾸지 않는다. `RULES`, `loop`의 점수/속도/목숨 코드는 손대지 않는다.

## 정할 점 (기본값으로 진행)
- 첫 판은 이전 기록이 0이라 0점보다 높으면 "새 기록"으로 표시. 동점은 새 기록 아님.
- 클리어는 항상 300점이라, 한 번 클리어하면 최고 점수는 300으로 고정되고 이후 클리어에는 "새 기록"이 안 뜬다.

## 확인 방법
1. `python3 tools/check.py` — 미디어 파일 점검 통과 확인.
2. 브라우저로 `index.html`을 열어서(Chrome 등) 확인:
   - 게임 오버: 최고 점수 표시 + 첫 판 "새 기록".
   - 새로고침 후 다시 플레이해서 더 낮은 점수로 끝나면 이전 최고 점수 유지, "새 기록" 없음.
   - 클리어 화면(콘솔에서 `score`를 올리는 대신 실제로 300점까지 플레이하거나, 테스트용으로 localStorage만 조작)에서도 표시.
   - 개발자도구 Application → Local Storage에 키가 저장됐는지 확인.
3. `git diff --stat`로 바뀐 파일과 줄 수 보고, `git diff`에서 `RULES`/점수/속도/목숨 코드와 `assets/`가 안 바뀐 것 확인.
