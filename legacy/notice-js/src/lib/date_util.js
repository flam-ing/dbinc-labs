// 날짜 유틸
// 2016.04 박준호
//
// 날짜는 "2016-04-20 09:00" 같은 문자열로 주고받음. Date는 안에서만 씀.
// 서버를 옮겨도 똑같이 나오게 UTC 함수만 씀 (getHours 쓰지 말 것!!)

function DateUtil() {
}

// "2016-04-20 09:00" 또는 "2016-04-20T09:00" 을 Date로
DateUtil.prototype.parse = function (str) {
  if (str == null || str == '') return null;
  str = String(str).replace('T', ' ');
  var a = str.split(' ');
  var ymd = a[0].split('-');
  var hm = (a[1] || '00:00').split(':');
  var d = new Date(Date.UTC(parseInt(ymd[0], 10), parseInt(ymd[1], 10) - 1, parseInt(ymd[2], 10),
    parseInt(hm[0], 10), parseInt(hm[1], 10)));
  if (isNaN(d.getTime())) return null;
  return d;
};

// Date를 "2016-04-20 09:00" 으로
DateUtil.prototype.format = function (d) {
  return d.getUTCFullYear() + '-' + this.pad(d.getUTCMonth() + 1) + '-' + this.pad(d.getUTCDate()) +
    ' ' + this.pad(d.getUTCHours()) + ':' + this.pad(d.getUTCMinutes());
};

DateUtil.prototype.pad = function (n) {
  if (n < 10) return '0' + n;
  return '' + n;
};

DateUtil.prototype.is_weekend = function (d) {
  var day = d.getUTCDay();
  return day == 0 || day == 6;
};

// 다음 근무일 아침 9시 (토, 일, 공휴일은 건너뜀)
DateUtil.prototype.next_workday = function (d) {
  var n = new Date(d.getTime() + 86400000);
  while (this.is_weekend(n)) {
    n = new Date(n.getTime() + 86400000);
  }
  n.setUTCHours(9, 0, 0, 0);
  return n;
};

// 업무시간(9시~18시)이면 그대로, 아니면 다음 근무일 9시
DateUtil.prototype.adjust = function (d) {
  if (this.is_weekend(d)) {
    return this.next_workday(d);
  }
  var h = d.getUTCHours();
  if (h < 9) {
    var t = new Date(d.getTime());
    t.setUTCHours(9, 0, 0, 0);
    return t;
  }
  if (h >= 18) {
    return this.next_workday(d);
  }
  return d;
};

// 문자 게이트웨이용 시각 "201604200900"
DateUtil.prototype.to_sms_time = function (d) {
  return this.format(d).replace(/[-: ]/g, '');
};

module.exports = DateUtil;
