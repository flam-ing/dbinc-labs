package com.nuri.room;

/**
 * 상수
 *
 * @author 정태윤
 * @since 2010.02
 */
public interface Const {

    // 회의실 운영 시간
    public static final int OPEN_TIME = 900;
    public static final int CLOSE_TIME = 1800;

    // 최대 예약 시간(분) : 2시간
    public static final int MAX_MIN = 120;

    // 예약 단위(분)
    public static final int UNIT_MIN = 30;

    // 며칠 앞까지 예약 받나
    public static final int MAX_DAY = 7;

    // 총무팀
    public static final String ADMIN_EMPNO = "10001";

    // 예약 상태
    public static final String ST_OK = "A";
    public static final String ST_CANCEL = "C";
    public static final String ST_DEL = "D";    // 안씀
}
