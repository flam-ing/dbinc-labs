<?php
include 'config.php';
include 'inc/lib_func.php';

$BOOKS = load_csv('books.csv');
$LOANS = load_csv('loans.csv');

$q = @trim($_GET['q']);
$field = @$_GET['field'];
// if (get_magic_quotes_gpc()) $q = stripslashes($q);  // PHP 8에서 없어져서 막음 (2021.03 한지원)

$idx = 1;
if ($field == 'author') $idx = 2;
if ($field == 'category') $idx = 3;

if ($q != '') {
    $q2 = addslashes($q);   // 2014 보안 점검 지적
    $rows = lib_find($BOOKS, "strpos(\$r[$idx], '$q2') !== false");
} else {
    $rows = $BOOKS;
}

$page_title = '도서 목록';
include 'inc/top.php';
?>
<form method="get" action="list.php">
<select name="field">
  <option value="title">제목</option>
  <option value="author" <?php if ($field == 'author') echo 'selected'; ?>>저자</option>
  <option value="category" <?php if ($field == 'category') echo 'selected'; ?>>분류</option>
</select>
<input type="text" name="q" value="<?php echo htmlspecialchars($q); ?>">
<input type="submit" value="검색">
</form>
<br>
<table border="1" cellpadding="4" cellspacing="0">
<tr bgcolor="#dddddd"><th>번호</th><th>제목</th><th>저자</th><th>분류</th><th>상태</th><th>반납예정</th></tr>
<?php
foreach ($rows as $b) {
    $due = '';
    if ($b[5] == 'OUT') {
        $st = '<font color="red">대출중</font>';
        foreach (lib_find($LOANS, "\$r[1] == '" . $b[0] . "' && \$r[5] == ''") as $l) $due = $l[4];
    } else if ($b[5] == 'LOST') {
        $st = '<font color="gray">분실</font>';
    } else {
        $st = '대출가능';
    }
    echo "<tr><td>$b[0]</td><td>$b[1]</td><td>$b[2]</td><td>$b[3]</td><td>$st</td><td>$due</td></tr>\n";
}
?>
</table>
<p>모두 <?php echo count($rows); ?>권</p>
<hr>
<small>문의: 총무팀 정민수 (내선 2213) / 연체료는 사랑의 책 나눔 기금으로 적립됩니다.</small>
</body>
</html>
