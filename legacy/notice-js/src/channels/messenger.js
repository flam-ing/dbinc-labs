'use strict';
/**
 * NuriTalk (messenger) message builder
 * 2022-02 Kim Doyun
 *
 * NuriTalk bot API limit: 500 chars per message.
 */
const holiday = require('../holiday');
const DateUtil = require('../lib/date_util');

const MAX_LENGTH = 500;
const CUT_NOTICE = '\n…(전문은 사내 포털 공지 게시판에서 확인해 주세요)';

class MessengerFormatter {
  constructor() {
    this.sent = new Set();
    this.cutCount = 0;
    this.du = new DateUtil();
  }

  isUrgent(notice) {
    return notice.level?.toLowerCase() === 'urgent' || notice.urgent === true;
  }

  sendTime(notice, base) {
    if (this.isUrgent(notice)) return base;
    if (holiday.isBizTime(base)) return base;
    if (holiday.isBizDay(base) && base.getUTCHours() < 9) {
      const t = new Date(base.getTime());
      t.setUTCHours(9, 0, 0, 0);
      return t;
    }
    return holiday.nextBizDay(base);
  }

  async format(notice, emp, base) {
    // same person listed twice (concurrent position) -> send once
    const key = `${notice.id}/${emp.empNo}`;
    if (this.sent.has(key)) return null;
    this.sent.add(key);

    let text = `[공지] ${notice.title}\n${notice.body}`;
    if (text.length > MAX_LENGTH) {
      text = text.substring(0, MAX_LENGTH - CUT_NOTICE.length) + CUT_NOTICE;
      this.cutCount++;
    }

    return {
      channel: 'messenger',
      notice: notice.id,
      to: emp.empNo,
      address: emp.empNo,
      sendAt: this.du.format(this.sendTime(notice, base)),
      text,
    };
  }
}

module.exports = { MessengerFormatter, MAX_LENGTH };
