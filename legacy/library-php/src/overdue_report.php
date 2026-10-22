<?php
/*
 * 연체 현황 보고 (매일 아침 크론으로 돌려서 총무팀에 메일로 보냄)
 *
 * 사용법: php overdue_report.php 기준일(YYYY-MM-DD) [데이터폴더]
 *
 * 2011.06 정민수
 */
include dirname(__FILE__) . '/config.php';
include dirname(__FILE__) . '/inc/lib_func.php';

$base = @$argv[1];
if ($base == '' || strtotime($base) === false) {
    echo "기준일을 YYYY-MM-DD로 넣어 주세요.\n";
    exit(1);
}
if ($argc > 2) $DATA_DIR = rtrim($argv[2], '/\\') . '/';

$BOOKS = load_csv('books.csv');
$MEMBERS = load_csv('members.csv');
$LOANS = load_csv('loans.csv');

$tb = strtotime($base);
$list = array();
$lost = array();
foreach ($LOANS as $l) {
    if ($l[5] != '') continue;      // 반납된 것

    // 연체일 (같은 해 안에서만 맞음. 연초는 수기 확인)
    $days = date('z', $tb) - date('z', strtotime($l[4]));
    if ($days <= 0) continue;

    $mk = get_member($l[2]);
    $bk = get_book($l[1]);
    $dept = $mk >= 0 ? $MEMBERS[$mk][2] : '(퇴사자)';
    $name = $mk >= 0 ? $MEMBERS[$mk][1] : '?';
    $title = $bk >= 0 ? $BOOKS[$bk][1] : '?';
    $list[$dept][] = array($l[2], $name, $title, $l[4], $days, $days * $FEE_PER_DAY);
    if ($days >= 60) $lost[] = $l[0] . ' ' . $title . ' (' . $l[2] . ' ' . $name . ', ' . $days . '일)';
}
ksort($list);

echo "누리상사 사내 도서관 연체 현황\n";
echo "기준일: $base\n";
echo "============================================================\n";
$cnt = 0;
$tot = 0;
foreach ($list as $dept => $rows) {
    echo "[$dept]\n";
    foreach ($rows as $r) {
        echo '  ' . str_pad($r[0], 7) . str_pad($r[1], 10) . str_pad($r[2], 30) . $r[3]
            . str_pad($r[4] . '일', 9, ' ', STR_PAD_LEFT)
            . str_pad(number_format($r[5]) . '원', 12, ' ', STR_PAD_LEFT) . "\n";
        $cnt++;
        $tot += $r[5];
    }
}
if ($cnt == 0) echo "연체 없음\n";
echo "------------------------------------------------------------\n";
echo "연체 {$cnt}건, 예상 연체료 합계 " . number_format($tot) . "원\n";

echo "\n분실 처리 검토 (60일 이상)\n";
if (count($lost) == 0) echo "  없음\n";
foreach ($lost as $x) echo "  $x\n";

echo "\n대출 정지 회원\n";
$n = 0;
foreach ($MEMBERS as $m) {
    if ($m[5] != '' && $m[5] >= $base) {
        echo '  ' . $m[0] . ' ' . $m[1] . ' (' . $m[5] . "까지)\n";
        $n++;
    }
}
if ($n == 0) echo "  없음\n";
?>
