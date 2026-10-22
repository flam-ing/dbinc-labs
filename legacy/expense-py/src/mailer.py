# -*- coding: utf-8 -*-
#
# 메일 보내기
#   2019.11 배치 서버에서 SMTP 로 바로 나가는 게 막혀서 outbox 폴더에 떨굼.
#   메일 에이전트가 5분마다 가져가서 보냄  - 윤서아
#
import os
# import smtplib
# from email.mime.text import MIMEText

from settings import CONFIG

HEAD = '<html><head><meta charset="utf-8"><title>출장비 정산</title></head>\n<body style="font-family:\'맑은 고딕\',sans-serif">\n'
TAIL = '<p style="color:#888">본 메일은 발신 전용입니다. 문의: 재무팀 출장비 담당 (내선 3120)</p>\n</body></html>\n'


def send(to, cc, subject, html, req_id):
    # msg = MIMEText(html, 'html', 'utf-8')
    # msg['Subject'] = subject
    # msg['From'] = CONFIG['mail_from']
    # msg['To'] = to
    # msg['Cc'] = ','.join(cc)
    # s = smtplib.SMTP(CONFIG['smtp_host'], CONFIG['smtp_port'])
    # s.login(CONFIG['smtp_user'], CONFIG['smtp_pass'])
    # s.sendmail(CONFIG['mail_from'], [to] + cc, msg.as_string())
    # s.quit()
    d = os.path.join(CONFIG['out_dir'], 'outbox')
    if not os.path.exists(d):
        os.mkdir(d)
    f = open(os.path.join(d, req_id + '.html'), 'w', encoding='utf-8')
    f.write('From: ' + CONFIG['mail_from'] + '\n')
    f.write('To: ' + to + '\n')
    f.write('Cc: ' + ','.join(cc) + '\n')
    f.write('Subject: ' + subject + '\n')
    f.write('X-Relay: ' + CONFIG['smtp_host'] + ':' + str(CONFIG['smtp_port']) + '\n')
    f.write('\n')
    f.write(html)
    f.close()
    return True
