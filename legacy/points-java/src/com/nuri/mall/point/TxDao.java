package com.nuri.mall.point;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

/**
 * 거래 DAO
 */
public class TxDao {

    public int readCnt = 0;
    public int errCnt = 0;

    public List<TxVo> selectList(String path) {
        List<TxVo> list = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(
                new InputStreamReader(new FileInputStream(path), StandardCharsets.UTF_8))) {
            String line = br.readLine();    // 헤더
            while ((line = br.readLine()) != null) {
                if (line.trim().isEmpty()) continue;
                readCnt++;
                String[] arr = line.split(",", -1);
                try {
                    TxVo tx = new TxVo();
                    tx.txId = arr[0].trim();
                    tx.memberId = arr[1].trim();
                    tx.txDt = arr[2].trim();
                    tx.type = arr[3].trim();
                    tx.amount = Integer.parseInt(arr[4].trim());
                    tx.orderNo = arr[5].trim();
                    list.add(tx);
                } catch (Exception e) {
                    errCnt++;
                }
            }
        } catch (IOException e) {
            System.out.println("[오류] 파일을 읽을 수 없습니다: " + path);
            System.exit(2);
        }
        return list;
    }
}
