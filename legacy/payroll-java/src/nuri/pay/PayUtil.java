package nuri.pay;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

/**
 * 급여 공통 함수
 * 작성 : 문태호 2008.04
 */
public class PayUtil {

    // 공휴일 (양력만, MMdd). 설, 추석은 근태 쪽에서 '휴일'로 넣어 줌
    static String[] arrHoliday = {"0101", "0301", "0505", "0606", "0815", "1003", "1225"};

    // 공휴일인지 확인
    public static boolean isHoliday(String strMMdd) {
        for (int i = 0; i < arrHoliday.length; i++) {
            if (arrHoliday[i].equals(strMMdd)) return true;
        }
        return false;
    }

    // 문자를 숫자로. 안 되면 0
    public static int toInt(String s) {
        try {
            return Integer.parseInt(s.trim());
        } catch (Exception e) {
            return 0;
        }
    }

    // 날짜 문자열(yyyy-MM-dd)을 Date로. 안 되면 null
    public static Date toDate(String s) {
        try {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
            return sdf.parse(s.trim());
        } catch (Exception e) {
            return null;
        }
    }

    // 두 날짜 사이 일수
    public static int getDays(Date d1, Date d2) {
        long lDiff = d2.getTime() - d1.getTime();
        return (int) (lDiff / (1000 * 60 * 60 * 24)) + 1;
    }

    // 그 달의 평일 수
    public static int getWorkDays(int nYear, int nMonth) {
        Calendar cal = Calendar.getInstance();
        cal.clear();
        cal.set(nYear, nMonth - 1, 1);
        int nLast = cal.getActualMaximum(Calendar.DAY_OF_MONTH);
        int nCnt = 0;
        for (int i = 1; i <= nLast; i++) {
            cal.set(Calendar.DAY_OF_MONTH, i);
            int w = cal.get(Calendar.DAY_OF_WEEK);
            if (w != Calendar.SATURDAY && w != Calendar.SUNDAY) nCnt++;
        }
        return nCnt;
    }

    // 금액에 콤마 (1234567 -> 1,234,567)
    public static String FmtWon(int n) {
        if (n < 0) return "-" + FmtWon(-n);
        String s = String.valueOf(n);
        StringBuffer sb = new StringBuffer();
        int nCnt = 0;
        for (int i = s.length() - 1; i >= 0; i--) {
            sb.insert(0, s.charAt(i));
            nCnt++;
            if (nCnt % 3 == 0 && i != 0) sb.insert(0, ',');
        }
        return sb.toString();
    }

    // 왼쪽을 공백으로 채움
    public static String lpad(String s, int n) {
        StringBuffer sb = new StringBuffer(s);
        while (sb.length() < n) sb.insert(0, ' ');
        return sb.toString();
    }

    // 오른쪽을 공백으로 채움
    public static String rpad(String s, int n) {
        StringBuffer sb = new StringBuffer(s);
        while (sb.length() < n) sb.append(' ');
        return sb.toString();
    }
}
