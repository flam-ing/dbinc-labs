# -*- coding: utf-8 -*-
# 동네카페 포인트 프로그램 (2일차 4교시 버그 실습판)
# 1일차에 본 카페 포인트 코드를 읽기 쉽게 조금 정리했어요.
# 교육용으로 버그를 일부러 넣었어요. 무엇이 버그인지는 수업 중에 이슈로 와요.
# 매일 마감할 때 실행해요. Windows는 py cafe.py, Mac은 python3 cafe.py
import csv
import os

VIP_GIJUN = 100000   # 누적 결제가 이 금액 이상이면 VIP
SAENGIL_KUPON = 3000  # 생일 쿠폰 (생일 달 첫 주문, 5,000원 이상)
CHOESO_SAYONG = 1000  # 포인트는 1,000점부터 써요


def load_members():
    members = {}
    with open("data/members.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            members[row["id"]] = row
    return members


def save_members(members):
    os.makedirs("out", exist_ok=True)
    with open("out/members.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "birth", "total", "points", "grade"])
        for a in members.values():
            w.writerow([a["id"], a["name"], a["birth"], a["total"], a["points"], a["grade"]])


def jeoklip_gyesan(gyeolje, grade):
    # 결제 금액의 1%를 쌓아요. VIP는 3%예요. 1점 미만은 버려요.
    if grade == "vip":
        return gyeolje * 3 // 100
    return gyeolje * 1 // 100


def run():
    members = load_members()
    maechul = 0
    gunsu = 0
    jeoklip_hap = 0
    sseun_kupon = []  # 생일 쿠폰을 이미 쓴 회원 (회원번호 + 월)
    print("=" * 30)
    print("  동네카페 영수증")
    print("=" * 30)
    with open("data/orders.csv", encoding="utf-8") as f:
        for o in csv.DictReader(f):
            gunsu = gunsu + 1
            amt = int(o["amount"])
            mid = o["member_id"]
            if mid == "":
                # 비회원
                maechul = maechul + amt
                print(o["date"], "비회원")
                print("  결제 금액:", amt, "원")
                print("-" * 30)
                continue
            a = members[mid]
            points = int(a["points"])
            use = int(o["use_points"])
            if use > points:
                use = points
            if use < CHOESO_SAYONG:
                use = 0
            kupon = 0
            mon = o["date"][5:7]
            if a["birth"][5:7] == mon and (mid + mon) not in sseun_kupon and amt >= 5000:
                kupon = SAENGIL_KUPON
            gyeolje = amt - kupon - use
            jeoklip = jeoklip_gyesan(gyeolje, a["grade"])
            points = points - use + jeoklip
            a["points"] = str(points)
            a["total"] = str(int(a["total"]) + gyeolje)
            if int(a["total"]) > VIP_GIJUN:
                a["grade"] = "VIP"
            maechul = maechul + gyeolje
            jeoklip_hap = jeoklip_hap + jeoklip
            print(o["date"], a["name"], "님 (", a["grade"], ")")
            print("  주문 금액:", amt, "원")
            if kupon > 0:
                print("  생일 쿠폰:", -kupon, "원")
            print("  포인트 사용:", -use, "점")
            print("  결제 금액:", gyeolje, "원")
            print("  적립:", jeoklip, "점 (일반 1%, VIP 3%)")
            print("  남은 포인트:", points, "점")
            if a["grade"] != "VIP":
                print("  VIP까지", VIP_GIJUN - int(a["total"]), "원 남았어요")
            print("-" * 30)
    save_members(members)
    vip = 0
    for a in members.values():
        if a["grade"] == "VIP":
            vip = vip + 1
    with open("out/report.txt", "w", encoding="utf-8") as rep:
        rep.write("동네카페 마감 보고\n")
        rep.write("주문 수: " + str(gunsu) + "건\n")
        rep.write("매출: " + str(maechul) + "원\n")
        rep.write("적립 포인트: " + str(jeoklip_hap) + "점\n")
        rep.write("VIP 회원: " + str(vip) + "명 (기준 누적 " + str(VIP_GIJUN) + "원 이상)\n")
    print("마감 끝. out/members.csv, out/report.txt 를 확인하세요")


if __name__ == "__main__":
    run()
