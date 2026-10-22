# 견본 5: 실습 2판 계획 (triage-js)

6교시 실습 2판 순서 그대로 해 본 결과예요. `labs/legacy/triage-js`를 새로 복사해서 받은 그대로 커밋하고, `labs/legacy-checks/triage-js/`의 `expected/`와 `verify.py`를 복사한 뒤 Plan 모드로 보냈어요. CLAUDE.md가 없는 새 폴더, 새 세션이에요.

- 모드: Plan
- 걸린 시간: 57초

## 보낸 말

```text
화면과 밤 배치가 같은 분류 규칙을 따로 갖고 있어서 서로 달라졌어. 규칙을 한 곳으로 모으는 첫 단계를 계획해 줘. 배치 결과는 그대로여야 하고, python3 verify.py로 확인해. 아직 고치지 마.
```

## Claude가 세운 계획

Plan 모드가 남긴 계획 원문이에요. 고치지 않았어요.

````markdown
# 분류 규칙 한 곳으로 모으기 — 1단계 계획

## Context
- 같은 분류 규칙이 `web/app.js`의 `onClassify`(2018 기준)와 `cli/triage.js:33-78`(2020.07 수정본)에 따로 있어요. CS-212.
- 차이: 장애 단어(`500` 포함 여부, `먹통`/`안돼요`), 결제 `환불`, 배송 `반송`, 계정 `탈퇴`, 대외 리스크 +5점(배치에만). SLA도 화면은 달력 시간, 배치는 영업시간.
- CS-212에서 "야간 배치가 최신"으로 정리됐어요. 그래서 **배치 규칙을 기준**으로 공유 파일을 만들어요.
- 화면은 서버 없이 `file://`로 열려서 `require`를 못 써요(CS-212 댓글). 공유 파일은 `<script>`와 `require` 둘 다 되게 만들어야 해요.

## 1단계 범위 (이번에 할 것)
배치의 분류 함수를 공유 파일로 옮기고, 배치가 그 파일을 쓰게 바꿔요. **화면은 아직 건드리지 않아요.**
배치 출력은 한 글자도 바뀌면 안 되고, 바뀌는 건 코드 위치뿐이에요.

### 1. 새 파일 `shared/rules.js`
- `cli/triage.js`의 `getCategory`, `getScore`, `getUrgency`, `getTeam`을 **그대로** 옮겨요(단어·순서·점수 그대로. 표 형태로 바꾸는 건 나중에).
- 화면에서도 쓸 수 있게 ES5 문법(`var`, `function`)과 UMD 꼴로 감싸요:
  ```js
  (function (root, factory) {
    if (typeof module === 'object' && module.exports) module.exports = factory();
    else root.TriageRules = factory();
  })(this, function () {
    'use strict';
    // getCategory / getScore / getUrgency / getTeam (cli/triage.js에서 옮김)
    return { getCategory: getCategory, getScore: getScore, getUrgency: getUrgency, getTeam: getTeam };
  });
  ```
- 파일 위 주석에 "화면과 배치가 같이 쓰는 분류 규칙. 기준은 2020.07 배치(CS-198, CS-212, 대외 리스크 키워드 위키)"를 적어요.

### 2. `cli/triage.js` 수정
- 33-78줄(분류 함수 4개)을 지우고 `const { getCategory, getScore, getUrgency, getTeam } = require('../shared/rules');`로 바꿔요.
- 등급 정규화(165줄 `toUpperCase() == 'VIP'`), 채널 `trim`, SLA·휴일·시각 처리, 출력은 그대로 둬요(입력 정리와 SLA는 이번 범위 밖).
- 맨 위 주석의 "web/app.js의 분류 로직을 가져와서"를 "shared/rules.js의 분류 규칙을 써서"로 고쳐요.

### 3. 문서
- `README.md` "분류 기준" 절: 기준이 바뀌면 `shared/rules.js`를 고친다고 바꾸고, 화면은 아직 옛 규칙(CS-212 진행 중)이라고 적어요.

## 이번에 하지 않는 것 (다음 단계)
- **2단계**: `web/index.html`에 `<script src="../shared/rules.js">`를 `app.js` 앞에 넣고 `onClassify`가 `TriageRules`를 쓰게 바꾸기. 화면 결과가 실제로 바뀌는 변경이라(`500` 빠짐, 리스크 +5 등) CS운영 안내와 브라우저 확인이 필요해요. verify.py는 화면을 검사하지 않아요.
- **3단계**: SLA(영업시간 계산)와 휴일 목록도 공유 파일로 빼기. 화면 SLA가 달력 시간→영업시간으로 바뀌고, CS-231(휴일 파일 분리)과 묶어서 보면 좋아요.
- 키워드를 표(배열) 데이터로 바꾸기, CS-205(Z 시각) 처리는 결과가 바뀌거나 범위가 달라서 따로 해요.

