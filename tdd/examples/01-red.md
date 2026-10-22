# 1. 빨강: 실제로 나온 결과

실제 실행 기록에서 그대로 옮겼어요. 전체 기록은 `_reference/claude-runs/01-api-red.md`와 `03-web-red.md`에 있어요. `…`는 줄인 부분이에요.

## 서버(api) Claude의 답 첫 부분

> RULES.md를 읽고 `api/src/test/java/com/example/guestbook/PrivacyMaskerTest.java`에 테스트를 썼어요. `PrivacyMasker`는 고치지 않았어요. `./gradlew build`를 돌리니 예상대로 실패했어요.
>
> **결과: 테스트 17개 중 12개 실패, `BUILD FAILED`**

## 서버(api) `./gradlew build`

```text
> Task :test FAILED

PrivacyMaskerTest > 주민등록번호는_뒷자리_첫_숫자만_남기고_가린다() FAILED
    org.opentest4j.AssertionFailedError: 
    expected: "900101-1******"
     but was: "900101-1234567"

PrivacyMaskerTest > 띄어_쓴_휴대폰_번호의_가운데를_가린다() FAILED
    org.opentest4j.AssertionFailedError: 
    expected: "010 **** 5678"
     but was: "010 1234 5678"

…

17 tests completed, 12 failed

FAILURE: Build failed with an exception.

* What went wrong:
Execution failed for task ':test'.
> There were failing tests. See the report at: file://…/api/build/reports/tests/test/index.html

* Try:
> Run with --scan to get full insights from a Build Scan (powered by Develocity).

BUILD FAILED in 918ms
```

```text
$ ls build/libs
ls: build/libs: No such file or directory
```

## 화면(web) `npm run build`

```text
 ❯ src/privacy.test.js (14 tests | 11 failed) 5ms
   ❯ 휴대폰 번호 (8)
     × 하이픈으로 나눈 번호의 가운데를 가려요 3ms
     × 붙여 쓴 번호도 가려요 0ms
     × 띄어 쓴 번호도 가려요 0ms
     × 가운데 3자리 번호는 같은 개수의 *로 가려요 0ms
     × 016로 시작하는 번호도 가려요 0ms
     × 017로 시작하는 번호도 가려요 0ms
     × 018로 시작하는 번호도 가려요 0ms
     × 019로 시작하는 번호도 가려요 0ms
…

 Test Files  1 failed | 1 passed (2)
      Tests  11 failed | 4 passed (15)
```

```text
$ ls dist
ls: dist: No such file or directory
```
