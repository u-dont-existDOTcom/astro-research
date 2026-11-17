"""Eighty-two timing techniques from seven traditions, each written as a function of a birth chart, so that the same
code can score one person's chart and other people's charts (decoys) against the same list of dates.
Every parameter was fixed before any result was looked at; none was tuned afterwards."""
from base import *
import swisseph as swe
FL = swe.FLG_SWIEPH | swe.FLG_SPEED
bi = {b: k for k, b in enumerate(BODY)}
HARD = [0, 90, 180]; H8 = [0, 45, 90, 135, 180]; MAJOR = [0, 60, 90, 120, 180]
TROP = 365.24219; LUNAR = 27.321582
PLAN10 = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
def rawlon(j, body): return swe.calc_ut(j, body, FL)[0][0]

# ---------- day tables that do not depend on anyone's chart ----------
_c2 = CACHE / f"tables_{ISO[0]}_{ND}.npz"
if _c2.exists():
    _z = np.load(_c2); DSTEM = _z["dstem"]; DBR = _z["dbr"]; YSTEM = _z["ystem"]; YBR = _z["ybr"]; MSTEM = _z["mstem"]; MBR = _z["mbr"]
    TZS = _z["tzs"]; TZN = _z["tzn"]; TGATE = _z["tgate"]; TNODE = _z["tnode"]
else:
    DSTEM = np.zeros(ND, int); DBR = np.zeros(ND, int); YSTEM = np.zeros(ND, int); YBR = np.zeros(ND, int); MSTEM = np.zeros(ND, int); MBR = np.zeros(ND, int)
    TZS = np.zeros(ND, int); TZN = np.zeros(ND, int); TNODE = np.zeros(ND)
    for i, d in enumerate(DAYS):
        DSTEM[i], DBR[i] = day_pillar(d.year, d.month, d.day)
        (ys, yb), (ms, mb), _ = bazi_year_month(d); YSTEM[i], YBR[i], MSTEM[i], MBR[i] = ys, yb, ms, mb
        m = maya(d.year, d.month, d.day); TZS[i], TZN[i] = m["sign_index"], m["number"]
        TNODE[i] = rawlon(JD[i], swe.TRUE_NODE)
    hb = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    cols = [POS[:, bi[b]] for b in hb] + [TNODE, (POS[:, bi["Sun"]] + 180) % 360, (TNODE + 180) % 360]
    TGATE = np.array([[longitude_to_gate_line(float(x)).gate for x in col] for col in cols]).T        # [day, 13 carriers]
    np.savez(_c2, dstem=DSTEM, dbr=DBR, ystem=YSTEM, ybr=YBR, mstem=MSTEM, mbr=MBR, tzs=TZS, tzn=TZN, tgate=TGATE, tnode=TNODE)
WEEKDAY = np.array([d.weekday() for d in DAYS]); MONTH = np.array([d.month for d in DAYS]); DOM = np.array([d.day for d in DAYS])
CH = [(c.gate_a, c.gate_b) for c in CHANNELS]
RULER = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]   # traditional
ZRY = [15, 8, 20, 25, 19, 20, 8, 15, 12, 27, 30, 12]

# ---------- a chart ----------
def chart_of(bdt, full=True):
    n = natal(bdt); bj = n["jd"]
    pts = {b: (n["tropical"][b] if b in n["tropical"] else rawlon(bj, BODIES[b])) for b in BODY}
    c = {"bdt": bdt, "bj": bj, "pts": pts, "asc": n["ASC"], "mc": n["MC"], "armc": n["ARMC"], "lat": LAT,
         "TL": np.array([pts[b] for b in BODY] + [n["ASC"], n["MC"]]), "moon_sid": n["sidereal"]["Moon"], "night": n["night_chart"],
         "spirit": n["lot_spirit"], "fortune": n["lot_fortune"], "gates": set(n["hd"]["gates"]), "hd_channels": set(n["hd"]["channels"])}
    c["eps"] = swe.calc_ut(bj, swe.ECL_NUT)[0][0]
    eq = [swe.calc_ut(bj, BODIES[b], FL | swe.FLG_EQUATORIAL)[0] for b in PLAN10]
    c["ra"] = np.array([e[0] for e in eq]); c["dec"] = np.array([e[1] for e in eq]); c["plon"] = np.array([pts[b] for b in PLAN10])
    ld = bdt.astimezone(TZ)
    ds, db = day_pillar(ld.year, ld.month, ld.day); (ys, yb), (ms, mb), _ = bazi_year_month(bdt); hs, hbr = bazi_hour(ds, ld.hour + ld.minute / 60)
    c["bazi"] = {"dm": ds, "db": db, "branches": [yb, mb, db, hbr], "stems": [ys, ms, ds, hs]}
    c["num"] = (ld.month, ld.day); m = maya(ld.year, ld.month, ld.day); c["maya"] = (m["sign_index"], m["number"])
    c["age"] = (JD - bj) / TROP
    return c

