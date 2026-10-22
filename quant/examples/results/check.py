"""backtest.py 검사: ① 미래 정보·수수료 점검 ② 같은 날 체결과 비교 ③ 전략 B 기준값 앞/뒤 1년 검증.
backtest.py는 건드리지 않고 load/sma/run/mdd와 상수만 가져다 쓴다."""
import csv
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import backtest as bt  # noqa: E402


def signals_a(prices):
    fast, slow = bt.sma(prices, bt.FAST), bt.sma(prices, bt.SLOW)
    s = [0] * len(prices)
    for i in range(1, len(prices)):
        if None in (slow[i], slow[i - 1]):
            continue
        if fast[i - 1] <= slow[i - 1] and fast[i] > slow[i]:
            s[i] = 1
        elif fast[i - 1] >= slow[i - 1] and fast[i] < slow[i]:
            s[i] = -1
    return s


def signals_b(fng, buy=bt.BUY_BELOW, sell=bt.SELL_ABOVE):
    return [1 if v < buy else -1 if v > sell else 0 for v in fng]


def ledger(dates, prices, signals, same_day=False):
    """backtest.run과 따로 짠 거래 장부. 체결일·가격·수수료를 남긴다."""
    cash, qty, log, eq = float(bt.INITIAL), 0.0, [], []
    pending = 0
    for i, p in enumerate(prices):
        act = signals[i] if same_day else pending
        if act == 1 and cash > 0:
            fee = cash * bt.FEE
            qty, cash = (cash - fee) / p, 0.0
            log.append((dates[i], "매수", p, fee))
        elif act == -1 and qty > 0:
            gross = qty * p
            fee = gross * bt.FEE
            cash, qty = gross - fee, 0.0
            log.append((dates[i], "매도", p, fee))
        pending = signals[i]
        eq.append(cash + qty * p)
    return eq, log, qty > 0


def row(name, eq, trades):
    return f"{name:<26}{eq[-1]:>16,.0f}{eq[-1] / bt.INITIAL - 1:>10.1%}{bt.mdd(eq):>10.1%}{trades:>8}"


HEAD = f"{'':<26}{'최종 금액(원)':>14}{'수익률':>10}{'MDD':>10}{'거래':>6}"


def part1(dates, prices, fng):
    print("=" * 70, "\n① 미래 정보·수수료 점검\n" + "=" * 70)
    with open(ROOT / "out" / "equity.csv", encoding="utf-8") as f:
        saved = list(csv.DictReader(f))
    for name, sig, col in [("A", signals_a(prices), "전략A"), ("B", signals_b(fng), "전략B")]:
        eq, log, held = ledger(dates, prices, sig)
        eq2, trades = bt.run(prices, sig)
        gap = max(abs(a - b) for a, b in zip(eq, eq2))
        gap_csv = max(abs(float(r[col]) - e) for r, e in zip(saved, eq))
        fees = sum(x[3] for x in log)
        print(f"[전략 {name}] 장부 재계산 vs run() 최대 차이 {gap:.6f}원 / vs out/equity.csv {gap_csv:.2f}원(반올림)")
        print(f"  거래 {len(log)}회(run() {trades}회), 낸 수수료 합계 {fees:,.0f}원, 기말 보유 중: {held}")
        if held:
            print(f"  → 기말 보유 물량을 팔 때 나갈 수수료 약 {eq[-1] * bt.FEE:,.0f}원은 최종 금액에서 빠지지 않음")
        late = [(d, s, p) for (d, s, p, _) in log]
        print("  체결 예: " + ", ".join(f"{d} {s}@{p:,.0f}" for d, s, p in late[:3]))

        # 신호일 → 체결일이 하루 뒤인지 (행 기준)
        idx = {d: i for i, d in enumerate(dates)}
        sig_days = [i for i, s in enumerate(sig) if s]
        exec_ok = all(idx[d] - 1 >= 0 and sig[idx[d] - 1] == (1 if s == "매수" else -1) for d, s, _, _ in log)
        print(f"  모든 체결이 바로 전 행의 신호에서 나왔는가: {exec_ok}")

        # 미래 가격/지수를 망가뜨려도 과거 평가금액이 그대로인가
        bad = []
        for k in (100, 250, 400, 600):
            p2 = prices[: k + 1] + [x * 3 for x in prices[k + 1 :]]
            f2 = fng[: k + 1] + [100 - v for v in fng[k + 1 :]]
            s2 = signals_a(p2) if name == "A" else signals_b(f2)
            e2, _ = bt.run(p2, s2)
            if any(abs(a - b) > 1e-6 for a, b in zip(e2[: k + 1], eq[: k + 1])):
                bad.append(k)
        print(f"  k일 이후 데이터를 바꿔도 k일까지 결과가 변하는 k: {bad or '없음'} (없으면 미래 정보 없음)\n")

    gaps = [(dates[i - 1], dates[i]) for i in range(1, len(dates))
            if (_d(dates[i]) - _d(dates[i - 1])).days != 1]
    print(f"날짜가 하루 이상 비는 곳: {gaps or '없음'}")
    print("  → 코드는 날짜가 아닌 행 번호로 '다음 날'과 이동평균 창을 정하므로(backtest.py 25, 36행),")
    print("    이 구간을 지나는 신호는 체결이 이틀 뒤가 되고 20/60일 창이 하루씩 더 넓어짐 (영향 작음)\n")


