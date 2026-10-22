package com.nuri.room;

import java.util.Vector;

/**
 * 회의실 예약 처리
 *
 * @author 정태윤 (전산팀)
 * @since 2010.02.08
 *
 * arrRsv 구조
 *   [0] 예약번호  [1] 회의실  [2] 날짜  [3] 시작  [4] 종료
 *   [5] 사번      [6] 이름    [7] 제목  [8] 상태 (A 정상, C 취소)
 *
 * 2010.07.19 그룹웨어 DB 막혀서 파일 방식으로 변경 (임시)
 */
public class RsvManager implements Const {

    public static String[][] arrRsv = new String[500][10];
    public static int iRsvCnt = 0;
    public static int iSeq = 0;

    public static int iOkCnt = 0;
    public static int iErrCnt = 0;

    public static Vector vHist = new Vector();   // 이력 (안씀)

    /*
    static Connection getConn() throws Exception {
        Class.forName("oracle.jdbc.driver.OracleDriver");
        return DriverManager.getConnection("jdbc:oracle:thin:@10.10.1.20:1521:GWDB", "gw_room", "DUMMY-gwroom2010");
    }

    static void insertRsv(String[] r) throws Exception {
        Connection conn = getConn();
        Statement stmt = conn.createStatement();
        stmt.executeUpdate("INSERT INTO TB_ROOM_RSV VALUES ('" + r[0] + "','" + r[1] + "','" + r[2] + "','"
            + r[3] + "','" + r[4] + "','" + r[5] + "','" + r[6] + "','" + r[7] + "','A')");
        stmt.close();
        conn.close();
    }
    */

    public static void process(int iLineNo, String strLine) {
        String[] arr = strLine.split(",");
        String strCmd = arr[0].trim().toUpperCase();
        try {
            if (strCmd.equals("RSV")) {
                doReserve(iLineNo, arr);
            } else if (strCmd.equals("CXL")) {
                doCancel(iLineNo, arr);
            } else if (strCmd.equals("CHG")) {
                doChange(iLineNo, arr);
            } else if (strCmd.equals("QRY")) {
                doQuery(iLineNo, arr);
            } else {
                err(iLineNo, strCmd, "알 수 없는 명령");
            }
        } catch (Exception e) {
            // e.printStackTrace();
            err(iLineNo, strCmd, "형식 오류");
        }
    }

