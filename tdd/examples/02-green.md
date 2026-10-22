# 2. 초록: 실제로 나온 결과

전체 기록은 `_reference/claude-runs/02-api-green.md`와 `04-web-green.md`에 있어요.

## 서버(api) Claude가 고친 파일

`PrivacyMasker.java`만 바뀌었어요. 테스트 파일은 그대로예요.

```java
package com.example.guestbook;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class PrivacyMasker {

	// 개인정보 가리기 규칙은 RULES.md에 있어요.

	// 주민등록번호: YYMMDD-NNNNNNN (뒷자리 첫 숫자만 남겨요)
	private static final Pattern RESIDENT_ID = Pattern.compile("(?<!\\d)(\\d{6}-\\d)\\d{6}(?!\\d)");

	// 휴대폰 번호: 구분자는 하이픈, 공백, 없음 중 앞뒤가 같은 것
	private static final Pattern MOBILE =
		Pattern.compile("(?<!\\d)(01[016-9])([-\\s]?)(\\d{3,4})\\2(\\d{4})(?!\\d)");

	public static String mask(String text) {
		if (text == null) {
			return null;
		}
		String masked = RESIDENT_ID.matcher(text).replaceAll(match -> match.group(1) + "******");
		return MOBILE.matcher(masked).replaceAll(PrivacyMasker::maskMobile);
	}

	private static String maskMobile(java.util.regex.MatchResult match) {
		String separator = match.group(2);
		String stars = "*".repeat(match.group(3).length());
		return Matcher.quoteReplacement(match.group(1) + separator + stars + separator + match.group(4));
	}
}
```

## 서버(api) `./gradlew build`

```text
> Task :testClasses
> Task :test
> Task :bootJar
> Task :assemble
> Task :check
> Task :build

BUILD SUCCESSFUL in 909ms
```

```text
$ ls build/libs
guestbook-0.0.1-SNAPSHOT.jar
```

## 화면(web) `npm run build`

```text
 Test Files  2 passed (2)
      Tests  15 passed (15)
…
dist/index.html                  0.32 kB │ gzip:  0.24 kB
dist/assets/index-CAMI8MII.js  220.46 kB │ gzip: 69.05 kB

✓ built in 47ms
```
