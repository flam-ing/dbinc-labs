using System;

namespace NuriClaim
{
    /// <summary>
    /// 공통 함수 (VB6 modCommon.bas 에서 옮김)
    /// </summary>
    public class modCommon
    {
        /// <summary>
        /// 문자열 -> 날짜. yyyyMMdd 또는 yyyy-MM-dd
        /// </summary>
        public static DateTime ToDate(string strDate)
        {
            if (strDate.Length == 8)
            {
                return DateTime.ParseExact(strDate, "yyyyMMdd", null);
            }
            return DateTime.Parse(strDate);
        }

        /// <summary>
        /// 숫자 변환. VB Val() 하고 같게 실패하면 0
        /// </summary>
        public static int ToInt(string strVal)
        {
            try
            {
                return Convert.ToInt32(strVal);
            }
            catch
            {
                return 0;
            }
        }

        public static decimal ToDec(string strVal)
        {
            try
            {
                return Convert.ToDecimal(strVal);
            }
            catch
            {
                return 0;
            }
        }

        /// <summary>
        /// 금액 표시 (#,##0)
        /// </summary>
        public static string FmtAmt(decimal decAmt)
        {
            return decAmt.ToString("#,##0");
        }

        /// <summary>
        /// VB Left()
        /// </summary>
        public static string Left(string strVal, int intLen)
        {
            if (strVal == null) return "";
            if (strVal.Length <= intLen) return strVal;
            return strVal.Substring(0, intLen);
        }

        /// <summary>
        /// 주민번호로 만 나이 계산 (2012.03 연령 할증 없어지면서 안 씀)
        /// </summary>
        public static int GetAge(string strJumin, DateTime dtBase)
        {
            int intYear = Convert.ToInt32(strJumin.Substring(0, 2));
            string strSex = strJumin.Substring(7, 1);
            if (strSex == "1" || strSex == "2")
                intYear = intYear + 1900;
            else
                intYear = intYear + 2000;

            int intAge = dtBase.Year - intYear;
            if (dtBase.Month < Convert.ToInt32(strJumin.Substring(2, 2))) intAge = intAge - 1;
            return intAge;
        }

        /// <summary>
        /// 윤년
        /// </summary>
        public static bool IsLeapYear(int intYear)
        {
            return (intYear % 4 == 0 && intYear % 100 != 0) || intYear % 400 == 0;
        }
    }
}
