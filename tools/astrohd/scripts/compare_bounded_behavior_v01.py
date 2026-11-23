#!/usr/bin/env python3
"""Exploratory, source-conditional comparison. Human inputs/results stay private.
No fitted weights, common-governor gate, complete doctrine or validation claim.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import numpy as np
from ptolemy_iii13_five_mode_aspect_century_v01 import (
    base, VARIANTS, PLANETS, TOLS, MERCURY_POLICIES, SCOPES,
    aspect_bounds, interval_leader, qualifier_flags,
)

ROOT = Path(__file__).resolve().parents[3]
MAP_SHA = "3424672432f7f071ec90ef9ddce52a67ff6794911e92b1a1e04f079262ea6200"
MODES = ("equinoctial", "fixed", "bicorporeal", "solstitial", "fixed", "bicorporeal",
         "equinoctial", "fixed", "bicorporeal", "solstitial", "fixed", "bicorporeal")
PLACES = {"mercury": 2, "moon": 1}
WEST_KEYS = {f"{p}_{m}" for p in PLACES for m in ("fixed", "bicorporeal", "solstitial")}
WEST_KEYS |= {"moon_waxing_frankness", "moon_waning_caution"}

def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()

def load_mapping(path):
    if digest(path) != MAP_SHA:
        raise ValueError("Frozen generic HD mapping SHA mismatch")
    obj = json.loads(Path(path).read_text())
    rows = [x for x in obj["mappings"] if x["status"] == "frozen"]
    if obj["model_version"] != "V4/V3.2-symbolic-v1" or len(rows) != 27:
        raise ValueError("Unexpected frozen mapping version or count")
    return admitted(rows)

def admitted(rows):
    return [r for r in rows if r["dependency_cluster"] != "AUTHORITY_DECISION"
            and r["chart_feature_predicate"]["feature"] != "authority"]

def norm(v):
    return "".join(c for c in str(v).lower() if c.isalnum())

def hd_active(chart, pred):
    f, op, vals = pred["feature"], pred["operator"], pred["values"]
    if f not in chart or chart[f] is None:
        return None
    value = chart[f]
    if f == "profile" and op == "profile_has_line":
        lines = str(value).split("/")
        if len(lines) != 2 or any(x not in "123456" or len(x) != 1 for x in lines):
            raise ValueError("Invalid HD profile")
        return bool(set(lines) & set(map(str, vals)))
    if f == "type" and op == "equals_any":
        return norm(value) in {norm(x) for x in vals}
    if f == "defined_centers" and op in ("contains_any", "not_contains_any"):
        if not isinstance(value, list):
            raise ValueError("Expected center list")
        alias = {"ego": "heart", "heartego": "heart", "will": "heart", "identity": "g"}
        def center(x):
            n = norm(x)
            return alias.get(n, n)
        present = bool({center(x) for x in value} & {center(x) for x in vals})
        return present if op == "contains_any" else not present
    raise ValueError("Unsupported admitted HD predicate")

def checked_obs(obs, keys):
    if set(obs) - set(keys):
        raise ValueError("Observation without admitted source mapping")
    if any(v is not None and (type(v) is not int or v not in (-1, 1)) for v in obs.values()):
        raise ValueError("Observations must be explicit +1, -1 or null")

def hd_score(chart, rows, obs):
    checked_obs(obs, [r["mapping_id"] for r in rows])
    groups = defaultdict(list)
    trace = {}
    for r in rows:
        i, g = r["mapping_id"], r["dependency_cluster"]
        v = obs.get(i)
        active = hd_active(chart, r["chart_feature_predicate"])
        trace[i] = {"observed": v, "active": active, "cluster": g}
        if v is not None:
            groups[g].append(v if active else 0)
    # Denominator fixed across candidates, including absent/unknown carriers.
    # Missing carrier is NOT a human contradiction. Coverage is separately explicit.
    clusters = {g: sum(v)/len(v) for g,v in groups.items()}
    return {"score": sum(clusters.values())/len(clusters) if clusters else 0.,
            "observed": sum(v is not None for v in obs.values()),
            "known_active_observed": sum(t["active"] is True and t["observed"] is not None for t in trace.values()),
            "unknown_carrier_observed": sum(t["active"] is None and t["observed"] is not None for t in trace.values()),
            "clusters": clusters, "trace": trace}

def mode(lon):
    if not np.isfinite(lon) or not 0 <= lon < 360:
        raise ValueError("Invalid longitude")
    return MODES[int(lon//30)]

def vote(obs, key):
    return obs.get(key) if obs.get(key) is not None else 0

def phase_key(lon):
    d = (lon[1]-lon[0]) % 360
    return "moon_waxing_frankness" if 0 < d < 180 else "moon_waning_caution" if 180 < d < 360 else None

def direct(lon, obs):
    m, l = (f"{p}_{mode(lon[i])}" for p,i in PLACES.items())
    phase = phase_key(lon)
    return {"mercury": vote(obs,m), "moon_mode": vote(obs,l),
            "moon_phase": vote(obs,phase), "mode_keys": [m,l], "phase_key": phase,
            "active_observations": [k for k in (m,l,phase) if obs.get(k) is not None]}

def bounded_place(lon, alt, ref, obs, guaranteed, possible):
    name = "mercury" if ref == 2 else "moon"
    bodies = np.flatnonzero(possible).tolist()
    vals = []
    flags = {}
    for b in bodies:
        key = f"{name}_{mode(lon[b])}"
        vals.append(vote(obs,key))
        f = qualifier_flags(np.asarray([lon]), np.asarray([alt]), np.asarray([b]))
        flags[PLANETS[b]] = {**{k: bool(v[0]) for k,v in f.items()},
                              "mode_key": key, "observed": obs.get(key)}
    # Near-horizon unknown yields no admitted governor claim, rather than
    # selecting a body or treating the chart as contradicted.
    strict = vote(obs, f"{name}_{mode(lon[guaranteed])}") if guaranteed >= 0 else 0
    return {"strict": strict, "possible": [min(vals), max(vals)] if vals else [0,0],
            "with_abstention": [min([0]+vals), max([0]+vals)],
            "guaranteed": PLANETS[guaranteed] if guaranteed >= 0 else None,
            "candidates": flags, "no_governor_admitted": not bodies}

def family(m, l, phase, hd):
    # Each place equally weighted; Moon phase and sign split the lunar slot.
    # These are declared arithmetic sensitivity weights, not ancient or fitted weights.
    w = (m + (l+phase)/2)/2
    return w, (hd+w)/2

def ranks(bounds):
    result = {}
    for i,(lo,hi) in bounds.items():
        others = [v for k,v in bounds.items() if k != i]
        result[i] = [1+sum(a > hi+1e-12 for a,b in others),
                     1+sum(b >= lo-1e-12 for a,b in others)]
    return result

def exact_rank(values):
    return {k: {"rank": 1+sum(b > a+1e-12 for b in values.values()),
                "tied": sum(abs(a-b)<1e-12 for b in values.values())}
            for k,a in values.items()}

def compare(units, rows, hd_obs, west_obs):
    checked_obs(west_obs,WEST_KEYS)
    ids = [u["private_id"] for u in units]
    if len(ids)<2 or len(set(ids)) != len(ids):
        raise ValueError("Need distinct comparison units")
    cases = {}
    lon, alt = [], []
    for u in units:
        i,c = u["private_id"],u["chart_midpoint"]
        w = c["Western"]["source_witness"]
        p = [float(w["traditional_planets"][b]["longitude_degrees"]) for b in PLANETS]
        a = float(w["sun_true_altitude_degrees"])
        if not np.isfinite(a) or abs(a)>90:
            raise ValueError("Invalid solar altitude")
        lon.append(p);alt.append(a)
        h = hd_score(c["HD"],rows,hd_obs)
        q = direct(p,west_obs)
        ws,j = family(q["mercury"],q["moon_mode"],q["moon_phase"],h["score"])
        cases[i] = {"hd":h,"direct":q,"western_direct":ws,"joint_direct":j,
                    "historical_score_read_only":u.get("historical_score")}
    lon,alt = np.asarray(lon),np.asarray(alt)
    valid = np.abs(alt)>base.SUN_ALT_UNCERTAINTY
    scenarios = {}
    for (scheme,co),tol,policy,scope in product(VARIANTS,TOLS,MERCURY_POLICIES,SCOPES):
        branches = {}
        for ref in (2,1):
            b=base.four_mode_votes(lon[:,ref],alt,scheme,co).astype(np.int16)
            low,high,_=aspect_bounds(lon,ref,tol,policy if ref==2 else "degree_near_rays",scope)
            branches[ref] = {label:interval_leader(b+low,b+upper,valid)
                             for label,upper in (("geometry",high),("phase_envelope",1))}
        for label in ("geometry","phase_envelope"):
            tag=f"{scheme}|{co}|{tol}|{policy}|{scope}|{label}"
            out={}; western={}; joint={}; strict={}
            for n,i in enumerate(ids):
                pl={}
                for ref in (2,1):
                    g,p=branches[ref][label]
                    pl[ref]=bounded_place(lon[n],alt[n],ref,west_obs,int(g[n]),p[n])
                h=cases[i]["hd"]["score"]; ph=cases[i]["direct"]["moon_phase"]
                # Phase is observed separately from the uncertain fifth-mode
                # phase claim. Conservative case allows zero for each testimony.
                m,l=pl[2]["with_abstention"],pl[1]["with_abstention"]
                wl,jl=family(m[0],l[0],min(0,ph),h)
                wh,jh=family(m[1],l[1],max(0,ph),h)
                w0,j0=family(pl[2]["strict"],pl[1]["strict"],ph,h)
                mp,lp=pl[2]["possible"],pl[1]["possible"]
                pwl,pjl=family(mp[0],lp[0],ph,h)
                pwh,pjh=family(mp[1],lp[1],ph,h)
                western[i]=[wl,wh];joint[i]=[jl,jh];strict[i]=j0
                out[i]={"mercury":pl[2],"moon":pl[1],"western_possible":[pwl,pwh],
                        "joint_possible":[pjl,pjh],"western_conservative":[wl,wh],
                        "joint_conservative":[jl,jh],"joint_strict":j0}
            scenarios[tag]={"cases":out,"western_conservative_rank_interval":ranks(western),
                            "joint_conservative_rank_interval":ranks(joint),
                            "joint_possible_rank_interval":ranks({i:v["joint_possible"] for i,v in out.items()}),
                            "joint_strict_rank":exact_rank(strict)}
    if len(scenarios)!=64:
        raise ValueError("Historical scenario cross-product incomplete")
    return {"status":"EXPLORATORY_POST_EXPOSURE_NOT_VALIDATED",
            "n":len(ids),"admitted_hd_mappings":len(rows),"hd_observations":len([v for v in hd_obs.values() if v is not None]),
            "western_observations":len([v for v in west_obs.values() if v is not None]),
            "cases":cases,"scenarios":scenarios,
            "direct_ranks":{key:exact_rank({i:c[key] if key!="hd" else c[key]["score"] for i,c in cases.items()})
                            for key in ("hd","western_direct","joint_direct")}}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("inventory","mapping-library","evidence","output"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    for path in (a.inventory,a.evidence,a.mapping_library,a.output):
        if path.resolve().is_relative_to(ROOT):
            p.error("Personal input/output and private mapping must be outside the public checkout")
    e=json.loads(a.evidence.read_text());u=json.loads(a.inventory.read_text())
    if e.get("inventory_sha256")!=digest(a.inventory):
        raise ValueError("Private inventory does not match frozen coding")
    out=compare(u["comparison_units"],load_mapping(a.mapping_library),e["hd"],e["western"])
    out["input_digests"]={"inventory":digest(a.inventory),"evidence":digest(a.evidence),
                          "mapping":digest(a.mapping_library),"scorer":digest(__file__)}
    import os
    os.umask(0o077)
    with a.output.open("x") as f:
        json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("Private exploratory comparison written;",out["n"],"units;",len(out["scenarios"]),"scenario branches.")

if __name__=="__main__":
    main()
