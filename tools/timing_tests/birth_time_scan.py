"""Birth-time scan: for every 5 minutes of the birth day (and the evening before), how well do the angle-dependent
timing techniques fit the person's dates?  Look-elsewhere is handled by comparing the best time of day with the best
time of day obtained for shifted date sets.
Usage: ASTRO_PERSON=person.json ASTRO_EPHE=/path/to/ephe python birth_time_scan.py scan.json"""
import sys, time
from techniques import *
t0 = time.time(); SH = SHIFTS[:1000]; IDX = (EVI[:, None] + SH[None, :]) % ND
FNS = {"primary directions to the angles (Naibod)": pd_naibod, "solar arcs involving the angles": sa_angles, "progressed angles": sp_angles,
       "slow transits to ASC and MC": lambda c: trc(c, SLOW, [12, 13], HARD, 1.0), "profected ASC and MC to natal planets": pr_continuous}
base = REF.replace(hour=21, minute=0) - timedelta(days=1); times = [base + timedelta(minutes=5 * k) for k in range(27 * 12)]
Z = {k: np.zeros(len(times)) for k in FNS}; ZN = {k: np.zeros((len(times), len(SH))) for k in FNS}
for i, t in enumerate(times):
    c = chart_of(t)
    for k, fn in FNS.items():
        A = np.asarray(fn(c), float); null = A[IDX].mean(0); m, s = null.mean(), null.std() + 1e-12
        Z[k][i] = (A[EVI].mean() - m) / s; ZN[k][i] = (null - m) / s
comb = sum(Z.values()) / math.sqrt(len(FNS)); combN = sum(ZN.values()) / math.sqrt(len(FNS))
out = {"grid": "every 5 minutes from 21:00 on the eve of the birth date to 23:55 on the birth date, local clock", "techniques": {}}
lab = [t.strftime("%d %H:%M") for t in times]; w = min(range(len(times)), key=lambda j: abs((times[j] - REF).total_seconds()))
for k in list(FNS) + ["all five combined"]:
    z = Z[k] if k in Z else comb; zn = ZN[k] if k in ZN else combN; b = int(z.argmax())
    out["techniques"][k] = {"z_at_working_time": round(float(z[w]), 2), "rank_of_working_time": int((z > z[w]).sum()) + 1, "of": len(times), "best_time": lab[b], "best_z": round(float(z[b]), 2),
                            "share_of_shifted_date_sets_whose_best_time_is_at_least_as_good": round(float((zn.max(0) >= z[b]).mean()), 3),
                            "top5_times": [(lab[j], round(float(z[j]), 2)) for j in np.argsort(-z)[:5]]}
# by rising sign: mean combined z
asc = [chart_of(t)["asc"] for t in times]; sign = [SIGNS[int(a // 30)] for a in asc]; bys = {}
for s in dict.fromkeys(sign): bys[s] = round(float(np.mean([comb[j] for j in range(len(times)) if sign[j] == s])), 2)
out["mean_combined_z_by_rising_sign"] = bys
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "scan.json", "w"), indent=1)
print(json.dumps(out, indent=1)); print("time", round(time.time() - t0))