def prog(c, factor, bodies, step):
    """Positions on the 'progressed' date for every day of the table (factor: ephemeris days per day of life)."""
    pj = c["bj"] + (JD - c["bj"]) * factor; g = np.arange(pj.min() - step, pj.max() + 2 * step, step); out = {}
    for b in bodies:
        v = np.unwrap(np.radians([rawlon(float(x), BODIES[b]) for x in g])); out[b] = np.degrees(np.interp(pj, g, v)) % 360
    return out, pj
def sec(c):
    if "sec" not in c: c["sec"], c["secj"] = prog(c, 1 / TROP, ["Sun", "Moon", "Mercury", "Venus", "Mars"], 0.02)
    return c["sec"]
def arc(c): return (sec(c)["Sun"] - c["pts"]["Sun"]) % 360
def orbf(diff, angles):
    """Distance to the nearest of the given aspect angles (fast paths for the usual sets)."""
    a = tuple(angles)
    def fold(m): x = np.mod(diff, m); return np.minimum(x, m - x)
    if a == (0,): return fold(360.0)
    if a == (0, 180): return fold(180.0)
    if a == (0, 90, 180): return fold(90.0)
    if a == (0, 45, 90, 135, 180): return fold(45.0)
    if a == (0, 60, 90, 120, 180): return np.minimum(fold(60.0), fold(90.0))
    if a == (0, 120): return np.minimum(fold(360.0), np.minimum(np.abs(np.mod(diff, 360.0) - 120), np.abs(np.mod(diff, 360.0) - 240)))
    if a == (60, 120): x = np.mod(diff, 60.0); y = np.mod(diff, 180.0); return np.where(np.minimum(y, 180 - y) < 30, 30.0 + 0 * x, np.minimum(x, 60 - x))
    return orb_to(diff, list(angles))
def hits(L, targets, angles, s, cut=None):
    """L: [day] or [day, k] moving longitudes; sum of bell-shaped closeness to every aspect with every target.
    With cut: count of pairs within that orb instead."""
    L = np.asarray(L); L = L[:, None] if L.ndim == 1 else L; T = np.asarray(targets); out = np.zeros(L.shape[0])
    for k in range(L.shape[1]):
        o = orbf(L[:, k][:, None] - T[None, :], angles)
        out += (o <= cut).sum(axis=1) if cut is not None else gauss(o, s).sum(axis=1)
    return out
def midpoints(tl):
    out = []
    for a in range(len(tl)):
        for b in range(a + 1, len(tl)): out.append((tl[a] + ((tl[b] - tl[a] + 180) % 360 - 180) / 2.0) % 360)
    return np.array(out)

# ---------- solar arc directions ----------
def sa_hard(c): return hits((c["TL"][None, :] + arc(c)[:, None]) % 360, c["TL"], HARD, 0.15)
def sa_h8(c): return hits((c["TL"][None, :] + arc(c)[:, None]) % 360, c["TL"], H8, 0.10)
def sa_mid(c): return hits((c["TL"][None, :] + arc(c)[:, None]) % 360, midpoints(c["TL"]), H8, 0.05)
def sa_angles(c):
    a = arc(c)[:, None]; ang = c["TL"][12:]; pl = c["TL"][:12]
    return hits((ang[None, :] + a) % 360, pl, HARD, 0.15) + hits((pl[None, :] + a) % 360, ang, HARD, 0.15)

# ---------- secondary progressions ----------
def sp_moon_major(c): return hits(sec(c)["Moon"], c["TL"], MAJOR, 0.5)
def sp_moon_hard(c): return hits(sec(c)["Moon"], c["TL"], HARD, 0.5)
def sp_moon_ingress(c): return gauss(np.minimum(sec(c)["Moon"] % 30, 30 - sec(c)["Moon"] % 30), 0.5)
def sp_phase(c):
    ph = (sec(c)["Moon"] - sec(c)["Sun"]) % 360; return gauss(np.minimum(ph % 45, 45 - ph % 45), 1.0)
