#!/usr/bin/env python3
"""Partial historical-condition behavioral pilot, not a complete honorability rule.
Private 15-chart panel only; no rank-based condition assignment.
"""
from __future__ import annotations
import argparse,json,os
from collections import Counter
from pathlib import Path
import numpy as np
import compare_planet_character_century_v01 as s
import compare_bounded_behavior_v01 as b
import ptolemy_iii13_five_mode_aspect_century_v01 as src

POLICIES=("familiarity_only","fixed_sect_contrast")

def condition(own,fixed_match,fixed_opposite,contrary,policy):
    if policy not in POLICIES:
        raise ValueError("Unknown partial condition sensitivity")
    if fixed_match and fixed_opposite:
        raise ValueError("Conflicting known fixed-sect evidence")
    # A contrary-square witness is not a sufficient adverse judgment.
    # It prevents positive admission in both deliberately partial rules.
    if contrary:
        return None
    if own or fixed_match:
        return 0
    if policy=="fixed_sect_contrast" and fixed_opposite:
        return 1
    return None

def place_condition(lon,alt,leader,policy):
    if leader<0 or src.PLANETS[leader] not in s.FIVE:
        return None
    v=src.qualifier_flags(lon,alt,np.array([leader]))
    def f(k):return bool(v[k][0])
    return condition(f("own_domicile"),f("fixed_sect_matches_chart"),
                     f("fixed_sect_opposite_chart"),f("opposite_fixed_sect_preceding_square_witness"),policy)

def compare(units,rows,reg,hdobs,obs):
    a,den,trace=s.tables(reg,obs)
    results={}
    for u in units:
        c=u["chart_midpoint"];w=c["Western"]["source_witness"]
        lon=np.array([[float(w["traditional_planets"][z]["longitude_degrees"]) for z in s.BODIES]])
        alt=np.array([float(w["sun_true_altitude_degrees"])])
        h=b.hd_score(c["HD"],rows,hdobs)["score"]
        scenarios={}
        for tag,gm,pm,gl,pl in s.branches(lon,alt):
            mi,li=int(gm[0]),int(gl[0])
            for pol in POLICIES:
                mc,lc=place_condition(lon,alt,mi,pol),place_condition(lon,alt,li,pol)
                m=float(a[mc,0,mi,mi]) if mc is not None else 0.
                l=float(a[lc,1,li,li]) if lc is not None else 0.
                v=(m+l)/2
                scenarios[tag+"|"+pol]={"mercury_condition":s.CONDITIONS[mc] if mc is not None else None,
                   "moon_condition":s.CONDITIONS[lc] if lc is not None else None,
                   "mercury":m,"moon":l,"western":v,"joint":(h+v)/2}
        results[u["private_id"]]=scenarios
    if len(results)!=len(units) or not results:raise ValueError("Panel identity drift")
    ranks={}
    for tag in next(iter(results.values())):
        ranks[tag]=b.exact_rank({i:v[tag]["joint"] for i,v in results.items()})
    return {"status":"PARTIAL_SOURCE_CONDITION_PANEL_ONLY_NOT_VALIDATED",
            "n":len(units),"observed_domains":den,"cases":results,"ranks":ranks}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("inventory","mapping-library","hd-evidence","evidence","output"):
        p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args()
    if any(x.resolve().is_relative_to(s.ROOT) for x in vars(a).values()):
        raise ValueError("Private input/output paths outside checkout required")
    inv=json.loads(a.inventory.read_text())
    h=json.loads(a.hd_evidence.read_text());e=json.loads(a.evidence.read_text())
    if h["inventory_sha256"]!=b.digest(a.inventory) or e["map_sha256"]!=s.MAP_SHA or e["hd_evidence_sha256"]!=b.digest(a.hd_evidence):
        raise ValueError("Frozen input mismatch")
    out=compare(inv["comparison_units"],b.load_mapping(a.mapping_library),s.load_registry(),h["hd"],e["observations"])
    out["source_hashes"]={k:b.digest(v) for k,v in vars(a).items() if k!="output"}
    out["runner_sha256"]=b.digest(__file__)
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("Private pilot complete:",out["n"],"units;",len(out["ranks"]),"historical/condition scenarios.")

if __name__=="__main__":main()