## 확인
1. 시작 전 기준선: `python3 verify.py` → 지금 **통과 8/8** 확인했어요(node v24.21.0).
2. 수정 후 `python3 verify.py` → 8/8이어야 해요(표·JSON·연휴·빈 파일·파일 없음·인자 없음 모두).
3. 공유 파일이 브라우저에서도 읽히는지 간단히: `node -e "const c={}; require('vm').runInNewContext(require('fs').readFileSync('shared/rules.js','utf8'), c); console.log(c.TriageRules.getCategory('앱 먹통'))"` (module이 없는 환경 = 브라우저 `<script>`와 같은 조건) → `장애`.
4. `git diff --stat`으로 `web/`가 안 바뀌었는지 봐요.
````

## 이 답에서 볼 곳

- 파일 이름을 적지 않았는데 화면 코드(`web/app.js`)와 배치 코드(`cli/triage.js`)를 스스로 찾았어요.
- 1단계는 위치만 옮겨서 배치 결과가 그대로예요. 화면이 바뀌는 일은 2단계로 미뤘어요.
- verify.py는 화면을 검사하지 않아요. 화면을 바꾸는 단계에서는 `web/index.html`을 브라우저로 직접 열어 봐요.

## Claude의 답

Claude가 마지막에 한 말 원문이에요. 강사 PC의 홈 폴더 경로만 `~`로 줄였고, 나머지는 고치지 않았어요.

````markdown
첫 단계 계획을 써 뒀어요. 코드는 아직 하나도 고치지 않았어요. 시작 전에 `python3 verify.py`를 돌려 보니 지금 **통과 8/8**이에요.

**지금 상태**
- 분류 규칙이 `web/app.js`의 `onClassify`(2018년 기준)와 `cli/triage.js:33-78`(2020년 7월에 고친 것) 두 군데에 따로 있어요.
- 둘이 다른 점:
  - 장애 단어: 화면에는 `500`이 있고, 배치에는 대신 `먹통`, `안돼요`가 있어요.
  - 배치에만 단어가 더 있어요: 결제 `환불`, 배송 `반송`, 계정 `탈퇴`.
  - 대외 리스크 +5점은 배치에만 있어요.
  - SLA 계산 방식도 서로 달라요.
- CS-212에서 "야간 배치가 최신"이라고 정리됐어요. 그래서 배치 규칙을 기준으로 삼아요.

**1단계: 배치 결과는 그대로 두고 코드 위치만 옮겨요**
1. `shared/rules.js`를 새로 만들어요. `getCategory`, `getScore`, `getUrgency`, `getTeam`을 배치에서 **고치지 않고 그대로** 옮겨요.
   - 화면은 서버 없이 `file://`로 열려서 `require`를 못 써요. 그래서 이 파일은 ES5 문법에 UMD 꼴로 감싸요. 그러면 `require`로도, `<script>` 태그로도 불러올 수 있어요. `<script>`로 불러오면 `window.TriageRules`로 쓸 수 있어요.
2. `cli/triage.js`에서 분류 함수 4개를 지우고 `require('../shared/rules')`로 바꿔요. 고객 등급 정리, SLA, 휴일, 시각 처리, 출력은 건드리지 않아요.
3. README에 "기준이 바뀌면 `shared/rules.js`를 고쳐요"라고 적어요.

**이번에 하지 않는 것 (다음 단계)**
- **2단계:** 화면이 `shared/rules.js`를 쓰게 바꿔요. 화면 결과가 실제로 달라지는 변경이에요(`500`이 빠지고 리스크 +5점이 생겨요). verify.py는 화면을 검사하지 않아서 브라우저로 직접 열어 봐야 하고, 상담원들에게도 미리 알려야 해요.
- **3단계:** SLA 계산과 휴일 목록도 공유 파일로 빼요. 휴일 목록을 코드 밖 파일로 빼 달라는 CS-231과 같이 하면 좋아요.

**확인 방법**
- 고친 뒤 `python3 verify.py`가 다시 8/8인지 봐요.
- `module`이 없는 환경(브라우저와 같은 조건)에서 `shared/rules.js`를 읽어서 `TriageRules.getCategory('앱 먹통')`이 `장애`를 돌려주는지 봐요.
- `git diff --stat`으로 `web/`가 안 바뀌었는지 봐요.

자세한 내용은 `~/.claude/plans/declarative-plotting-orbit.md`에 있어요. 진행할까요?
````
