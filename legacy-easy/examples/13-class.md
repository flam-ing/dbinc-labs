# 절차형 함수를 클래스로: 실제로 나온 답

[prompts.md](prompts.md)의 말을 그대로 보낸 실제 답이에요. 답은 고치지 않았어요.

| 항목 | 값 |
| --- | --- |
| 날짜 | 2026-10-19 |
| Claude Code | 2.1.302 |
| 모델 | Sonnet 5.5 |
| 모드 | Auto |
| 폴더 | 카페 포인트(화면 정리 다음) 사본 |
| 걸린 시간 | 38초 |

## 보낸 말

```text
주문 계산(calculate_order)과 그 안의 규칙(포인트 사용, 생일 쿠폰, 적립)을 LoyaltyPolicy라는 클래스 하나로 묶어 줘. 동작은 그대로 두고, python3 cafe.py 결과가 before/와 같은지 확인한 다음 커밋해 줘. 함수로 둘 때와 클래스로 묶을 때 무엇이 좋아지는지 두세 줄로 알려 줘.
```

## 실제 답

`calculate_order`와 그 안의 규칙을 `cafe.py`의 `LoyaltyPolicy` 클래스로 묶어서 커밋했어요(`fe14c55`). 리팩터링 전후 모두 `python3 cafe.py`의 화면 출력이 `before/screen.txt`와, `out/`이 `before/out`과 똑같았어요.

**바뀐 것**
- `LoyaltyPolicy` 안에 `calculate_order`, `usable_points`(포인트 사용), `claim_birthday_coupon`(생일 쿠폰), `earned_points`(적립)가 들어 있어요.
- 이번 마감에서 쓴 생일 쿠폰 기록(`used_coupons`)은 함수 인자로 넘기지 않고 클래스가 직접 들고 있어요.
- `settle_orders`는 `LoyaltyPolicy()`를 하나 만들어 주문마다 `policy.calculate_order(order, members)`를 불러요.
- `CLAUDE.md`에서 `calculate_order`를 가리키던 두 줄을 새 위치로 고쳤어요.
- CAFE-5의 `earn_base` 동작은 그대로 두었어요. 위치만 `earned_points`로 옮겼어요.

**함수일 때와 클래스일 때**
- 함수는 `used_coupons` 같은 상태를 호출하는 쪽이 만들어 계속 넘겨야 했어요. 클래스는 그 상태를 안에 가지고 있어서 호출하는 쪽이 단순해져요.
- 규칙 이름(`usable_points`, `claim_birthday_coupon`, `earned_points`)이 생겨서 CAFE 이슈의 정책 변경이 어디를 건드리는지 바로 보여요. 규칙 하나만 따로 테스트하기도 쉬워요.
- 대신 지금은 정책 종류가 하나뿐이라, 코드가 늘고 얻는 건 주로 읽기 쉬움이에요.

CLAUDE.md의 "리팩터링은 단계마다 커밋"에 맞춰 이번 변경 하나만 커밋했어요. `out/`은 원래대로 git에 올리지 않았어요.
