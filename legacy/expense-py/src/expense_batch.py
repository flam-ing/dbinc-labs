# -*- coding: utf-8 -*-
"""
출장비 정산 배치

    python expense_batch.py <신청서 폴더> <환율 json> <정산일> [출력 폴더]

매월 15일, 말일 18:00 (재무팀 배치 서버, 작업 스케줄러 EXP_SETTLE)

2019-04-22  김도윤  처음 만듦
2019-06-10  김도윤  중복 신청 막기, 파일 순서 정렬
2019-11-08  윤서아  메일 -> outbox 폴더
2020-03-16  윤서아  해외 환율 출발일 기준 (FIN-212)
"""
import os
import sys
import json

from settings import *
from util import *
import fx
import mailer

SEEN = {}       # 중복 신청 확인용  사번/출발일 -> 신청번호


def main():
    if len(sys.argv) < 4:
        print('사용법: python expense_batch.py <신청서 폴더> <환율 json> <정산일 YYYY-MM-DD> [출력 폴더]')
        sys.exit(1)

    run_date = parse_date(sys.argv[3])
    if run_date is None:
        print('정산일을 읽을 수 없음: ' + sys.argv[3])
        sys.exit(3)
    CONFIG['run_date'] = run_date

    if len(sys.argv) > 4:
        CONFIG['out_dir'] = sys.argv[4]
        CONFIG['audit_file'] = os.path.join(sys.argv[4], 'audit.log')

    if not os.path.isdir(sys.argv[1]):
        print('신청서 폴더 없음: ' + sys.argv[1])
        sys.exit(2)
    if not os.path.isfile(sys.argv[2]):
        print('환율 파일 없음: ' + sys.argv[2])
        sys.exit(2)
    if not os.path.isdir(CONFIG['out_dir']):
        print('출력 폴더 없음: ' + CONFIG['out_dir'])
        sys.exit(2)

    fx.load(sys.argv[2])
    process(sys.argv[1])


