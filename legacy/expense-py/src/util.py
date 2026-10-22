# -*- coding: utf-8 -*-
import datetime


def parse_date(s):
    # 엑셀 업로드 건은 날짜 형식이 제각각이라 다 받아줌
    s = s.strip()
    for fmt in ['%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d', '%Y%m%d']:
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except:
            pass
    return None


def to_num(v):
    # "45,000" / "45000원" 같은 것도 들어옴
    if v is None:
        return 0
    if type(v) == int or type(v) == float:
        return v
    try:
        return float(str(v).replace(',', '').replace('원', '').strip())
    except:
        return 0


def won(n):
    return '{:,}'.format(int(n))


def krw(amount, rate):
    # 원 미만 절사 (재무팀 기준)
    return int(amount * rate)


def days_between(a, b):
    return (b - a).days
