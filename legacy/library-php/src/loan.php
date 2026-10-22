<?php
include 'config.php';
include 'inc/lib_func.php';

$BOOKS = load_csv('books.csv');
$MEMBERS = load_csv('members.csv');
$LOANS = load_csv('loans.csv');

$msg = '';
if (@$_POST['mode'] == 'loan') {
    $emp = addslashes(@trim($_POST['emp_no']));
    $book = addslashes(@trim($_POST['book_id']));
    $today = date('Y-m-d');
    $mk = get_member($emp);
    $bk = get_book($book);
    if ($mk < 0) {
        $msg = '<font color="red">사번을 확인하세요.</font>';
    } else if ($bk < 0) {
        $msg = '<font color="red">도서번호를 확인하세요.</font>';
    } else if ($MEMBERS[$mk][5] != '' && $MEMBERS[$mk][5] >= $today) {
        $msg = '<font color="red">대출 정지 중입니다. (' . $MEMBERS[$mk][5] . '까지)</font>';
    } else if ($BOOKS[$bk][5] != 'IN') {
        $msg = '<font color="red">지금 빌릴 수 없는 책입니다.</font>';
    } else {
        $my = lib_find($LOANS, "\$r[2] == '$emp' && \$r[5] == ''");
        if (count($my) >= $MAX_LOAN) {
            $msg = '<font color="red">' . $MAX_LOAN . '권까지 빌릴 수 있습니다.</font>';
        } else {
            $days = $LOAN_DAYS;
            if ($MEMBERS[$mk][3] == '부장') $days = 21;
            $due = date('Y-m-d', strtotime("+$days day"));
            $LOANS[] = array(new_loan_id(), $book, $emp, $today, $due, '', 0, 0);
            $BOOKS[$bk][5] = 'OUT';
            save_csv('loans.csv', $LOAN_HEAD, $LOANS);
            save_csv('books.csv', $BOOK_HEAD, $BOOKS);
            $msg = '대출되었습니다. 반납 예정일은 <b>' . $due . '</b> 입니다.';
            // send_due_mail($emp, $BOOKS[$bk][1], $due);
        }
    }
}

$page_title = '도서 대출';
include 'inc/top.php';
?>
<p><?php echo $msg; ?></p>
<form method="post" action="loan.php">
<input type="hidden" name="mode" value="loan">
사번 <input type="text" name="emp_no" size="10">
도서번호 <input type="text" name="book_id" size="10">
<input type="submit" value="대출">
</form>
<p>대출 기간은 <?php echo $LOAN_DAYS; ?>일입니다. (부장 21일)</p>
<hr>
<small>문의: 총무팀 정민수 (내선 2213) / 연체료는 사랑의 책 나눔 기금으로 적립됩니다.</small>
</body>
</html>
