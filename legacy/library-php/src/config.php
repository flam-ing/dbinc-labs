<?php
/*
 * 사내 도서 대여 시스템 설정
 * 2011.03 총무팀 정민수
 */
error_reporting(E_ALL ^ E_NOTICE);
date_default_timezone_set('Asia/Seoul');

$DATA_DIR = dirname(__FILE__) . '/../data/store/';
// $DATA_DIR = 'D:/APM_Setup/htdocs/library/data/';

$SITE_TITLE = '누리상사 사내 도서관';

// 관리자 화면용 (admin.php는 2013년에 지움)
$ADMIN_ID = 'admin';
$ADMIN_PW = 'DUMMY-lib2011!';

$LOAN_DAYS = 14;
$MAX_LOAN = 5;      // 2013.04 3권에서 5권으로 늘림
$FEE_PER_DAY = 100;

$BOOK_HEAD = 'book_id,title,author,category,price,status';
$MEMBER_HEAD = 'emp_no,name,dept,grade,overdue_cnt,suspend_until';
$LOAN_HEAD = 'loan_id,book_id,emp_no,loan_date,due_date,return_date,ext_cnt,fee';
$RESV_HEAD = 'book_id,emp_no,reserved_at';
?>
