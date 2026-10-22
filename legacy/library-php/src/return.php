<?php
include 'config.php';
include 'inc/lib_func.php';

$BOOKS = load_csv('books.csv');
$MEMBERS = load_csv('members.csv');
$LOANS = load_csv('loans.csv');

$msg = '';
if (@$_POST['mode'] == 'return') {
    $book = addslashes(@trim($_POST['book_id']));
    $today = date('Y-m-d');
    $found = lib_find($LOANS, "\$r[1] == '$book' && \$r[5] == ''");
    if (count($found) == 0) {
        $msg = '<font color="red">대출 기록이 없습니다.</font>';
    } else {
        $lk = key($found);
        // 연체일
        $late = (int)((strtotime($today) - strtotime($LOANS[$lk][4])) / (60 * 60 * 24));
        $fee = 0;
        if ($late > 0) {
            $fee = $late * $FEE_PER_DAY;
            if ($fee > 3000) $fee = 3000;
            $mk = get_member($LOANS[$lk][2]);
            $MEMBERS[$mk][4]++;
            if ($MEMBERS[$mk][4] > 3) {
                $MEMBERS[$mk][5] = date('Y-m-d', strtotime('+30 day'));
                $MEMBERS[$mk][4] = 0;
            }
            add_donation($today, $LOANS[$lk][2], $fee, '연체료 ' . $LOANS[$lk][0]);
        }
        $LOANS[$lk][5] = $today;
        $LOANS[$lk][7] = $fee;
        $bk = get_book($book);
        $BOOKS[$bk][5] = 'IN';
        save_csv('loans.csv', $LOAN_HEAD, $LOANS);
        save_csv('books.csv', $BOOK_HEAD, $BOOKS);
        save_csv('members.csv', $MEMBER_HEAD, $MEMBERS);
        $msg = '반납되었습니다.';
        if ($fee > 0) {
            $msg .= ' 연체료 <b>' . number_format($fee) . '원</b>은 사랑의 책 나눔 기금으로 적립됩니다.';
        }
    }
}

$page_title = '도서 반납';
include 'inc/top.php';
?>
<p><?php echo $msg; ?></p>
<form method="post" action="return.php">
<input type="hidden" name="mode" value="return">
도서번호 <input type="text" name="book_id" size="10">
<input type="submit" value="반납">
</form>
<p>하루 늦을 때마다 <?php echo $FEE_PER_DAY; ?>원이 사랑의 책 나눔 기금으로 적립됩니다.</p>
<hr>
<small>문의: 총무팀 정민수 (내선 2213) / 연체료는 사랑의 책 나눔 기금으로 적립됩니다.</small>
</body>
</html>
