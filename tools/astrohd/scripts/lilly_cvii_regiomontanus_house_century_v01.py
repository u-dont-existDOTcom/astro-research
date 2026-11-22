#!/usr/bin/env python3
"""Lilly CVII source-aligned first HOUSE (Regiomontanus) geometric census.

Planet within the Regiomontanus first house = ecliptic longitude in the
oriented arc from cusp 1 INCLUSIVE to cusp 2 EXCLUSIVE. Houses calculated
using swisseph.houses_ex (... hsys=b'R') at each of the actual original
3,506,400 15-minute UTC timestamps and exact original fixed research site.
All 36 original planet+Placidus reference angle binary shards SHA256 verified.
Strict Swiss version 2.10.03 and sampled rebuilt Placidus cross-check verify
clock/longitude orientation against the old original cache.

Because Lilly's ascendant/horoscope significators also depend on
intercepted signs, planetary strength, dignity, disposition and aspects,
this is still geometric source qualification, not his completed algorithm.
House system b'R' is source-aligned historically, but the original 1647
edition's complete interpretive precedence remains under adjudication.
User/participant natal records never enter this script.

The prior ASC-sign and Placidus-house geometry are retained as
counterfactual sensitivity comparisons; neither substitutes silently
for the actual Regiomontanus first house.

Source-neutral astronomy, not evidence natal astrology predicts people.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import importlib.util
import json
import numpy as np
import swisseph as swe

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location(
  "lillyhouses",HERE/"lilly_cvii_house_vs_asc_sign_placidus_diagnostic_v01.py")
house=importlib.util.module_from_spec(sp);sp.loader.exec_module(house)
lilly=house.lilly2
initial=lilly.initial
SWISS_VERSION="2.10.03"
SEP_TOL_DEG=0.0002

def julian_from_utc(value:str):
    dt=datetime.fromisoformat(value.replace("Z","+00:00"))
    if dt.tzinfo is None or dt.utcoffset()!=timezone.utc.utcoffset(dt):
        raise ValueError("Exact UTC source start required")
    return swe.julday(dt.year,dt.month,dt.day,
                      dt.hour+dt.minute/60+dt.second/3600)

def cusp_member(planets,cusp1,cusp2):
    p=np.asarray(planets,dtype=np.float64)
    c1=np.asarray(cusp1,dtype=np.float64)
    c2=np.asarray(cusp2,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or c1.shape!=(len(p),) or c2.shape!=(len(p),):
        raise ValueError("Expected Nx7 traditional planets and N house cusps")
    if not np.all(np.isfinite(p)) or not np.all(np.isfinite(c1)) or not np.all(np.isfinite(c2)):
        raise ValueError("Invalid nonfinite source")
    if np.any((p<0)|(p>=360)) or np.any((c1<0)|(c1>=360)) or np.any((c2<0)|(c2>=360)):
        raise ValueError("Unnormalized house longitude")
    arc=(c2-c1)%360
    if np.any((arc<=0)|(arc>180)):
        raise ValueError("Invalid first-house arc")
    return ((p-c1[:,None])%360)<arc[:,None]

def calc_chunk(planets,angles,*,jd_start,lat,lon,index_first):
    p=np.asarray(planets,dtype=np.float64)
    a=np.asarray(angles,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or a.shape!=(len(p),17):
        raise ValueError("Invalid source sample shapes")
    n=len(p)
    cusps=np.empty((n,2),dtype=np.float64)
    if not (-90<lat<90 and -180<=lon<=180):
        raise ValueError("Invalid source calculation site")
    # Deterministic absolute sample index avoids cumulative date drift.
    for i in range(n):
        j=jd_start+(index_first+i)/96.
        reg,aa=swe.houses_ex(j,lat,lon,b'R')
        cusps[i,0]=reg[0]
        cusps[i,1]=reg[1]
    # Astro library re-generation is checked against the ACTUAL precomputed
    # Placidus angles from the original frozen source for each source shard:
    # first, middle, last, exact year, plus every ~1000 instants.
    checks=set((0,n//2,n-1))
    checks.update(range(0,n,1000))
    maxerr=0.
    for i in sorted(checks):
        j=jd_start+(index_first+i)/96.
        oldc,oldarms=swe.houses_ex(j,lat,lon,b'P')
        for before,after in (
            (oldc[0],a[i,5]),(oldc[1],a[i,6]),
            (oldarms[0],a[i,0]),(cusps[i,0],a[i,0])
        ):
            err=abs((before-after+180.)%360.-180.)
            maxerr=max(maxerr,err)
            if err>SEP_TOL_DEG:
                raise RuntimeError("Source time/site/angle reconstruction mismatch")
    regio=cusp_member(p,cusps[:,0],cusps[:,1]).any(axis=1)
    placidus=cusp_member(p,a[:,5],a[:,6]).any(axis=1)
    asc=np.floor(a[:,0]/30.).astype(np.int8)
    asc_hit=(np.floor(p/30.).astype(np.int8)==asc[:,None]).any(axis=1)
    c=Counter({
        "regio_first_house_any":int(regio.sum()),
        "regio_first_house_none":int((~regio).sum()),
        "placidus_first_house_any":int(placidus.sum()),
        "asc_sign_any":int(asc_hit.sum()),
        "regio_only_not_placidus":int((regio&~placidus).sum()),
        "placidus_only_not_regio":int((placidus&~regio).sum()),
        "regio_only_not_sign":int((regio&~asc_hit).sum()),
        "sign_only_not_regio":int((asc_hit&~regio).sum()),
        "regio_and_sign_both":int((regio&asc_hit).sum()),
        "regio_and_placidus_both":int((regio&placidus).sum()),
        "source_site_and_ASC_reference_checks":len(checks)*4,
    })
    for t in lilly.THRESHOLDS:
        k=str(int(t))
        joined=house.joined_4_externals(p,t)
        c[f"{k}deg_joined_4_externals_when_regio_house_empty"]=int((joined&~regio).sum())
        c[f"{k}deg_joined_4_externals_when_ASC_sign_empty"]=int((joined&~asc_hit).sum())
        c[f"{k}deg_joined_4_externals_when_placidus_house_empty"]=int((joined&~placidus).sum())
    return c,maxerr

def run(west:Path,angles:Path,hashes=True):
    if swe.version!=SWISS_VERSION:
        raise RuntimeError("Swiss ephemeris engine version unexpected")
    wplanpath=west/"plan.json";wmanifestpath=west/"verified_manifest.json"
    aplanpath=angles/"plan.json";amanifestpath=angles/"verified_manifest.json"
    wp=json.loads(wplanpath.read_bytes());wm=json.loads(wmanifestpath.read_bytes())
    ap=json.loads(aplanpath.read_bytes());am=json.loads(amanifestpath.read_bytes())
    n=initial.check_manifest(wp,wm,ap,am)
    if wm["plan_sha256"]!=initial.source_hash(wplanpath) or am["plan_sha256"]!=initial.source_hash(aplanpath):
        raise RuntimeError("Plan SHA source mismatch")
    if ap.get("cols",[])[5:7]!=["placidus_cusp_1","placidus_cusp_2"]:
        raise RuntimeError("Historical source cache misbinding")
    if ap.get("swisseph_version")!=SWISS_VERSION:
        raise RuntimeError("Source version differs")
    lat=float(ap["latitude"]);lon=float(ap["longitude"])
    jd0=julian_from_utc(wp["utc_start_inclusive"])
    counts=Counter()
    maxerr=0.
    for w,a in zip(wm["chunks"],am["shards"]):
        planet=west/"chunks"/w["file"];location=angles/"shards"/a["file"]
        k=w["count"]
        if planet.stat().st_size!=k*64 or location.stat().st_size!=k*136:
            raise RuntimeError("Original source-shard byte size drift")
        if hashes and (initial.source_hash(planet)!=w["sha256"] or initial.source_hash(location)!=a["sha256"]):
            raise RuntimeError("Original source-shard SHA drift")
        p=np.memmap(planet,dtype="<f8",shape=(k,8),mode="r")
        ang=np.memmap(location,dtype="<f8",shape=(k,17),mode="r")
        subset,err=calc_chunk(p[:,:7],ang,jd_start=jd0,lat=lat,lon=lon,
                              index_first=w["first_index"])
        counts.update(subset)
        maxerr=max(maxerr,err)
    c=dict(counts)
    if c["regio_first_house_any"]+c["regio_first_house_none"]!=n:
        raise RuntimeError("Regiomontanus first-house count invalid")
    if c["regio_only_not_sign"]+c["sign_only_not_regio"]+c["regio_and_sign_both"] !=c["regio_first_house_any"]+c["sign_only_not_regio"]:
        raise RuntimeError("Regiomontanus vs sign overlap math failed")
    if c["asc_sign_any"]!=1428060:
        raise RuntimeError("Former first sign source count changed")
    if c["placidus_first_house_any"]!=1407259:
        raise RuntimeError("Old Placidus diagnostic baseline changed")
    return {
      "schema":"lilly_CVII_historical_Regiomontanus_first_house_vs_sign_and_Placidus_census_v01",
      "status":"REGIOMONTANUS_FIRST_HOUSE_GEOMETRY_ACTUALLY_CALCULATED_3_5M_GRID_MANNERS_UNSCORED",
      "source_scope":"Lilly Christian Astrology III CVII; geometric first house; intercepted sign, planetary strengths, dispositions, Moon/Mercury joining and later fallbacks require further source adjudication",
      "geometry_source_house_system":"REGIOMONTANUS",
      "counterfactual_geometry":["ASC 30-degree zodiac sign","Placidus first house from original cache"],
      "historical_source_claims_not_completed":["intercepted signs independent participation","planetary dignity and fortification","correct source-conjunction orb and priority","Asc lord seeing its dispositor","partile and stellar testimony"],
      "source_original_manifest_sha256":{
           "planet":initial.source_hash(wmanifestpath),
           "angles":initial.source_hash(amanifestpath)},
      "source_original_72_shards_sha256_reverified":hashes,
      "Regiomontanus_vs_source_Placidus_cross_checks":c["source_site_and_ASC_reference_checks"],
      "maximum_longitude_difference_to_source_cache_deg":maxerr,
      "data_samples":n,
      "UTC_horizon":[wp["utc_start_inclusive"],wp["utc_end_exclusive"]],
      "time_step_minutes":15,
      "source_fixed_research_site_not_respondent":True,
      "source_site_coordinates_suppressed_from_public_aggregate":True,
      "longitude_count_categories":c,
      "thresholds_degrees_not_original_Lilly_joining_orbs":list(lilly.THRESHOLDS),
      "source_manners_significator_computed":False,
      "human_behavior_prediction_verified":False,
      "user_birth_records_not_loaded":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--west",type=Path,required=True)
    p.add_argument("--angles",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--skip-shard-hashes",action="store_true")
    a=p.parse_args()
    if a.out.exists():raise FileExistsError("Do not overwrite historical source-bound results")
    j=run(a.west,a.angles,not a.skip_shard_hashes)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(j,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":j["status"],"total":j["data_samples"],
          "categories":j["longitude_count_categories"],
          "original_hashes":j["source_original_72_shards_sha256_reverified"],
          "max_source_cusp_error_deg":j["maximum_longitude_difference_to_source_cache_deg"]},sort_keys=True))

if __name__=="__main__":main()
