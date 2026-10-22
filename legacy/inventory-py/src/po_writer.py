# -*- coding: utf-8 -*-
#
# po_writer.py  -  발주 파일 (EDI 업로드용) 쓰기
#
#   !!! 열 순서 바꾸지 말것. EDI 에서 위치로 읽음 !!!
#
import io
import os


def write_po(out_dir, today, orders):
    ymd = today.strftime('%Y%m%d')
    fname = 'PO_' + ymd + '.csv'
    path = os.path.join(out_dir, fname)

    # py3: 'wb' 로 열던 것 바꿈. newline='' 안 주면 윈도우에서 줄이 두번 바뀜 (lhe)
    f = io.open(path, 'w', encoding='utf-8', newline='')
    f.write(u'PO_DATE,WH,SKU,ITEM_NAME,SUPPLIER,ORDER_QTY,UNIT_COST,AMOUNT\r\n')
    for o in orders:
        amt = o[4] * o[5]
        line = ymd + ',' + o[0] + ',' + o[1] + ',' + o[2] + ',' + o[3] + ',' + str(o[4]) + ',' + str(o[5]) + ',' + str(amt)
        f.write(line + '\r\n')
    f.write(u'EOF\r\n')
    f.close()
    return fname


def write_po_old(out_dir, today, orders):
    # 2012 버전. EDI 가 cp949 만 받던 때
    path = out_dir + 'PO_' + today.strftime('%Y%m%d') + '.csv'
    f = open(path, 'wb')
    f.write('PO_DATE,WH,SKU,ITEM_NAME,SUPPLIER,ORDER_QTY,UNIT_COST,AMOUNT\r\n')
    for o in orders:
        s = '%s,%s,%s,%s,%s,%d,%d,%d\r\n' % (today.strftime('%Y%m%d'), o[0], o[1], o[2], o[3], o[4], o[5], o[4] * o[5])
        f.write(s.encode('cp949'))
    f.write('EOF\r\n')
    f.close()
