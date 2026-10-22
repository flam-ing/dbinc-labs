package com.nuri.mall.point;

/**
 * 회원 VO
 */
public class MemberVo {

    private String memberId;
    private String name;
    private String grade;
    private String email;
    private String joinDt;
    private String adAgree;

    public String getMemberId() {
        return memberId;
    }

    public void setMemberId(String memberId) {
        this.memberId = memberId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getGrade() {
        return grade;
    }

    public void setGrade(String grade) {
        this.grade = grade;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getJoinDt() {
        return joinDt;
    }

    public void setJoinDt(String joinDt) {
        this.joinDt = joinDt;
    }

    public String getAdAgree() {
        return adAgree;
    }

    public void setAdAgree(String adAgree) {
        this.adAgree = adAgree;
    }
}
