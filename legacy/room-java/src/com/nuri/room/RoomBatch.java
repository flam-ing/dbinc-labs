package com.nuri.room;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.TimeZone;

/**
 * 회의실 예약 일괄 처리
 *
 * 사용법 : java com.nuri.room.RoomBatch [명령파일]
 *
 * @author 정태윤 (전산팀)
 * @since 2010.02.08
 */
public class RoomBatch {

    public static void main(String[] args) {

        // 지우지 마시오!!! (2011.03.14)
        TimeZone.setDefault(TimeZone.getTimeZone("Asia/Seoul"));

        if (args.length < 1) {
            System.out.println("사용법: RoomBatch [명령파일]");
            System.exit(1);
        }

        String strFileNm = args[0];
        BufferedReader br = null;
        try {
            br = new BufferedReader(new InputStreamReader(new FileInputStream(strFileNm), "UTF-8"));
        } catch (Exception e) {
            System.out.println("파일을 열 수 없습니다 : " + strFileNm);
            System.exit(2);
        }

        System.out.println("회의실 예약 처리 : " + strFileNm);
        System.out.println("------------------------------------------------------------");

        int iLineNo = 0;
        String strLine = null;
        try {
            while ((strLine = br.readLine()) != null) {
                iLineNo++;
                strLine = strLine.trim();
                if (strLine.equals("")) continue;
                if (strLine.startsWith("#")) continue;   // 주석
                RsvManager.process(iLineNo, strLine);
            }
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                br.close();
            } catch (Exception e) {
            }
        }

        System.out.println("------------------------------------------------------------");
        RsvPrinter.printAll();
        System.out.println("------------------------------------------------------------");
        System.out.println("명령 " + (RsvManager.iOkCnt + RsvManager.iErrCnt) + "건 : 성공 "
                + RsvManager.iOkCnt + "건, 실패 " + RsvManager.iErrCnt + "건");
    }
}
