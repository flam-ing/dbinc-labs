package com.nuri.room;

/**
 * 회의실 정보
 *
 * TODO 그룹웨어 DB 로 옮길것
 */
public class RoomInfo {

    // {번호, 이름, 정원, 층}
    public static String[][] ROOMS = {
        {"R01", "대회의실", "20", "10"},
        {"R02", "중회의실A", "8", "10"},
        {"R03", "중회의실B", "8", "10"},
        {"R04", "소회의실", "4", "9"},
        {"R05", "화상회의실", "6", "9"},
        // {"R06", "9층라운지", "12", "9"},   2010.06 없어짐
    };

    public static int getIdx(String strRoomNo) {
        for (int i = 0; i < ROOMS.length; i++) {
            if (ROOMS[i][0].equals(strRoomNo)) {
                return i;
            }
        }
        return -1;
    }

    public static String getName(String strRoomNo) {
        int i = getIdx(strRoomNo);
        if (i < 0) return "";
        return ROOMS[i][1];
    }

    public static int getCapa(String strRoomNo) {
        int i = getIdx(strRoomNo);
        try {
            return Integer.parseInt(ROOMS[i][2]);
        } catch (Exception e) {
            return 0;
        }
    }

    public static String getFloor(String strRoomNo) {
        int i = getIdx(strRoomNo);
        if (i < 0) return "";
        return ROOMS[i][3];
    }
}