    /**
     * 예약
     * RSV,요청시각,사번,이름,회의실,날짜,시작,종료,인원,제목
     */
    static void doReserve(int iLineNo, String[] arr) throws Exception {
        String strReqTm = arr[1].trim();
        String strEmpNo = arr[2].trim();
        String strName = arr[3].trim();
        if (!RsvUtil.chkRoom(arr, 4)) {
            err(iLineNo, "RSV", "없는 회의실 " + arr[4].trim());
            return;
        }
        String strRoom = arr[4].trim();
        String strDate = arr[5].trim();
        String strFrom = arr[6].trim();
        String strTo = arr[7].trim();
        int iCnt = 0;
        try {
            iCnt = Integer.parseInt(arr[8].trim());
        } catch (Exception e) {}
        String strTitle = arr[9].trim();

        // 날짜
        if (!RsvUtil.isDate(strDate)) {
            err(iLineNo, "RSV", "날짜 오류 " + strDate);
            return;
        }
        // 30분 단위
        int iFrom = Integer.parseInt(strFrom);
        int iTo = Integer.parseInt(strTo);
        if (iFrom % 100 != 0 && iFrom % 100 != 30 || iTo % 100 != 0 && iTo % 100 != 30) {
            err(iLineNo, "RSV", "30분 단위로만 예약 " + strFrom + "~" + strTo);
            return;
        }
        // 운영 시간
        int iOpen = 900;
        if (strRoom.equals("R05")) iOpen = 700;
        if (iFrom < iOpen || iTo > 1800 || iFrom >= iTo) {
            err(iLineNo, "RSV", "예약 시간 오류 " + strFrom + "~" + strTo);
            return;
        }
        // 최대 3시간 (임원 제외)
        if (RsvUtil.toMin(strTo) - RsvUtil.toMin(strFrom) > 180 && !strEmpNo.startsWith("9")) {
            err(iLineNo, "RSV", "3시간 초과");
            return;
        }
        // 지난 시간
        if ((strDate + strFrom).compareTo(strReqTm) < 0) {
            err(iLineNo, "RSV", "지난 시간");
            return;
        }
        // 2주
        if (RsvUtil.dayDiff(strReqTm.substring(0, 8), strDate) > 14) {
            err(iLineNo, "RSV", "2주 넘게 남은 날짜");
            return;
        }
        // 정원
        if (iCnt > RoomInfo.getCapa(strRoom) + 2) {
            err(iLineNo, "RSV", "정원 초과 " + iCnt + "명 (정원 " + RoomInfo.getCapa(strRoom) + "명)");
            return;
        }
        // 대회의실 점심 청소
        if (strRoom.equals("R01") && strFrom.compareTo("1300") < 0 && strTo.compareTo("1200") > 0) {
            err(iLineNo, "RSV", "청소 시간 (12:00~13:00)");
            return;
        }
        // 겹치는 예약
        for (int i = 0; i < iRsvCnt; i++) {
            if (arrRsv[i][9].equals("C")) continue;
            if (!arrRsv[i][1].equals(strRoom)) continue;
            String strS1 = arrRsv[i][2] + arrRsv[i][3];
            String strE1 = arrRsv[i][2] + arrRsv[i][4];
            String strS2 = strDate + strFrom;
            String strE2 = strDate + strTo;
            if (strS2.compareTo(strE1) < 0 && strE2.compareTo(strS1) > 0) {
                err(iLineNo, "RSV", "겹침 " + arrRsv[i][0] + " "
                        + RsvUtil.fmtTime(arrRsv[i][3]) + "~" + RsvUtil.fmtTime(arrRsv[i][4]));
                return;
            }
        }

        iSeq++;
        String strNo = "R" + RsvUtil.lpad(String.valueOf(iSeq), 4, '0');
        arrRsv[iRsvCnt][0] = strNo;
        arrRsv[iRsvCnt][1] = strRoom;
        arrRsv[iRsvCnt][2] = strDate;
        arrRsv[iRsvCnt][3] = strFrom;
        arrRsv[iRsvCnt][4] = strTo;
        arrRsv[iRsvCnt][5] = strEmpNo;
        arrRsv[iRsvCnt][6] = strName;
        arrRsv[iRsvCnt][7] = String.valueOf(iCnt);
        arrRsv[iRsvCnt][8] = strTitle;
        arrRsv[iRsvCnt][9] = "A";
        iRsvCnt++;
        // sendSms(strEmpNo, strNo + " 예약되었습니다");

        ok(iLineNo, "RSV", strNo + " " + RoomInfo.getName(strRoom) + " " + RsvUtil.fmtDate(strDate) + " "
                + RsvUtil.fmtTime(strFrom) + "~" + RsvUtil.fmtTime(strTo) + " " + strName + " " + iCnt + "명");
    }

    /**
     * 취소
     * CXL,요청시각,사번,예약번호
     */
    static void doCancel(int iLineNo, String[] arr) throws Exception {
        String strReqTm = arr[1].trim();
        String strEmpNo = arr[2].trim();
        String strNo = arr[3].trim();

        int idx = -1;
        for (int i = 0; i < iRsvCnt; i++) {
            if (arrRsv[i][0].equals(strNo)) {
                idx = i;
                break;
            }
        }
        if (idx == -1) {
            err(iLineNo, "CXL", "없는 예약 " + strNo);
            return;
        }
        if (arrRsv[idx][9].equals("C")) {
            err(iLineNo, "CXL", "이미 취소된 예약 " + strNo);
            return;
        }
        // 본인만 (총무팀은 가능)
        if (!arrRsv[idx][5].equals(strEmpNo) && !strEmpNo.equals("10001")) {
            err(iLineNo, "CXL", "본인 예약만 취소 가능 " + strNo);
            return;
        }
        arrRsv[idx][9] = "C";
        ok(iLineNo, "CXL", strNo + " 취소 " + RoomInfo.getName(arrRsv[idx][1]) + " " + RsvUtil.fmtDate(arrRsv[idx][2])
                + " " + RsvUtil.fmtTime(arrRsv[idx][3]) + "~" + RsvUtil.fmtTime(arrRsv[idx][4]));
    }

