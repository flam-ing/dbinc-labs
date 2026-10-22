// 메일 만들기
// 2016.04 박준호

var config = require('../config');
var DateUtil = require('../lib/date_util');

var du = new DateUtil();

function MailBuilder() {
  this.cnt = 0;
  this.delay_cnt = 0;
}

// cb(err, mail)
MailBuilder.prototype.build = function (notice, emp, base, cb) {
  if (!emp.email) {
    cb(new Error('메일 주소 없음 ' + emp.empNo));
    return;
  }

  var subject = '[누리상사 공지] ' + notice.title;
  var send_dt = base;
  if (notice.urgent == true || notice.level == 'urgent') {   // 2019 level 추가
    subject = '[긴급] ' + notice.title;
  } else {
    send_dt = du.adjust(base);
    if (send_dt.getTime() != base.getTime()) this.delay_cnt++;
  }

  // 처음엔 이름 붙였는데 총무팀 요청으로 뺌 (2016.06)
  // var body = emp.name + '님, 안녕하세요.\n\n' + notice.body + config.MAIL_FOOTER;
  var body = notice.body + config.MAIL_FOOTER;

  this.cnt++;
  cb(null, {
    to: emp.empNo,
    address: emp.email,
    channel: 'mail',
    notice: notice.id,
    sendAt: du.format(send_dt),
    subject: subject,
    text: body
  });
};

module.exports = MailBuilder;
