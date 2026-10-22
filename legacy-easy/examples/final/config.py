# 정책 숫자는 여기에만 둔다.
from grades import Grade

# (시작 날짜, 등급별 적립률). 새것이 먼저. 이 표에 있는 등급만 그 날짜부터 쓸 수 있다.
RATE_SCHEDULE = [
    ("2027-01-01", {Grade.NORMAL: 0.02, Grade.VIP: 0.03, Grade.GOLD: 0.05}),  # CAFE-4: 골드 등급
    ("2026-11-01", {Grade.NORMAL: 0.02, Grade.VIP: 0.03}),  # CAFE-1: 일반 회원 2%
    ("0000-00-00", {Grade.NORMAL: 0.01, Grade.VIP: 0.03}),
]
GRADE_THRESHOLDS = {Grade.NORMAL: 0, Grade.VIP: 100000, Grade.GOLD: 300000}  # 등급이 되는 누적 결제 금액(원)
BIRTHDAY_COUPON = 3000  # 생일 쿠폰 할인 금액(원)
BIRTHDAY_MIN_ORDER = 5000  # 생일 쿠폰을 쓸 수 있는 최소 주문 금액(원)
MIN_USE_POINTS = 1000  # 한 번에 쓸 수 있는 최소 포인트
CHRISTMAS_DATE = "2020-12-25"  # 포인트 두 배 이벤트 날짜
CHRISTMAS_MULTIPLIER = 2  # 이벤트 날 적립 배수


def point_rates(date):
    """주문 날짜(YYYY-MM-DD)에 적용하는 등급별 적립률."""
    for start_date, rates in RATE_SCHEDULE:
        if date >= start_date:
            return rates


def grade_for_total(total, date):
    """누적 결제 금액으로 받을 수 있는 가장 높은 등급(그 날짜에 쓸 수 있는 등급 중에서)."""
    reached = [grade for grade in point_rates(date) if total >= GRADE_THRESHOLDS[grade]]
    return reached[-1]


def next_grade(grade, date):
    """grade 다음 등급. 마지막 등급이면 None."""
    grades = list(point_rates(date))
    index = grades.index(grade) + 1
    return grades[index] if index < len(grades) else None
