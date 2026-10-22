<?php
/*
 * 도서 대여 일괄 처리
 * 총무팀이 모은 신청서(엑셀)를 CSV로 저장해서 돌림
 *
 * 사용법: php batch.php 요청파일.csv 기준일(YYYY-MM-DD) [데이터폴더]
 *
 * 2011.04 정민수
 * 2012.02 데이터폴더 인자 추가 (정민수)
 */
include dirname(__FILE__) . '/config.php';
include dirname(__FILE__) . '/inc/lib_func.php';

if ($argc < 3) {
    echo "사용법: php batch.php <요청CSV> <기준일 YYYY-MM-DD> [데이터폴더]\n";
    exit(1);
}
$req_file = $argv[1];
$today = $argv[2];
if ($argc > 3) $DATA_DIR = rtrim($argv[3], '/\\') . '/';

if (strtotime($today) === false) {
    echo "기준일 오류: $today\n";
    exit(1);
}

$BOOKS = load_csv('books.csv');
$MEMBERS = load_csv('members.csv');
$LOANS = load_csv('loans.csv');
$RESV = load_csv('reservations.csv');

$lines = @file($req_file) or die("요청 파일을 열 수 없습니다: $req_file\n");

echo "=== 사내 도서 일괄 처리 ===\n";
echo "요청 파일: $req_file\n";
echo "기준일: $today\n";
echo "-------------------------------------------\n";

$cnt_ok = 0;
$cnt_ng = 0;
$cnt_err = 0;
$fee_sum = 0;
$lost_sum = 0;

// 한 줄 결과 찍기
function result($kind, $msg) {
    global $no, $type, $emp, $book, $cnt_ok, $cnt_ng, $cnt_err;
    echo sprintf("[%02d] %s %s %s : %s", $no, $type, $emp, $book, $kind);
    if ($msg != '') echo " - $msg";
    echo "\n";
    if ($kind == '완료') $cnt_ok++;
    if ($kind == '거부') $cnt_ng++;
    if ($kind == '오류') $cnt_err++;
    lib_log("$type $emp $book $kind $msg");
}

