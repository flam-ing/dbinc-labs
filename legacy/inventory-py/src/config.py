# -*- coding: utf-8 -*-
#
# 설정. 서버 옮기면 여기만 고치면 됨
#
OUT_DIR = 'D:\\nuri\\edi\\out\\'
BACKUP_DIR = 'D:\\nuri\\edi\\backup\\'

# EDI (2015 부터 FTP 안 쓰고 아침에 손으로 올림)
EDI_HOST = 'edi.nuri.example'
EDI_USER = 'nuri_po'
EDI_PASS = 'DUMMY-EDI-PASS-0000'

SAFETY_K = 1.5          # 안전재고 계수
REVIEW_DAYS = 7         # 발주 주기 (주 1회)
SALES_DAYS = 30

WAREHOUSES = ['W01', 'W02', 'W03', 'W04']
