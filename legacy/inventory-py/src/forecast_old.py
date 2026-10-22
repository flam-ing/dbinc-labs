# -*- coding: utf-8 -*-
#
# 수요예측 (지수평활) - 2013.10 시험중. 아직 안씀!!
# 컨설팅 때 받은 엑셀 공식 옮김. 숫자가 이상하게 나와서 보류 -cjh
#
from __future__ import print_function

ALPHA = 0.3
MIN_DAYS = 14


def calcForecast(salesList, alpha=ALPHA):
    if len(salesList) == 0:
        return 0
    f = salesList[0]
    for x in salesList[1:]:
        f = alpha * x + (1 - alpha) * f
    return f


def forecastAll(salesByDay):
    result = {}
    for key in salesByDay.keys():
        if len(salesByDay[key]) < MIN_DAYS:
            result[key] = None
            continue
        result[key] = calcForecast(salesByDay[key])
    return result


#def main():
#    import invlib
#    invlib.load_sales_by_day('D:\\nuri\\pos\\sales_90d.csv')
#    r = forecastAll(invlib.SALES_BY_DAY)
#    for k in sorted(r.keys()):
#        print k, r[k]
#
#if __name__ == '__main__':
#    main()