for ($i = 1; $i < count($lines); $i++) {
    if (trim($lines[$i]) == '') continue;
    $no = $i;
    $c = explode(',', trim($lines[$i]));
    $type = trim($c[0]);
    $emp = @trim($c[1]);
    $book = @trim($c[2]);
    $d = @trim($c[3]);
    if ($d == '') $d = $today;

    $t = strtotime($d);
    if ($t === false) {
        result('오류', "처리일을 읽을 수 없음 ($d)");
        continue;
    }
    $d = date('Y-m-d', $t);

    switch ($type) {
    case '대출':
        $mk = get_member($emp);
        if ($mk < 0) { result('오류', '없는 사번'); break; }
        if ($MEMBERS[$mk][5] != '' && $MEMBERS[$mk][5] >= $d) {
            result('거부', '대출 정지 중 (' . $MEMBERS[$mk][5] . '까지)');
            break;
        }
        $bk = get_book($book);
        if ($bk < 0) { result('오류', '없는 도서'); break; }
        if ($BOOKS[$bk][5] == 'LOST') { result('거부', '분실 도서'); break; }
        if ($BOOKS[$bk][5] != 'IN') { result('거부', '대출 중'); break; }

        $my = lib_find($LOANS, "\$r[2] == '$emp' && \$r[5] == ''");
        if (count($my) >= 3) { result('거부', '대출 한도 초과 (3권)'); break; }

        // 예약자가 있으면 예약자만 빌릴 수 있음
        $rv = lib_find($RESV, "\$r[0] == '$book'");
        $blocked = false;
        foreach ($rv as $rk => $r) {
            if ($r[1] == $emp) unset($RESV[$rk]);
            else $blocked = true;
        }
        if ($blocked) { result('거부', '예약 도서 (예약자 우선)'); break; }

        $days = $LOAN_DAYS;
        if ($MEMBERS[$mk][3] == '부장' || $MEMBERS[$mk][3] == '임원') $days = 21;
        $due = date('Y-m-d', strtotime("+$days day", $t));
        $LOANS[] = array(new_loan_id(), $book, $emp, $d, $due, '', 0, 0);
        $BOOKS[$bk][5] = 'OUT';
        result('완료', "반납예정 $due");
        break;

    case '반납':
        $found = lib_find($LOANS, "\$r[1] == '$book' && \$r[5] == ''");
        if (count($found) == 0) { result('오류', '대출 기록 없음'); break; }
        $lk = key($found);
        $late = diff_days($LOANS[$lk][4], $d);
        $fee = 0;
        if ($late > 0) {
            $fee = $late * $FEE_PER_DAY;
            if ($fee > 5000) $fee = 5000;
        }
        $LOANS[$lk][5] = $d;
        $LOANS[$lk][7] = $fee;
        $bk = get_book($book);
        $BOOKS[$bk][5] = 'IN';

        if ($late > 0) {
            $mk = get_member($LOANS[$lk][2]);
            $MEMBERS[$mk][4] = $MEMBERS[$mk][4] + 1;
            $msg = "연체 {$late}일, 연체료 " . number_format($fee) . "원 기부금 적립";
            if ($MEMBERS[$mk][4] >= 3) {
                $MEMBERS[$mk][5] = add_days($d, 30);
                $MEMBERS[$mk][4] = 0;
                $msg .= ', 연체 3회라 ' . $MEMBERS[$mk][5] . '까지 대출 정지';
            }
            add_donation($d, $LOANS[$lk][2], $fee, '연체료 ' . $LOANS[$lk][0]);
            $fee_sum += $fee;
            result('완료', $msg);
        } else {
            result('완료', '정상 반납');
        }
        foreach (lib_find($RESV, "\$r[0] == '$book'") as $r) {
            $rm = get_member($r[1]);
            echo "     예약자 " . $r[1] . " " . $MEMBERS[$rm][1] . "님에게 연락하세요\n";
        }
        break;

    case '연장':
        $found = lib_find($LOANS, "\$r[1] == '$book' && \$r[2] == '$emp' && \$r[5] == ''");
        if (count($found) == 0) { result('오류', '대출 기록 없음'); break; }
        $lk = key($found);
        if ($LOANS[$lk][6] >= 1) { result('거부', '연장은 1회만'); break; }
        if (count(lib_find($RESV, "\$r[0] == '$book'")) > 0) { result('거부', '예약자 있음'); break; }
        $LOANS[$lk][4] = date('Y-m-d', strtotime($LOANS[$lk][4]) + 7 * 86400);
        $LOANS[$lk][6] = $LOANS[$lk][6] + 1;
        result('완료', '반납예정 ' . $LOANS[$lk][4]);
        break;

    case '분실':
        $found = lib_find($LOANS, "\$r[1] == '$book' && \$r[5] == ''");
        if (count($found) == 0) { result('오류', '대출 기록 없음'); break; }
        $lk = key($found);
        $LOANS[$lk][5] = $d;
        $LOANS[$lk][7] = 0;     // 분실은 연체료 안 받음
        $bk = get_book($book);
        $BOOKS[$bk][5] = 'LOST';
        $lost_sum += $BOOKS[$bk][4];
        result('완료', '분실 처리, 변상금 ' . number_format($BOOKS[$bk][4]) . '원 (총무팀 수납)');
        break;

    default:
        result('오류', "알 수 없는 구분 ($type)");
    }
}

save_csv('books.csv', $BOOK_HEAD, $BOOKS);
save_csv('members.csv', $MEMBER_HEAD, $MEMBERS);
save_csv('loans.csv', $LOAN_HEAD, $LOANS);
save_csv('reservations.csv', $RESV_HEAD, $RESV);

echo "-------------------------------------------\n";
echo "완료 {$cnt_ok}건, 거부 {$cnt_ng}건, 오류 {$cnt_err}건\n";
echo "연체료 " . number_format($fee_sum) . "원 (기부금 적립), 변상금 " . number_format($lost_sum) . "원\n";
echo "저장했습니다: books.csv, members.csv, loans.csv, reservations.csv\n";
?>
