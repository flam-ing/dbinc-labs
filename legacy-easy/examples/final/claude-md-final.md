# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 개요

동네카페 포인트 적립 프로그램. 매일 마감 때 `python3 cafe.py`를 실행한다(저장소 루트에서 실행해야 `data/` 상대경로가 맞는다). 외부 의존성, 빌드, 린트, 테스트 설정은 없다.

- 입력: `data/orders.csv`(오늘 주문), `data/members.csv`(회원 명부)
- 출력: `out/members.csv`(갱신된 명부), `out/report.txt`(마감 보고), 영수증은 stdout. `out/`는 git에 올리지 않는 산출물이다.
- `cafe.py`는 `__main__`일 때만 `run()`을 호출한다. 함수 단위로 import해서 테스트할 수 있다.
- `issues/CAFE-*.md`에 요청된 정책 변경과 버그가 있다(적립률, VIP 기준, 생일 쿠폰, 새 등급, 적립 버그). 작업 전에 해당 이슈의 "같이 바꿀 것"을 확인한다.

## 구조와 주의점

- `config.py`: 정책 숫자(날짜별 등급별 적립률 `RATE_SCHEDULE`, 등급 기준 금액 `GRADE_THRESHOLDS`, 생일 쿠폰, 최소 사용 포인트, 크리스마스 이벤트)는 여기에만 둔다. 영수증과 마감 보고의 숫자 문구도 이 값에서 만든다.
- `grades.py`: `Grade` enum. `cafe.py`는 명부를 읽을 때 등급 문자열을 `Grade`로 바꾸고 저장할 때만 문자열(`.value`)로 되돌린다. 등급 추가(CAFE-4)는 `Grade`, `config.GRADE_THRESHOLDS`, `config.RATE_SCHEDULE`에 넣는다. 승급·다음 등급 안내·보고 줄은 이 값에서 만들어지므로 `cafe.py`는 고치지 않는다.
- `config.RATE_SCHEDULE`에 쓴 등급 순서가 곧 등급 순서다(낮은 등급부터). 날짜별로 그 표에 있는 등급만 쓸 수 있다.
- `cafe.py`: 계산(`LoyaltyPolicy.calculate_order`, `summarize`)과 출력(`format_receipt`, `format_report`)이 나뉘어 있고, `run()`은 순서만 정한다.
- `web/src/points.ts`의 적립률과 `web/src/grades.ts`의 등급 값은 Python과 별도로 하드코딩되어 있다. 정책을 바꾸면 함께 확인한다.
- 크리스마스(`2020-12-25`) 포인트 두 배 이벤트는 정책이라 남겨 두었다(`config.CHRISTMAS_*`).
- CAFE-5 버그(생일 쿠폰을 쓴 날 쿠폰 차감 전 금액으로 적립)는 `LoyaltyPolicy.earned_points`의 `earn_base`에 그대로 있다. 정책이 정해지기 전에는 고치지 않는다.
- 저장이 실패하면 예외가 그대로 나온다.

## 규칙이 흩어져 있는 곳

정책을 바꿀 때 이 목록을 확인한다. 이슈의 "같이 바꿀 것"도 함께 본다.

| 규칙 | 있는 곳 |
| --- | --- |
| 날짜별 등급별 적립률 | `config.RATE_SCHEDULE` (Python), `web/src/points.ts`의 `RATE_SCHEDULE` (별도 복사본) |
| 등급 이름과 순서 | `grades.py`의 `Grade`, `web/src/grades.ts` (별도 복사본) |
| 등급이 되는 누적 금액 | `config.GRADE_THRESHOLDS` |
| 생일 쿠폰 금액·최소 주문 | `config.BIRTHDAY_COUPON`, `config.BIRTHDAY_MIN_ORDER` |
| 최소 사용 포인트 | `config.MIN_USE_POINTS` |
| 크리스마스 두 배 | `config.CHRISTMAS_DATE`, `config.CHRISTMAS_MULTIPLIER` |
| 영수증·마감 보고의 숫자 문구 | 따로 없음. 위 값에서 만든다 |
| 사람이 읽는 규칙 설명 | `README.md`의 "규칙" |

`web/`은 읽기 전용이라 Python 쪽만 바꾸면 화면과 어긋난다. 어긋남을 이슈나 보고에 남긴다.

## web/

키오스크 회원 화면(React, `App.tsx`/`MemberCard.tsx`/`GradeBadge.tsx`/`points.ts`). `package.json`이 없어 빌드·실행할 수 없고 읽기 전용으로 취급한다(`web/README.md`). 포인트 계산 로직이 Python과 별도로 중복되어 있어 정책 변경 시 함께 확인한다.

## 코드 규칙

- 파이썬 이름은 영어로 써요. 함수와 변수는 snake_case, 상수는 UPPER_SNAKE_CASE, 클래스는 CapWords예요(PEP 8, Google Python 스타일 가이드).
- 안 쓰는 코드는 남기지 않아요. 주석 처리한 옛 코드, 아무도 부르지 않는 함수, 디버그 print는 지워요. 옛 코드는 git 기록에 있어요.
- 비밀번호 같은 비밀값은 코드에 쓰지 않아요.
- 오류를 `except: pass`로 삼키지 않아요.
- 등급은 `grades.py`의 `Grade` enum으로만 다뤄요.
- 적립률, VIP 기준, 쿠폰 금액 같은 정책 숫자는 설정 한 곳에만 둬요.
- 화면 코드는 TypeScript(`.tsx`, `.ts`)로 통일하고, 컴포넌트 안에서 다른 컴포넌트를 만들지 않아요.
- 리팩터링은 동작을 바꾸지 않아요. 고치기 전과 뒤의 결과를 비교하고, 단계마다 커밋해요.
