// 누리상사 사내 공지 알림 봇
// 2016.04 박준호 (총무팀 시스템)
// 2019.03 이서연  공휴일, 쪽지, 문자 추가 / 2019.06 요약 파일
// 2022.02 김도윤  쪽지를 누리톡(메신저)으로 바꿈, outbox 클래스로 바꿈
//
// 사용법: node src/bot.js <공지.json> <직원.json> <휴일.json> <기준시각> <출력폴더>
//   기준시각 예) 2022-03-14T08:50  (크론이 넣어 줌)

var fs = require('fs');
var config = require('./config');
var DateUtil = require('./lib/date_util');
var MailBuilder = require('./channels/mail');
var holiday = require('./holiday');
var makeSms = require('./channels/sms');
const { MessengerFormatter } = require('./channels/messenger');
const OutboxWriter = require('./outbox');

var du = new DateUtil();

var stat = {
  notice: 0, dup: 0, bad_date: 0,
  retired: 0, no_channel: 0, sms_skip: 0,
  delayed: 0
};

if (process.argv.length < 7) {
  console.log('사용법: node src/bot.js <공지.json> <직원.json> <휴일.json> <기준시각> <출력폴더>');
  process.exit(1);
}

var notice_file = process.argv[2];
var emp_file = process.argv[3];
var holiday_file = process.argv[4];
config.now = du.parse(process.argv[5]);
var out_dir = process.argv[6];

// 받는 부서
//   2016 양식: target: "영업1팀,재무팀" 또는 "ALL"
//   2019 양식: depts: ["영업1팀", "재무팀"]
function get_targets(n) {
  if (n.depts) return n.depts;
  if (n.target == 'ALL') return ['ALL'];
  if (!n.target) return [];
  return n.target.split(',');
}

function run(notices, emps, done) {
  var mail = new MailBuilder();
  var messenger = new MessengerFormatter();
  var outbox = [];
  var jobs = [];
  var seen = {};

  for (var i = 0; i < notices.length; i++) {
    var n = notices[i];
    if (seen[n.id]) {
      stat.dup++;
      continue;
    }
    seen[n.id] = 1;
    stat.notice++;

    // 예약 시각 (2016 양식은 send_at)
    var str_at = n.sendAt || n.send_at;
    var base = du.parse(str_at);
    if (str_at && !base) {
      stat.bad_date++;
    }
    if (!base || base.getTime() < config.now.getTime()) {
      base = config.now;   // 예약이 없거나 지났으면 지금 보냄
    }

    var depts = get_targets(n);
    for (var j = 0; j < emps.length; j++) {
      var emp = emps[j];
      if (depts.indexOf('ALL') == -1 && depts.indexOf(emp.dept) == -1) continue;
      if (emp.active === false) {
        stat.retired++;
        continue;
      }
      var chs = emp.channels || ['mail'];   // 옛날 직원 데이터는 channels가 없음
      if (chs.length == 0) {
        stat.no_channel++;
        continue;
      }
      if (config.debug) console.log('>>> ' + n.id + ' ' + emp.empNo + ' ' + chs.join(','));

      for (var k = 0; k < chs.length; k++) {
        if (chs[k] == 'mail') {
          mail.build(n, emp, base, function (err, m) {
            if (err) return;
            outbox.push(m);
          });
        } else if (chs[k] == 'sms') {
          jobs.push(makeSms(n, emp, base).then(function (m) {
            if (m) outbox.push(m);
            else stat.sms_skip++;
          }));
        } else if (chs[k] == 'messenger') {
          jobs.push(messenger.format(n, emp, base).then(function (m) {
            if (!m) return;
            outbox.push(m);
            if (m.sendAt != du.format(base)) stat.delayed++;   // 업무시간 밖이라 미룸
          }));
        }
      }
    }
  }

  Promise.all(jobs).then(function () {
    stat.delayed = stat.delayed + mail.delay_cnt;
    console.log('여기', outbox.length);
    done(null, outbox, messenger.cutCount);
  });
}

// 요약 파일 (2019.06 이서연) - 운영팀 메일에 붙여서 보냄
function writeSummary(dir, count, byChannel, cut) {
  let lines = [];
  lines.push(`[${config.BOT_NAME}] 실행 요약`);
  lines.push(`기준 시각: ${du.format(config.now)}`);
  lines.push(`공지: ${stat.notice}건 (중복 ${stat.dup}건 건너뜀, 예약 시각 오류 ${stat.bad_date}건)`);
  lines.push(`메시지: ${count}건 (메신저 ${byChannel.messenger}, 메일 ${byChannel.mail}, 문자 ${byChannel.sms})`);
  lines.push(`업무시간 밖이라 미룬 메시지: ${stat.delayed}건`);
  lines.push(`메신저 글자 수 초과로 자른 메시지: ${cut}건`);
  lines.push(`건너뜀: 퇴사 ${stat.retired}, 채널 없음 ${stat.no_channel}, 긴급 아닌 문자 ${stat.sms_skip}`);
  return new Promise((resolve, reject) => {
    fs.writeFile(dir + '/summary.txt', lines.join('\n') + '\n', 'utf8', (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

fs.readFile(notice_file, 'utf8', function (err, text) {
  if (err) {
    console.log('공지 파일을 못 읽었음: ' + err.message);
    return;
  }
  var notices = JSON.parse(text);
  fs.readFile(emp_file, 'utf8', function (err, text2) {
    if (err) {
      console.log('직원 파일을 못 읽었음: ' + err.message);
      return;
    }
    var emps = JSON.parse(text2);
    holiday.loadHolidays(holiday_file).then(function () {
      run(notices, emps, function (err, outbox, cut) {
        var writer = new OutboxWriter(out_dir);
        writer.write(outbox).then(function (count) {
          var by_ch = { messenger: 0, mail: 0, sms: 0 };
          outbox.forEach(function (m) {
            by_ch[m.channel]++;
          });
          console.log('완료. 메시지 ' + count + '건');
          writeSummary(out_dir, count, by_ch, cut).then(() => {
            console.log('요약 저장함');
          });
        });
      });
    }).catch(function (e) {
      console.log('휴일 파일 오류', e.message);
    });
  });
});
