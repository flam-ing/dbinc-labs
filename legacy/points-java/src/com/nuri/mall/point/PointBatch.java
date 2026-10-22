package com.nuri.mall.point;

/**
 * 포인트 배치 실행
 *
 * java com.nuri.mall.point.PointBatch [거래CSV] [회원CSV] [기준일 yyyy-MM-dd] [outbox폴더]
 *
 * @author 한동욱
 */
public class PointBatch {

    private static final String BASE_DIR = "C:\\points\\data\\";

    public static void main(String[] args) {
        String txFile = BASE_DIR + "transactions.csv";
        String memberFile = BASE_DIR + "members.csv";
        String baseDt = DateUtil.today();
        String outDir = BASE_DIR + "outbox";

        if (args.length > 0) txFile = args[0];
        if (args.length > 1) memberFile = args[1];
        if (args.length > 2) baseDt = args[2];
        if (args.length > 3) outDir = args[3];

        PointService.getInstance().execute(txFile, memberFile, baseDt, outDir);
    }
}
