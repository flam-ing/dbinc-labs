# 2일차 3교시 실습 문장 · 지침, 스킬, 테스트, 훅

2일차 3교시 [프로젝트 지침, 스킬, TDD와 훅](../../../docs/day2-rules.md)에서 보내는 문장이에요. 실습은 네 번이에요. `<꺾쇠>` 안은 내 말로 바꿔도 되고, 그대로 보내도 돼요. 보낼 때 꺾쇠 표시는 지워요.

**쓰는 폴더**: 오늘 1교시에 쓴 `~/legacy/cafe-points`예요. Code 탭에서 이 폴더로 세션을 하나 열어요. 모드는 Accept edits가 편해요.

**강사 결과**: 강사가 리팩토링을 끝까지 해 둔 결과본(`labs/legacy-easy/examples/final`)을 복사한 폴더에서 2026-10-23에 Claude Code 2.1.308과 Sonnet으로 돌렸어요. Claude가 만든 파일은 [made-by-claude/cafe-points/](made-by-claude/cafe-points/)에 있어요. 내 결과는 조금씩 달라요.

**Windows**: 실습 2와 실습 3 문장 끝에 "py로 돌려 줘"를, 실습 4 문장 끝에 "명령은 py로 써 줘"를 붙여요. `python3` 명령이 없을 수 있어요.

## 실습 1. 규칙 세 줄 넣기 (4분)

```text
어제 내가 여러 번 한 말은 <‘외부 패키지는 넣지 마’, ‘끝나면 cafe.py 돌려 봐’, ‘정책 숫자는 config.py에만 둬’>야. 이 세 가지를 CLAUDE.md에 규칙 세 줄로 넣어 줘. 지켰는지 확인할 수 있는 문장으로 써 줘.
```

끝나면 Edited 카드의 View changes로 바뀐 줄을 봐요. 강사 사본에서는 16초 걸렸어요. Claude는 줄마다 확인하는 방법(import 목록, `grep`, 실행 결과)도 같이 적었어요. 바뀐 줄은 [CLAUDE.md.diff](made-by-claude/cafe-points/CLAUDE.md.diff)에 있어요.

## 실습 2. 스킬 하나 만들기 (4분)

```text
내가 자주 하는 말 <‘끝나면 cafe.py 돌리고 결과만 짧게 알려 줘’>를 run-check라는 스킬로 만들어 줘. 내가 /run-check로 부를 때만 돌고, 파일은 고치지 않는 스킬이야.
```

`.claude` 폴더에 파일을 쓸 때는 승인 카드가 떠요. 내용을 읽고 Accept를 눌러요. 그다음 입력창에 `/run-check`를 쳐요. 목록에 없으면 + New session으로 새 세션을 열어요.

강사 사본에서는 14초 만에 [SKILL.md](made-by-claude/cafe-points/.claude/skills/run-check/SKILL.md)가 생겼어요. 사람이 부를 때만 돌게 하는 `disable-model-invocation: true` 줄도 들어갔어요.

## 실습 3. 테스트를 먼저 쓰게 하기 (4분)

```text
<issues/CAFE-5.md>의 기대 결과를 테스트로 먼저 써 주고, 실행해서 실패하는 걸 보여 줘. 그다음 테스트는 건드리지 말고 코드만 고쳐서 통과시켜 줘.
```

강사 사본에서는 29초 걸렸어요. 테스트 세 개를 먼저 썼고, 고치기 전에 두 개가 실패했어요. 그다음 `cafe.py`의 적립 계산만 고쳐서 셋 다 통과했어요. 테스트는 [test_cafe.py](made-by-claude/cafe-points/test_cafe.py), 고친 줄은 [cafe.py.diff](made-by-claude/cafe-points/cafe.py.diff)에 있어요. `CLAUDE.md`에 CAFE-5를 고치지 말라는 줄이 있으면 Claude가 먼저 물을 수 있어요. 그때는 "이번에는 고쳐도 돼"라고 답해요.

더 해 보기: "방금 쓴 테스트가 각각 무엇을 확인하는지 한 줄씩 알려 줘."

## 실습 4. 훅 하나 걸어 보기 (4분)

```text
<파일을 고칠 때마다> 테스트가 돌게 훅을 걸어 줘.
```

강사 사본에서는 `.claude/settings.json`에 PostToolUse 훅이 걸렸어요. 테스트를 돌리는 [run_tests.py](made-by-claude/cafe-points/.claude/hooks/run_tests.py)도 생겼어요. 설정은 [settings.json](made-by-claude/cafe-points/.claude/settings.json)에 있어요. 다 되면 새 세션을 열고 `/hooks`로 걸린 훅을 봐요. 실습 3의 `test_cafe.py`가 있어야 훅이 돌릴 테스트가 있어요.

더 해 보기: 새 세션에서 일부러 테스트를 깨는 부탁을 해요.

```text
cafe.py에서 적립 기준을 쿠폰 차감 전 금액으로 되돌려 줘. 테스트는 건드리지 마.
```

강사 사본에서는 Claude가 테스트를 직접 돌리지 않았는데도 실패한 테스트 두 개의 이름을 보고했어요. 훅이 돌려준 내용이에요. 끝나면 "원래대로 되돌려 줘"라고 보내거나 `/rewind`로 되감아요.
