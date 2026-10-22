# 정책 숫자는 여기에만 둔다.
from grades import Grade

POINT_RATES = {Grade.NORMAL: 0.01, Grade.VIP: 0.03}  # 등급별 적립률
VIP_THRESHOLD = 100000  # VIP가 되는 누적 결제 금액(원)
BIRTHDAY_COUPON = 3000  # 생일 쿠폰 할인 금액(원)
BIRTHDAY_MIN_ORDER = 5000  # 생일 쿠폰을 쓸 수 있는 최소 주문 금액(원)
MIN_USE_POINTS = 1000  # 한 번에 쓸 수 있는 최소 포인트
CHRISTMAS_DATE = "2020-12-25"  # 포인트 두 배 이벤트 날짜
CHRISTMAS_MULTIPLIER = 2  # 이벤트 날 적립 배수