def sp_inner(c): return hits(np.stack([sec(c)[b] for b in ["Sun", "Mercury", "Venus", "Mars"]], axis=1), c["TL"], HARD, 0.08)
def sp_moon_to_prog(c): return sum(gauss(orb_to(sec(c)["Moon"] - sec(c)[b], MAJOR), 0.5) for b in ["Sun", "Mercury", "Venus", "Mars"])
def prog_angles(c):
    """Progressed MC by solar arc in longitude; ASC derived from it for the birth latitude."""
    if "pang" not in c:
        mcp = (c["mc"] + arc(c)) % 360; e = math.radians(c["eps"])
        ramc = np.degrees(np.arctan2(np.sin(np.radians(mcp)) * math.cos(e), np.cos(np.radians(mcp)))) % 360
        ascp = np.array([swe.houses_armc(float(r), c["lat"], c["eps"], b"P")[1][0] for r in ramc]); c["pang"] = (mcp, ascp)
    return c["pang"]
def sp_angles(c):
    mcp, ascp = prog_angles(c); pl = c["TL"][:12]
    A = hits(np.stack([mcp, ascp], axis=1), pl, HARD, 0.10)
    return A + hits(np.stack([sec(c)[b] for b in ["Sun", "Mercury", "Venus", "Mars"]], axis=1), c["TL"][12:], HARD, 0.08) + hits(sec(c)["Moon"], c["TL"][12:], HARD, 0.5)

# ---------- tertiary and minor progressions ----------
def ter(c):
    if "ter" not in c: c["ter"], _ = prog(c, 1 / LUNAR, ["Sun", "Moon", "Mercury", "Venus", "Mars"], 0.05)
    return c["ter"]
def mnr(c):
    if "mnr" not in c: c["mnr"], _ = prog(c, LUNAR / TROP, ["Sun", "Moon", "Mercury", "Venus", "Mars"], 0.1)
    return c["mnr"]
def tp_inner(c): return hits(np.stack([ter(c)[b] for b in ["Sun", "Mercury", "Venus", "Mars"]], axis=1), c["TL"], HARD, 0.15)
def tp_moon(c): return hits(ter(c)["Moon"], c["TL"], [0, 180], 1.0)
def mp_inner(c): return hits(np.stack([mnr(c)[b] for b in ["Sun", "Mercury", "Venus", "Mars"]], axis=1), c["TL"], HARD, 0.15)
def mp_moon(c): return hits(mnr(c)["Moon"], c["TL"], [0, 180], 1.0)

# ---------- primary directions to the angles ----------
def pd_arcs(c, zodiacal_aspects=False, converse=False):
    phi = math.radians(c["lat"]); e = math.radians(c["eps"]); ra = list(c["ra"]); dec = list(c["dec"])
    if zodiacal_aspects:
        for l in c["plon"]:
            for a in (60, 90, 120, 180, 240, 270, 300):
                x = math.radians((l + a) % 360)
                ra.append(math.degrees(math.atan2(math.sin(x) * math.cos(e), math.cos(x))) % 360); dec.append(math.degrees(math.asin(math.sin(e) * math.sin(x))))
    ra = np.array(ra); dec = np.radians(np.array(dec)); ad = np.degrees(np.arcsin(np.clip(np.tan(dec) * math.tan(phi), -1, 1)))
    A = c["armc"]; arcs = [(ra - A) % 360, (ra - A - 180) % 360, (ra - ad - A - 90) % 360, (ra + ad - A - 270) % 360]
    if converse: arcs += [(-x) % 360 for x in arcs]
    return np.concatenate(arcs)
def pd(c, key=0.98564733, zodiacal_aspects=False, converse=False, sig=45.0):
    arcs = pd_arcs(c, zodiacal_aspects, converse); t = c["bj"] + arcs / key * TROP
    t = t[(t > JD[0] - 200) & (t < JD[-1] + 200)]
    return gauss(JD[:, None] - t[None, :], sig).sum(axis=1) if len(t) else np.zeros(ND)
