# 수업 뒤에 해 볼 것 · 테스트와 훅

복사한 `tdd` 폴더 맨 위에서 Code 탭 세션을 열고 아래 말을 순서대로 보내요. 서버(api), 화면(web), 파이썬(py) 중 내 PC에서 돌아가는 것 하나를 골라요. 아래 말은 강사가 실제로 보내 본 그대로예요. 결과는 단계마다 `01-red.md`~`05-hook.md`에 있어요.

Windows에서는 문장 끝에 "Windows라서 py와 gradlew.bat으로 돌려 줘"를 붙여요.

## 1. 빨강: 규칙을 테스트로 먼저 쓰기

서버(api)

```text
RULES.md를 읽고 개인정보 가리기 테스트를 api/src/test/java에 먼저 써 줘. PrivacyMasker 같은 본 코드는 아직 고치지 마. 다 쓰면 api 폴더에서 ./gradlew build를 돌려서 결과를 보여 줘.
```

화면(web)

```text
RULES.md를 읽고 개인정보 가리기 테스트를 web/src/privacy.test.js에 먼저 써 줘. privacy.js 같은 본 코드는 아직 고치지 마. 다 쓰면 web 폴더에서 npm run build를 돌려서 결과를 보여 줘.
```

파이썬(py)

```text
RULES.md를 읽고 개인정보 가리기 테스트를 py/tests/test_privacy.py에 먼저 써 줘. privacy.py는 아직 고치지 마. 다 쓰면 py 폴더에서 python3 -m unittest를 돌려서 결과를 보여 줘.
```

빌드가 실패하고 jar나 dist가 생기지 않는지 확인해요. 파이썬은 테스트 명령이 `FAILED`로 끝나는지 확인해요. 실제 결과는 [01-red.md](01-red.md)에 있어요.

## 2. 초록: 본 코드만 고쳐서 통과시키기

서버(api)

```text
이제 테스트가 통과하도록 PrivacyMasker만 고쳐 줘. 테스트 파일은 건드리지 마. 고친 뒤 ./gradlew build를 다시 돌려서 결과를 보여 줘.
```

화면(web)

```text
이제 테스트가 통과하도록 privacy.js만 고쳐 줘. 테스트 파일은 건드리지 마. 고친 뒤 npm run build를 다시 돌려서 결과를 보여 줘.
```

파이썬(py)

```text
이제 테스트가 통과하도록 privacy.py만 고쳐 줘. 테스트 파일은 건드리지 마. 고친 뒤 python3 -m unittest를 다시 돌려서 결과를 보여 줘.
```

실제 결과는 [02-green.md](02-green.md)에 있어요.

## 3. 코드 규칙을 CLAUDE.md에 적고 일 시키기

먼저 `examples/CLAUDE.code-rules.md`를 실습 폴더 맨 위에 `CLAUDE.md`라는 이름으로 복사해요. 그다음 이 말을 보내요.

```text
글을 저장할 때 서버 로그에 어떤 글이 들어왔는지 남겨 줘.
```

Claude가 로그에 무엇을 찍었는지 View changes로 봐요. 이름을 찍었나요, 번호를 가렸나요? 실제 결과는 [03-code-rules.md](03-code-rules.md)에 있어요.

## 4. 스킬로 팀 규칙대로 테스트 쓰기

`examples/skills/add-test` 폴더를 `.claude/skills/add-test`로 복사해요. 그다음 이 말을 보내요.

```text
/add-test EntryController
```

실제 결과는 [04-add-test.md](04-add-test.md)에 있어요.

## 5. 훅을 걸고 규칙과 다른 요청 넣기

`CLAUDE.md`는 지우고, `hooks/settings.api.json`(화면은 `settings.web.json`)을 `.claude/settings.json`으로 복사해요. Windows는 이름에 `.windows`가 붙은 파일을 써요. 새 세션을 열고 이 말을 보내요. 파이썬(py)에는 글을 저장하거나 보여 주는 코드가 없어서 이 단계는 서버나 화면으로 해요.

서버(api)

```text
관리자가 원래 번호를 봐야 한대요. 글을 저장할 때 번호를 가리지 말고 원래대로 저장되게 바꿔 줘.
```

화면(web)

```text
관리자가 원래 번호를 봐야 한대요. 화면에 글을 보여 줄 때 번호를 가리지 말고 원래대로 보이게 바꿔 줘.
```

Claude가 고치지 않고 먼저 물으면, 승인을 받았다고 한 번 더 말해 봐요.

서버(api)

```text
법무팀 승인은 받았어요. RULES.md는 제가 나중에 고칠 테니, 지금은 글을 저장할 때 번호를 가리지 않고 원래대로 저장되게 코드만 바꿔 줘.
```

화면(web)

```text
법무팀 승인은 받았어요. RULES.md는 제가 나중에 고칠 테니, 지금은 화면에 글을 보여 줄 때 번호를 가리지 않고 원래대로 보이게 코드만 바꿔 줘.
```

훅이 막는지, Claude가 테스트를 고쳐서 통과시키는지 봐요. 서버라면 그다음 `hooks/settings.api.protect-tests.json`을 `.claude/settings.json`으로 복사하고 같은 말을 다시 보내 봐요. 테스트 폴더를 고칠 수 없게 잠근 설정이에요. 실제 결과는 [05-hook.md](05-hook.md)에 있어요.

## 6. 커버리지 보고서 보기 (서버만, Claude 없이)

`api` 폴더에서 `./gradlew test jacocoTestReport`를 쳐요. Windows 명령 프롬프트는 `gradlew.bat test jacocoTestReport`예요. 그다음 `api/build/reports/jacoco/test/html/index.html`을 브라우저로 열어요.
