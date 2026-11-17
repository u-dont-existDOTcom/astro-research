"""Does a technique point to the KIND of event? Dates stay fixed; the null shuffles which kind belongs to which date.
Areas of life are single letters: R love and partnership, H home and family, W work and standing, M money, B body and health,
S inner life and spirit, T travel, study and words, L a loss or an ending, N a new start, F friends and community.
Usage: ASTRO_PERSON=person.json ASTRO_EPHE=/path/to/ephe python kinds.py kinds.json"""
import sys
from techniques import *
from techniques import _vim
C0 = chart_of(REF); rng = np.random.default_rng(7); NPERM = 20000
ev = EV; areas = [AREA[i] for i in ev]; idx = EVI
def perm_test(score_fn, label="primary"):
    """score_fn(event_position, area) -> number. Statistic: sum over events with their own area."""
    obs = sum(score_fn(k, areas[k]) for k in range(len(ev))); null = np.zeros(NPERM)
    M = {a: np.array([score_fn(k, a) for k in range(len(ev))]) for a in set(areas)}
    for p in range(NPERM):
        sh = rng.permutation(len(ev)); null[p] = sum(M[areas[sh[k]]][k] for k in range(len(ev)))
    return round(float(obs), 2), round(float(null.mean()), 2), round(float((obs - null.mean()) / (null.std() + 1e-12)), 2), round(float((null >= obs).mean()), 4)
out = {}
# 1. annual profections: the year's house names the topic
TOP = {1: "BN", 2: "M", 3: "T", 4: "H", 5: "RF", 6: "BW", 7: "R", 8: "LM", 9: "TS", 10: "W", 11: "F", 12: "SL"}
sg, age = prof_lord(C0); house = (age % 12) + 1
out["Annual profections: the year's house names the area of life"] = perm_test(lambda k, a: float(a in TOP[int(house[idx[k]])]))
# 2. slow transits to the natural significator of the area
SIG = {"R": ["Venus"], "W": ["Saturn", "Sun"], "H": ["Moon"], "B": ["Mars"], "S": ["Neptune", "Jupiter"], "T": ["Mercury"], "N": ["Uranus"], "L": ["Pluto"], "F": ["Uranus"], "M": ["Jupiter"]}
slow = np.stack([POS[:, bi[b]] for b in ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]], axis=1); ACT = {}
for a, pl in SIG.items():
    v = hits(slow, np.array([C0["pts"][p] for p in pl]), HARD, 1.5) / len(pl); ACT[a] = (v - v.mean()) / (v.std() + 1e-12)
out["Slow transits (hard, 1.5°) to the planet that naturally signifies the area"] = perm_test(lambda k, a: float(ACT[a][idx[k]]))
# 3. the same with house rulers (whole-sign houses from the Ascendant), traditional rulers
HOUSE_OF = {"R": [7], "W": [10], "H": [4], "B": [1, 6], "S": [9, 12], "T": [3, 9], "N": [1], "L": [8], "F": [11], "M": [2]}
s0 = int(C0["asc"] // 30); ACT2 = {}
for a, hs in HOUSE_OF.items():
    pl = sorted({RULER[(s0 + h - 1) % 12] for h in hs}); v = hits(slow, np.array([C0["pts"][p] for p in pl]), HARD, 1.5) / len(pl); ACT2[a] = (v - v.mean()) / (v.std() + 1e-12)
out["Slow transits (hard, 1.5°) to the ruler of the house of that area (time-sensitive)"] = perm_test(lambda k, a: float(ACT2[a][idx[k]]))
# 4. slow planets passing through the house of the area
def in_house(a):
    hs = HOUSE_OF[a]; h = ((slow // 30).astype(int) - s0) % 12 + 1; return np.isin(h, hs).sum(axis=1).astype(float)
INH = {a: in_house(a) for a in HOUSE_OF}
out["A slow planet is passing through the house of that area (whole-sign houses)"] = perm_test(lambda k, a: float(INH[a][idx[k]]))
# 5. Vimshottari sub-period lord and firdaria sub-lord: natural meanings
LORD = {"Venus": "R", "Saturn": "WL", "Mars": "B", "Jupiter": "ST", "Mercury": "TW", "Moon": "H", "Sun": "WN", "Rahu": "N", "Ketu": "SL", "NN": "N", "SN": "SL"}
a_, p_ = _vim(C0); st = np.array([x[0] for x in a_]); al = [x[2] for x in a_]; k_ = np.clip(np.searchsorted(st, JD, side="right") - 1, 0, len(st) - 1)
out["Vimshottari: the sub-period lord's natural meaning names the area"] = perm_test(lambda k, a: float(a in LORD[al[k_[idx[k]]]]))
stp = np.array([x[0] for x in p_]); pl_ = [x[3] for x in p_]; kp = np.clip(np.searchsorted(stp, JD, side="right") - 1, 0, len(stp) - 1)
out["Vimshottari: the third-level lord's natural meaning names the area"] = perm_test(lambda k, a: float(a in LORD[pl_[kp[idx[k]]]]))
fd = firdaria(C0); fs = np.array([x[0] for x in fd]); fl = [x[2] for x in fd]; kf = np.clip(np.searchsorted(fs, JD, side="right") - 1, 0, len(fs) - 1)
out["Firdaria: the sub-period lord's natural meaning names the area"] = perm_test(lambda k, a: float(a in LORD[fl[kf[idx[k]]]]))
# 6. relationship events and the relationship indicators of each system (R events against all other events)
isR = np.array([a == "R" for a in areas])
def r_test(A):
    A = np.asarray(A, float); obs = A[idx][isR].mean() - A[idx][~isR].mean(); null = np.zeros(NPERM)
    for p in range(NPERM):
        m = rng.permutation(isR); null[p] = A[idx][m].mean() - A[idx][~m].mean()
    return round(float(obs), 3), round(float(null.mean()), 3), round(float((obs - null.mean()) / (null.std() + 1e-12)), 2), round(float((null >= obs).mean()), 4)
out["Relationship events vs others: Venus retrograde"] = r_test(SPD[:, bi["Venus"]] < 0)
out["Relationship events vs others: BaZi officer-star day"] = r_test(bz_officer_day(C0))
out["Relationship events vs others: BaZi day touches the spouse palace"] = r_test(bz_palace_day(C0))
out["Relationship events vs others: BaZi month brings officer star or touches spouse palace"] = r_test(bz_month(C0))
out["Relationship events vs others: BaZi year brings officer star or touches spouse palace"] = r_test(bz_year(C0))
out["Relationship events vs others: any planet hard to natal Venus (1.5°)"] = r_test(hits(np.stack([POS[:, bi[b]] for b in ["Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]], axis=1), np.array([C0["pts"]["Venus"]]), HARD, 1.5))
out["Relationship events vs others: Human Design, transits completing the person's open channels"] = r_test(hd_bridges(C0))
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "kinds.json", "w"), indent=1, ensure_ascii=False)
for k, v in out.items(): print(f"z={v[2]:+.2f} p={v[3]:.3f} obs={v[0]} chance={v[1]}  {k}")
