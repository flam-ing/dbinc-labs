package nuri.pay;

/**
 * 공제 계산
 * 작성 : 문태호 2008.04
 * 수정 : 2012.01 요율 변경
 */
public class Deduct {

    // 전체 공제 합계 (PayMain 합계 줄에서 씀)
    public static int nTotDeduct = 0;

    /**
     * 공제 항목 계산
     * @return {연금, 건강보험, 고용보험, 소득세, 사우회비}
     */
    public static int[] calc(int nBasePay, int nGross, boolean bSawoo) {
        int[] arr = new int[5];

        // 연금 4% (기본급 기준)
        arr[0] = (int) (nBasePay * 0.045);
        arr[0] = arr[0] / 10 * 10;

        // 건강보험 3.5%
        arr[1] = (int) (nGross * 0.035);
        arr[1] = arr[1] / 10 * 10;

        // 고용보험 0.9%
        arr[2] = (int) (nGross * 0.009);
        arr[2] = arr[2] / 10 * 10;

        // 소득세 (간이 구간)
        if (nGross < 1500000) {
            arr[3] = 0;
        } else if (nGross < 3000000) {
            arr[3] = (int) (nGross * 0.02);
        } else if (nGross < 4500000) {
            arr[3] = (int) (nGross * 0.04);
        } else if (nGross < 7000000) {
            arr[3] = (int) (nGross * 0.06);
        } else {
            arr[3] = (int) (nGross * 0.08);
        }
        arr[3] = arr[3] / 10 * 10;

        // 사우회비
        if (bSawoo) arr[4] = 10000;

        // if (nGross > 10000000) arr[3] = arr[3] + 50000; // 고액 가산 (2010 폐지)

        for (int i = 0; i < arr.length; i++) {
            nTotDeduct += arr[i];
        }
        return arr;
    }
}
