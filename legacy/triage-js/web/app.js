// 상담 분류 도우미
// 2018.05 최지안 (CS팀 요청)
// 2018.07 엑셀 복사, 마지막 줄 지우기 추가
//
// 티켓 내용을 넣고 [분류]를 누르면 아래 표에 한 줄씩 붙어요.
// 분류 기준: 위키 "상담 분류 기준" (2018.05 워크숍)

var rowNo = 0;
var lastRow = null;

function fmt(d) {
  function p(n) { return n < 10 ? '0' + n : '' + n; }
  return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
}

function onClassify() {
  var title = document.getElementById('title').value;
  var body = document.getElementById('body').value;
  var grade = document.getElementById('grade').value;
  var channel = document.querySelector('input[name="channel"]:checked').value;
  var received = document.getElementById('received').value;

  if (title == '' && body == '') {
    alert('제목이나 내용을 넣어 주세요');
    return;
  }

  var text = title + ' ' + body;

  // 카테고리 (장애를 먼저 봐야 함!!)
  var cat = '기타';
  if (text.indexOf('오류') > -1 || text.indexOf('에러') > -1 || text.indexOf('접속') > -1 || text.indexOf('500') > -1 || text.indexOf('안 돼요') > -1) {
    cat = '장애';
  } else if (text.indexOf('결제') > -1 || text.indexOf('카드') > -1 || text.indexOf('청구') > -1) {
    cat = '결제';
  } else if (text.indexOf('배송') > -1 || text.indexOf('택배') > -1 || text.indexOf('송장') > -1) {
    cat = '배송';
  } else if (text.indexOf('로그인') > -1 || text.indexOf('비밀번호') > -1 || text.indexOf('계정') > -1) {
    cat = '계정';
  }

  // 점수
  var score = 0;
  if (cat == '장애') score += 3;
  if (cat == '결제') score += 2;
  if (cat == '배송' || cat == '계정') score += 1;
  if (grade == 'VIP') score += 3;
  if (grade == '우수') score += 1;
  if (channel == '전화') score += 2;
  if (channel == '채팅') score += 1;
  if (text.indexOf('긴급') > -1 || text.indexOf('급해요') > -1 || text.indexOf('당장') > -1) score += 2;

  var urg = 'P4';
  if (score >= 7) urg = 'P1';
  else if (score >= 5) urg = 'P2';
  else if (score >= 3) urg = 'P3';

  // 담당 팀
  var team = '고객상담1팀';
  if (cat == '장애') team = 'IT운영팀';
  else if (grade == 'VIP') team = 'VIP전담팀';
  else if (cat == '결제') team = '결제지원팀';
  else if (cat == '배송') team = '물류CS팀';
  else if (cat == '계정') team = '회원지원팀';

  // SLA 마감
  var h = 72;
  if (urg == 'P1') h = 2;
  if (urg == 'P2') h = 4;
  if (urg == 'P3') h = 24;
  var r = received ? new Date(received) : new Date();
  var deadline = new Date(r.getTime() + h * 3600000);

  rowNo++;
  var tr = document.createElement('tr');
  tr.className = urg;
  tr.innerHTML = '<td>' + rowNo + '</td><td>' + title + '</td><td>' + cat + '</td>' +
    '<td class="urg">' + urg + '</td><td>' + team + '</td>' +
    '<td>' + fmt(r) + '</td><td class="dl">' + fmt(deadline) + '</td>';
  document.getElementById('list').appendChild(tr);
  lastRow = tr;

  document.getElementById('title').value = '';
  document.getElementById('body').value = '';
  refreshStats();
}

// 표를 다시 읽어서 통계를 냄 (표가 곧 데이터)
function refreshStats() {
  var rows = document.getElementById('list').getElementsByTagName('tr');
  if (rows.length == 0) {
    document.getElementById('stats').innerHTML = '아직 분류한 티켓이 없어요.';
    return;
  }
  var c = { P1: 0, P2: 0, P3: 0, P4: 0 };
  var late = 0;
  var now = new Date();
  for (var i = 0; i < rows.length; i++) {
    var u = rows[i].getElementsByClassName('urg')[0].innerHTML;
    c[u]++;
    var dl = rows[i].getElementsByClassName('dl')[0].innerHTML;
    if (new Date(dl.replace(' ', 'T')) < now) late++;
  }
  document.getElementById('stats').innerHTML = '모두 ' + rows.length + '건 &nbsp; P1 <b>' + c.P1 + '</b> · P2 <b>' + c.P2 +
    '</b> · P3 <b>' + c.P3 + '</b> · P4 <b>' + c.P4 + '</b> &nbsp; 마감 지남 <b class="late">' + late + '</b>';
}

function onDeleteLast() {
  if (!lastRow) return;
  lastRow.parentNode.removeChild(lastRow);
  lastRow = null;
  rowNo--;
  refreshStats();
}

function onSample() {
  document.getElementById('title').value = '결제했는데 주문 내역이 안 보여요';
  document.getElementById('body').value = '카드 결제는 됐다고 문자가 왔는데 앱 주문 내역에 없어요. 당장 확인 부탁드려요.';
  document.getElementById('grade').value = 'VIP';
  document.querySelector('input[name="channel"][value="채팅"]').checked = true;
}

// 엑셀에 붙여 넣기용 (탭으로 나눔)
function onCopy() {
  var txt = '';
  var rows = document.getElementById('list').getElementsByTagName('tr');
  for (var i = 0; i < rows.length; i++) {
    var tds = rows[i].getElementsByTagName('td');
    for (var j = 0; j < tds.length; j++) {
      txt += tds[j].innerText + (j < tds.length - 1 ? '\t' : '\n');
    }
  }
  // navigator.clipboard는 사내 크롬 버전에서 안 돼서 textarea로 함
  var ta = document.createElement('textarea');
  ta.value = txt;
  document.body.appendChild(ta);
  ta.select();
  document.execCommand('copy');
  document.body.removeChild(ta);
  alert(rows.length + '줄 복사했어요');
}
