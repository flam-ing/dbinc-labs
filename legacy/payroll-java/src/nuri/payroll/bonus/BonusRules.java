package nuri.payroll.bonus;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.YearMonth;
import java.time.format.DateTimeParseException;
import java.util.Set;

/**
 * 성과 상여 (2021 성과급 제도 개편)
 *
 * - 분기 실적이 확정된 다음 달(1, 4, 7, 10월)에 지급
 * - 등급별 지급률 S 30%, A 20%, B 10%
 * - 지급월 1일 기준 입사 3개월 미만은 제외
 *
 * @author 이도윤 (2021-09)
 */
public final class BonusRules {

    public record Target(String empNo, long baseSalary, String grade, String hireDate) {}

    private static final Set<Integer> PAY_MONTHS = Set.of(1, 4, 7, 10);

    private BonusRules() {
    }

    public static long bonusFor(Target t, YearMonth ym) {
        if (!PAY_MONTHS.contains(ym.getMonthValue())) {
            return 0L;
        }
        var rate = switch (t.grade() == null ? "" : t.grade().trim()) {
            case "S" -> new BigDecimal("0.30");
            case "A" -> new BigDecimal("0.20");
            case "B" -> new BigDecimal("0.10");
            default -> BigDecimal.ZERO;
        };
        if (rate.signum() == 0) {
            return 0L;
        }

        LocalDate hire;
        try {
            hire = LocalDate.parse(t.hireDate());
        } catch (DateTimeParseException e) {
            System.out.printf("경고 | 상여 | %s | 입사일을 읽을 수 없어 0원 처리 (%s)%n", t.empNo(), t.hireDate());
            return 0L;
        }
        if (hire.isAfter(ym.atDay(1).minusMonths(3))) {
            System.out.printf("경고 | 상여 | %s | 입사 3개월 미만이라 제외%n", t.empNo());
            return 0L;
        }

        // 10원 단위로 맞춤
        return BigDecimal.valueOf(t.baseSalary())
                .multiply(rate)
                .setScale(-1, RoundingMode.HALF_EVEN)
                .longValueExact();
    }
}
