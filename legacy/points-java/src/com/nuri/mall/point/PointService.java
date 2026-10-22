package com.nuri.mall.point;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.NumberFormat;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

/**
 * 포인트 적립/사용/소멸 배치
 *
 * @author 한동욱 (커머스개발팀)
 * @since 2016.04.11
 */
public class PointService {

    private static PointService instance;

    public static PointService getInstance() {
        if (instance == null) {
            instance = new PointService();
        }
        return instance;
    }

    private PointService() {
    }

    // 적립률
    private static final double RATE_NORMAL = 0.01;
    private static final double RATE_VIP = 0.02;

    private static final String CS_MAIL = "point-cs@nurimall.example";

    private Map<String, MemberVo> memberMap = new HashMap<>();
    private Map<String, List<Map<String, Object>>> lotMap = new HashMap<>();
    private Map<String, int[]> sumMap = new TreeMap<>();   // 0 적립 1 사용 2 회수 3 조정 4 소멸

    private int noticeCnt = 0;
    private int alertCnt = 0;

    public void execute(String txFile, String memberFile, String baseDt, String outDir) {

        // 1. 회원
        MemberDao memberDao = new MemberDao();
        List<MemberVo> members = memberDao.selectList(memberFile);
        for (MemberVo m : members) {
            memberMap.put(m.getMemberId(), m);
            lotMap.put(m.getMemberId(), new ArrayList<Map<String, Object>>());
            sumMap.put(m.getMemberId(), new int[5]);
        }

        // 2. 거래
        TxDao txDao = new TxDao();
        List<TxVo> txList = txDao.selectList(txFile);

        System.out.println("=== 누리몰 포인트 배치 (기준일 " + baseDt + ") ===");
        System.out.println("회원 " + members.size() + "명, 거래 " + txDao.readCnt + "줄 (형식 오류 " + txDao.errCnt + "줄 건너뜀)");

        // 중복 거래 빼기 (2016.09 중복 적립 장애)
        Set<String> txIds = new HashSet<>();
        List<TxVo> list = new ArrayList<>();
        int futureCnt = 0;
        for (TxVo tx : txList) {
            if (txIds.contains(tx.txId)) {
                System.out.println("[경고] 중복 거래 건너뜀 " + tx.txId);
                continue;
            }
            txIds.add(tx.txId);
            if (tx.txDt.substring(0, 10).compareTo(baseDt) > 0) {
                futureCnt++;
                continue;
            }
            list.add(tx);
        }
        System.out.println("기준일 이후 거래 " + futureCnt + "건 제외");

        list.sort((a, b) -> a.txDt.compareTo(b.txDt));

        // 3. 계산
        for (TxVo tx : list) {
            MemberVo m = memberMap.get(tx.memberId);
            if (m == null) {
                System.out.println("[경고] 회원 없음 " + tx.memberId + " (" + tx.txId + ")");
                continue;
            }
            int[] sum = sumMap.get(tx.memberId);
            List<Map<String, Object>> lots = lotMap.get(tx.memberId);
            String txDate = tx.txDt.substring(0, 10);

            // 소멸 먼저
            for (Map<String, Object> lot : lots) {
                int remain = (Integer) lot.get("remain");
                if (remain > 0 && ((String) lot.get("expireDt")).compareTo(txDate) < 0) {
                    sum[4] += remain;
                    lot.put("remain", 0);
                }
            }

            if (tx.type.equals("BUY")) {
                double rate = RATE_NORMAL;
                if ("VIP".equals(m.getGrade())) rate = RATE_VIP;
                if ("STAFF".equals(m.getGrade())) rate = 0;
                // 창립 기념 주간 2배
                if (tx.txDt.compareTo("2016-10-01") >= 0 && tx.txDt.compareTo("2016-10-07") <= 0) {
                    rate = rate * 2;
                }
                // 2017.01 서예진 - 설 연휴 2배
                LocalDate d = LocalDate.parse(txDate);
                if (!d.isBefore(LocalDate.of(2017, 1, 26)) && !d.isAfter(LocalDate.of(2017, 1, 30))) {
                    rate = rate * 2;
                }
                double supply = tx.amount / 1.1;
                int point = (int) (supply * rate);
                if (point <= 0) continue;

                Map<String, Object> lot = new HashMap<>();
                lot.put("earnDt", txDate);
                lot.put("expireDt", DateUtil.getExpireDate(txDate));
                lot.put("orig", point);
                lot.put("remain", point);
                lot.put("orderNo", tx.orderNo);
                lots.add(lot);
                sum[0] += point;

            } else if (tx.type.equals("USE")) {
                int bal = 0;
                for (Map<String, Object> lot : lots) {
                    bal += (Integer) lot.get("remain");
                }
                if (tx.amount > bal) {
                    System.out.println("[경고] 사용 거부 " + tx.memberId + " 요청 " + tx.amount + " 잔액 " + bal + " (" + tx.txId + ")");
                    writeCsAlert(outDir, tx, m, "사용 요청 " + fmt(tx.amount) + "점, 잔액 " + fmt(bal) + "점 (사용 거부)");
                    continue;
                }
                int need = tx.amount;
                for (Map<String, Object> lot : lots) {
                    int remain = (Integer) lot.get("remain");
                    if (remain == 0) continue;
                    int take = Math.min(remain, need);
                    lot.put("remain", remain - take);
                    need = need - take;
                    if (need == 0) break;
                }
                sum[1] += tx.amount;

            } else if (tx.type.equals("CANCEL")) {
                Map<String, Object> org = null;
                for (Map<String, Object> lot : lots) {
                    if (tx.orderNo.equals(lot.get("orderNo"))) {
                        org = lot;
                        break;
                    }
                }
                if (org == null) {
                    System.out.println("[경고] 원 주문 없음 " + tx.orderNo + " (" + tx.txId + ")");
                    continue;
                }
                int need = (Integer) org.get("orig");
                int orgRemain = (Integer) org.get("remain");
                int orgTake = Math.min(orgRemain, need);
                org.put("remain", orgRemain - orgTake);
                need = need - orgTake;
                // 이미 쓴 만큼은 다른 포인트에서
                for (Map<String, Object> lot : lots) {
                    int remain = (Integer) lot.get("remain");
                    if (remain == 0) continue;
                    int take = Math.min(remain, need);
                    lot.put("remain", remain - take);
                    need = need - take;
                    if (need == 0) break;
                }
                if (need > 0) {
                    System.out.println("[경고] 회수 부족 " + tx.memberId + " " + need + "점 (" + tx.txId + ")");
                    writeCsAlert(outDir, tx, m, "회수 못 한 포인트 " + fmt(need) + "점");
                }
                sum[2] += (Integer) org.get("orig") - need;

            } else if (tx.type.equals("ADJ")) {
                if (tx.amount > 0) {
                    Map<String, Object> lot = new HashMap<>();
                    lot.put("earnDt", txDate);
                    lot.put("expireDt", DateUtil.getExpireDate(txDate));
                    lot.put("orig", tx.amount);
                    lot.put("remain", tx.amount);
                    lot.put("orderNo", tx.txId);
                    lots.add(lot);
                    sum[3] += tx.amount;
                } else {
                    int need = -tx.amount;
                    int done = 0;
                    for (Map<String, Object> lot : lots) {
                        int remain = (Integer) lot.get("remain");
                        if (remain == 0) continue;
                        int take = Math.min(remain, need);
                        lot.put("remain", remain - take);
                        need = need - take;
                        done = done + take;
                        if (need == 0) break;
                    }
                    sum[3] -= done;
                }
            }
        }

        // 4. 기준일 소멸
        for (String memberId : sumMap.keySet()) {
            for (Map<String, Object> lot : lotMap.get(memberId)) {
                int remain = (Integer) lot.get("remain");
                if (remain > 0 && ((String) lot.get("expireDt")).compareTo(baseDt) < 0) {
                    sumMap.get(memberId)[4] += remain;
                    lot.put("remain", 0);
                }
            }
        }

        // 5. 출력, 소멸 예정 알림
        String limitDt = LocalDate.parse(baseDt).plusDays(30).toString();
        String line = "--------------------------------------------------------------------------";
        System.out.println(line);
        System.out.println(String.format("%-6s %-4s %-6s %7s %7s %7s %7s %7s %7s %7s",
                "회원", "이름", "등급", "적립", "사용", "회수", "조정", "소멸", "잔액", "소멸예정"));
        int[] total = new int[7];
        for (String memberId : sumMap.keySet()) {
            MemberVo m = memberMap.get(memberId);
            int[] sum = sumMap.get(memberId);
            int bal = 0;
            int soon = 0;
            String firstDt = null;
            for (Map<String, Object> lot : lotMap.get(memberId)) {
                int remain = (Integer) lot.get("remain");
                String exp = (String) lot.get("expireDt");
                bal += remain;
                if (remain > 0 && exp.compareTo(baseDt) >= 0 && exp.compareTo(limitDt) <= 0) {
                    soon += remain;
                    if (firstDt == null || exp.compareTo(firstDt) < 0) firstDt = exp;
                }
            }
            System.out.println(String.format("%-6s %-4s %-6s %7d %7d %7d %7d %7d %7d %7d",
                    memberId, m.getName(), m.getGrade(), sum[0], sum[1], sum[2], sum[3], sum[4], bal, soon));
            for (int i = 0; i < 5; i++) total[i] += sum[i];
            total[5] += bal;
            total[6] += soon;

            if (soon > 0 && m.getEmail() != null && !m.getEmail().equals("")) {
                // if ("Y".equals(m.getAdAgree())) {    2016.11 법무팀 요청으로 뺌
                writeNotice(outDir, baseDt, m, soon, firstDt, bal);
                // }
            }
        }
        System.out.println(line);
        System.out.println(String.format("%-6s %-4s %-6s %7d %7d %7d %7d %7d %7d %7d",
                "합계", "", "", total[0], total[1], total[2], total[3], total[4], total[5], total[6]));
        System.out.println("소멸 예정 기간: " + baseDt + " ~ " + limitDt);
        System.out.println("알림 파일: 소멸 예정 " + noticeCnt + "건, CS " + alertCnt + "건");
    }

