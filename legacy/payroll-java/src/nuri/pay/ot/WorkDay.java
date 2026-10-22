package nuri.pay.ot;

import java.time.LocalDate;
import java.time.LocalTime;

/**
 * One row of the attendance file.
 */
public class WorkDay {

    private String empId;
    private LocalDate date;
    private LocalTime in;
    private LocalTime out;
    private String kind; // 근무, 휴일, 휴가

    public WorkDay(String empId, LocalDate date, LocalTime in, LocalTime out, String kind) {
        this.empId = empId;
        this.date = date;
        this.in = in;
        this.out = out;
        this.kind = kind;
    }

    public String getEmpId() { return empId; }
    public void setEmpId(String empId) { this.empId = empId; }

    public LocalDate getDate() { return date; }
    public void setDate(LocalDate date) { this.date = date; }

    public LocalTime getIn() { return in; }
    public void setIn(LocalTime in) { this.in = in; }

    public LocalTime getOut() { return out; }
    public void setOut(LocalTime out) { this.out = out; }

    public String getKind() { return kind; }
    public void setKind(String kind) { this.kind = kind; }

    @Override
    public String toString() {
        return "WorkDay{" + empId + ", " + date + ", " + in + "~" + out + ", " + kind + "}";
    }
}
