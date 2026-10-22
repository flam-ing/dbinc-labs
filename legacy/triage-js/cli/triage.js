#!/usr/bin/env node
'use strict';
/*
 * 상담 티켓 야간 분류 배치
 * 2020.06 정우진
 *
 * web/app.js의 분류 로직을 가져와서(화면 코드는 뺌) 티켓 시스템이 내보낸 파일을 한꺼번에 분류해요.
 * 2020.07 키워드 수정 (CS팀 요청)
 *
 * 사용법: node cli/triage.js <티켓.json> [--now 2020-10-05T10:00] [--json]
 */
const fs = require('fs');
const HOLIDAYS = require('./holidays');

// ---------- 인자 ----------
const argv = process.argv.slice(2);
let file = null;
let nowArg = null;
let asJson = false;
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--json') asJson = true;
  else if (argv[i] === '--now') nowArg = argv[++i];
  else file = argv[i];
}
if (!file) {
  console.log('사용법: node cli/triage.js <티켓.json> [--now YYYY-MM-DDTHH:mm] [--json]');
  process.exit(1);
}

// 서버가 UTC라서 9시간 더함 (한국 시각 숫자를 UTC 칸에 넣고 계산)
const NOW = nowArg ? parseTime(nowArg) : new Date(Date.now() + 9 * 3600 * 1000);

// ---------- 분류 (app.js에서 복사) ----------
function getCategory(text) {
  // 장애를 먼저 봐야 함!!
  if (text.indexOf('오류') > -1 || text.indexOf('에러') > -1 || text.indexOf('접속') > -1 || text.indexOf('먹통') > -1 || text.indexOf('안 돼요') > -1 || text.indexOf('안돼요') > -1) {
    return '장애';
  } else if (text.indexOf('결제') > -1 || text.indexOf('카드') > -1 || text.indexOf('청구') > -1 || text.indexOf('환불') > -1) {
    return '결제';
  } else if (text.indexOf('배송') > -1 || text.indexOf('택배') > -1 || text.indexOf('송장') > -1 || text.indexOf('반송') > -1) {
    return '배송';
  } else if (text.indexOf('로그인') > -1 || text.indexOf('비밀번호') > -1 || text.indexOf('계정') > -1 || text.indexOf('탈퇴') > -1) {
    return '계정';
  }
  // if (text.indexOf('500') > -1) return '장애';
  return '기타';
}

function getScore(cat, grade, channel, text) {
  let score = 0;
  if (cat == '장애') score += 3;
  if (cat == '결제') score += 2;
  if (cat == '배송' || cat == '계정') score += 1;
  if (grade == 'VIP') score += 3;
  if (grade == '우수') score += 1;
  if (channel == '전화') score += 2;
  if (channel == '채팅') score += 1;
  if (text.indexOf('긴급') > -1 || text.indexOf('급해요') > -1 || text.indexOf('당장') > -1) score += 2;
  // 2020.07 대외 리스크 키워드 (CS팀장님 요청)
  if (text.indexOf('소송') > -1 || text.indexOf('신고') > -1 || text.indexOf('언론') > -1 || text.indexOf('기자') > -1) score += 5;
  return score;
}

function getUrgency(score) {
  if (score >= 7) return 'P1';
  if (score >= 5) return 'P2';
  if (score >= 3) return 'P3';
  return 'P4';
}

function getTeam(cat, grade) {
  if (cat == '장애') return 'IT운영팀';
  if (grade == 'VIP') return 'VIP전담팀';
  if (cat == '결제') return '결제지원팀';
  if (cat == '배송') return '물류CS팀';
  if (cat == '계정') return '회원지원팀';
  return '고객상담1팀';
}

// ---------- SLA ----------
// P1은 그냥 2시간. 나머지는 영업시간(평일 9시~18시)만 셈
function getDeadline(received, urg) {
  if (urg == 'P1') {
    return new Date(received.getTime() + 2 * 60 * 60 * 1000);
  }
  let mins = 27 * 60;
  if (urg == 'P2') mins = 4 * 60;
  if (urg == 'P3') mins = 9 * 60;

  let t = new Date(received.getTime());
  if (!isBizDay(t) || t.getUTCHours() >= 18) {
    t = nextBizMorning(t);
  } else if (t.getUTCHours() < 9) {
    t.setUTCHours(9, 0, 0, 0);
  }
  while (true) {
    const end = new Date(t.getTime());
    end.setUTCHours(18, 0, 0, 0);
    const left = (end.getTime() - t.getTime()) / 60000;
    if (mins <= left) {
      return new Date(t.getTime() + mins * 60000);
    }
    mins = mins - left;
    t = nextBizMorning(t);
  }
}