def _d(s):
    import datetime
    return datetime.date.fromisoformat(s)


def part2(dates, prices, fng):
    print("=" * 70, "\n② 같은 날 종가 체결(미래 정보 포함)과 비교\n" + "=" * 70)
    print(HEAD)
    for name, sig in [("A (MA20/60)", signals_a(prices)), ("B (25/75)", signals_b(fng))]:
        for label, same in [("다음 날 체결(정상)", False), ("같은 날 체결(부정)", True)]:
            eq, log, _ = ledger(dates, prices, sig, same)
            print(row(f"{name} {label}", eq, len(log)))
        print()
    q = bt.INITIAL * (1 - bt.FEE) / prices[0]
    print(row("단순 보유(참고)", [q * p for p in prices], 1))
    print()


def part3(dates, prices, fng):
    print("=" * 70, "\n③ 전략 B 기준값 탐색: 앞 1년 선택 → 뒤 1년 적용\n" + "=" * 70)
    cut = 365
    parts = {"앞": (prices[:cut], fng[:cut]), "뒤": (prices[cut:], fng[cut:])}
    print(f"앞 {dates[0]}~{dates[cut - 1]} ({cut}일), 뒤 {dates[cut]}~{dates[-1]} ({len(dates) - cut}일); 각 구간은 1,000만 원 새로 시작\n")
    buys, sells = range(10, 45, 5), range(60, 95, 5)

    res = {}
    for b in buys:
        for s in sells:
            for k, (p, f) in parts.items():
                eq, t = bt.run(p, signals_b(f, b, s))
                res[(b, s, k)] = (eq[-1] / bt.INITIAL - 1, bt.mdd(eq), t)

    for k in ("앞", "뒤"):
        print(f"{k} 1년 수익률(%) — 행: 살 기준(미만), 열: 팔 기준(초과)")
        print("      " + "".join(f"{s:>8}" for s in sells))
        for b in buys:
            print(f"{b:>5} " + "".join(f"{res[(b, s, k)][0] * 100:>8.1f}" for s in sells))
        print()

    keys = [(b, s) for b in buys for s in sells]
    best = max(keys, key=lambda x: res[(*x, "앞")][0])
    ranked2 = sorted(keys, key=lambda x: -res[(*x, "뒤")][0])
    hind = ranked2[0]
    rank = ranked2.index(best) + 1
    med2 = statistics.median(res[(*x, "뒤")][0] for x in keys)

    def hold(k):
        p = parts[k][0]
        q = bt.INITIAL * (1 - bt.FEE) / p[0]
        eq = [q * x for x in p]
        return eq[-1] / bt.INITIAL - 1, bt.mdd(eq)

    print(f"{'':<30}{'앞 1년':>16}{'뒤 1년':>16}")
    def line(label, key):
        a, b = res[(*key, "앞")], res[(*key, "뒤")]
        print(f"{label:<30}{a[0]:>9.1%} {a[1]:>6.1%}{b[0]:>9.1%} {b[1]:>6.1%}   (거래 {a[2]}/{b[2]})")
    line(f"앞 1년 최고 {best[0]}/{best[1]}", best)
    line("기본값 25/75", (25, 75))
    line(f"뒤 1년 최고 {hind[0]}/{hind[1]} (사후)", hind)
    h1, h2 = hold("앞"), hold("뒤")
    print(f"{'단순 보유':<30}{h1[0]:>9.1%} {h1[1]:>6.1%}{h2[0]:>9.1%} {h2[1]:>6.1%}")
    print("(각 칸: 수익률 MDD)\n")
    print(f"앞 1년 최고 기준 {best[0]}/{best[1]}의 뒤 1년 순위: 49개 중 {rank}위, 49개 중앙값 수익률 {med2:.1%}")
    top = sorted(keys, key=lambda x: -res[(*x, "앞")][0])[:5]
    print("앞 1년 상위 5개 → 뒤 1년: " + ", ".join(f"{b}/{s}: {res[(b, s, '앞')][0]:.0%}→{res[(b, s, '뒤')][0]:.0%}" for b, s in top))
    ties = [x for x in keys if res[(*x, "앞")][0] == res[(*best, "앞")][0]]
    print(f"앞 1년 최고와 수익률이 같은 조합: {len(ties)}개 (여럿이면 살 기준·팔 기준이 작은 순으로 첫 번째를 채택)")


def main():
    dates, prices, fng = bt.load()
    part1(dates, prices, fng)
    part2(dates, prices, fng)
    part3(dates, prices, fng)


if __name__ == "__main__":
    main()
