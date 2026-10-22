# 변경 기록

## 2026-10-19

### 정책

- CAFE-1: 2026-11-01 주문부터 일반 회원 적립률 1% → 2%.
- CAFE-4: 2027-01-01부터 골드 등급 추가(누적 30만 원, 적립 5%). 이후 등급은 `Grade`, `config.GRADE_THRESHOLDS`, `config.RATE_SCHEDULE`에 더한다.

### 정리 (동작은 그대로)

- 안 쓰는 코드, 오류 삼키기, `time.sleep`, 코드 안의 비밀번호를 지움.
- 정책 숫자를 `config.py` 한 곳으로 모음.
- 복사본이던 두 분기를 하나로 합치고, 등급을 `Grade` enum으로 통일.
- 이름을 영어로 바꾸고 전역 변수를 없앰(자세한 건 docs/renames.md).
- 계산(`LoyaltyPolicy`)과 출력(`format_receipt`, `format_report`)을 나누고 `run()`을 작은 함수로 나눔.
- `web/src`를 TypeScript로 통일하고 관리자 버튼을 뺌.

### 아직 안 한 것

- CAFE-2(VIP 기준 20만 원), CAFE-3(생일 쿠폰 5,000원), CAFE-5(생일 쿠폰을 쓴 날 적립 버그)는 열려 있다.
