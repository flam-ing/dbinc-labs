package com.nuri.room;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

/**
 * 공통 유틸
 *
 * @author 정태윤
 */
public class RsvUtil {

    private static final String[] YOIL = {"", "일", "월", "화", "수", "목", "금", "토"};

    public static String nvl(String s) {
        if (s == null) return "";
        return s.trim();
    }

    /**
     * 회의실 번호 체크
     */
    public static boolean chkRoom(String[] arr, int idx) {
        String s = nvl(arr[idx]);
        for (int i = 0; i < RoomInfo.ROOMS.length; i++) {
            if (RoomInfo.ROOMS[i][1].equals(s)) {
                arr[idx] = RoomInfo.ROOMS[i][0];
                return true;
            }
        }
        return RoomInfo.getIdx(s) >= 0;
    }

    /**
     * 날짜 체크 (yyyyMMdd)
     */
    public static boolean isDate(String strYmd) {
        if (strYmd == null || strYmd.length() != 8) return false;
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd");
        sdf.setLenient(false);
        try {
            sdf.parse(strYmd);
        } catch (ParseException e) {
            return false;
        }
        return true;
    }

    /**
     * 두 날짜 사이 일수
     */
    public static long dayDiff(String strFrom, String strTo) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd");
        try {
            Date d1 = sdf.parse(strFrom);
            Date d2 = sdf.parse(strTo);
            return (d2.getTime() - d1.getTime()) / (1000 * 60 * 60 * 24);
        } catch (Exception e) {
        }
        return 0;
    }

    /**
     * HHmm -> 분
     */
    public static int toMin(String strHHmm) {
        int i = Integer.parseInt(strHHmm);
        return (i / 100) * 60 + (i % 100);
    }

    /**
     * 0900 -> 09:00
     */
    public static String fmtTime(String strHHmm) {
        return strHHmm.substring(0, 2) + ":" + strHHmm.substring(2);
    }

    /**
     * 20100315 -> 2010-03-15
     */
    public static String fmtDate(String strYmd) {
        return strYmd.substring(0, 4) + "-" + strYmd.substring(4, 6) + "-" + strYmd.substring(6);
    }

    public static String getYoil(String strYmd) {
        try {
            Date d = new SimpleDateFormat("yyyyMMdd").parse(strYmd);
            Calendar cal = Calendar.getInstance();
            cal.setTime(d);
            return YOIL[cal.get(Calendar.DAY_OF_WEEK)];
        } catch (Exception e) {
            return "";
        }
    }

    public static String lpad(String s, int len, char c) {
        StringBuffer sb = new StringBuffer();
        for (int i = s.length(); i < len; i++) {
            sb.append(c);
        }
        sb.append(s);
        return sb.toString();
    }

    public static String rpad(String s, int len) {
        StringBuffer sb = new StringBuffer(s);
        while (sb.length() < len) {
            sb.append(' ');
        }
        return sb.toString();
    }

    /**
     * 임원 여부
     */
    public static boolean isExec(String strEmpNo) {
        // 총무팀도 임원 취급
        return strEmpNo.startsWith("9") || strEmpNo.equals("10001");
    }

    /**
     * 현재시각 yyyyMMddHHmm (테스트용)
     */
    public static String getNow() {
        return new SimpleDateFormat("yyyyMMddHHmm").format(new Date());
    }
}