    /**
     * 변경
     * CHG,요청시각,사번,예약번호,날짜,시작,종료
     */
    static void doChange(int iLineNo, String[] arr) throws Exception {
        String strReqTm = arr[1].trim();
        String strEmpNo = arr[2].trim();
        String strNo = arr[3].trim();
        String strDate = arr[4].trim();
        String strFrom = arr[5].trim();
        String strTo = arr[6].trim();

        int idx = -1;
        for (int i = 0; i < iRsvCnt; i++) {
            if (arrRsv[i][0].equals(strNo)) {
                idx = i;
                break;
            }
        }
        if (idx == -1) {
            err(iLineNo, "CHG", "없는 예약 " + strNo);
            return;
        }
        if (arrRsv[idx][9].equals("C")) {
            err(iLineNo, "CHG", "취소된 예약 " + strNo);
            return;
        }
        if (!arrRsv[idx][5].equals(strEmpNo) && !strEmpNo.equals("10001")) {
            err(iLineNo, "CHG", "본인 예약만 변경 가능 " + strNo);
            return;
        }
        String strRoom = arrRsv[idx][1];

        // 날짜
        if (!RsvUtil.isDate(strDate)) {
            err(iLineNo, "CHG", "날짜 오류 " + strDate);
            return;
        }
        // 30분 단위
        int iFrom = Integer.parseInt(strFrom);
        int iTo = Integer.parseInt(strTo);
        if (iFrom % 100 != 0 && iFrom % 100 != 30 || iTo % 100 != 0 && iTo % 100 != 30) {
            err(iLineNo, "CHG", "30분 단위로만 예약 " + strFrom + "~" + strTo);
            return;
        }
        // 운영 시간
        int iOpen = 900;
        if (strRoom.equals("R05")) iOpen = 700;
        if (iFrom < iOpen || iTo > 1800 || iFrom >= iTo) {
            err(iLineNo, "CHG", "예약 시간 오류 " + strFrom + "~" + strTo);
            return;
        }
        // 최대 3시간 (임원 제외)
        if (RsvUtil.toMin(strTo) - RsvUtil.toMin(strFrom) > 180 && !strEmpNo.startsWith("9")) {
            err(iLineNo, "CHG", "3시간 초과");
            return;
        }
        // 지난 시간
        if ((strDate + strFrom).compareTo(strReqTm) < 0) {
            err(iLineNo, "CHG", "지난 시간");
            return;
        }
        // 2주
        if (RsvUtil.dayDiff(strReqTm.substring(0, 8), strDate) > 14) {
            err(iLineNo, "CHG", "2주 넘게 남은 날짜");
            return;
        }
        // 겹치는 예약
        for (int i = 0; i < iRsvCnt; i++) {
            if (i == idx) continue;
            if (arrRsv[i][9].equals("C")) continue;
            if (!arrRsv[i][1].equals(strRoom)) continue;
            String strS1 = arrRsv[i][2] + arrRsv[i][3];
            String strE1 = arrRsv[i][2] + arrRsv[i][4];
            String strS2 = strDate + strFrom;
            String strE2 = strDate + strTo;
            if (strS2.compareTo(strE1) < 0 && strE2.compareTo(strS1) > 0) {
                err(iLineNo, "CHG", "겹침 " + arrRsv[i][0] + " "
                        + RsvUtil.fmtTime(arrRsv[i][3]) + "~" + RsvUtil.fmtTime(arrRsv[i][4]));
                return;
            }
        }

        String strOld = RsvUtil.fmtDate(arrRsv[idx][2]) + " "
                + RsvUtil.fmtTime(arrRsv[idx][3]) + "~" + RsvUtil.fmtTime(arrRsv[idx][4]);
        arrRsv[idx][2] = strDate;
        arrRsv[idx][3] = strFrom;
        arrRsv[idx][4] = strTo;
        ok(iLineNo, "CHG", strNo + " " + RoomInfo.getName(strRoom) + " " + strOld + " -> "
                + RsvUtil.fmtDate(strDate) + " " + RsvUtil.fmtTime(strFrom) + "~" + RsvUtil.fmtTime(strTo));
    }

    /**
     * 조회
     * QRY,요청시각,날짜
     */
    static void doQuery(int iLineNo, String[] arr) throws Exception {
        String strDate = arr[2].trim();
        if (!RsvUtil.isDate(strDate)) {
            err(iLineNo, "QRY", "날짜 오류 " + strDate);
            return;
        }
        ok(iLineNo, "QRY", RsvUtil.fmtDate(strDate) + " (" + RsvUtil.getYoil(strDate) + ") "
                + RsvPrinter.countDay(strDate) + "건");
        RsvPrinter.printDay(strDate);
    }

    static void ok(int iLineNo, String strCmd, String strMsg) {
        iOkCnt++;
        System.out.println("[" + RsvUtil.lpad(String.valueOf(iLineNo), 4, '0') + "] " + strCmd + " OK  " + strMsg);
    }

    static void err(int iLineNo, String strCmd, String strMsg) {
        iErrCnt++;
        System.out.println("[" + RsvUtil.lpad(String.valueOf(iLineNo), 4, '0') + "] " + strCmd + " ERR " + strMsg);
    }

    // 예약 문자 알림 - 문자 서버 계약 끝나서 안씀 (2010.12)
    static void sendSms(String strEmpNo, String strMsg) {
        String strUrl = "http://10.10.1.35:8080/sms/send.jsp?emp=" + strEmpNo + "&msg=" + strMsg
                + "&key=DUMMY-SMS-KEY-0000";
        // TODO 문자 서버 연동
        System.out.println(strUrl);
    }
}
