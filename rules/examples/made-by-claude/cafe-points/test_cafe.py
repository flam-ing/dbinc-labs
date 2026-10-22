import unittest

import cafe
from grades import Grade


def make_member():
    return {"id": "M1", "name": "박노을", "birth": "1990-10-05", "total": "0", "points": "0", "grade": Grade.NORMAL}


def make_order(date, amount):
    return {"date": date, "member_id": "M1", "amount": str(amount), "use_points": "0"}


class BirthdayCouponEarnTest(unittest.TestCase):
    """CAFE-5: 생일 쿠폰을 쓴 날은 쿠폰을 뺀 결제 금액으로 적립한다."""

    def test_earns_on_paid_amount_after_coupon(self):
        members = {"M1": make_member()}
        settlement = cafe.LoyaltyPolicy().calculate_order(make_order("2026-10-17", 9000), members)

        self.assertTrue(settlement.is_birthday)
        self.assertEqual(settlement.paid, 6000)
        self.assertEqual(settlement.earned, 60)
        self.assertEqual(members["M1"]["points"], "60")

    def test_receipt_shows_earned_60(self):
        members = {"M1": make_member()}
        settlement = cafe.LoyaltyPolicy().calculate_order(make_order("2026-10-17", 9000), members)

        self.assertIn("적립: 60 점", cafe.format_receipt(settlement))

    def test_non_birthday_order_unchanged(self):
        members = {"M1": make_member()}
        members["M1"]["birth"] = "1990-03-05"
        settlement = cafe.LoyaltyPolicy().calculate_order(make_order("2026-10-17", 9000), members)

        self.assertFalse(settlement.is_birthday)
        self.assertEqual(settlement.earned, 90)


if __name__ == "__main__":
    unittest.main()
