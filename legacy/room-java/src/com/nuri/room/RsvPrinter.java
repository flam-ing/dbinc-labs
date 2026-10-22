package com.nuri.room;

/**
 * 예약표 출력
 *
 * @author 정태윤
 */
public class RsvPrinter {

    /**
     * 전체 예약표 (날짜별)
     */
    public static void printAll() {
        String[][] arr = getList(null);
        System.out.println("[예약표]");
        if (arr.length == 0) {
            System.out.println("예약 없음");
            return;
        }
        String strOldDate = "";
        for (int i = 0; i < arr.length; i++) {
            if (!arr[i][2].equals(strOldDate)) {
                System.out.println("== " + RsvUtil.fmtDate(arr[i][2]) + " (" + RsvUtil.getYoil(arr[i][2]) + ") ==");
                strOldDate = arr[i][2];
            }
            System.out.println(makeLine(arr[i]));
        }
    }

    /**
     * 하루치 예약표
     */
    public static void printDay(String strDate) {
        String[][] arr = getList(strDate);
        for (int i = 0; i < arr.length; i++) {
            System.out.println("    " + makeLine(arr[i]));
        }
    }

    public static int countDay(String strDate) {
        return getList(strDate).length;
    }

    // 정상 예약만 골라서 정렬
    static String[][] getList(String strDate) {
        int n = 0;
        String[][] tmp = new String[RsvManager.iRsvCnt][];
        for (int i = 0; i < RsvManager.iRsvCnt; i++) {
            if (!"A".equals(RsvManager.arrRsv[i][9])) continue;
            if (strDate != null && !strDate.equals(RsvManager.arrRsv[i][2])) continue;
            tmp[n++] = RsvManager.arrRsv[i];
        }
        String[][] arr = new String[n][];
        for (int i = 0; i < n; i++) {
            arr[i] = tmp[i];
        }
        // 버블정렬 (날짜 + 회의실 + 시작)
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - 1 - i; j++) {
                String k1 = arr[j][2] + arr[j][1] + arr[j][3];
                String k2 = arr[j + 1][2] + arr[j + 1][1] + arr[j + 1][3];
                if (k1.compareTo(k2) > 0) {
                    String[] t = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = t;
                }
            }
        }
        return arr;
    }

    static String makeLine(String[] r) {
        return r[1] + " " + RsvUtil.rpad(RoomInfo.getName(r[1]), 6) + " "
                + RsvUtil.fmtTime(r[3]) + "~" + RsvUtil.fmtTime(r[4]) + " "
                + r[0] + " " + RsvUtil.rpad(r[6], 4) + " "
                + RsvUtil.lpad(r[7], 2, ' ') + "명 " + r[8];
    }
}
