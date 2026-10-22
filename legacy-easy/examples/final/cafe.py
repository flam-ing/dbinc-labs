# -*- coding: utf-8 -*-
# 동네카페 포인트 프로그램
# 2019.03 처음 만듦 (사장님 조카)
# 2020.11 생일 쿠폰 추가
# 2020.12 크리스마스 이벤트 (포인트 두 배)
# 2021.05 등급 enum (grades.py)
# 매일 마감할 때 python3 cafe.py 실행하세요
import csv
import os
from dataclasses import dataclass
from typing import Optional
import config
from grades import Grade


def rate_note(date):
    return ", ".join(f"{grade.value} {rate:.0%}" for grade, rate in config.point_rates(date).items())


def load_members():
    members = {}
    with open("data/members.csv", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            row["grade"] = Grade(row["grade"])
            members[row["id"]] = row
    return members


def save_members(members):
    if not os.path.exists("out"):
        os.mkdir("out")
    with open("out/members.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "birth", "total", "points", "grade"])
        for member in members.values():
            writer.writerow(
                [member["id"], member["name"], member["birth"], member["total"], member["points"], member["grade"].value]
            )


@dataclass
class Settlement:
    """주문 하나를 계산한 결과. member_name이 None이면 비회원."""

    date: str
    amount: int
    paid: int
    member_name: Optional[str] = None
    grade: Optional[Grade] = None
    is_birthday: bool = False
    coupon: int = 0
    use_points: int = 0
    earned: int = 0
    balance: int = 0
    total: int = 0


@dataclass
class DailySummary:
    date: Optional[str]
    order_count: int
    sales: int
    earned_total: int
    grade_counts: dict


class LoyaltyPolicy:
    """주문 계산 규칙(포인트 사용, 생일 쿠폰, 적립)을 묶고, 이번 마감에서 쓴 생일 쿠폰을 기억한다."""

    def __init__(self):
        self.used_coupons = []

    def calculate_order(self, order, members):
        """주문 하나를 계산하고 회원 정보와 쿠폰 사용 기록을 갱신한다."""
        amount = int(order["amount"])
        member_id = order["member_id"]
        if member_id == "":
            return Settlement(date=order["date"], amount=amount, paid=amount)
        member = members[member_id]
        balance = int(member["points"])
        use_points = self.usable_points(int(order["use_points"]), balance)
        is_birthday = self.claim_birthday_coupon(order, member, amount)
        coupon = config.BIRTHDAY_COUPON if is_birthday else 0
        paid = amount - coupon - use_points
        earned = self.earned_points(order["date"], member, amount, paid, is_birthday)
        balance = balance - use_points + earned
        member["points"] = str(balance)
        member["total"] = str(int(member["total"]) + paid)
        member["grade"] = self.upgraded_grade(order["date"], member)
        return Settlement(
            date=order["date"],
            amount=amount,
            paid=paid,
            member_name=member["name"],
            grade=member["grade"],
            is_birthday=is_birthday,
            coupon=coupon,
            use_points=use_points,
            earned=earned,
            balance=balance,
            total=int(member["total"]),
        )

    def upgraded_grade(self, date, member):
        """누적 결제 금액이 올라가면 등급을 올린다. 내리지는 않는다."""
        grades = list(Grade)
        reached = config.grade_for_total(int(member["total"]), date)
        return max(member["grade"], reached, key=grades.index)

    def usable_points(self, use_points, balance):
        if use_points > 0:
            if use_points > balance:
                use_points = balance
            if use_points < config.MIN_USE_POINTS:
                use_points = 0
        return use_points

    def claim_birthday_coupon(self, order, member, amount):
        """생일 쿠폰을 쓸 수 있으면 사용 기록에 남기고 True를 돌려준다."""
        month = order["date"][5:7]
        coupon_key = member["id"] + month
        is_birthday = (
            member["birth"][5:7] == month
            and coupon_key not in self.used_coupons
            and amount >= config.BIRTHDAY_MIN_ORDER
        )
        if is_birthday:
            self.used_coupons.append(coupon_key)
        return is_birthday

    def earned_points(self, date, member, amount, paid, is_birthday):
        # CAFE-5: 생일 쿠폰을 쓴 날은 쿠폰 차감 전 금액으로 적립한다(정책 확정 전이라 그대로 둠)
        earn_base = amount if is_birthday else paid
        earned = int(earn_base * config.point_rates(date)[member["grade"]])
        if date == config.CHRISTMAS_DATE:
            earned = earned * config.CHRISTMAS_MULTIPLIER  # 크리스마스 이벤트
        return earned


def format_receipt(settlement):
    if settlement.member_name is None:
        lines = [
            f"{settlement.date} 비회원",
            f"  주문 금액: {settlement.amount} 원",
            f"  결제 금액: {settlement.paid} 원",
        ]
    else:
        lines = [
            f"{settlement.date} {settlement.member_name} 님 ( {settlement.grade.value} )",
            f"  주문 금액: {settlement.amount} 원",
        ]
        if settlement.is_birthday:
            lines.append(f"  생일 쿠폰: {-settlement.coupon} 원")
        lines += [
            f"  포인트 사용: {-settlement.use_points} 점",
            f"  결제 금액: {settlement.paid} 원",
            f"  적립: {settlement.earned} 점 ({rate_note(settlement.date)})",
            f"  남은 포인트: {settlement.balance} 점",
        ]
        upcoming = config.next_grade(settlement.grade, settlement.date)
        if upcoming is not None:
            remaining = config.GRADE_THRESHOLDS[upcoming] - settlement.total
            lines.append(f"  {upcoming.value}까지 {remaining} 원 남았어요")
    lines.append("-" * 30)
    return "\n".join(lines)


def summarize(settlements, members):
    grade_counts = {grade: 0 for grade in Grade}
    for member in members.values():
        grade_counts[member["grade"]] += 1
    return DailySummary(
        date=settlements[-1].date if settlements else None,
        order_count=len(settlements),
        sales=sum(s.paid for s in settlements),
        earned_total=sum(s.earned for s in settlements),
        grade_counts=grade_counts,
    )


def format_report(summary):
    date = summary.date or config.RATE_SCHEDULE[0][0]
    grade_lines = "".join(
        f"{grade.value} 회원: {summary.grade_counts[grade]}명 (기준 누적 {config.GRADE_THRESHOLDS[grade]}원)\n"
        for grade in config.point_rates(date)
        if config.GRADE_THRESHOLDS[grade] > 0
    )
    return (
        "동네카페 마감 보고\n"
        f"주문 수: {summary.order_count}건\n"
        f"매출: {summary.sales}원\n"
        f"적립 포인트: {summary.earned_total}점\n"
        f"{grade_lines}"
        f"적립률: {rate_note(date)}\n"
    )


def print_header():
    print("=" * 30)
    print("  동네카페 영수증")
    print("=" * 30)


def read_orders():
    with open("data/orders.csv", encoding="utf-8") as orders_file:
        yield from csv.DictReader(orders_file)


def settle_orders(members):
    """주문을 차례로 계산하며 영수증을 찍고, 계산 결과 목록을 돌려준다."""
    policy = LoyaltyPolicy()
    settlements = []
    for order in read_orders():
        settlement = policy.calculate_order(order, members)
        settlements.append(settlement)
        print(format_receipt(settlement))
    return settlements


def write_report(summary):
    with open("out/report.txt", "w", encoding="utf-8") as report:
        report.write(format_report(summary))


def run():
    members = load_members()
    print_header()
    settlements = settle_orders(members)
    save_members(members)
    write_report(summarize(settlements, members))
    print("마감 끝. out/members.csv, out/report.txt 를 확인하세요")


if __name__ == "__main__":
    run()
