"""Test of the rule of thumb published for Mastro Expert's forecast curves (Godbout, NCGR Research Journal, winter 2018-19;
Mastro user guide): an event should fall from 4 days before to 3 days after one of the year's five highest points of the
curve for the matching theme; pure chance is said to be about one in ten.

Inputs (both private, neither belongs in this repository):
  maximums.json  {"themes": [...], "years": {"2016": {"mariage": [[month, day, score], ...by rank], ...}, ...}}
                 one set of curves per calendar year, as read from the program's Maximums table
  events.json    [{"date": "2016-05-21", "theme": "mariage", "area_themes": ["amour", "engagement", ...]}, ...]
                 the theme of every event is fixed BEFORE any curve is looked at

Chance is not assumed to be one in ten. For every event it is the share of that year's days that lie inside the
windows of the event's theme, so repeated or overlapping peaks are counted honestly.
Usage: python forecast_rule_test.py maximums.json events.json out.json"""
import json, sys, datetime as dt
import numpy as np
M = json.load(open(sys.argv[1])); EVENTS = json.load(open(sys.argv[2])); YEARS = M["years"]; THEMES = M["themes"]; rng = np.random.default_rng(11)
def ndays(y): return 366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365
def peaks(y, th, k=5, distinct=False):
    out = []
    for m, d, sc in YEARS[str(y)].get(th, []):
        try: p = dt.date(y, m, d)
        except ValueError: continue
        if distinct and any(abs((p - q).days) <= 3 for q in out): continue
        out.append(p)
        if len(out) == k: break
    return out
def cover(y, ths, k=5, distinct=False, before=4, after=3):
    c = np.zeros(ndays(y), bool); j0 = dt.date(y, 1, 1)
    for th in ths:
        for p in peaks(y, th, k, distinct):
            a, b = (p - j0).days - before, (p - j0).days + after; c[max(a, 0):min(b, len(c) - 1) + 1] = True
    return c
def tail(ps, k):
    d = np.zeros(len(ps) + 1); d[0] = 1.0
    for p in ps: d[1:] = d[1:] * (1 - p) + d[:-1] * p; d[0] *= (1 - p)
    return float(d[k:].sum())
ev = [(dt.date.fromisoformat(e["date"]), e) for e in EVENTS if e["date"][:4] in YEARS]
def doy(d): return (d - dt.date(d.year, 1, 1)).days
def run(label, sets, k=5, distinct=False):
    hits = [bool(cover(d.year, s, k, distinct)[doy(d)]) for (d, _), s in zip(ev, sets)]; cov = [float(cover(d.year, s, k, distinct).mean()) for (d, _), s in zip(ev, sets)]
    h = int(sum(hits)); return {"test": label, "events": len(ev), "hits": h, "expected_by_chance": round(sum(cov), 2), "chance_rate": round(float(np.mean(cov)), 3), "p_at_least_this_many": round(tail(cov, h), 4)}
prim = [[e["theme"]] for _, e in ev]; out = {"years": sorted(YEARS), "themes": len(THEMES)}
out["primary"] = run("one theme per event, the year's five highest points as listed (the published rule)", prim)
out["primary_7"] = run("one theme per event, seven highest points", prim, k=7)
out["primary_distinct"] = run("one theme per event, five separate peaks (points within 3 days merged)", prim, k=5, distinct=True)
if all("area_themes" in e for _, e in ev): out["area"] = run("every theme of the event's area of life", [e["area_themes"] for _, e in ev])
h0 = out["primary"]["hits"]; null = np.array([sum(bool(cover(d.year, prim[j])[doy(d)]) for (d, _), j in zip(ev, rng.permutation(len(ev)))) for _ in range(20000)])
out["theme_shuffle"] = {"mean_hits_when_themes_are_shuffled_among_the_same_dates": round(float(null.mean()), 2), "share_of_shuffles_with_at_least_as_many_hits": round(float((null >= h0).mean()), 4)}
S = {y: sum(cover(int(y), [th]).astype(int) for th in THEMES) for y in YEARS}; tot = sum(int(S[str(d.year)][doy(d)]) for d, _ in ev)
sim = np.array([sum(int(S[str(d.year)][rng.integers(0, ndays(d.year))]) for d, _ in ev) for _ in range(20000)])
out["any_theme"] = {"themes_with_a_top_five_point_around_the_dates": tot, "expected_by_chance": round(float(sim.mean()), 1), "share_of_random_date_sets_with_at_least_as_many": round(float((sim >= tot).mean()), 4)}
json.dump(out, open(sys.argv[3] if len(sys.argv) > 3 else "out.json", "w"), indent=1, ensure_ascii=False); print(json.dumps(out, indent=1, ensure_ascii=False))
