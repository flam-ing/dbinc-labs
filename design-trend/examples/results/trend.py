"""안쪽(우리 시안 클릭률)과 바깥(위키백과 조회수)의 스타일별 추세를 표로 보여 준다.

사용: python3 trend.py
"""
import csv
from collections import defaultdict

DESIGNS = "data/our_designs.csv"
TRENDS = "data/trends_wikipedia_monthly.csv"

# 우리 시안 스타일 -> 위키백과 문서. 1:1 대응이 아닌 것은 아래 NOTES에 적는다.
TERM = {
    "flat": "Flat design",
    "material": "Material Design",
    "neumorph": "Neumorphism",
    "pixel-retro": "Pixel art",
    "swiss": "Swiss Style (design)",
    "y2k": "Y2K aesthetic",
    "glass": "Liquid Glass",
    "skeuo": "Skeuomorph",
}
NOTES = {
    "pixel-retro": "'Pixel art' 문서로 대신함(레트로 전체가 아님)",
    "glass": "'Liquid Glass'로 대신함. 비슷한 Frutiger Aero는 따로 있음",
}

MIN_DESIGNS = 8        # 이보다 적으면 '믿기 어려움'
MIN_DOC_MONTHS = 30    # 문서 기록이 이보다 짧으면 '믿기 어려움'
SPIKE_RATIO = 5        # 최근 6개월 중 한 달이 그 앞 12개월 중앙값의 이 배수를 넘으면 '일시 급등'


def months_back(ym, n):
    y, m = int(ym[:4]), int(ym[5:])
    k = y * 12 + m - 1 - n
    return f"{k // 12:04d}-{k % 12 + 1:02d}"


def load():
    with open(DESIGNS, encoding="utf-8") as f:
        designs = list(csv.DictReader(f))
    views = defaultdict(dict)
    with open(TRENDS, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            views[r["term"]][r["month"]] = int(r["views"])
    return designs, views


def ctr(rows):
    imp = sum(int(r["impressions"]) for r in rows)
    return sum(int(r["clicks"]) for r in rows) / imp if imp else None


def inside(designs, last):
    """최근 12개월 클릭률과 그 앞 12개월 클릭률 비교."""
    cut_new = months_back(last, 11)
    cut_old = months_back(last, 23)
    out = {}
    for s in TERM:
        rows = [r for r in designs if r["style"] == s]
        new = [r for r in rows if r["month"] >= cut_new]
        old = [r for r in rows if cut_old <= r["month"] < cut_new]
        a, b = ctr(old), ctr(new)
        out[s] = dict(n=len(rows), n_new=len(new), n_old=len(old),
                      all=ctr(rows), old=a, new=b,
                      change=(b - a) if a is not None and b is not None else None,
                      first=min((r["month"] for r in rows), default=None))
    return out


def outside(views, last):
    """최근 6개월 조회수 합과 1년 전 같은 6개월 합 비교(계절 효과를 피하려는 것)."""
    new_m = [months_back(last, i) for i in range(6)]
    old_m = [months_back(last, i + 12) for i in range(6)]
    out = {}
    for s, term in TERM.items():
        v = views[term]
        new = sum(v.get(m, 0) for m in new_m)
        old_have = [m for m in old_m if m in v]
        old = sum(v[m] for m in old_have)
        out[s] = dict(term=term, months=len(v), first=min(v), new=new,
                      old=old if len(old_have) == 6 else None,
                      yoy=(new / old - 1) if len(old_have) == 6 and old else None,
                      peak=max(v, key=v.get))
    return out


def spikes(views, last):
    """최근 6개월 중 평소(그 앞 12개월 중앙값)보다 훨씬 높은 달을 찾는다."""
    out = {}
    for s, term in TERM.items():
        v = views[term]
        base = sorted(v[months_back(last, i)] for i in range(6, 18) if months_back(last, i) in v)
        if len(base) < 6:
            continue
        med = base[len(base) // 2]
        hot = [(m, v[m]) for m in (months_back(last, i) for i in range(6)) if m in v and v[m] > SPIKE_RATIO * med]
        if hot:
            out[s] = (med, hot)
    return out


def pct(x, signed=False):
    return "-" if x is None else f"{x:{'+' if signed else ''}.1%}"


def pp(x):
    return "-" if x is None else f"{x * 100:+.2f}%p"


def main():
    designs, views = load()
    last = max(r["month"] for r in designs)
    ins, outs = inside(designs, last), outside(views, last)

    print(f"기준: 시안 {len(designs)}건, 마지막 달 {last}\n")
    print("## 안쪽: 최근 12개월 클릭률 vs 그 앞 12개월")
    print("| 스타일 | 시안 수(전체/최근/이전) | 전체 클릭률 | 이전 12개월 | 최근 12개월 | 변화 |")
    print("|---|---|---|---|---|---|")
    for s, d in sorted(ins.items(), key=lambda x: -(x[1]["change"] if x[1]["change"] is not None else -9)):
        print(f"| {s} | {d['n']}/{d['n_new']}/{d['n_old']} | {pct(d['all'])[:-1]}% | "
              f"{'-' if d['old'] is None else pct(d['old'])} | {'-' if d['new'] is None else pct(d['new'])} | {pp(d['change'])} |")

    print("\n## 바깥: 위키백과 조회수, 최근 6개월 vs 1년 전 같은 6개월")
    print("| 스타일 | 문서 | 기록 달 수 | 최근 6개월 합 | 1년 전 6개월 합 | 증감 |")
    print("|---|---|---|---|---|---|")
    for s, d in sorted(outs.items(), key=lambda x: -(x[1]["yoy"] if x[1]["yoy"] is not None else -9)):
        print(f"| {s} | {d['term']} | {d['months']} ({d['first']}~) | {d['new']:,} | "
              f"{'-' if d['old'] is None else format(d['old'], ',')} | {pct(d['yoy'], True)} |")

    sp = spikes(views, last)
    print("\n## 믿기 어려운 곳")
    for s in TERM:
        why = []
        if ins[s]["n"] < MIN_DESIGNS:
            why.append(f"시안 {ins[s]['n']}건뿐")
        if ins[s]["n_old"] == 0 or ins[s]["n_new"] == 0:
            why.append("비교할 한쪽 기간에 시안이 없음")
        if outs[s]["months"] < MIN_DOC_MONTHS:
            why.append(f"문서 기록 {outs[s]['months']}개월({outs[s]['first']}부터)")
        if outs[s]["old"] is None:
            why.append("1년 전 비교 기간이 없음")
        if s in NOTES:
            why.append(NOTES[s])
        if s in sp:
            med, hot = sp[s]
            why.append("일시 급등 의심: " + ", ".join(f"{m} {n:,}회(평소 약 {med:,})" for m, n in hot)
                       + " -> 위 증감은 이 한 달이 거의 다 만든 값")
        if why:
            print(f"- {s}: " + "; ".join(why))


if __name__ == "__main__":
    main()
