# -*- coding: utf-8 -*-
#
# invlib.py  -  재고 발주 공통 (파일 읽기, 전역 자료)
#
#   STOCK  : 'W01|A-1001' -> {wh, sku, name, qty, use_yn}
#   SALES  : 'W01|A-1001' -> 최근 30일 판매 합
#   SUPP   : 'A-1001'     -> {sup, lead, moq, cost}
#   ORDERS : [창고, 상품, 상품명, 공급처, 수량, 단가] 목록
#
from __future__ import print_function

import io
import csv
import datetime

try:
    unicode
except NameError:
    unicode = str     # py3 (2015.09 lhe)


STOCK = {}
SALES = {}
SUPP = {}
ORDERS = []
CNT = {'sample': 0, 'disc': 0, 'nosupp': 0}
BAD_LINES = 0


def load_stock(path):
    # 재고 시스템에서 내려받은 csv. 상품명에 쉼표 있어서 csv 모듈 씀
    f = io.open(path, 'r', encoding='utf-8')
    rd = csv.reader(f)
    first = True
    for r in rd:
        if first:
            first = False
            continue
        if len(r) < 5:
            continue
        k = r[0] + '|' + r[1]
        try:
            q = int(r[3])
        except:
            q = 0
        STOCK[k] = {'wh': r[0], 'sku': r[1], 'name': unicode(r[2]), 'qty': q,
                    'use_yn': r[4].strip().upper()}
    f.close()


def load_sales(path, today):
    global BAD_LINES
    # 기준일 전날까지 30일. 날짜는 yyyy-mm-dd 로만 오니까 문자열로 비교
    d_from = (today - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    d_to = today.strftime('%Y-%m-%d')

    f = io.open(path, 'r', encoding='utf-8')
    n = 0
    for line in f:
        n = n + 1
        if n == 1:
            continue          # 헤더
        line = line.strip()
        if line == '':
            continue
        try:
            c = line.split(',')
            d = c[0].strip()
            if d < d_from or d >= d_to:
                continue
            q = int(c[3])
            if q <= 0:
                continue      # 반품은 안 뺌
            k = c[1] + '|' + c[2]
            #if SALES.has_key(k):
            if k in SALES:
                SALES[k] = SALES[k] + q
            else:
                SALES[k] = q
        except:
            BAD_LINES = BAD_LINES + 1
    f.close()


def load_supp(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    for line in lines[1:]:
        c = line.strip().split(',')
        if len(c) < 5:
            continue
        try:
            lead = int(c[2])
        except:
            lead = 7          # 모르면 1주
        SUPP[c[0]] = {'sup': c[1], 'lead': lead, 'moq': int(c[3]), 'cost': int(c[4])}


def wh_name(code):
    if code == 'W01':
        return u'이천'
    elif code == 'W02':
        return u'부산'
    elif code == 'W03':
        return u'제주'
    elif code == 'W04':
        return u'대전'
    return code


def dump_debug():
    # 구매팀이 숫자 이상하다고 할때 돌려봄
    f = io.open('C:\\temp\\inv_debug.txt', 'w', encoding='utf-8')
    for k, v in STOCK.items():      # iteritems -> items (py3)
        f.write(u'%s %s %s\n' % (k, v['qty'], SALES.get(k, 0)))
    f.close()
    #print "debug written"
