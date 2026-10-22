"""data/btc.csv로 전략 A(이동평균 교차), 전략 B(공포·탐욕), 단순 보유를 백테스트한다."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INITIAL = 10_000_000
FEE = 0.0005
FAST, SLOW = 20, 60
BUY_BELOW, SELL_ABOVE = 25, 75


def load():
    with open(ROOT / "data" / "btc.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return (
        [r["날짜"] for r in rows],
        [float(r["종가"]) for r in rows],
        [int(r["공포탐욕지수"]) for r in rows],
    )


def sma(prices, n):
    out = [None] * len(prices)
    for i in range(n - 1, len(prices)):
        out[i] = sum(prices[i - n + 1 : i + 1]) / n
    return out


def run(prices, signals):
    """signals[i]: i일 종가를 보고 낸 신호 (+1 매수, -1 매도, 0 없음).
    미래 정보를 쓰지 않도록 체결은 다음 날 종가로 한다."""
    cash, qty, trades = float(INITIAL), 0.0, 0
    equity = []
    pending = 0
    for i, p in enumerate(prices):
        if pending == 1 and cash > 0:
            qty = cash * (1 - FEE) / p
            cash = 0.0
            trades += 1
        elif pending == -1 and qty > 0:
            cash = qty * p * (1 - FEE)
            qty = 0.0
            trades += 1
        pending = signals[i]
        equity.append(cash + qty * p)
    return equity, trades


def mdd(equity):
    peak, worst = equity[0], 0.0
    for e in equity:
        peak = max(peak, e)
        worst = min(worst, e / peak - 1)
    return worst


def main():
    dates, prices, fng = load()
    n = len(prices)

    fast, slow = sma(prices, FAST), sma(prices, SLOW)
    a = [0] * n
    for i in range(1, n):
        if None in (slow[i], slow[i - 1]):
            continue
        if fast[i - 1] <= slow[i - 1] and fast[i] > slow[i]:
            a[i] = 1
        elif fast[i - 1] >= slow[i - 1] and fast[i] < slow[i]:
            a[i] = -1

    b = [1 if v < BUY_BELOW else -1 if v > SELL_ABOVE else 0 for v in fng]
    # 보유: 첫날 종가에 매수. run()은 신호 다음 날 체결이므로 전날(-1)이 없어 직접 계산한다.
    qty = INITIAL * (1 - FEE) / prices[0]
    hold_eq = [qty * p for p in prices]

    results = {
        "전략 A (MA20/60 교차)": run(prices, a),
        "전략 B (공포·탐욕 25/75)": run(prices, b),
        "단순 보유": (hold_eq, 1),
    }

    print(f"기간 {dates[0]} ~ {dates[-1]} ({n}일), 시작 {INITIAL:,}원, 수수료 {FEE:.2%}\n")
    print(f"{'전략':<24}{'최종 금액(원)':>16}{'수익률':>10}{'MDD':>10}{'거래 횟수':>10}")
    for name, (eq, t) in results.items():
        print(f"{name:<22}{eq[-1]:>18,.0f}{eq[-1] / INITIAL - 1:>10.1%}{mdd(eq):>10.1%}{t:>10}")

    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    with open(out / "equity.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["날짜", "전략A", "전략B", "단순보유"])
        eqs = [e for e, _ in results.values()]
        for i, d in enumerate(dates):
            w.writerow([d] + [f"{e[i]:.0f}" for e in eqs])


if __name__ == "__main__":
    main()
