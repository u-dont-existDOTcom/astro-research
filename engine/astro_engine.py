"""Shared calculation engine: Swiss Ephemeris positions and the cycle tables of seven traditions
(Western, Hellenistic, Jyotish, Human Design, BaZi, numerology, the Maya day-count).

Strict Swiss Ephemeris (SWIEPH with .se1 files; no Moshier fallback). Nothing personal lives in this file:
the place and time zone come from the environment (ASTRO_LAT, ASTRO_LON, ASTRO_TZ) or from set_place().
ASTRO_EPHE must point to a folder with the Swiss Ephemeris files sepl_18.se1 and semo_18.se1.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

import swisseph as swe

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hdmatch.chart.calculator import calculate_chart  # noqa: E402
from hdmatch.chart.ephemeris import SwissEphemerisProvider  # noqa: E402
from hdmatch.chart.rave_mandala import longitude_to_gate_line  # noqa: E402
from hdmatch.chart.bodygraph import CHANNELS  # noqa: E402

import os
EPHE = Path(os.environ.get("ASTRO_EPHE", "ephe"))
swe.set_ephe_path(str(EPHE))
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
F = swe.FLG_SWIEPH | swe.FLG_SPEED
MASK = swe.FLG_JPLEPH | swe.FLG_SWIEPH | swe.FLG_MOSEPH
UTC = timezone.utc
TZ = ZoneInfo(os.environ.get("ASTRO_TZ", "UTC"))
LAT, LON = float(os.environ.get("ASTRO_LAT", "0")), float(os.environ.get("ASTRO_LON", "0"))


def set_place(lat: float, lon_east: float, tz: str) -> None:
    """Set the place used for houses and local dates."""
    global LAT, LON, TZ
    LAT, LON, TZ = float(lat), float(lon_east), ZoneInfo(tz)

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
         "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
BODIES = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS, "Mars": swe.MARS,
    "Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO, "North Node": swe.TRUE_NODE, "Mean Node": swe.MEAN_NODE, "Chiron": swe.CHIRON,
}
ASPECTS = {0: "conjunction", 60: "sextile", 90: "square", 120: "trine", 180: "opposition"}
RET_FLAGS: set[int] = set()


def jd_of(dt: datetime) -> float:
    d = dt.astimezone(UTC)
    return swe.julday(d.year, d.month, d.day, d.hour + d.minute / 60 + d.second / 3600 + d.microsecond / 3.6e9)


def dt_of(jd: float) -> datetime:
    return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(days=jd - 2440587.5)


def local(jd: float, fmt: str = "%Y-%m-%d %H:%M") -> str:
    return dt_of(jd).astimezone(TZ).strftime(fmt)


def wrap(x: float) -> float:
    return (x + 180.0) % 360.0 - 180.0


def fmt_lon(x: float) -> str:
    x %= 360.0
    d = int(x % 30)
    m = int(round((x % 30 - d) * 60))
    if m == 60:
        d, m = d + 1, 0
    s = int(x // 30)
    if d == 30:
        d, s = 0, (s + 1) % 12
    return f"{d}°{m:02d}′ {SIGNS[s]}"


def sign_of(x: float) -> str:
    return SIGNS[int((x % 360) // 30)]


@lru_cache(maxsize=2_000_000)
def pos(jd: float, body: int, sid: bool = False):
    xx, r = swe.calc_ut(jd, body, F | (swe.FLG_SIDEREAL if sid else 0))
    assert r & MASK == swe.FLG_SWIEPH, (body, r)
    RET_FLAGS.add(r & MASK)
    return xx


def lon(jd: float, body: int, sid: bool = False) -> float:
    return pos(jd, body, sid)[0]


def roots(fun, a: float, b: float, step: float = 0.25):
    """Sign-change roots of fun on [a,b] (fun returns wrapped degrees or a speed)."""
    out = []
    t = a
    v = fun(t)
    while t < b:
        u = min(t + step, b)
        w = fun(u)
        if v == 0:
            out.append(t)
        elif v * w < 0 and abs(v - w) < 180:
            lo, hi, flo = t, u, v
            for _ in range(48):
                mid = (lo + hi) / 2
                fm = fun(mid)
                if flo * fm <= 0:
                    hi = mid
                else:
                    lo, flo = mid, fm
            x = (lo + hi) / 2
            if not out or x - out[-1] > 1e-6:
                out.append(x)
        t, v = u, w
    return out


def houses(jd: float, hsys: bytes = b"P", lat: float | None = None, lng: float | None = None):
    cusps, ascmc = swe.houses_ex(jd, LAT if lat is None else lat, LON if lng is None else lng, hsys)
    return list(cusps), list(ascmc)


def whole_sign_house(x: float, asc: float) -> int:
    return int(((x % 360) // 30 - (asc % 360) // 30) % 12) + 1


def placidus_house(x: float, cusps: list[float]) -> int:
    x %= 360
    for i in range(12):
        a, b = cusps[i] % 360, cusps[(i + 1) % 12] % 360
        if a <= b:
            if a <= x < b:
                return i + 1
        else:
            if x >= a or x < b:
                return i + 1
    return 0


def natal(bdt: datetime) -> dict:
    j = jd_of(bdt)
    cp, ax = houses(j, b"P")
    cr, _ = houses(j, b"R")
    trop = {k: lon(j, b) for k, b in BODIES.items()}
    speed = {k: pos(j, b)[3] for k, b in BODIES.items()}
    asc, mc = ax[0], ax[1]
    ayan = swe.get_ayanamsa_ut(j)
    sid = {k: (v - ayan) % 360 for k, v in trop.items()}
    sid["ASC"] = (asc - ayan) % 360
    sid["MC"] = (mc - ayan) % 360
    # sect: Sun below horizon -> night. Sun is above horizon if it is in houses 7-12 (Placidus).
    sun_house = placidus_house(trop["Sun"], cp)
    night = sun_house <= 6
    if night:
        fortune = (asc + trop["Sun"] - trop["Moon"]) % 360
        spirit = (asc + trop["Moon"] - trop["Sun"]) % 360
    else:
        fortune = (asc + trop["Moon"] - trop["Sun"]) % 360
        spirit = (asc + trop["Sun"] - trop["Moon"]) % 360
    hd = calculate_chart(SwissEphemerisProvider((EPHE / "sepl_18.se1", EPHE / "semo_18.se1")), bdt.astimezone(UTC))
    bg = hd.bodygraph
    rec = {
        "local": bdt.isoformat(), "utc": bdt.astimezone(UTC).isoformat(), "jd": j,
        "tropical": trop, "speed": speed, "ASC": asc, "MC": mc, "ARMC": ax[2], "Vertex": ax[3],
        "placidus_cusps": cp, "regiomontanus_cusps": cr, "ayanamsa_lahiri": ayan, "sidereal": sid,
        "night_chart": night, "lot_fortune": fortune, "lot_spirit": spirit,
        "hd": {
            "type": str(bg.type), "strategy": str(bg.strategy), "authority": str(bg.authority),
            "profile": bg.profile, "definition": str(bg.definition), "channels": list(bg.channels),
            "defined_centers": sorted(str(c) for c in bg.defined_centers),
            "gates": sorted({a.gate for a in hd.activations}),
            "activations": [
                {"side": a.side, "body": a.body.value, "longitude": a.longitude, "gate": a.gate, "line": a.line}
                for a in hd.activations
            ],
            "design_utc": hd.design_utc.isoformat(),
        },
    }
    return rec


def natal_points(n: dict, with_angles: bool = True) -> dict:
    pts = {k: v for k, v in n["tropical"].items() if k not in ("Mean Node",)}
    if with_angles:
        pts["ASC"] = n["ASC"]
        pts["MC"] = n["MC"]
    return pts


def transit_hits(n_pts: dict, a: float, b: float, movers=None, step=0.25, aspects=ASPECTS) -> list[dict]:
    movers = movers or ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    out = []
    for m in movers:
        bid = BODIES[m]
        st = 0.04 if m == "Moon" else step
        for tgt, v in n_pts.items():
            for ang, nm in aspects.items():
                for sg in ((1, -1) if ang in (60, 90, 120) else (1,)):
                    for t in roots(lambda t, bid=bid, v=v, ang=ang, sg=sg: wrap(lon(t, bid) - v - ang * sg), a, b, st):
                        out.append({"mover": m, "target": tgt, "aspect": nm, "angle": ang, "jd": t,
                                    "local": local(t), "retro": pos(t, bid)[3] < 0,
                                    "mover_lon": lon(t, bid)})
    out.sort(key=lambda x: x["jd"])
    return out


def stations(a: float, b: float) -> list[dict]:
    out = []
    for m in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
        bid = BODIES[m]
        for t in roots(lambda t, bid=bid: pos(t, bid)[3], a, b, 0.5):
            after = pos(t + 0.5, bid)[3]
            out.append({"body": m, "jd": t, "local": local(t), "lon": lon(t, bid),
                        "kind": "direct" if after > 0 else "retrograde"})
    out.sort(key=lambda x: x["jd"])
    return out


def lunations(a: float, b: float) -> list[dict]:
    out = []
    for ang, nm in ((0, "New Moon"), (90, "First Quarter"), (180, "Full Moon"), (270, "Last Quarter")):
        for t in roots(lambda t, ang=ang: wrap(lon(t, swe.MOON) - lon(t, swe.SUN) - ang), a, b, 0.25):
            out.append({"kind": nm, "jd": t, "local": local(t), "moon_lon": lon(t, swe.MOON), "sun_lon": lon(t, swe.SUN)})
    out.sort(key=lambda x: x["jd"])
    return out


def eclipses(a: float, b: float) -> list[dict]:
    out = []
    t = a
    while True:
        r, tret = swe.sol_eclipse_when_glob(t, swe.FLG_SWIEPH, 0, False)
        tm = tret[0]
        if tm > b:
            break
        kind = "total" if r & swe.ECL_TOTAL else "annular" if r & swe.ECL_ANNULAR else "hybrid" if r & swe.ECL_ANNULAR_TOTAL else "partial"
        out.append({"kind": f"solar ({kind})", "jd": tm, "local": local(tm), "lon": lon(tm, swe.SUN)})
        t = tm + 20
    t = a
    while True:
        r, tret = swe.lun_eclipse_when(t, swe.FLG_SWIEPH, 0, False)
        tm = tret[0]
        if tm > b:
            break
        kind = "total" if r & swe.ECL_TOTAL else "partial" if r & swe.ECL_PARTIAL else "penumbral"
        out.append({"kind": f"lunar ({kind})", "jd": tm, "local": local(tm), "lon": lon(tm, swe.MOON)})
        t = tm + 20
    out.sort(key=lambda x: x["jd"])
    return out


def ingresses(a: float, b: float, movers=("Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")) -> list[dict]:
    out = []
    for m in movers:
        bid = BODIES[m]
        for bound in range(0, 360, 30):
            for t in roots(lambda t, bid=bid, bound=bound: wrap(lon(t, bid) - bound), a, b, 0.04 if m == "Moon" else 0.5):
                sp = pos(t, bid)[3]
                to = SIGNS[bound // 30] if sp > 0 else SIGNS[(bound // 30 - 1) % 12]
                out.append({"body": m, "jd": t, "local": local(t), "to": to, "retro": sp < 0})
    out.sort(key=lambda x: x["jd"])
    return out


TROPICAL_YEAR = 365.24219


def progressed_jd(birth_jd: float, obs_jd: float) -> float:
    return birth_jd + (obs_jd - birth_jd) / TROPICAL_YEAR


def closest_aspect(x: float, y: float):
    sep = abs(wrap(x - y))
    orb, ang = min((abs(sep - a), a) for a in ASPECTS)
    return ang, orb


# ---------- Human Design transit overlay ----------
HD_BODIES = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "North Node"]


def hd_state(jd: float, natal_gates: set[int]) -> dict:
    by = {}
    for nm in HD_BODIES:
        a = longitude_to_gate_line(lon(jd, BODIES[nm]))
        by[nm] = {"gate": a.gate, "line": a.line}
    for nm, parent in (("Earth", "Sun"), ("South Node", "North Node")):
        a = longitude_to_gate_line((lon(jd, BODIES[parent]) + 180) % 360)
        by[nm] = {"gate": a.gate, "line": a.line}
    tg = {v["gate"] for v in by.values()}
    uni = natal_gates | tg
    ch = []
    for c in CHANNELS:
        a, b = c.gate_a, c.gate_b
        if a in uni and b in uni:
            if a in natal_gates and b in natal_gates:
                kind = "natal"
            elif a in natal_gates or b in natal_gates:
                kind = "natal_completed"
            else:
                kind = "wholly_transit"
            ch.append({"channel": c.identifier, "kind": kind,
                       "carriers": {nm: v["gate"] for nm, v in by.items() if v["gate"] in (a, b)}})
    return {"gates": by, "channels": ch}


# ---------- Vimshottari ----------
NAK = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
       "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
       "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
       "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}


def vimshottari(moon_sid: float, birth_jd: float, year_days: float = 365.25, depth: int = 3) -> list[dict]:
    span = 360 / 27
    idx = int(moon_sid // span)
    frac = (moon_sid % span) / span
    start_lord = DASHA_ORDER[idx % 9]
    out = []
    t = birth_jd - frac * DASHA_YEARS[start_lord] * year_days
    i = DASHA_ORDER.index(start_lord)
    for k in range(10):
        lord = DASHA_ORDER[(i + k) % 9]
        dur = DASHA_YEARS[lord] * year_days
        md = {"lord": lord, "start": t, "end": t + dur, "sub": []}
        tt = t
        j0 = DASHA_ORDER.index(lord)
        for kk in range(9):
            al = DASHA_ORDER[(j0 + kk) % 9]
            ad = dur * DASHA_YEARS[al] / 120
            sub = {"lord": al, "start": tt, "end": tt + ad, "sub": []}
            if depth >= 3:
                t3 = tt
                j1 = DASHA_ORDER.index(al)
                for k3 in range(9):
                    pl = DASHA_ORDER[(j1 + k3) % 9]
                    pd = ad * DASHA_YEARS[pl] / 120
                    sub["sub"].append({"lord": pl, "start": t3, "end": t3 + pd})
                    t3 += pd
            md["sub"].append(sub)
            tt += ad
        out.append(md)
        t += dur
    return out


def dasha_at(tree: list[dict], jd: float):
    for md in tree:
        if md["start"] <= jd < md["end"]:
            for ad in md["sub"]:
                if ad["start"] <= jd < ad["end"]:
                    pd = next((p for p in ad["sub"] if p["start"] <= jd < p["end"]), None)
                    return md, ad, pd
    return None, None, None


# ---------- BaZi ----------
STEMS = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
STEMS_CN = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
BRANCHES_CN = "子丑寅卯辰巳午未申酉戌亥"
ANIMALS = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
STEM_ELEM = ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Metal", "Metal", "Water", "Water"]
BRANCH_ELEM = ["Water", "Earth", "Wood", "Wood", "Earth", "Fire", "Fire", "Earth", "Metal", "Metal", "Earth", "Water"]
ELEMS = ["Wood", "Fire", "Earth", "Metal", "Water"]


def pillar_name(si: int, bi: int) -> str:
    return f"{STEMS[si]} {BRANCHES[bi]} ({STEMS_CN[si]}{BRANCHES_CN[bi]}) — {'Yang' if si % 2 == 0 else 'Yin'} {STEM_ELEM[si]} {ANIMALS[bi]}"


def ten_god(dm: int, other: int) -> str:
    """Relation of stem `other` to Day Master stem `dm`."""
    de, oe = ELEMS.index(STEM_ELEM[dm]), ELEMS.index(STEM_ELEM[other])
    same_pol = (dm % 2) == (other % 2)
    rel = (oe - de) % 5
    names = {
        0: ("Friend (peer)", "Rob Wealth (rival peer)"),
        1: ("Eating God (gentle output)", "Hurting Officer (bold output)"),
        2: ("Indirect Wealth", "Direct Wealth"),
        3: ("Seven Killings (pressure)", "Direct Officer (authority)"),
        4: ("Indirect Resource", "Direct Resource"),
    }
    return names[rel][0 if same_pol else 1]


def day_pillar(y: int, m: int, d: int):
    jdn = int(swe.julday(y, m, d, 12.0) + 0.5)
    idx = (jdn + 49) % 60
    return idx % 10, idx % 12


def solar_longitude_local_date(y, m, d, tz=None) -> float:
    return lon(jd_of(datetime(y, m, d, 12, tzinfo=tz or TZ)), swe.SUN)


def bazi_year_month(dt: datetime):
    """Year and month pillars from the Sun's longitude (solar-term boundaries)."""
    j = jd_of(dt)
    sl = lon(j, swe.SUN)
    # month branch: Yin (Tiger) month starts at 315 deg (Li Chun); each 30 deg after
    k = int(((sl - 315) % 360) // 30)  # 0 = Yin month
    mb = (2 + k) % 12
    # year: changes at Li Chun (315 deg)
    y = dt.astimezone(UTC).year
    # find whether we are before this civil year's Li Chun
    lichun = roots(lambda t: wrap(lon(t, swe.SUN) - 315), swe.julday(y, 1, 20, 0), swe.julday(y, 2, 15, 0), 0.5)[0]
    yy = y if j >= lichun else y - 1
    ys = (yy - 4) % 10
    yb = (yy - 4) % 12
    # month stem: Tiger month stem = (ys*2 + 2) % 10
    ms = ((ys % 5) * 2 + 2 + k) % 10
    return (ys, yb), (ms, mb), lichun


def bazi_hour(day_stem: int, hour_local: float):
    hb = int(((hour_local + 1) % 24) // 2)
    hs = ((day_stem % 5) * 2 + hb) % 10
    return hs, hb


# ---------- Maya ----------
TZOLKIN = ["Imix", "Ik'", "Ak'bal", "K'an", "Chikchan", "Kimi", "Manik'", "Lamat", "Muluk", "Ok", "Chuwen", "Eb",
           "Ben", "Ix", "Men", "Kib", "Kaban", "Etz'nab", "Kawak", "Ajaw"]
KICHE = ["Imox", "Iq'", "Aq'ab'al", "K'at", "Kan", "Kame", "Kej", "Q'anil", "Toj", "Tz'i'", "B'atz'", "E",
         "Aj", "I'x", "Tz'ikin", "Ajmaq", "No'j", "Tijax", "Kawoq", "Ajpu"]
HAAB = ["Pop", "Wo", "Sip", "Sotz'", "Sek", "Xul", "Yaxk'in", "Mol", "Ch'en", "Yax", "Sak", "Keh", "Mak",
        "K'ank'in", "Muwan", "Pax", "K'ayab", "Kumk'u", "Wayeb"]


def maya(y: int, m: int, d: int) -> dict:
    jdn = int(swe.julday(y, m, d, 12.0) + 0.5)
    days = jdn - 584283
    num = (days + 3) % 13 + 1
    name = (days + 19) % 20
    haab_day = (days + 348) % 365
    lc = []
    rem = days
    for unit in (144000, 7200, 360, 20, 1):
        lc.append(rem // unit)
        rem %= unit
    return {"tzolkin": f"{num} {TZOLKIN[name]}", "kiche": f"{num} {KICHE[name]}", "number": num, "sign_index": name,
            "haab": f"{haab_day % 20} {HAAB[haab_day // 20]}", "long_count": ".".join(str(x) for x in lc),
            "lord_of_night": f"G{(days % 9) or 9}"}


# ---------- Numerology (Pythagorean; Y as consonant per project protocol) ----------
PYTH = {c: (i % 9) + 1 for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
TR = str.maketrans({"Â": "A", "â": "a", "İ": "I", "ı": "i", "Ş": "S", "ş": "s", "Ç": "C", "ç": "c", "Ğ": "G",
                    "ğ": "g", "Ö": "O", "ö": "o", "Ü": "U", "ü": "u", "Î": "I", "î": "i", "Û": "U", "û": "u"})
VOWELS = set("AEIOU")


def reduce_num(n: int, keep_master: bool = True) -> int:
    while n > 9 and not (keep_master and n in (11, 22, 33)):
        n = sum(int(c) for c in str(n))
    return n


def name_numbers(full: str) -> dict:
    parts = [p for p in full.translate(TR).upper().split() if p]
    def part_sum(p, pred):
        return sum(PYTH[c] for c in p if c.isalpha() and pred(c))
    res = {}
    for label, pred in (("expression", lambda c: True), ("soul_urge", lambda c: c in VOWELS),
                        ("personality", lambda c: c not in VOWELS)):
        reduced_parts = [reduce_num(part_sum(p, pred)) for p in parts]
        total = sum(reduced_parts)
        res[label] = {"parts_raw": [part_sum(p, pred) for p in parts], "parts_reduced": reduced_parts,
                      "compound": total, "root": reduce_num(total, keep_master=False),
                      "display": f"{total}/{reduce_num(total, keep_master=False)}" if total > 9 else str(total)}
    return res


def date_numbers(y: int, m: int, d: int) -> dict:
    rm, rd, ry = reduce_num(m), reduce_num(d), reduce_num(sum(int(c) for c in str(y)))
    lp = reduce_num(rm + rd + ry)
    p1 = reduce_num(rm + rd, False); p2 = reduce_num(rd + ry, False); p3 = reduce_num(p1 + p2, False); p4 = reduce_num(rm + ry, False)
    rm1, rd1, ry1 = reduce_num(m, False), reduce_num(d, False), reduce_num(ry, False)
    c1 = abs(rm1 - rd1); c2 = abs(rd1 - ry1); c3 = abs(c1 - c2); c4 = abs(rm1 - ry1)
    first_end = 36 - reduce_num(lp, False)
    return {"life_path": lp, "birthday": f"{d}/{reduce_num(d, False)}", "attitude": reduce_num(reduce_num(m) + reduce_num(d), False),
            "pinnacles": [p1, p2, p3, p4], "challenges": [c1, c2, c3, c4],
            "pinnacle_ages": [f"0–{first_end}", f"{first_end + 1}–{first_end + 9}", f"{first_end + 10}–{first_end + 18}", f"{first_end + 19}+"],
            "periods": [reduce_num(m, False), reduce_num(d, False), reduce_num(ry, False)]}


def personal_year(bm: int, bd: int, year: int) -> int:
    return reduce_num(reduce_num(bm, False) + reduce_num(bd, False) + reduce_num(sum(int(c) for c in str(year)), False), False)


def personal_month(py: int, month: int) -> int:
    return reduce_num(py + reduce_num(month, False), False)


def personal_day(pm: int, day: int) -> int:
    return reduce_num(pm + reduce_num(day, False), False)


def dump(obj, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=1, default=str))