function isBizDay(d) {
  const day = d.getUTCDay();
  if (day == 0 || day == 6) return false;
  return HOLIDAYS.indexOf(d.toISOString().substring(0, 10)) == -1;
}

function nextBizMorning(d) {
  const n = new Date(d.getTime());
  do {
    n.setUTCDate(n.getUTCDate() + 1);
  } while (!isBizDay(n));
  n.setUTCHours(9, 0, 0, 0);
  return n;
}

// ---------- 시각 ----------
// 채널마다 형식이 달라요
//   웹, 이메일  "2020-09-28 09:12"
//   채팅        "2020-09-28T09:12:00+09:00"
//   전화(CTI)   1601252520000  (숫자)
function parseTime(v) {
  if (typeof v == 'number') {
    return new Date(v + 9 * 3600 * 1000);
  }
  if (!v) return null;
  const s = String(v).trim().replace('T', ' ').substring(0, 16);   // 뒤에 붙은 +09:00은 버림
  const m = /^(\d{4})-(\d\d)-(\d\d) (\d\d):(\d\d)$/.exec(s);
  if (!m) return null;
  return new Date(Date.UTC(+m[1], m[2] - 1, +m[3], +m[4], +m[5]));
}

function fmt(d) {
  if (!d) return '-';
  return d.toISOString().replace('T', ' ').substring(0, 16);
}

function pad(s, n) {
  s = String(s);
  while (s.length < n) s += ' ';
  return s;
}

// ---------- 실행 ----------
let tickets;
try {
  tickets = JSON.parse(fs.readFileSync(file, 'utf8'));
} catch (e) {
  console.error('티켓 파일을 읽을 수 없어요: ' + e.message);
  process.exit(2);
}

const results = [];
let skipped = 0;
for (let i = 0; i < tickets.length; i++) {
  const t = tickets[i];
  try {
    const text = t.title + ' ' + (t.body || '');
    const grade = (t.grade || '일반').toUpperCase() == 'VIP' ? 'VIP' : (t.grade || '일반');
    const channel = t.channel.trim();
    const cat = getCategory(text);
    const score = getScore(cat, grade, channel, text);
    const urg = getUrgency(score);
    const received = parseTime(t.receivedAt);
    const deadline = received ? getDeadline(received, urg) : null;
    results.push({
      id: t.id,
      category: cat,
      urgency: urg,
      score: score,
      team: getTeam(cat, grade),
      receivedAt: fmt(received),
      deadline: fmt(deadline),
      overdue: deadline ? deadline.getTime() < NOW.getTime() : false
    });
  } catch (e) {
    skipped++;
  }
}

// 급한 것부터
results.sort((a, b) => a.urgency.localeCompare(b.urgency));

if (asJson) {
  console.log(JSON.stringify(results, null, 2));
} else {
  console.log('상담 티켓 분류 결과 (기준 ' + fmt(NOW) + ')');
  console.log(pad('번호', 10) + pad('카테고리', 6) + pad('긴급도', 5) + pad('담당 팀', 9) + pad('접수', 18) + pad('마감', 18) + '상태');
  console.log('-'.repeat(76));
  const cnt = { P1: 0, P2: 0, P3: 0, P4: 0 };
  let late = 0;
  results.forEach((r) => {
    cnt[r.urgency]++;
    if (r.overdue) late++;
    console.log(pad(r.id, 10) + pad(r.category, 6) + pad(r.urgency, 5) + pad(r.team, 9) + pad(r.receivedAt, 18) + pad(r.deadline, 18) + (r.overdue ? '지남' : ''));
  });
  console.log('-'.repeat(76));
  console.log(`합계 ${results.length}건 (P1 ${cnt.P1}, P2 ${cnt.P2}, P3 ${cnt.P3}, P4 ${cnt.P4}) / 마감 지남 ${late}건` + (skipped ? ` / 건너뜀 ${skipped}건` : ''));
}
