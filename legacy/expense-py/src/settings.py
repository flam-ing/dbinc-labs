# -*- coding: utf-8 -*-
#
# 출장비 정산 배치 설정 (운영 서버 기준)
# 규정 바뀌면 여기 표만 고치면 됨  - 김도윤 2019.04
#

CONFIG = {
    'smtp_host': 'smtp.nuri.example',
    'smtp_port': 25,
    'smtp_user': 'expense-bot',
    'smtp_pass': 'DUMMY-SMTP-PASS-1234',
    'mail_from': 'expense-bot@nuri.example',
    'finance_cc': 'travel-desk@nuri.example',
    'out_dir': 'C:/expense/out',
    'audit_file': 'C:/expense/out/audit.log',
    'deadline_days': 30,
    'no_receipt_limit': 30000,      # 2019.03 규정 개정 (2만 -> 3만)
    'run_date': None,
}

# 국내 일비 (원/일)
PER_DIEM_KRW = {
    '사원': 20000,
    '대리': 20000,
    '과장': 25000,
    '차장': 25000,
    '부장': 30000,
}

# 해외 일비 (USD/일)
PER_DIEM_USD = {
    '사원': 40,
    '대리': 40,
    '과장': 40,
    '차장': 40,
    '부장': 50,
}

EXEC_GRADES = ['상무', '전무', '부사장', '사장']
EXEC_PER_DIEM_KRW = 40000
EXEC_PER_DIEM_USD = 70

# 숙박 상한 (1박)
LODGING_KRW = {'A': 100000, 'B': 70000}
A_CITIES = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종']

LODGING_USD = {1: 250, 2: 180, 3: 150}
CITY_GRADE = {
    '뉴욕': 1, '런던': 1, '파리': 1, '도쿄': 1, '싱가포르': 1, '홍콩': 1,
    '상하이': 2, '베이징': 2, '오사카': 2, '프랑크푸르트': 2, 'LA': 2,
    '하노이': 3, '호찌민': 3, '자카르타': 3, '방콕': 3,
}
