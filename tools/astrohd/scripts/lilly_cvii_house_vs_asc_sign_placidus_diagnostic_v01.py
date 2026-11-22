#!/usr/bin/env python3
"""Lilly CVII first-house geometry SENSITIVITY (Placidus vs ASC-sign proxy).

The existing historical Western source cache includes Placidus cusps, but
Lilly used historically different quadrant conventions (Regiomontanus).
This diagnostic quantifies the bias of replacing a *house* with the
30-degree zodiacal *ASC sign*. It does NOT claim Placidus is Lilly's rule
nor that this is a complete original 1647 manners-significator algorithm.

Original source 1926–2026 fixed-site 15-minute Swiss longitude and
Placidus cusp grid: all 36+36 binary shards SHA256 verified. First-house
arc from cusp 1 inclusive to cusp 2 exclusive follows increasing ecliptic
longitude modulo 360. Discontinuities/boundary equality are not certified
between sample times. Source join orb 1/3/5/10° is *engineering only*.
"""
from __future__ import annotations
import argparse
from collections import Counter
import importlib.util
from pathlib import Path
import json
import numpy as np

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("lilly2",HERE/"lilly_cvii_second_order_conjunction_grid_v01.py")
lilly2=importlib.util.module_from_spec(sp);sp.loader.exec_module(lilly2)
initial=lilly2.initial

