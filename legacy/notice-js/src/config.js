// 공지봇 설정
// 2016.04 박준호
// !! 운영 서버의 config.js는 서버에서 직접 고쳐서 씀. 배포할 때 덮어쓰지 말 것 !!

var config = {
  BOT_NAME: '누리 공지봇',
  OUTBOX_DIR: '/home/notice/outbox',     // 2019.06 출력 폴더는 실행 인자로 받게 바뀜
  SMS_URL: 'http://sms-gw.nuri.local:8080/send',
  SMS_KEY: 'DUMMY-SMS-KEY-0000-0000',
  MAIL_FROM: 'notice-bot@nuri.example',
  MAIL_FOOTER: '\n\n--\n이 메일은 발신 전용이에요. 문의는 총무팀(내선 2040)으로 해 주세요.',
  WORK_START: 9,
  WORK_END: 18,
  // NURITALK_TOKEN: 'DUMMY-NURITALK-TOKEN-0000',   // 2022 김도윤: 게이트웨이로 옮김
  debug: true
};

// 실행 중에 bot.js, holiday.js가 채워 넣음
config.now = null;
config.holidays = [];

module.exports = config;
