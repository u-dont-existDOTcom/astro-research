"""Common tables and the one fair test used for every technique.

One person's data is read from a JSON file that is NOT part of this repository (set ASTRO_PERSON to its path):
  {"birth_local": "1970-01-01T12:00", "tz": "Europe/Paris", "lat": 48.85, "lon": 2.35,
   "table_start": "2012-01-01", "table_days": 5433,
   "events": [{"date": "2014-03-09", "area": "W"}, ...]}
Only events dated to the day belong in the list.

The test: mean activation of a technique on the person's dates, against the same set of dates shifted together
through the daily table. Shifting them together keeps their clustering, which independent random dates would not.
"""
import json, math, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "engine"))
P = json.load(open(os.environ["ASTRO_PERSON"]))
os.environ.setdefault("ASTRO_LAT", str(P["lat"])); os.environ.setdefault("ASTRO_LON", str(P["lon"])); os.environ.setdefault("ASTRO_TZ", P["tz"])
from astro_engine import *          # noqa: E402,F401,F403
import numpy as np                  # noqa: E402
CACHE = Path(os.environ.get("ASTRO_CACHE", ".cache")); CACHE.mkdir(exist_ok=True)
REF = datetime.fromisoformat(P["birth_local"]).replace(tzinfo=TZ); BJ = jd_of(REF); NAT = natal(REF)
_d0 = datetime.fromisoformat(P.get("table_start", "2012-01-01")); D0 = datetime(_d0.year, _d0.month, _d0.day, 12, tzinfo=TZ); ND = int(P.get("table_days", 5433))
DAYS = [D0 + timedelta(days=i) for i in range(ND)]
JD = np.array([jd_of(d) for d in DAYS]); ISO = [d.strftime("%Y-%m-%d") for d in DAYS]; IDX = {s: i for i, s in enumerate(ISO)}
YEAR = np.array([d.year for d in DAYS])
BODY = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Mean Node", "Chiron"]
_cache = CACHE / f"pos_{ISO[0]}_{ND}.npz"
if _cache.exists():
    _z = np.load(_cache); POS = _z["pos"]; SPD = _z["spd"]
else:
    POS = np.zeros((ND, len(BODY))); SPD = np.zeros((ND, len(BODY)))
    for i, j in enumerate(JD):
        for k, b in enumerate(BODY):
            POS[i, k] = lon(j, BODIES[b]); SPD[i, k] = ((lon(j + 0.5, BODIES[b]) - lon(j - 0.5, BODIES[b]) + 180) % 360) - 180
    np.savez(_cache, pos=POS, spd=SPD)
NP = {b: NAT["tropical"][b] if b in NAT["tropical"] else lon(BJ, BODIES[b]) for b in BODY}
NPL = np.array([NP[b] for b in BODY]); ASC, MC = NAT["ASC"], NAT["MC"]
TARGETS = {b: NP[b] for b in BODY}; TARGETS.update({"ASC": ASC, "MC": MC})
TN = list(TARGETS); TL = np.array([TARGETS[k] for k in TN])
_ev = sorted((e for e in P["events"] if e["date"] in IDX), key=lambda e: e["date"])
EV = list(range(len(_ev))); EVI = np.array([IDX[e["date"]] for e in _ev]); AREA = {k: e.get("area", "") for k, e in enumerate(_ev)}
ALT = {k: set(e.get("alternates", "")) | {e.get("area", "")} for k, e in enumerate(_ev)}
H1 = np.array([k for k in EV if k < len(EV) // 2 + len(EV) % 2]); H2 = np.array([k for k in EV if k >= len(EV) // 2 + len(EV) % 2])     # earlier and later half
def sep(a, b): return np.abs((a - b + 180.0) % 360.0 - 180.0)
def orb_to(diff, angles):
    d = np.mod(diff, 360.0)[..., None]; a = np.array(sorted(set(list(angles) + [360 - x for x in angles if x not in (0, 180)])), dtype=float)
    return np.min(np.abs((d - a + 180.0) % 360.0 - 180.0), axis=-1)
def gauss(o, s): return np.exp(-0.5 * (o / s) ** 2)
RNG = np.random.default_rng(20261117); SHIFTS = RNG.integers(120, ND - 120, 4000)
def test(A, idx=None, shifts=SHIFTS):
    """z and one-sided p for 'activation is higher on the person's dates'."""
    idx = EVI if idx is None else idx
    obs = A[idx].mean(); null = np.array([A[(idx + s) % ND].mean() for s in shifts])
    sd = null.std() or 1e-9
    return float((obs - null.mean()) / sd), float((null >= obs).mean()), float(obs), float(null.mean())
RESULTS = []
def run(name, A, note="", tsens=False, family=""):
    A = np.asarray(A, dtype=float)
    z, p, obs, nm = test(A); z1, p1, _, _ = test(A, EVI[H1]); z2, p2, _, _ = test(A, EVI[H2])
    RESULTS.append({"name": name, "family": family, "z": round(z, 2), "p": round(p, 4), "z_earlier_half": round(z1, 2), "z_later_half": round(z2, 2),
                    "on_dates": round(obs, 4), "baseline": round(nm, 4), "birth_time_sensitive": tsens, "note": note})
    return z
def peak_rule(A, top=5, before=4, after=3, min_gap=7):
    """Godbout's rule of thumb applied to any daily curve: an event counts if it falls from 4 days before to 3 days after
    one of the year's five highest peaks."""
    win = np.zeros(ND, dtype=bool)
    for y in sorted(set(YEAR)):
        ii = np.nonzero(YEAR == y)[0]; a = A[ii]; order = np.argsort(-a); picked = []
        for k in order:
            if all(abs(int(k) - q) >= min_gap for q in picked): picked.append(int(k))
            if len(picked) == top: break
        for q in picked:
            lo, hi = max(0, ii[0] + q - before), min(ND - 1, ii[0] + q + after); win[lo:hi + 1] = True
    hits = int(win[EVI].sum()); null = np.array([win[(EVI + s) % ND].sum() for s in SHIFTS])
    return hits, float(win.mean()), float(null.mean()), float((null >= hits).mean())
def save(path): json.dump(RESULTS, open(path, "w"), indent=1, ensure_ascii=False)
