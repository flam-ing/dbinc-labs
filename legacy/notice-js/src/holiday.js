/**
 * 공휴일 처리
 * 2019.03 이서연
 *
 * date_util.next_workday가 공휴일을 몰라서 새로 만들었어요.
 * 쪽지 알림은 이걸 쓰고, 메일은 나중에 바꿀 예정.
 */
const fs = require('fs');
const config = require('./config');

let holidays = [];

/**
 * 휴일 파일 읽기  [{ "date": "2019-03-01", "name": "삼일절" }, ...]
 * @param {string} file
 * @returns {Promise<string[]>}
 */
function loadHolidays(file) {
  return new Promise((resolve, reject) => {
    fs.readFile(file, 'utf8', (err, text) => {
      if (err) {
        reject(err);
        return;
      }
      let list = JSON.parse(text);
      holidays = list.map(h => h.date);
      config.holidays = holidays;   // 다른 파일에서도 쓸 수 있게
      resolve(holidays);
    });
  });
}

function toYmd(d) {
  return d.toISOString().slice(0, 10);
}

function isHoliday(d) {
  return holidays.indexOf(toYmd(d)) !== -1;
}

function isBizDay(d) {
  let day = d.getUTCDay();
  if (day === 0 || day === 6) {
    return false;
  }
  return !isHoliday(d);
}

function isBizTime(d) {
  let h = d.getUTCHours();
  return isBizDay(d) && h >= 9 && h < 18;
}

/**
 * 다음 영업일 9시
 * 휴일 다음 날이 주말이면 한 번 더 넘겨요. 연휴도 이걸로 돼요.
 */
function nextBizDay(d) {
  let next = new Date(d.getTime() + 24 * 60 * 60 * 1000);
  if (isHoliday(next)) {
    next = new Date(next.getTime() + 24 * 60 * 60 * 1000);
  }
  if (next.getUTCDay() === 6) {
    next = new Date(next.getTime() + 2 * 24 * 60 * 60 * 1000);
  } else if (next.getUTCDay() === 0) {
    next = new Date(next.getTime() + 24 * 60 * 60 * 1000);
  }
  next.setUTCHours(9, 0, 0, 0);
  return next;
}

module.exports = {
  loadHolidays: loadHolidays,
  isHoliday: isHoliday,
  isBizDay: isBizDay,
  isBizTime: isBizTime,
  nextBizDay: nextBizDay
};
