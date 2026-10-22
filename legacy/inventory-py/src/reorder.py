#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# reorder.py  -  창고 재고 보고 발주 목록 만들기
#
#   매일 07:00 자동 (작업 스케줄러 INV_REORDER, 배치서버 2호기)
#   결과 파일은 EDI 로 공급처에 올라감
#
#   2012.03.05  최지훈  처음 만듦 (이천만)
#   2013.07.22  최지훈  부산 창고 추가
#   2014.02.17  최지훈  제주 창고 추가, 안전재고 계수 바꿈
#   2015.09.21  이하은  python 3 으로 옮김
#   2016.04.11  이하은  S03 박스 단위
#   2018.11.05  박준서  제주 리드타임
#
from __future__ import print_function
from __future__ import division

import sys
import os
import io
import math
import datetime

from invlib import *
import po_writer
import config

#reload(sys)
#sys.setdefaultencoding('utf-8')      # py2 때 한글 때문에 넣었던 것. py3 에서는 에러남

if sys.version_info[0] >= 3:
    # 서버 콘솔에서 한글 깨져서 넣음. 지우지 말것 (lhe)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def print_line(wh, sku, qty, avg, ss, rop, q, sup):
    if q == 0:
        q = '-'
    print('%-4s %-9s %5d %7.2f %5d %6d %5s   %s' % (wh, sku, qty, avg, int(math.ceil(ss)), int(math.ceil(rop)), q, sup))


def calc(today):
    # 창고마다 조금씩 달라서 따로 씀
    for k in sorted(STOCK.keys()):
        row = STOCK[k]
        wh = row['wh']
        sku = row['sku']

        # 샘플, 증정품은 발주 안함
        if sku[:2] == 'X-':
            CNT['sample'] = CNT['sample'] + 1
            continue

        #------------------------------------------------------------
        # 이천 (본창고)
        #------------------------------------------------------------
        if wh == 'W01':
            # 단종 제외
            if row['use_yn'] == 'N':
                CNT['disc'] += 1
                continue
            total = SALES.get(k, 0)
            avg = total // 30          # 예전 리포트랑 숫자 맞춤
            try:
                s = SUPP[sku]
            except:
                print('  ** 공급처 없음 %s %s' % (wh, sku))
                CNT['nosupp'] += 1
                continue
            lt = s['lead']
            ss = avg * lt * 1.65
            rop = avg * lt + ss
            if row['qty'] > rop:
                print_line(wh, sku, row['qty'], avg, ss, rop, 0, s['sup'])
                continue
            need = rop + avg * 7 - row['qty']
            q = int(math.ceil(need))
            if q < s['moq']:
                q = s['moq']
            if s['sup'] == 'S03':
                # 박스 단위로만 받음 (2016.04)
                q = int(math.ceil(q / s['moq'])) * s['moq']
            ORDERS.append([wh, sku, row['name'], s['sup'], q, s['cost']])
            print_line(wh, sku, row['qty'], avg, ss, rop, q, s['sup'])

        #------------------------------------------------------------
        # 부산
        #------------------------------------------------------------
        elif wh == 'W02':
            # 단종 제외
            total = SALES.get(k, 0)
            avg = total / 30
            try:
                s = SUPP[sku]
            except:
                print('  ** 공급처 없음 %s %s' % (wh, sku))
                CNT['nosupp'] += 1
                continue
            lt = s['lead'] + 1         # 이천에서 한번 더 싣고 감
            ss = avg * lt * 1.65
            rop = avg * lt + ss
            if row['qty'] > rop:
                print_line(wh, sku, row['qty'], avg, ss, rop, 0, s['sup'])
                continue
            need = rop + avg * 7 - row['qty']
            q = int(math.ceil(need))
            if q < s['moq']:
                q = s['moq']
            if s['sup'] == 'S03':
                q = (q + s['moq'] - 1) // s['moq'] * s['moq']
            ORDERS.append([wh, sku, row['name'], s['sup'], q, s['cost']])
            print_line(wh, sku, row['qty'], avg, ss, rop, q, s['sup'])

        #------------------------------------------------------------
        # 제주
        #------------------------------------------------------------
        elif wh == 'W03':
            # 단종 제외
            if row['use_yn'] == 'N':
                CNT['disc'] += 1
                continue
            total = SALES.get(k, 0)
            avg = total / 30.0
            try:
                s = SUPP[sku]
            except:
                print(f'  ** 공급처 없음 {wh} {sku}')
                CNT['nosupp'] += 1
                continue
            lt = s['lead'] + 3         # 배편. 2 -> 3 (2018.11 pjs)
            ss = avg * lt * 1.65
            rop = avg * lt + ss
            if row['qty'] > rop:
                print_line(wh, sku, row['qty'], avg, ss, rop, 0, s['sup'])
                continue
            need = rop + avg * 7 - row['qty']
            q = int(math.ceil(need))
            if q < s['moq']:
                q = s['moq']
            if s['sup'] == 'S03':
                q = int(math.ceil(q / s['moq'])) * s['moq']
            ORDERS.append([wh, sku, row['name'], s['sup'], q, s['cost']])
            print_line(wh, sku, row['qty'], avg, ss, rop, q, s['sup'])

        else:
            # W04 대전은 2014.12 폐쇄
            #print "unknown wh", wh
            pass


