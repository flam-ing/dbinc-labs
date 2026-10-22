package nuri.pay;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStreamReader;
import java.time.YearMonth;
import java.util.Calendar;
import java.util.Date;
import java.util.Hashtable;
import java.util.TimeZone;
import java.util.Vector;

import nuri.pay.ot.OvertimeCalc;
import nuri.payroll.bonus.BonusRules;

/**
 * 월 급여 계산 배치
 *
 * 작성 : 문태호 (전산실) 2008.04
 * 수정 : 2012.01 공제 요율 변경 (문태호)
 *        2015.07 연장/야간/휴일 수당 모듈 연결 (김수진)
 *        2021.10 성과상여 연결 (이도윤)
 *
 * 실행 : java nuri.pay.PayMain 직원파일 근태파일 대상월(yyyy-MM)
 */
public class PayMain {

    // 예전 운영 서버 경로. 지금은 인자로 받음
    // static String EMP_FILE = "D:\\PAY\\IN\\EMP.CSV";
    // static String ATT_FILE = "D:\\PAY\\IN\\ATT.CSV";

    // 2010년까지 오라클에서 직접 읽었음
    static String DB_URL = "jdbc:oracle:thin:@10.10.1.5:1521:PAYDB";
    static String DB_USER = "payadm";
    static String DB_PW = "DUMMY-pay2008!";

    static {
        // 서버 시간대가 GMT라서 날짜가 하루씩 밀림 (2009.02)
        TimeZone.setDefault(TimeZone.getTimeZone("Asia/Seoul"));
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.out.println("사용법: java nuri.pay.PayMain 직원파일 근태파일 대상월(yyyy-MM)");
            System.exit(1);
        }
        String strEmpFile = args[0];
        String strAttFile = args[1];
        String strMonth = args[2];

        if (!strMonth.matches("\\d{4}-\\d{2}")) {
            System.out.println("대상월 형식이 잘못되었습니다: " + strMonth);
            System.exit(1);
        }
        int nYear = Integer.parseInt(strMonth.substring(0, 4));
        int nMonth = Integer.parseInt(strMonth.substring(5, 7));
        if (nMonth < 1 || nMonth > 12) {
            System.out.println("대상월 형식이 잘못되었습니다: " + strMonth);
            System.exit(1);
        }

        System.out.println("누리상사 급여 계산 PAYROLL v1.3");

        // ---- 직원 파일 읽기 ----
        Vector vecEmp = new Vector();
        Hashtable htSeen = new Hashtable();
        BufferedReader br = null;
        try {
            br = new BufferedReader(new InputStreamReader(new FileInputStream(strEmpFile), "UTF-8"));
            // br = new BufferedReader(new InputStreamReader(new FileInputStream(strEmpFile), "MS949"));
            String strLine = br.readLine(); // 첫 줄은 제목
            while ((strLine = br.readLine()) != null) {
                if (strLine.trim().length() == 0) continue;
                String[] arrCol = strLine.split(",", -1);
                if (htSeen.containsKey(arrCol[0])) {
                    System.out.println("** 경고: 중복 사번 " + arrCol[0] + " (뒤의 줄은 무시)");
                    continue;
                }
                htSeen.put(arrCol[0], "Y");
                vecEmp.addElement(arrCol);
            }
        } catch (FileNotFoundException e) {
            System.out.println("파일을 찾을 수 없습니다: " + strEmpFile);
            System.exit(2);
        } finally {
            if (br != null) try { br.close(); } catch (Exception e) {}
        }

        // ---- 근태 (2015.07 김수진) ----
        OvertimeCalc ot = new OvertimeCalc(nYear, nMonth);
        ot.load(strAttFile);

        Calendar cal = Calendar.getInstance();
        cal.clear();
        cal.set(nYear, nMonth - 1, 1);
        Date dtFrom = cal.getTime();
        cal.set(Calendar.DAY_OF_MONTH, cal.getActualMaximum(Calendar.DAY_OF_MONTH));
        Date dtTo = cal.getTime();

        System.out.println("==================================================");
        System.out.println(" 급여 대장  대상월 " + strMonth);
        System.out.println("==================================================");

        int nCnt = 0;
        int nTotGross = 0;
        int nTotNet = 0;
        Vector vecDept = new Vector();
        Hashtable htDept = new Hashtable();

