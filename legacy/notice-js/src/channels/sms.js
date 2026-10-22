/**
 * 문자(SMS) 만들기
 * 2019.03 이서연
 *
 * 긴급 공지만 문자로 보내요. 제목만 보내요(본문은 안 보냄).
 */
const DateUtil = require('../lib/date_util');
const du = new DateUtil();

const SMS_MAX = 45;

function makeSms(notice, emp, base) {
  return new Promise((resolve) => {
    let urgent = notice.level === 'urgent' || notice.urgent === true;
    if (!urgent || !emp.phone) {
      resolve(null);
      return;
    }
    let text = '[누리상사] ' + notice.title;
    if (text.length > SMS_MAX) {
      text = text.substr(0, SMS_MAX - 1) + '…';
    }
    // 옛 문자 게이트웨이 (2019.06 발송 게이트웨이로 바뀜)
    // request.post(config.SMS_URL, { form: { key: config.SMS_KEY, to: emp.phone, msg: text } }, function (err) {});
    resolve({
      channel: 'sms',
      notice: notice.id,
      to: emp.empNo,
      address: emp.phone.replace(/-/g, ''),
      sendAt: du.format(base),
      text: text
    });
  });
}

module.exports = makeSms;
