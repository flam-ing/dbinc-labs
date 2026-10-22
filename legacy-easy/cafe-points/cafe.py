# -*- coding: utf-8 -*-
# 동네카페 포인트 프로그램
# 2019.03 처음 만듦 (사장님 조카)
# 2020.11 생일 쿠폰 추가
# 2020.12 크리스마스 이벤트 (포인트 두 배)
# 2021.05 등급 enum 만들다 말았음 (grades.py)
# 매일 마감할 때 python3 cafe.py 실행하세요
import csv
import os
import time
from grades import Grade

ADMIN_PASSWORD = "cafe1234"  # 사장님 비번 (바꾸면 키오스크도 바꿔야 함)

maechul = 0  # 오늘 매출 (여기저기서 씀)


def hoewon_bulleogi():
    m = {}
    f = open("data/members.csv", encoding="utf-8")
    r = csv.DictReader(f)
    for row in r:
        m[row["id"]] = row
    f.close()
    return m


def load_members():
    # 회원 불러오기 새 버전 (2021) - 위에 거랑 같은 일인데 일단 둠
    members = {}
    with open("data/members.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            members[row["id"]] = row
    return members


def saveMembers(m):
    if not os.path.exists("out"):
        os.mkdir("out")
    f = open("out/members.csv", "w", encoding="utf-8", newline="")
    w = csv.writer(f)
    w.writerow(["id", "name", "birth", "total", "points", "grade"])
    for k in m:
        a = m[k]
        w.writerow([a["id"], a["name"], a["birth"], a["total"], a["points"], a["grade"]])
    f.close()


def reset_points(password):
    # 관리자용: 모든 회원 포인트를 0으로 (절대 쓰지 마세요)
    if password == ADMIN_PASSWORD:
        m = hoewon_bulleogi()
        for k in m:
            m[k]["points"] = "0"
        saveMembers(m)


def run():
    global maechul
    m = hoewon_bulleogi()
    f = open("data/orders.csv", encoding="utf-8")
    r = csv.DictReader(f)
    gunsu = 0
    jeoklip_hap = 0
    sseun_kupon = []
    print("=" * 30)
    print("  동네카페 영수증")
    print("=" * 30)
    for o in r:
        gunsu = gunsu + 1
        amt = int(o["amount"])
        mid = o["member_id"]
        if mid == "":
            # 비회원
            gyeolje = amt
            maechul = maechul + gyeolje
            print(o["date"], "비회원")
            print("  주문 금액:", amt, "원")
            print("  결제 금액:", gyeolje, "원")
            print("-" * 30)
            continue
        a = m[mid]
        tmp = int(a["points"])
        use = int(o["use_points"])
        if use > 0:
            if use > tmp:
                use = tmp
            if use < 1000:
                use = 0
        mon = o["date"][5:7]
        if a["birth"][5:7] == mon and (mid + mon) not in sseun_kupon and amt >= 5000:
            # 생일 쿠폰
            sseun_kupon.append(mid + mon)
            gyeolje = amt - 3000 - use
            # if a["grade"] == "VIP":
            #     jeoklip = int(amt * 0.05)  # 2019년 VIP 5% (너무 많이 줘서 내림)
            # else:
            #     jeoklip = int(amt * 0.02)
            if a["grade"] == "VIP":
                jeoklip = int(amt * 0.03)
            else:
                jeoklip = int(amt * 0.01)
            if o["date"] == "2020-12-25":
                jeoklip = jeoklip * 2  # 크리스마스 이벤트
            tmp = tmp - use + jeoklip
            a["points"] = str(tmp)
            a["total"] = str(int(a["total"]) + gyeolje)
            if int(a["total"]) >= 100000:
                a["grade"] = "VIP"
            maechul = maechul + gyeolje
            jeoklip_hap = jeoklip_hap + jeoklip
            # print("여기까지 옴!!!!", a)
            print(o["date"], a["name"], "님 (", a["grade"], ")")
            print("  주문 금액:", amt, "원")
            print("  생일 쿠폰: -3000 원")
            print("  포인트 사용:", -use, "점")
            print("  결제 금액:", gyeolje, "원")
            print("  적립:", jeoklip, "점 (일반 1%, VIP 3%)")
            print("  남은 포인트:", tmp, "점")
            if a["grade"] != "VIP":
                print("  VIP까지", 100000 - int(a["total"]), "원 남았어요")
            print("-" * 30)
        else:
            gyeolje = amt - use
            if a["grade"] == "VIP":
                jeoklip = int(gyeolje * 0.03)
            else:
                jeoklip = int(gyeolje * 0.01)
            if o["date"] == "2020-12-25":
                jeoklip = jeoklip * 2  # 크리스마스 이벤트
            tmp = tmp - use + jeoklip
            a["points"] = str(tmp)
            a["total"] = str(int(a["total"]) + gyeolje)
            if int(a["total"]) >= 100000:
                a["grade"] = "VIP"
            maechul = maechul + gyeolje
            jeoklip_hap = jeoklip_hap + jeoklip
            print(o["date"], a["name"], "님 (", a["grade"], ")")
            print("  주문 금액:", amt, "원")
            print("  포인트 사용:", -use, "점")
            print("  결제 금액:", gyeolje, "원")
            print("  적립:", jeoklip, "점 (일반 1%, VIP 3%)")
            print("  남은 포인트:", tmp, "점")
            if a["grade"] != "VIP":
                print("  VIP까지", 100000 - int(a["total"]), "원 남았어요")
            print("-" * 30)
    f.close()
    try:
        saveMembers(m)
    except:
        pass
    time.sleep(1)  # 지우지 마시오!!! (왜인지는 모름)
    v = 0
    for k in m:
        if m[k]["grade"] == Grade.VIP.value:
            v = v + 1
    rep = open("out/report.txt", "w", encoding="utf-8")
    rep.write("동네카페 마감 보고\n")
    rep.write("주문 수: " + str(gunsu) + "건\n")
    rep.write("매출: " + str(maechul) + "원\n")
    rep.write("적립 포인트: " + str(jeoklip_hap) + "점\n")
    rep.write("VIP 회원: " + str(v) + "명 (기준 누적 100000원)\n")
    rep.write("적립률: 일반 1%, VIP 3%\n")
    rep.close()
    print("마감 끝. out/members.csv, out/report.txt 를 확인하세요")


def run2():
    # 새 마감 (2021년에 만들다 말았음. 아직 안 씀)
    members = load_members()
    print("새 마감 준비 중...", len(members), "명")


run()
