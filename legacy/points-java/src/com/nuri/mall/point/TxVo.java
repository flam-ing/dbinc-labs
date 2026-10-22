package com.nuri.mall.point;

/**
 * 거래 (getter/setter 귀찮아서 public)
 */
public class TxVo {

    public String txId;
    public String memberId;
    public String txDt;      // yyyy-MM-dd HH:mm:ss
    public String type;      // BUY, USE, CANCEL, ADJ
    public int amount;       // BUY/CANCEL 은 결제금액(원), USE/ADJ 는 포인트
    public String orderNo;

    @Override
    public String toString() {
        return txId + "," + memberId + "," + txDt + "," + type + "," + amount + "," + orderNo;
    }
}