def pd_naibod(c): return pd(c)
def pd_ptolemy(c): return pd(c, key=1.0)
def pd_naibod_asp(c): return pd(c, zodiacal_aspects=True)
def pd_naibod_conv(c): return pd(c, converse=True)

# ---------- annual profections ----------
def prof_lord(c):
    s0 = int(c["asc"] // 30); a = np.floor(c["age"]).astype(int); return (s0 + a) % 12, a
def pr_lord_transits(c):
    sg, _ = prof_lord(c); A = np.zeros(ND)
    for s in range(12):
        m = sg == s
        if m.any():
            b = RULER[s]; sgm = 6.5 if b == "Moon" else 1.0
            A[m] = hits(POS[m, bi[b]], c["TL"], HARD, sgm)
    return A
def pr_to_lord(c):
    sg, _ = prof_lord(c); A = np.zeros(ND); slow = np.stack([POS[:, bi[b]] for b in ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]], axis=1)
    for s in range(12):
        m = sg == s
        if m.any(): A[m] = hits(slow[m], np.array([c["pts"][RULER[s]]]), HARD, 1.0)
    return A
def pr_continuous(c):
    d = (c["age"] * 30.0)[:, None]; return hits((c["TL"][12:][None, :] + d) % 360, c["TL"][:12], HARD, 1.0)

# ---------- zodiacal releasing ----------
def zr(start_sign, bj, t0, t1):
    """Periods at levels 1-3 from a lot's sign. Returns lists of (start_jd, sign, loosing_flag) for L2 and L3."""
    L2, L3 = [], []; t = bj; s = start_sign
    while t < t1:
        end1 = t + ZRY[s] * 360.0
        if end1 > t0:
            u = t; s2 = s; n = 0
            while u < end1:
                loose = False
                if n and n % 12 == 0: s2 = (s2 + 6) % 12; loose = True      # loosing of the bond after a full circuit
                end2 = min(u + ZRY[s2] * 30.0, end1)
                if end2 > t0 and u < t1:
                    L2.append((u, s2, loose)); v = u; s3 = s2; k = 0
                    while v < end2:
                        l3 = False
                        if k and k % 12 == 0: s3 = (s3 + 6) % 12; l3 = True
                        L3.append((v, s3, l3)); v += ZRY[s3] * 2.5; s3 = (s3 + 1) % 12; k += 1
                u = end2; s2 = (s2 + 1) % 12; n += 1
        t = end1; s = (s + 1) % 12
    return L2, L3
