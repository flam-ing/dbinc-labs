package com.nuri.mall.point;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

/**
 * 날짜 유틸
 */
public class DateUtil {

    public static String today() {
        return new SimpleDateFormat("yyyy-MM-dd").format(new Date());
    }

    /**
     * 소멸일 : 적립일로부터 1년
     */
    public static String getExpireDate(String strDt) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        try {
            Calendar cal = Calendar.getInstance();
            cal.setTime(sdf.parse(strDt));
            cal.add(Calendar.YEAR, 1);
            cal.set(Calendar.DAY_OF_MONTH, cal.getActualMaximum(Calendar.DAY_OF_MONTH));
            return sdf.format(cal.getTime());
        } catch (ParseException e) {
            return strDt;
        }
    }

    /**
     * 소멸 여부
     */
    public static boolean isExpired(String expireDt, String baseDt) {
        return expireDt.compareTo(baseDt) <= 0;
    }
}
