using System;
using System.Collections;
using System.Text;

namespace NuriClaim
{
    /// <summary>
    /// 전역 변수 (VB6 modGlobal.bas 에서 옮김)
    /// </summary>
    public class modGlobal
    {
        // ---------------- 사유 코드 ----------------
        //  00  정상
        //  11  한도 초과 (부분 지급)
        //  21  면책 기간
        //  22  암 면책 (1년)
        //  23  입원 3일 이하
        //  24  청구 기한 (3년)
        //  31  상품 없음
        //  32  단종 상품
        //  33  해지 계약
        //  41  중복 청구
        //  51  고액 (300만원 이상, 재보험)
        //  90  자료 오류
        // ------------------------------------------

        public static DateTime g_dtBase;                        // 심사 기준일
        public static string g_strBaseDt = "";
        public static Hashtable g_htDup = new Hashtable();      // 중복 체크 (증권번호 + 사고일)
        public static int[] g_arrCnt = new int[4];              // 0 AUTO, 1 PART, 2 REJECT, 3 MANUAL
        public static decimal[] g_arrAmt = new decimal[4];
        public static int g_intLineNo = 0;
        public static StringBuilder g_sbOut = new StringBuilder();

        public const string OUT_DIR = @"D:\CLAIM\OUT\";
        public const string DB_CONN = "Data Source=CLAIMDB01;Initial Catalog=CLAIM;User Id=claim_bat;Password=DUMMY-claim-0000;";
    }
}