def flags(planets,angles):
    p=np.asarray(planets,dtype=np.float64)
    a=np.asarray(angles,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or a.shape!=(len(p),17):
        raise ValueError("Expected seven classical longitudes and 17 Placidus/ASC fields")
    if not np.all(np.isfinite(p)) or not np.all(np.isfinite(a[:,:2])) or not np.all(np.isfinite(a[:,5:7])):
        raise ValueError("Nonfinite longitude/cusp")
    if np.any((p<0)|(p>=360)) or np.any((a[:,[0,5,6]]<0)|(a[:,[0,5,6]]>=360)):
        raise ValueError("Unnormalized zodiacal longitude")
    start=a[:,5];end=a[:,6]
    widths=(end-start)%360.
    if np.any((widths<=0)|(widths>180)):
        raise ValueError("Invalid first-house cusp arc width")
    placidus=((p-start[:,None])%360)<widths[:,None]
    in_house=placidus.any(axis=1)
    asc_sign=np.floor(a[:,0]/30).astype(np.int8)
    in_asc_sign=(np.floor(p/30).astype(np.int8)==asc_sign[:,None]).any(axis=1)
    return {
      "any_placidus_first_house":in_house,
      "any_ASC_zodiac_sign":in_asc_sign,
      "first_house_only":in_house&~in_asc_sign,
      "asc_zodiac_sign_only":in_asc_sign&~in_house,
      "both_have_planet":in_house&in_asc_sign,
      "neither_has_planet":~in_house&~in_asc_sign,
      "no_placidus_house_planet":~in_house,
      "no_ASC_sign_planet":~in_asc_sign,
      "placidus_first_house_arc_deg":widths,
    }

def joined_4_externals(planets,t):
    p=np.asarray(planets,dtype=np.float64)
    joined=np.zeros(len(p),dtype=bool)
    for k in (3,4,5,6):
        joined|=(lilly2.separation(p[:,k],p[:,1])<=t) | (lilly2.separation(p[:,k],p[:,2])<=t)
    return joined

def scan(planet_rows,angle_rows):
    p=np.asarray(planet_rows,dtype=np.float64)
    a=np.asarray(angle_rows,dtype=np.float64)
    data=flags(p[:,:7],a)
    out={}
    for name,m in data.items():
        if name!="placidus_first_house_arc_deg":
            out[name]=int(m.sum())
    out["placidus_first_house_arc_above_30_deg"]=int((data["placidus_first_house_arc_deg"]>30).sum())
    out["placidus_first_house_arc_below_30_deg"]=int((data["placidus_first_house_arc_deg"]<30).sum())
    for t in lilly2.THRESHOLDS:
        k=str(int(t))
        joined=joined_4_externals(p[:,:7],t)
        out[f"{k}deg_four_external_when_ASC_sign_empty"]=int((joined&data["no_ASC_sign_planet"]).sum())
        out[f"{k}deg_four_external_when_placidus_first_house_empty"]=int((joined&data["no_placidus_house_planet"]).sum())
    return out

def run(west,angles,hashes=True):
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    wplan=json.loads(wp.read_bytes());wman=json.loads(wm.read_bytes())
    aplan=json.loads(ap.read_bytes());aman=json.loads(am.read_bytes())
    n=initial.check_manifest(wplan,wman,aplan,aman)
    if wman["plan_sha256"]!=initial.source_hash(wp) or aman["plan_sha256"]!=initial.source_hash(ap):
        raise RuntimeError("Manifest source plan hash mismatch")
    if aplan.get("cols",[])[5:7]!=["placidus_cusp_1","placidus_cusp_2"]:
        raise RuntimeError("Placidus boundaries are not in declared columns")
    results=Counter()
    for w,a in zip(wman["chunks"],aman["shards"]):
        pw=west/"chunks"/w["file"];pa=angles/"shards"/a["file"]
        count=w["count"]
        if pw.stat().st_size!=count*64 or pa.stat().st_size!=count*136:
            raise RuntimeError("Unexpected source binary shard byte size")
        if hashes and (initial.source_hash(pw)!=w["sha256"] or initial.source_hash(pa)!=a["sha256"]):
            raise RuntimeError("Original source binary shard SHA mismatch")
        planet=np.memmap(pw,dtype="<f8",shape=(count,8),mode="r")
        angle=np.memmap(pa,dtype="<f8",shape=(count,17),mode="r")
        results.update(scan(planet,angle))
    c=dict(results)
    if c["any_ASC_zodiac_sign"]!=1428060 or c["no_ASC_sign_planet"]!=2078340:
        raise RuntimeError("Original 3.5m ASC-zodiac-sign source counts changed")
    if c["any_placidus_first_house"]+c["no_placidus_house_planet"]!=n:
        raise RuntimeError("Placidus 1st house coverage incomplete")
    if c["first_house_only"]+c["asc_zodiac_sign_only"]+c["both_have_planet"]+c["neither_has_planet"]!=n:
        raise RuntimeError("Geometry comparison is not a partition")
    for t in lilly2.THRESHOLDS:
        k=str(int(t))
        if c[f"{k}deg_four_external_when_ASC_sign_empty"]>c["no_ASC_sign_planet"] or c[f"{k}deg_four_external_when_placidus_first_house_empty"]>c["no_placidus_house_planet"]:
            raise RuntimeError("Proximity source upper bound exceeded")
    return {
       "schema":"Lilly_CVII_source_house_vs_ASC_sign_proxy_placidus_diagnostic_v01",
       "status":"SOURCE_INACCURATE_PLACIDUS_HOUSE_VS_SIGN_PROXY_DIAGNOSTIC_ONLY_NO_LILLY_HISTORICAL_RECONSTRUCTION",
       "original_Lilly_1647_historical_house_system":"REGIOMONTANUS_ORIGINAL_NOT_CALCULATED_HERE",
       "modern_house_system_in_binary_source":"Placidus",
       "not_historically_substitutable":True,
       "source_planet_rule_first_house_not_equivalent_to_ASC_zodiac_sign":True,
       "data_sample_count":n,
       "sampling_minutes":15,
       "time_grid":[wplan["utc_start_inclusive"],wplan["utc_end_exclusive"]],
       "source_manifest_sha256":{"planet":initial.source_hash(wm),"angles":initial.source_hash(am)},
       "source_shards_sha256_reverified":hashes,
       "counts":c,
       "thresholds_joining_external_degrees_ENGINEERING_ONLY":list(lilly2.THRESHOLDS),
       "original_dispositor_and_fortification_rules_not_computed":True,
       "no_private_natal_data":True,
       "no_human_behavior_score_or_prediction":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--west",type=Path,required=True)
    p.add_argument("--angles",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--skip-shard-hashes",action="store_true")
    a=p.parse_args()
    if a.out.exists():raise FileExistsError("Source-bound diagnostic immutable output exists")
    j=run(a.west,a.angles,not a.skip_shard_hashes)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(j,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":j["status"],"sample_count":j["data_sample_count"],
                      "counts":j["counts"],"shard_hashes_verified":j["source_shards_sha256_reverified"]},sort_keys=True))

if __name__=="__main__":
    main()