def main():
    if len(sys.argv) < 5:
        print('사용법: python reorder.py <재고.csv> <판매.csv> <공급처.csv> <기준일 YYYY-MM-DD> [출력폴더]')
        sys.exit(1)

    try:
        today = datetime.datetime.strptime(sys.argv[4], '%Y-%m-%d')
    except:
        print('기준일이 이상합니다: ' + sys.argv[4])
        sys.exit(3)

    out_dir = config.OUT_DIR
    if len(sys.argv) >= 6:
        out_dir = sys.argv[5]

    for f in sys.argv[1:4]:
        if not os.path.exists(f):
            print('파일 없음: %s' % f)
            sys.exit(2)
    if not os.path.isdir(out_dir):
        print('출력 폴더 없음: %s' % out_dir)
        sys.exit(2)

    load_stock(sys.argv[1])
    load_sales(sys.argv[2], today)
    load_supp(sys.argv[3])

    d1 = today - datetime.timedelta(days=30)
    d2 = today - datetime.timedelta(days=1)
    print('=' * 60)
    print(' 재고 발주 리포트    기준일 ' + today.strftime('%Y-%m-%d'))
    print(' 판매 집계 %s ~ %s (30일)' % (d1.strftime('%Y-%m-%d'), d2.strftime('%Y-%m-%d')))
    print('=' * 60)
    print('WH   SKU        재고  일평균  안전 발주점  발주   공급처')
    print('-' * 60)

    calc(today)

    print('-' * 60)
    n1 = n2 = n3 = 0
    tot_q = 0
    tot_amt = 0
    for o in ORDERS:
        if o[0] == 'W01': n1 += 1
        if o[0] == 'W02': n2 += 1
        if o[0] == 'W03': n3 += 1
        tot_q = tot_q + o[4]
        tot_amt = tot_amt + o[4] * o[5]
    print('창고별 발주  이천 %d건 / 부산 %d건 / 제주 %d건' % (n1, n2, n3))
    print(f'발주 합계  {len(ORDERS)}건  {tot_q:,}개  {tot_amt:,}원')
    print('제외  샘플 %d / 단종 %d / 공급처 없음 %d' % (CNT['sample'], CNT['disc'], CNT['nosupp']))
    print('판매자료 오류 %d줄' % BAD_LINES)

    fname = po_writer.write_po(out_dir, today, ORDERS)
    print('발주 파일  ' + fname)


if __name__ == '__main__':
    main()