        for (int i = 0; i < vecEmp.size(); i++) {
            String[] a = (String[]) vecEmp.elementAt(i);
            String strEmpNo = a[0].trim();
            String strName = a[1];
            String strDept = a[2];
            String strGrade = a[3];
            Date dtHire = PayUtil.toDate(a[4]);
            Date dtRetire = PayUtil.toDate(a[5]);
            int nBaseFull = PayUtil.toInt(a[6]);
            boolean bSawoo = "Y".equals(a[7]);

            // 이번 달 재직자만
            if (dtHire != null && dtHire.after(dtTo)) continue;
            if (dtRetire != null && dtRetire.before(dtFrom)) continue;

            if (nBaseFull == 0) {
                System.out.println("** 경고: " + strEmpNo + " 기본급이 0원입니다. 인사팀 확인 필요");
            }

            // 입사/퇴사 달은 일할 계산 (30일 기준)
            int nBasePay = nBaseFull;
            String strDayInfo = "";
            boolean bIn = dtHire != null && dtHire.after(dtFrom);
            boolean bOut = dtRetire != null && dtRetire.before(dtTo);
            if (bIn || bOut) {
                Date d1 = bIn ? dtHire : dtFrom;
                Date d2 = bOut ? dtRetire : dtTo;
                int nDays = PayUtil.getDays(d1, d2);
                if (nDays > 30) nDays = 30;
                nBasePay = nBaseFull * nDays / 30;
                strDayInfo = "  (일할 " + nDays + "/30)";
            }

            // 연장/야간/휴일 : {연장분, 야간분, 휴일분, 연장수당, 야간수당, 휴일수당}
            long[] arrOt = ot.payFor(strEmpNo, nBaseFull, strGrade);
            int nOt = (int) arrOt[3];
            int nNight = (int) arrOt[4];
            int nHol = (int) arrOt[5];

            // 성과상여 (2021.10 이도윤)
            int nBonus = (int) BonusRules.bonusFor(
                    new BonusRules.Target(strEmpNo, nBaseFull, a[8], a[4].trim()),
                    YearMonth.of(nYear, nMonth));

            // 식대 비과세 (2009.03 인사팀 요청으로 뺌)
            // int nMeal = 100000;
            // nTaxable = nGross - nMeal;

            int nGross = nBasePay + nOt + nNight + nHol + nBonus;
            int[] arrDed = Deduct.calc(nBasePay, nGross, bSawoo);
            int nDed = 0;
            for (int k = 0; k < arrDed.length; k++) nDed += arrDed[k];
            int nNet = (nGross - nDed) / 10 * 10; // 실지급 10원 미만 절사

            System.out.println("[" + strEmpNo + "] " + strName + "  " + strDept + " / " + strGrade);
            prt("기본급", nBasePay, strDayInfo);
            prt("연장수당", nOt, "  (" + arrOt[0] + "분)");
            prt("야간수당", nNight, "  (" + arrOt[1] + "분)");
            prt("휴일수당", nHol, "  (" + arrOt[2] + "분)");
            prt("성과상여", nBonus, "");
            prt("지급계", nGross, "");
            prt("연금", arrDed[0], "");
            prt("건강보험", arrDed[1], "");
            prt("고용보험", arrDed[2], "");
            prt("소득세", arrDed[3], "");
            prt("사우회비", arrDed[4], "");
            prt("공제계", nDed, "");
            prt("실지급", nNet, nNet < 0 ? "  ** 확인 필요" : "");
            System.out.println();

            nCnt++;
            nTotGross += nGross;
            nTotNet += nNet;
            if (!htDept.containsKey(strDept)) {
                vecDept.addElement(strDept);
                htDept.put(strDept, Integer.valueOf(0));
            }
            int nOld = ((Integer) htDept.get(strDept)).intValue();
            htDept.put(strDept, Integer.valueOf(nOld + nNet));
        }

        System.out.println("==================================================");
        System.out.println(" 합계  " + nCnt + "명");
        prt("지급계", nTotGross, "");
        prt("공제계", Deduct.nTotDeduct, "");
        prt("실지급", nTotNet, "");
        System.out.println(" 부서별 실지급");
        for (int i = 0; i < vecDept.size(); i++) {
            String d = (String) vecDept.elementAt(i);
            prt(d, ((Integer) htDept.get(d)).intValue(), "");
        }
        System.out.println("==================================================");
    }

    static void prt(String strLabel, int nAmt, String strTail) {
        System.out.println("  " + PayUtil.rpad(strLabel, 8) + PayUtil.lpad(PayUtil.FmtWon(nAmt), 12) + strTail);
    }
}
