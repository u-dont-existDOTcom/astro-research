"""Score every technique against one person's dated events, with three controls:
1. the date-shift test for each technique (base.test), on all dates and on the earlier and later halves;
2. the family-wise question: is the best of all techniques better than the best technique of shifted date sets?
3. fit-then-test: weight the techniques by their fit on one half of the dates and score the other half.
Usage: ASTRO_PERSON=person.json ASTRO_EPHE=/path/to/ephe python run_all.py results.json"""
import sys
from techniques import *
from techniques import _LU, _EC, _ST
C0 = chart_of(REF); names, fams, cols = [], [], []
for name, fam, ts, fn in TECHS1 + TECHS:
    A = np.asarray(fn(C0), float); names.append(name); fams.append(fam); cols.append(A); run(name, A, family=fam, tsens=ts)
def sky(name, A, fam="sky only"):
    names.append(name); fams.append(fam); cols.append(np.asarray(A, float)); run(name, A, family=fam)
A = np.zeros(ND)
for l in _LU: A += gauss(np.abs(JD - l["jd"]), 1.0)
sky("Any New or Full Moon (a day either side)", A)
A = np.zeros(ND)
for e in _EC: A += gauss(np.abs(JD - e["jd"]), 10.0)
sky("Any eclipse (about 10 days either side)", A)
A = np.zeros(ND)
for s in _ST: A += gauss(np.abs(JD - s["jd"]), 4.0)
sky("Any planet turning retrograde or direct (within about 4 days)", A)
for m in ["Mercury", "Venus", "Mars"]: sky(m + " retrograde", (SPD[:, bi[m]] < 0).astype(float))
sky("Waxing Moon (New to Full)", (((POS[:, bi["Moon"]] - POS[:, bi["Sun"]]) % 360) < 180).astype(float))
sky("Control: weekend", (WEEKDAY >= 5).astype(float), "controls")
X = np.array(cols).T; X = (X - X.mean(0)) / (X.std(0) + 1e-12); K = X.shape[1]
IDXM = lambda idx: (idx[:, None] + SHIFTS[None, :]) % ND
def zs(M, idx):
    null = M[IDXM(idx)].mean(0); return (M[idx].mean(0) - null.mean(0)) / (null.std(0) + 1e-12)
def z1(v, idx):
    null = v[IDXM(idx)].mean(0); return float((v[idx].mean() - null.mean()) / (null.std() + 1e-12)), float((null >= v[idx].mean()).mean())
out = {"events": int(len(EVI)), "techniques": K, "table": sorted(RESULTS, key=lambda r: -r["z"])}
zall = zs(X, EVI); null = X[IDXM(EVI)].mean(0); zn = (null - null.mean(0)) / (null.std(0) + 1e-12)
out["family_wise"] = {"best_technique": names[int(zall.argmax())], "best_z": round(float(zall.max()), 2),
                      "share_of_shifted_date_sets_whose_best_technique_is_at_least_as_good": round(float((zn.max(1) >= zall.max()).mean()), 3),
                      "techniques_over_z_1.645": int((zall > 1.645).sum()), "expected_by_chance": round(float((zn > 1.645).sum(1).mean()), 2), "mean_z": round(float(zall.mean()), 3)}
i1, i2 = EVI[H1], EVI[H2]; out["fit_then_test"] = {}
for lab, tr, te in (("fit on the earlier half, test on the later half", i1, i2), ("fit on the later half, test on the earlier half", i2, i1)):
    w = zs(X, tr); res = {}
    for rule, ww in (("all techniques weighted by their fit", w), ("only techniques with fit z > 1", np.where(w > 1, w, 0)), ("the five best-fitting techniques", np.where(w >= np.sort(w)[-5], w, 0)), ("the single best-fitting technique", np.where(w >= w.max(), 1.0, 0))):
        s = X @ ww; res[rule] = {"in_sample_z": round(z1(s, tr)[0], 2), "out_of_sample_z": round(z1(s, te)[0], 2), "out_of_sample_p": round(z1(s, te)[1], 3)}
    out["fit_then_test"][lab] = {"results": res, "best_in_fit": [names[k] for k in np.argsort(-w)[:5]]}
out["correlation_of_fit_between_halves"] = round(float(np.corrcoef(zs(X, i1), zs(X, i2))[0, 1]), 3)
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "results.json", "w"), indent=1, ensure_ascii=False)
for r in out["table"][:12]: print(f'{r["z"]:+5.2f} p={r["p"]:.3f} [{r["z_earlier_half"]:+5.2f} | {r["z_later_half"]:+5.2f}] {r["name"]}')
print(json.dumps(out["family_wise"], indent=1)); print(json.dumps(out["fit_then_test"], indent=1)[:900])