def process(req_dir):
    run_date = CONFIG['run_date']
    ymd = run_date.strftime('%Y-%m-%d')

    files = [x for x in os.listdir(req_dir) if x.lower().endswith('.json')]
    files.sort()        # 서버마다 순서가 달라서 정렬 (2019-06 dy)

    audit = open(CONFIG['audit_file'], 'a', encoding='utf-8')
    audit.write(ymd + '|BATCH|START|' + str(len(files)) + '\n')

    print('출장비 정산 배치   정산일 ' + ymd)
    print('-' * 64)

    rows = []
    cnt_read = 0
    cnt_fail = 0
    cnt_ok = 0
    cnt_ng = 0
    sum_ok = 0
    by_line = {}

    for fn in files:
        if not fn.endswith(".json"):
            continue

        # ---------- 1. 읽기 ----------
        try:
            f = open(os.path.join(req_dir, fn), encoding='utf-8')
            req = json.load(f)
            f.close()
        except:
            print('  ! 읽기 실패 ' + fn)
            audit.write(ymd + '|' + fn + '|-|READ_FAIL|0|-\n')
            cnt_fail += 1
            continue
        cnt_read += 1

        req_id = req.get('req_id') or fn.replace('.json', '')
        emp_no = str(req.get('emp_no', '')).strip()
        name = req.get('name', '')
        grade = str(req.get('grade', '')).strip()
        trip = str(req.get('trip_type', 'DOMESTIC')).upper()
        city = req.get('city', '')
        dep = parse_date(str(req.get('depart', '')))
        ret = parse_date(str(req.get('return', '')))
        is_exec = grade in EXEC_GRADES

        status = 'OK'
        reason = ''
        days = 0
        nights = 0
        per_diem = 0
        hotel = 0
        hotel_ok = 0
        trans = 0
        etc = 0
        no_rcpt = 0
        no_rcpt_ok = 0
        usd = None

        # ---------- 2. 검사 ----------
        if dep == None or ret == None:
            status = 'NG'
            reason = '날짜 없음'
        elif ret < dep:
            status = 'NG'
            reason = '일정 오류'
        elif (run_date - ret).days > CONFIG['deadline_days']:
            status = 'NG'
            reason = '신청 기한 지남'
        elif not grade in PER_DIEM_KRW and not is_exec:
            status = 'NG'
            reason = '직급 확인 필요'

        key = emp_no + '/' + str(dep)
        if status == 'OK':
            if key in SEEN:
                status = 'NG'
                reason = '중복 신청(' + SEEN[key] + ')'
            else:
                SEEN[key] = req_id

        if status == 'OK':
            days = (ret - dep).days + 1
            nights = days - 1
            # 15일 넘는 장기 출장은 사전 승인 번호 필요 -> 2019.06 규정에서 빠짐
            # if days > 14 and not req.get('pre_approval'):
            #     status = 'NG'
            #     reason = '사전 승인 없음'
            if trip == 'OVERSEAS':
                usd = fx.get_rate('USD', dep)
                if usd is None:
                    status = 'NG'
                    reason = '환율 없음(USD)'

        # ---------- 3. 일비 ----------
        if status == 'OK':
            if trip == 'DOMESTIC':
                if is_exec:
                    pd = EXEC_PER_DIEM_KRW
                else:
                    pd = PER_DIEM_KRW[grade]
                if days == 1:
                    per_diem = int(pd * 0.5)        # 당일 출장
                else:
                    per_diem = pd * days
            else:
                if is_exec:
                    pd = EXEC_PER_DIEM_USD
                else:
                    pd = PER_DIEM_USD[grade]
                per_diem = round(pd * days * usd)

        # ---------- 4. 영수증 ----------
        if status == 'OK':
            for r in req.get('receipts', []):
                cur = str(r.get('currency', 'KRW')).upper()
                # rate = fx.get_rate(cur, parse_date(r['date']))     # 영수증 날짜 기준 (~2020.03)
                rate = fx.get_rate(cur, dep)                          # 출발일 기준 FIN-212
                if rate is None:
                    status = 'NG'
                    reason = '환율 없음(' + cur + ')'
                    break
                amt = int(to_num(r.get('amount')) * rate)
                kind = str(r.get('type', 'ETC')).upper()
                # print(req_id, kind, cur, rate, amt)
                if not r.get('receipt', True):
                    no_rcpt += amt
                elif kind == 'HOTEL':
                    hotel += amt
                elif kind in ('AIR', 'TRAIN', 'BUS', 'TAXI', 'CAR'):
                    trans += amt
                else:
                    etc += amt

        # ---------- 5. 한도 ----------
        if status == 'OK':
            if is_exec:
                hotel_ok = hotel        # 임원은 실비
            elif trip == 'DOMESTIC':
                if city in A_CITIES:
                    cap = LODGING_KRW['A'] * nights
                else:
                    cap = LODGING_KRW['B'] * nights
                hotel_ok = min(hotel, cap)
            else:
                cap = int(LODGING_USD[CITY_GRADE.get(city, 3)] * nights * usd)
                hotel_ok = min(hotel, cap)

            if no_rcpt > CONFIG['no_receipt_limit']:
                no_rcpt_ok = CONFIG['no_receipt_limit']
            else:
                no_rcpt_ok = no_rcpt

        ok_amt = per_diem + hotel_ok + trans + etc + no_rcpt_ok
        ng_amt = (hotel - hotel_ok) + (no_rcpt - no_rcpt_ok)
        if status != 'OK':
            ok_amt = 0
            ng_amt = 0

        # ---------- 6. 결재선 ----------
        # 전결 규정: 100만 이하 팀장 / 300만 이하 본부장 / 그 위 재무이사
        line = ''
        if status == 'OK':
            if is_exec:
                line = '대표이사'
            elif ok_amt <= 1000000:
                line = '팀장'
            elif ok_amt <= 3000000:
                line = '팀장>본부장'
            else:
                line = '팀장>본부장>재무이사'
            if trip == 'OVERSEAS' and line == '팀장':
                line = '팀장>본부장'           # 해외는 본부장까지

        # ---------- 7. 결과 줄 ----------
        if status == 'OK':
            st = '정산완료'
            cnt_ok += 1
            sum_ok += ok_amt
            by_line[line] = by_line.get(line, 0) + 1
        else:
            st = '반려'
            cnt_ng += 1
            per_diem = hotel_ok = trans = etc = no_rcpt_ok = 0
        if trip == 'DOMESTIC':
            trip_k = '국내'
        else:
            trip_k = '해외'
        rows.append([req_id, emp_no, name, grade, trip_k, days, per_diem, hotel_ok, trans, etc,
                     no_rcpt_ok, ok_amt, ng_amt, line, st, reason])

        # ---------- 8. 메일 ----------
        html = mailer.HEAD
        html += '<p>' + name + ' 님, 출장비 정산 결과를 알려 드립니다.</p>\n'
        html += '<table border="1" cellpadding="4" style="border-collapse:collapse">\n'
        html += '<tr><th>신청번호</th><td>' + req_id + '</td></tr>\n'
        html += '<tr><th>출장</th><td>' + trip_k + ' ' + city + ' (' + str(dep) + ' ~ ' + str(ret) + ')</td></tr>\n'
        if status == 'OK':
            html += '<tr><th>일비</th><td align="right">' + won(per_diem) + '</td></tr>\n'
            html += '<tr><th>숙박</th><td align="right">' + won(hotel_ok) + '</td></tr>\n'
            html += '<tr><th>교통</th><td align="right">' + won(trans) + '</td></tr>\n'
            html += '<tr><th>기타</th><td align="right">' + won(etc + no_rcpt_ok) + '</td></tr>\n'
            html += '<tr><th>지급 합계</th><td align="right"><b>' + won(ok_amt) + '</b></td></tr>\n'
            if ng_amt > 0:
                html += '<tr><th>불인정</th><td align="right" style="color:red">' + won(ng_amt) + '</td></tr>\n'
            html += '<tr><th>결재</th><td>' + line.replace('>', ' &gt; ') + '</td></tr>\n'
        else:
            html += '<tr><th>결과</th><td style="color:red">반려 - ' + reason + '</td></tr>\n'
        html += '</table>\n'
        if req.get('memo'):
            html += '<p>신청 메모: ' + req.get('memo') + '</p>\n'
        html += mailer.TAIL

        subject = '[출장비] ' + req_id + ' ' + st
        mailer.send(emp_no.lower() + '@nuri.example', [CONFIG['finance_cc']], subject, html, req_id)

        # ---------- 9. 감사 로그 ----------
        if status == 'OK':
            audit.write('%s|%s|%s|SETTLED|%d|%s\n' % (ymd, req_id, emp_no, ok_amt, line))
        else:
            audit.write('%s|%s|%s|REJECTED|0|%s\n' % (ymd, req_id, emp_no, reason))

        # ---------- 10. 화면 ----------
        print('%-13s %-4s %s %-5s %12s  %s' % (req_id, name, trip_k, st, won(ok_amt), line if status == 'OK' else reason))

    audit.write(f'{ymd}|BATCH|END|ok={cnt_ok},ng={cnt_ng},fail={cnt_fail}\n')
    audit.close()

    # ---------- 결과 파일 ----------
    out_name = 'settlement_' + run_date.strftime('%Y%m%d') + '.csv'
    out = open(os.path.join(CONFIG['out_dir'], out_name), 'w', encoding='utf-8-sig')    # 엑셀에서 한글 깨져서 (FIN-142)
    out.write('req_id,emp_no,name,grade,type,days,per_diem,lodging,transport,etc,no_receipt,approved,rejected,approval,status,reason\n')
    for r in rows:
        out.write(','.join([str(x) for x in r]) + '\n')
    out.close()

    print('-' * 64)
    print('읽음 %d건 / 읽기 실패 %d건' % (cnt_read, cnt_fail))
    print('정산완료 %d건  지급 합계 %s원' % (cnt_ok, won(sum_ok)))
    print('반려 %d건' % cnt_ng)
    print('결재선  ' + '  '.join([k + ' ' + str(by_line.get(k, 0)) for k in ['팀장', '팀장>본부장', '팀장>본부장>재무이사', '대표이사']]))
    print('결과 파일 ' + out_name + ' / 메일 ' + str(cnt_read) + '통')


if __name__ == '__main__':
    main()
