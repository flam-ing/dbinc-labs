<?php
/*
 * 공통 함수
 * 2011.03 정민수
 */

// CSV 읽기 (첫 줄은 제목이라 버림)
function load_csv($name) {
    global $DATA_DIR;
    $rows = array();
    $lines = @file($DATA_DIR . $name);
    if (!$lines) return $rows;
    for ($i = 1; $i < count($lines); $i++) {
        $line = trim($lines[$i]);
        if ($line == '') continue;
        $rows[] = explode(',', $line);
    }
    return $rows;
}

// CSV 저장 (통째로 다시 씀)
function save_csv($name, $head, $rows) {
    global $DATA_DIR;
    $out = $head . "\n";
    foreach ($rows as $r) {
        $out .= implode(',', $r) . "\n";
    }
    $fp = @fopen($DATA_DIR . $name, 'w');
    @fwrite($fp, $out);
    @fclose($fp);
}

// 조건에 맞는 줄 찾기 (SQL where 처럼 쓰려고 만듦)
// 예: lib_find($LOANS, "\$r[1] == 'B0007' && \$r[5] == ''")
function lib_find($rows, $cond) {
    $found = array();
    foreach ($rows as $k => $r) {
        $ok = false;
        eval('$ok = (' . $cond . ');');
        if ($ok) $found[$k] = $r;
    }
    return $found;
}

// 회원 찾기. 없으면 -1
function get_member($emp_no) {
    global $MEMBERS;
    foreach ($MEMBERS as $k => $m) {
        if ($m[0] == $emp_no) return $k;
    }
    return -1;
}

// 도서 찾기. 없으면 -1
function get_book($book_id) {
    global $BOOKS;
    foreach ($BOOKS as $k => $b) {
        if ($b[0] == $book_id) return $k;
    }
    return -1;
}

// 새 대출번호
function new_loan_id() {
    global $LOANS;
    $max = 0;
    foreach ($LOANS as $l) {
        $n = (int)substr($l[0], 1);
        if ($n > $max) $max = $n;
    }
    return 'L' . sprintf('%04d', $max + 1);
}

// 날짜 + 일수
function add_days($ymd, $n) {
    return date('Y-m-d', strtotime($ymd) + $n * 86400);
}

// 두 날짜 사이 일수
function diff_days($from, $to) {
    return floor((strtotime($to) - strtotime($from)) / 86400);
}

// 연체료는 사랑의 책 나눔 기금 장부에 적음
function add_donation($ymd, $emp_no, $amount, $memo) {
    global $DATA_DIR;
    $line = $ymd . ',' . $emp_no . ',' . $amount . ',' . $memo . "\n";
    @file_put_contents($DATA_DIR . 'donation.csv', $line, FILE_APPEND);
}

// 처리 기록 (2012년 서버 옮긴 뒤로 APM_Setup 폴더 없음)
function lib_log($msg) {
    @file_put_contents('C:/APM_Setup/logs/library.log', date('Y-m-d H:i:s') . ' ' . $msg . "\n", FILE_APPEND);
}

// 반납 예정 메일 (메일 서버 없어져서 안 씀)
function send_due_mail($emp_no, $title, $due) {
    $smtp = 'mail.nuri.local';
    $from = 'library@nuri.local';
    $body = $title . ' 반납 예정일은 ' . $due . ' 입니다.';
    // @mail($emp_no . '@nuri.local', '[도서관] 반납 안내', $body, 'From: ' . $from);
    return false;
}
?>
