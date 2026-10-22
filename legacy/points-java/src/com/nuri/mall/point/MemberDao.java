package com.nuri.mall.point;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

/**
 * 회원 DAO
 *
 * 2016.04 몰 DB 접근 권한 안나와서 일단 CSV 로 받음
 */
public class MemberDao {

    // private static final String URL = "jdbc:mysql://10.20.0.15:3306/nurimall?characterEncoding=utf8";
    // private static final String USER = "point_batch";
    // private static final String PASS = "DUMMY-pointbatch-2016";

    public List<MemberVo> selectList(String path) {
        List<MemberVo> list = new ArrayList<MemberVo>();
        BufferedReader br = null;
        try {
            br = new BufferedReader(new InputStreamReader(new FileInputStream(path), "UTF-8"));
            String line = br.readLine();    // 헤더
            while ((line = br.readLine()) != null) {
                if (line.trim().length() == 0) continue;
                String[] arr = line.split(",");
                if (arr.length < 4) continue;
                MemberVo vo = new MemberVo();
                vo.setMemberId(arr[0].trim());
                vo.setName(arr[1].trim());
                vo.setGrade(arr[2].trim());
                vo.setEmail(arr[3].trim());
                if (arr.length > 4) vo.setJoinDt(arr[4].trim());
                if (arr.length > 5) vo.setAdAgree(arr[5].trim());
                list.add(vo);
            }
        } catch (IOException e) {
            System.out.println("[오류] 파일을 읽을 수 없습니다: " + path);
            System.exit(2);
        } finally {
            try {
                if (br != null) br.close();
            } catch (IOException e) {
            }
        }
        return list;
    }

    /*
    public MemberVo selectOne(Connection conn, String memberId) throws SQLException {
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM TB_MEMBER WHERE MEMBER_ID = '" + memberId + "'");
        ...
    }
    */
}
