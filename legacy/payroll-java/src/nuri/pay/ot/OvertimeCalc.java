package nuri.pay.ot;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.TreeMap;
import java.util.stream.Collectors;

import nuri.pay.PayUtil;

/**
 * Overtime / night / holiday allowance.
 * Replaces the HR Excel macro. (2015-07, Kim Sujin)
 *
 * Rates follow the HR guideline mail (2015-06-29).
 * Each day is rounded with Math.round, same as the Excel macro.
 */
public class OvertimeCalc {

    // managers get night pay only
    private static final List<String> MANAGERS = Arrays.asList("부장", "이사", "임원");

    private static final double OT_RATE = 1.5;
    private static final double NIGHT_RATE = 0.5;

    private int year;
    private int month;
    private Map<String, Map<LocalDate, WorkDay>> workDays = new HashMap<>();

    public OvertimeCalc(int year, int month) {
        this.year = year;
        this.month = month;
    }

    public void load(String path) {
        List<String[]> rows;
        try {
            rows = Files.readAllLines(Paths.get(path), StandardCharsets.UTF_8).stream()
                    .skip(1)
                    .filter(line -> !line.trim().isEmpty())
                    .map(line -> line.split(",", -1))
                    .collect(Collectors.toList());
        } catch (IOException e) {
            throw new RuntimeException("cannot read attendance file: " + path, e);
        }

        for (int i = 0; i < rows.size(); i++) {
            String[] r = rows.get(i);
            if (r.length < 5) {
                System.out.println("[WARN] bad line: " + String.join(",", r));
                continue;
            }
            String empId = r[0].trim();
            LocalDate date;
            try {
                date = LocalDate.parse(r[1].trim());
            } catch (DateTimeParseException e) {
                System.out.println("[WARN] skip " + empId + " " + r[1] + ": bad date");
                continue;
            }
            if (date.getYear() != year || date.getMonthValue() != month) {
                continue; // other month
            }
            Optional<LocalTime> in = parseTime(r[2]);
            Optional<LocalTime> out = parseTime(r[3]);
            if (in == null || out == null || !in.isPresent() || !out.isPresent()) {
                System.out.println("[WARN] skip " + empId + " " + date + ": no clock-in/out");
                continue;
            }
            // same day twice -> corrected row from the attendance system, keep the last one
            workDays.computeIfAbsent(empId, k -> new TreeMap<>())
                    .put(date, new WorkDay(empId, date, in.get(), out.get(), r[4].trim()));
        }
    }

    /**
     * @return {otMin, nightMin, holidayMin, otPay, nightPay, holidayPay}
     */
    public long[] payFor(String empId, int baseSalary, String grade) {
        long[] result = new long[6];
        Map<LocalDate, WorkDay> days = workDays.get(empId);
        if (days == null) return result;

        double hourly = baseSalary / 209.0;
        boolean isManager = MANAGERS.contains(grade);

        for (WorkDay wd : days.values()) {
            int start = wd.getIn().getHour() * 60 + wd.getIn().getMinute();
            int end = wd.getOut().getHour() * 60 + wd.getOut().getMinute();
            if (end <= start) end += 24 * 60; // night shift ends next day
            int span = end - start;
            int brk = span > 480 ? 60 : span > 240 ? 30 : 0;
            int worked = span - brk;

            int night = 0;
            for (int t = start; t < end; t++) {
                int m = t % 1440;
                if (m >= 22 * 60 || m < 6 * 60) night++;
            }

            int ot = 0;
            int hol = 0;
            if (!isManager) {
                if (isHoliday(wd)) hol = worked;
                else ot = Math.max(0, worked - 480);
            }

            result[0] += ot;
            result[1] += night;
            result[2] += hol;
            result[3] += Math.round(hourly * OT_RATE * ot / 60);
            result[4] += Math.round(hourly * NIGHT_RATE * night / 60);
            result[5] += Math.round(hourly * 1.5 * Math.min(hol, 480) / 60
                    + hourly * 2.0 * Math.max(0, hol - 480) / 60);
        }
        return result;
    }

    private boolean isHoliday(WorkDay wd) {
        DayOfWeek dow = wd.getDate().getDayOfWeek();
        if (dow == DayOfWeek.SATURDAY || dow == DayOfWeek.SUNDAY) return true;
        if ("휴일".equals(wd.getKind())) return true;
        // reuse the old holiday table
        return PayUtil.isHoliday(wd.getDate().format(DateTimeFormatter.ofPattern("MMdd")));
    }

    // returns empty when blank, null when the format is wrong
    private static Optional<LocalTime> parseTime(String s) {
        if (s == null || s.trim().isEmpty()) return Optional.empty();
        try {
            String t = s.trim();
            if (t.length() == 4) t = "0" + t; // 9:05 -> 09:05
            return Optional.of(LocalTime.parse(t));
        } catch (Exception e) {
            return null;
        }
    }

    // TODO weekly holiday allowance. HR said not now (2015-08)
    @SuppressWarnings("unused")
    private long weeklyHolidayPay(String empId, double hourly) {
        return 0L;
    }
}
