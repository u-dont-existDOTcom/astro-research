"""Decoy test: score the chart-based techniques for other birth moments (same place, born within two years of the person)
against the person's real dates. If a technique reads THIS chart, this chart should beat the decoys.
Usage: ASTRO_PERSON=person.json ASTRO_EPHE=/path/to/ephe python decoys.py 300 decoys.json"""
import sys
from multiprocessing import Pool
from techniques import *
ALL = TECHS1 + TECHS; IDXM = (EVI[:, None] + SHIFTS[None, :]) % ND
def zrow(c):
    out = []
    for name, fam, ts, fn in ALL:
        A = np.asarray(fn(c), dtype=float); null = A[IDXM].mean(axis=0); out.append((A[EVI].mean() - null.mean()) / (null.std() or 1e-9))
    return out
def one(k):
    r = np.random.default_rng(1000 + k); t = REF + timedelta(days=float(r.uniform(-730.5, 730.5)), minutes=float(r.uniform(0, 1440)))
    try: return zrow(chart_of(t))
    except Exception: return None
if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300; true = np.array(zrow(chart_of(REF)))
    with Pool(os.cpu_count() or 2) as p: Z = np.array([r for r in p.map(one, range(N), chunksize=5) if r is not None])
    pct = (Z < true[None, :]).mean(axis=0); fam = [t[1] for t in ALL]
    def omni(f): t = f(true); d = np.array([f(z) for z in Z]); return {"person": round(float(t), 3), "decoy_mean": round(float(d.mean()), 3), "share_of_decoys_at_or_above": round(float((d >= t).mean()), 3)}
    out = {"decoys": int(len(Z)), "mean_z_over_all_techniques": omni(lambda z: z.mean()), "best_single_technique": omni(lambda z: z.max()),
           "techniques_over_z_1.645": omni(lambda z: (z > 1.645).sum()),
           "by_family": {f: omni(lambda z, ii=[k for k, x in enumerate(fam) if x == f]: z[ii].mean()) for f in sorted(set(fam))},
           "per_technique": [{"name": ALL[k][0], "z": round(float(true[k]), 2), "share_of_decoys_beaten": round(float(pct[k]), 3)} for k in np.argsort(-pct)]}
    json.dump(out, open(sys.argv[2] if len(sys.argv) > 2 else "decoys.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("decoys", "mean_z_over_all_techniques", "best_single_technique", "techniques_over_z_1.645")}, indent=1))
