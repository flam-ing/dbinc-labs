# -*- coding: utf-8 -*-
#
# 환율
#   자금 담당이 매일 아침 매매기준율을 json 으로 올려줌
#   {"2019-06-03": {"USD": 1182.5, "JPY": 1093.42, "EUR": 1325.1, "CNY": 171.2}, ...}
#
import json
import datetime

RATES = {}


def load(path):
    global RATES
    f = open(path, encoding='utf-8')
    RATES = json.load(f)
    f.close()


def get_rate(cur, d):
    if cur == 'KRW' or cur == '':
        return 1.0
    # 주말, 공휴일은 환율이 없어서 앞 날짜로 감 (최대 5일, 설/추석)
    for i in range(6):
        k = (d - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        if k in RATES:
            if cur in RATES[k]:
                r = RATES[k][cur]
                if cur == 'JPY':
                    r = r / 100
                return r
    return None


def get_rate_by_receipt(receipt):
    # 예전 방식 - 영수증 날짜 환율 (2020.03 까지). 지금 안씀
    try:
        d = datetime.datetime.strptime(receipt['date'], '%Y-%m-%d').date()
        return get_rate(receipt.get('currency', 'KRW'), d)
    except Exception as e:
        print(e)
        return None