    private void writeNotice(String outDir, String baseDt, MemberVo m, int soon, String firstDt, int bal) {
        String fileNm = "EXP_" + baseDt.substring(0, 7).replace("-", "") + "_" + m.getMemberId() + ".txt";
        try {
            File dir = new File(outDir);
            if (!dir.exists()) dir.mkdirs();
            BufferedWriter bw = new BufferedWriter(new FileWriter(new File(dir, fileNm)));
            bw.write("TO: " + m.getEmail());
            bw.newLine();
            bw.write("SUBJECT: [누리몰] 포인트 소멸 예정 안내");
            bw.newLine();
            bw.newLine();
            bw.write(m.getName() + " 회원님, 30일 안에 소멸되는 포인트가 " + fmt(soon) + "점 있습니다.");
            bw.newLine();
            bw.write("가장 빠른 소멸일: " + firstDt);
            bw.newLine();
            bw.write("현재 잔액: " + fmt(bal) + "점");
            bw.newLine();
            bw.close();
            noticeCnt++;
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void writeCsAlert(String outDir, TxVo tx, MemberVo m, String msg) {
        try {
            File dir = new File(outDir);
            if (!dir.exists()) dir.mkdirs();
            BufferedWriter bw = new BufferedWriter(new FileWriter(outDir + File.separator + "CS_" + tx.txId + ".txt"));
            bw.write("TO: " + CS_MAIL);
            bw.newLine();
            bw.write("SUBJECT: [포인트배치] 확인 요청 " + tx.txId);
            bw.newLine();
            bw.newLine();
            bw.write("회원: " + m.getMemberId() + " " + m.getName());
            bw.newLine();
            bw.write("거래: " + tx.txId + " " + tx.type + " " + tx.orderNo + " " + tx.txDt);
            bw.newLine();
            bw.write("내용: " + msg);
            bw.newLine();
            bw.close();
            alertCnt++;
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private String fmt(int n) {
        return NumberFormat.getInstance(Locale.KOREA).format(n);
    }

    // 문자 발송 (2016.06 문자 단가 문제로 보류)
    public void sendSms(String phone, String msg) {
        String url = "https://sms.nurimall.example/api/send?key=DUMMY-SMS-0000&to=" + phone + "&text=" + msg;
        System.out.println("SMS " + url);
    }
}