def _zr(c, lot="spirit"):
    k = "zr_" + lot
    if k not in c: c[k] = zr(int(c[lot] // 30), c["bj"], JD[0] - 400, JD[-1] + 400)
    return c[k]
def near(times, sig):
    t = np.array([x for x in times if JD[0] - 6 * sig < x < JD[-1] + 6 * sig]); return gauss(JD[:, None] - t[None, :], sig).sum(axis=1) if len(t) else np.zeros(ND)
def zr_l2(c): return near([p[0] for p in _zr(c)[0]], 7.0)
def zr_l3(c): return near([p[0] for p in _zr(c)[1]], 1.0)
def zr_l2_fortune(c): return near([p[0] for p in _zr(c, "fortune")[0]], 7.0)
def zr_peak(c):
    """Days whose level-3 sign from Spirit is angular (1st, 4th, 7th, 10th) from the sign of Fortune."""
    L3 = _zr(c)[1]; f = int(c["fortune"] // 30); st = np.array([p[0] for p in L3]); sg = np.array([p[1] for p in L3])
    k = np.clip(np.searchsorted(st, JD, side="right") - 1, 0, len(st) - 1); return (((sg[k] - f) % 3) == 0).astype(float)

# ---------- firdaria ----------
def firdaria(c):
    day = [("Sun", 10), ("Venus", 8), ("Mercury", 13), ("Moon", 9), ("Saturn", 11), ("Jupiter", 12), ("Mars", 7), ("NN", 3), ("SN", 2)]
    night = [("Moon", 9), ("Saturn", 11), ("Jupiter", 12), ("Mars", 7), ("Sun", 10), ("Venus", 8), ("Mercury", 13), ("NN", 3), ("SN", 2)]
    seq = night if c["night"] else day; chal = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]; t = c["bj"]; out = []
    for cyc in range(2):
        for lord, yrs in seq:
            if lord in chal:
                k = chal.index(lord)
                for j in range(7): out.append((t + j * yrs * TROP / 7, lord, chal[(k + j) % 7]))
            else: out.append((t, lord, lord))
            t += yrs * TROP
    return out
def fd_changes(c): return near([p[0] for p in firdaria(c)], 15.0)

# ---------- Vimshottari ----------
def _vim(c, yd=365.25):
    k = f"vim{yd}"
    if k not in c:
        tree = vimshottari(c["moon_sid"], c["bj"], year_days=yd, depth=3); a, p = [], []
        for m in tree:
            for s in m["sub"]:
                a.append((s["start"], m["lord"], s["lord"]))
                for q in s["sub"]: p.append((q["start"], m["lord"], s["lord"], q["lord"]))
        c[k] = (a, p)
    return c[k]
def vd_prat(c): return near([x[0] for x in _vim(c)[1]], 3.0)
def vd_antar(c): return near([x[0] for x in _vim(c)[0]], 10.0)
def vd_prat360(c): return near([x[0] for x in _vim(c, 360.0)[1]], 3.0)

# ---------- Human Design ----------
def _hd(c):
    if "hdb" not in c:
        g = c["gates"]; br = np.zeros(ND); sunbr = np.zeros(ND)
        for a, b in CH:
            if (a in g) == (b in g): continue
            need = b if a in g else a
            br += (TGATE == need).any(axis=1); sunbr += (TGATE[:, [0, 11]] == need).any(axis=1)
        ga = np.array(sorted(g)); c["hdb"] = (br, sunbr, np.isin(TGATE[:, [0, 11]], ga).any(axis=1).astype(float))
    return c["hdb"]
def hd_bridges(c): return _hd(c)[0]
def hd_sun_bridge(c): return (_hd(c)[1] > 0).astype(float)
def hd_sun_natal_gate(c): return _hd(c)[2]

# ---------- BaZi ----------
def _officers(dm): e = dm // 2; ctrl = (e + 3) % 5; return [ctrl * 2, ctrl * 2 + 1]      # the element that controls the day master
def bz_officer_day(c): return np.isin(DSTEM, _officers(c["bazi"]["dm"])).astype(float)
def bz_palace_day(c):
    db = c["bazi"]["db"]; return np.isin(DBR, [(db + 6) % 12, (13 - db) % 12]).astype(float)
def bz_clash_day(c): return np.isin(DBR, [(b + 6) % 12 for b in c["bazi"]["branches"]]).astype(float)
def bz_month(c):
    db = c["bazi"]["db"]; return (np.isin(MSTEM, _officers(c["bazi"]["dm"])) | np.isin(MBR, [(db + 6) % 12, (13 - db) % 12])).astype(float)
def bz_year(c):
    db = c["bazi"]["db"]; return (np.isin(YSTEM, _officers(c["bazi"]["dm"])) | np.isin(YBR, [(db + 6) % 12, (13 - db) % 12])).astype(float)
def bz_luck_change(c):
    """Ten-year luck pillar changes. Start age = days to the next (forward) or previous (backward) month-opening solar term / 3."""
    ys = c["bazi"]["stems"][0]; forward = (ys % 2 == 1) == (P.get("sex", "F") == "F")     # forward for a woman born in a yin year or a man born in a yang year
    j = c["bj"]; sl = rawlon(j, swe.SUN); k = ((sl - 315) % 360) // 30; target = (315 + 30 * (k + (1 if forward else 0))) % 360
    f = lambda t: ((rawlon(t, swe.SUN) - target + 180) % 360) - 180
    lo, hi = (j, j + 33) if forward else (j - 33, j)
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(mid) > 0: hi = mid
        else: lo = mid
    days = abs((lo + hi) / 2 - j); start = j + days / 3 * TROP
    return near([start + 10 * TROP * n for n in range(8)], 30.0)

# ---------- numerology, Maya, biorhythm ----------
def _pd(c):
    if "pday" not in c:
        bm, bd = c["num"]; py = np.array([personal_year(bm, bd, d.year) for d in DAYS]); pm = np.array([personal_month(int(p), d.month) for p, d in zip(py, DAYS)])
        c["pday"] = (py, pm, np.array([personal_day(int(p), d.day) for p, d in zip(pm, DAYS)]))
    return c["pday"]
def nu_day(c): return np.isin(_pd(c)[2], [1, 5, 9]).astype(float)
def nu_month(c): return np.isin(_pd(c)[1], [1, 5, 9]).astype(float)
def nu_year(c): return np.isin(_pd(c)[0], [1, 5, 9]).astype(float)
def my_sign(c): return (TZS == c["maya"][0]).astype(float)
def my_tone(c): return (TZN == c["maya"][1]).astype(float)
def my_kin(c):
    m = (TZS == c["maya"][0]) & (TZN == c["maya"][1]); A = m.astype(float); A[1:] += m[:-1]; A[:-1] += m[1:]; return np.minimum(A, 1.0)
def bio_critical(c):
    t = JD - c["bj"]; A = np.zeros(ND, bool)
    for P in (23, 28, 33):
        x = t % (P / 2); A |= np.minimum(x, P / 2 - x) <= 0.75
    return A.astype(float)
def bio_emotional_extreme(c): return (np.abs(np.sin(2 * np.pi * (JD - c["bj"]) / 28)) > 0.9).astype(float)
def birthday(c):
    x = (c["age"] % 1.0) * TROP; return (np.minimum(x, TROP - x) <= 7).astype(float)

TECHS = [
 ("Solar arcs: every directed point to every natal point, conjunction, square, opposition", "solar arcs", True, sa_hard),
 ("Solar arcs with the half-squares added (Ebertin's set)", "solar arcs", True, sa_h8),
 ("Solar arcs to natal midpoints (Ebertin)", "solar arcs", True, sa_mid),
 ("Solar arcs involving the Ascendant or Midheaven only", "solar arcs", True, sa_angles),
 ("Progressed Moon, any major aspect to a natal point", "secondary progressions", True, sp_moon_major),
 ("Progressed Moon, conjunction, square or opposition to a natal point", "secondary progressions", True, sp_moon_hard),
 ("Progressed Moon changing sign", "secondary progressions", False, sp_moon_ingress),
 ("Progressed Sun-Moon phase at one of its eight turning points", "secondary progressions", False, sp_phase),
 ("Progressed Sun, Mercury, Venus, Mars: hard aspects to natal points", "secondary progressions", True, sp_inner),
 ("Progressed Moon to the progressed Sun, Mercury, Venus, Mars", "secondary progressions", False, sp_moon_to_prog),
 ("Progressed angles to natal planets, and progressed planets to natal angles", "secondary progressions", True, sp_angles),
 ("Tertiary progressions: Sun, Mercury, Venus, Mars hard to natal points", "tertiary and minor progressions", True, tp_inner),
 ("Tertiary progressed Moon on or opposite a natal point", "tertiary and minor progressions", True, tp_moon),
 ("Minor progressions: Sun, Mercury, Venus, Mars hard to natal points", "tertiary and minor progressions", True, mp_inner),
 ("Minor progressed Moon on or opposite a natal point", "tertiary and minor progressions", True, mp_moon),
 ("Primary directions of planets to the four angles (Naibod key)", "primary directions", True, pd_naibod),
 ("Primary directions to the angles (Ptolemy's key, one degree a year)", "primary directions", True, pd_ptolemy),
 ("Primary directions to the angles, with zodiacal aspects (Naibod)", "primary directions", True, pd_naibod_asp),
 ("Primary directions to the angles, direct and converse (Naibod)", "primary directions", True, pd_naibod_conv),
 ("Profections: the year's ruling planet making hard transits to the natal chart", "profections", True, pr_lord_transits),
 ("Profections: slow planets making hard transits to the year's ruling planet", "profections", True, pr_to_lord),
 ("Profected Ascendant and Midheaven (30 degrees a year) reaching natal planets", "profections", True, pr_continuous),
 ("Zodiacal releasing from Spirit: change of level-2 period", "zodiacal releasing", True, zr_l2),
 ("Zodiacal releasing from Spirit: change of level-3 period", "zodiacal releasing", True, zr_l3),
 ("Zodiacal releasing from Fortune: change of level-2 period", "zodiacal releasing", True, zr_l2_fortune),
 ("Zodiacal releasing: 'peak' days (level 3 angular to Fortune)", "zodiacal releasing", True, zr_peak),
 ("Firdaria: change of sub-period", "firdaria", True, fd_changes),
 ("Vimshottari: change of third-level period (pratyantar)", "Vimshottari dasha", True, vd_prat),
 ("Vimshottari: change of second-level period (antardasha)", "Vimshottari dasha", True, vd_antar),
 ("Vimshottari with 360-day years: change of third-level period", "Vimshottari dasha", True, vd_prat360),
 ("Human Design: number of the person's open channels completed by the day's transits", "Human Design", False, hd_bridges),
 ("Human Design: the transiting Sun or Earth completes one of the person's channels", "Human Design", False, hd_sun_bridge),
 ("Human Design: the transiting Sun or Earth sits in one of the person's own gates", "Human Design", False, hd_sun_natal_gate),
 ("BaZi: the day's stem is one of the person's 'officer' stars", "BaZi", False, bz_officer_day),
 ("BaZi: the day's branch clashes or combines with the spouse palace", "BaZi", False, bz_palace_day),
 ("BaZi: the day's branch clashes with a branch of the chart", "BaZi", True, bz_clash_day),
 ("BaZi: the month brings an officer star or touches the spouse palace", "BaZi", False, bz_month),
 ("BaZi: the year brings an officer star or touches the spouse palace", "BaZi", False, bz_year),
 ("BaZi: change of ten-year luck pillar (within about a month)", "BaZi", True, bz_luck_change),
 ("Numerology: personal day 1, 5 or 9", "numerology", False, nu_day),
 ("Numerology: personal month 1, 5 or 9", "numerology", False, nu_month),
 ("Numerology: personal year 1, 5 or 9", "numerology", False, nu_year),
 ("Maya calendar: a day with the birth day-sign", "Maya calendar", False, my_sign),
 ("Maya calendar: a day with the birth number", "Maya calendar", False, my_tone),
 ("Maya calendar: the birth day returning (every 260 days, a day either side)", "Maya calendar", False, my_kin),
 ("Control: biorhythm 'critical' days", "controls", False, bio_critical),
 ("Control: biorhythm emotional cycle at its high or low", "controls", False, bio_emotional_extreme),
 ("Control: within a week of the birthday", "controls", False, birthday),
]

# ---------- transits, cycles, curves in the manner of Godbout, stations, eclipses, lunations, the Moon ----------
SLOW = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]; OUTER = ["Saturn", "Uranus", "Neptune", "Pluto"]; FAST = ["Sun", "Mercury", "Venus", "Mars"]
SOFT = [60, 120]; TNi = {n: k for k, n in enumerate(BODY + ["ASC", "MC"])}; PERSi = [TNi[x] for x in ["Sun", "Moon", "Mercury", "Venus", "Mars", "ASC", "MC"]]
def trc(c, movers, tidx, angles, s): return hits(np.stack([POS[:, bi[m]] for m in movers], axis=1), c["TL"][tidx], angles, s)
ALLT = list(range(14)); PLT = list(range(12))
def _mk(movers, tidx, angles, s): return lambda c: trc(c, movers, tidx, angles, s)
def ret_cycle(m): return lambda c: gauss(orbf(POS[:, bi[m]] - c["pts"][m], HARD), 2.0)
ALLM = FAST + SLOW + ["Mean Node"]
def gb(c, movers, mp_angles, with_aspects=True, with_mid=True):
    A = np.zeros(ND); L = np.stack([POS[:, bi[m]] for m in movers], axis=1)
    if with_aspects: A += hits(L, c["TL"], MAJOR, 0, cut=1.32)
    if with_mid: A += hits(L, midpoints(c["TL"]), mp_angles, 0, cut=0.35)
    return A
_ST = stations(JD[0] - 20, JD[-1] + 20); _EC = eclipses(JD[0] - 40, JD[-1] + 40)
_LU = [l for l in lunations(JD[0] - 5, JD[-1] + 5) if l["kind"] in ("New Moon", "Full Moon")]
def _events_near(c, ev, lonkey, angles, orb, sig, window=None):
    A = np.zeros(ND)
    for e in ev:
        if float(orbf(e[lonkey] - c["TL"], angles).min()) <= orb:
            t = np.abs(JD - e["jd"]); A += (t <= window).astype(float) if window else gauss(t, sig)
    return A
def moon_ret(c): return (sep(POS[:, bi["Moon"]], c["pts"]["Moon"]) <= 7).astype(float)
def moon_lights(c): return (orbf(POS[:, bi["Moon"]][:, None] - np.array([c["pts"]["Sun"], c["pts"]["Moon"], c["asc"], c["mc"]])[None, :], [0, 180]) <= 7).any(axis=1).astype(float)
def phase_ret(c): return (sep((POS[:, bi["Moon"]] - POS[:, bi["Sun"]]) % 360, (c["pts"]["Moon"] - c["pts"]["Sun"]) % 360) <= 12).astype(float)
TECHS1 = [
 ("Slow planets, hard aspects to all natal points (1°)", "transits", True, _mk(SLOW, ALLT, HARD, 1.0)),
 ("Slow planets, soft aspects to all natal points (1°)", "transits", True, _mk(SLOW, ALLT, SOFT, 1.0)),
 ("Saturn to Pluto, hard, to personal points (1°)", "transits", True, _mk(OUTER, PERSi, HARD, 1.0)),
 ("Saturn to Pluto, conjunctions and oppositions only, personal points (1.5°)", "transits", True, _mk(OUTER, PERSi, [0, 180], 1.5)),
] + [(f"{m}, hard aspects to natal planets (1°)", "transits", False, _mk([m], PLT, HARD, 1.0)) for m in SLOW + ["Mean Node", "Chiron"]] + [
 ("Slow planets to ASC and MC only, hard (1°)", "transits", True, _mk(SLOW, [12, 13], HARD, 1.0)),
 ("Mars, hard aspects to natal points (1.5°)", "transits", True, _mk(["Mars"], ALLT, HARD, 1.5)),
 ("Sun, Mercury, Venus, Mars: hard aspects to natal points (1°)", "transits", True, _mk(FAST, ALLT, HARD, 1.0)),
 ("Jupiter and Venus, conjunctions and trines to natal points (1.5°): 'easy' days", "transits", True, _mk(["Jupiter", "Venus"], ALLT, [0, 120], 1.5)),
 ("Uranus, any major aspect to natal points (1°): sudden change", "transits", True, _mk(["Uranus"], ALLT, MAJOR, 1.0)),
] + [(f"{m} return cycle: conjunction, square, opposition to its own natal place (2°)", "cycles", False, ret_cycle(m)) for m in ["Jupiter", "Saturn", "Mean Node", "Mars", "Venus"]] + [
 ("All planets, aspects 1.32° + midpoints 0.35° (0/90/180)", "Godbout-style curves", True, lambda c: gb(c, ALLM, HARD)),
 ("All planets, aspects 1.32° + midpoints 0.35° (multiples of 45°)", "Godbout-style curves", True, lambda c: gb(c, ALLM, H8)),
 ("Mars to Pluto only, aspects + midpoints (0/90/180)", "Godbout-style curves", True, lambda c: gb(c, ["Mars"] + SLOW, HARD)),
 ("Midpoints only, all planets (0/90/180)", "Godbout-style curves", True, lambda c: gb(c, ALLM, HARD, with_aspects=False)),
 ("Midpoints only, slow planets (multiples of 45°)", "Godbout-style curves", True, lambda c: gb(c, SLOW, H8, with_aspects=False)),
 ("Aspects only at 1.32°, all planets", "Godbout-style curves", True, lambda c: gb(c, ALLM, HARD, with_mid=False)),
 ("A planet turning retrograde or direct within 1.5° of a natal point (within about 5 days)", "stations", True, lambda c: _events_near(c, _ST, "lon", HARD, 1.5, 5.0)),
 ("Eclipse within 3° of a natal point by conjunction, square or opposition (about 10 days either side)", "eclipses", True, lambda c: _events_near(c, _EC, "lon", HARD, 3.0, 10.0)),
 ("Same eclipses, a window of 45 days either side", "eclipses", True, lambda c: _events_near(c, _EC, "lon", HARD, 3.0, 0, window=45)),
 ("New or Full Moon conjunct or opposite a natal point within 3° (a day or two either side)", "lunations", True, lambda c: _events_near(c, _LU, "moon_lon", [0, 180], 3.0, 1.5)),
 ("Moon back at its natal place (lunar return, within 7°, about half a day)", "Moon", False, moon_ret),
 ("Moon conjunct or opposite natal Sun, Moon, ASC or MC that day (7°)", "Moon", True, moon_lights),
 ("Sun-Moon angle the same as at birth (lunation-phase return, within 12°)", "Moon", False, phase_ret),
]
