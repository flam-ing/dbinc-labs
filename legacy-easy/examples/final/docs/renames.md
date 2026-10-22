# 바뀐 이름

옛 이름으로 git 기록이나 옛 메모를 찾을 때 쓰는 표예요.

## Python (cafe.py, config.py)

| 옛 이름 | 새 이름 | 비고 |
| --- | --- | --- |
| `hoewon_bulleogi()` | `load_members()` | 같은 일을 하던 복사본 둘을 하나로 합침 |
| `saveMembers(m)` | `save_members(members)` | |
| `maechul` (전역 변수) | `sales` | 전역을 없애고 `DailySummary.sales`로 |
| `gunsu` | `order_count` | |
| `jeoklip`, `jeoklip_hap` | `earned`, `earned_total` | |
| `gyeolje` | `paid` | |
| `sseun_kupon` | `LoyaltyPolicy`가 기억하는 쓴 쿠폰 | |
| `calculate_order(order, members, used_coupons)` | `LoyaltyPolicy.calculate_order(order, members)` | |
| `NORMAL_RATE`, `VIP_RATE` | `config.RATE_SCHEDULE` | 날짜별 등급별 표 |
| `POINT_RATES` | `config.RATE_SCHEDULE`, `config.point_rates(date)` | |
| `VIP_THRESHOLD` | `config.GRADE_THRESHOLDS` | 등급별 기준 금액 |
| `RATE_NOTE` (상수) | `rate_note(date)` | 날짜에 맞는 안내 문구 |

## 지운 것

| 이름 | 이유 |
| --- | --- |
| `run2()` | 안 쓰는 미완성 마감 |
| `reset_points()`, `ADMIN_PASSWORD` | 안 쓰는 관리자 기능. 비밀번호는 코드에 두지 않음 |
| `web/src`의 관리자 버튼과 `ADMIN_PASSWORD` | 위와 같은 이유 |

## web/src

| 옛 이름 | 새 이름 |
| --- | --- |
| `GradeBadge.jsx` | `GradeBadge.tsx` |
| `points.js` | `points.ts` |
| `App.tsx` 안의 `HoewonCard` | `MemberCard.tsx` |
| (없음) | `grades.ts`, `types.ts` |
