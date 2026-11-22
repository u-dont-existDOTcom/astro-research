#!/usr/bin/env python3
"""Lilly Christian Astrology III Ch.CVII partial ordered manners-branch census.

Source pp.535–536, original text reconstructed in 45-page scanned facsimile.
Original author describes the following ORDER:
1 planets occupying ascending or intercepted signs, plus dispositor/strength;
2 if no planet in Ascendant, observe joining to Moon or Mercury;
3 then Lord of Ascendant WITH its aspecting dispositor;
4 partile aspects to Moon/Mercury; then greater essential dignity;
5 other modifiers and fixed stars.

Only (1) an ASCENDING SIGN (not entire ascendant house or interceptions)
geometrical *PROXY*, and (2) conjunction angular distance *sensitivity*
are calculated on a uniform 15-minute tropical grid.

Lilly doesn't set one numeric conjunction orb in these two sentences.
Thresholds 1°, 3°, 5°, 10° are engineering exploratory variants, not
source definitions, not scores and NOT human personality predictions.
Two successive sets of external candidate definitions are reported:
a) Venus/Mars/Jupiter/Saturn
b) include Sun
c) include Mercury-Moon mutual joining
No variant is silently adopted as the historical complete interpretation.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location(
 "lilly_original",HERE/"lilly_cvii_initial_geom_grid_census_v01.py")
initial=importlib.util.module_from_spec(spec);spec.loader.exec_module(initial)
THRESHOLDS=(1.,3.,5.,10.)
EXTERNAL_NONLUM=(3,4,5,6)
ASCENT_SIGN_PROXY_NOTE="ASC_SIGN_ONLY_NOT_FULL_HOUSE_OR_INTERCEPTED_SIGNS"

def sha(path:Path)->str:
 return initial.source_hash(path)

def separation(a,b):
 a=np.asarray(a,dtype=np.float64);b=np.asarray(b,dtype=np.float64)
 if a.shape!=b.shape or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
  raise ValueError("Aligned finite longitudes required")
 if np.any((a<0)|(a>=360)) or np.any((b<0)|(b>=360)):
  raise ValueError("Normalized longitude required")
 return np.abs((a-b+180.)%360.-180.)

def classify_source_proxy(planets,asc):
 p=np.asarray(planets,dtype=np.float64)
 a=np.asarray(asc,dtype=np.float64)
 if p.ndim!=2 or p.shape[1]!=7 or a.shape!=(len(p),):
  raise ValueError("Expected Nx7 traditional longitudes and Nx1 ASC")
 if not np.all(np.isfinite(p)) or not np.all(np.isfinite(a)):
  raise ValueError("Non-finite source longitudes")
 if np.any((p<0)|(p>=360)) or np.any((a<0)|(a>=360)):
  raise ValueError("Unnormalized zodiacal longitudes")
 ascs=np.floor(a/30).astype(np.int8)
 hit=np.floor(p/30).astype(np.int8)==ascs[:,None]
 any_first=hit.any(axis=1)
 first_none=~any_first
 moon=p[:,1];mercury=p[:,2]
 out={"no_planet_in_ASC_ZODIAC_SIGN_PROXY":int(first_none.sum()),
      "any_planet_in_ASC_ZODIAC_SIGN_PROXY":int(any_first.sum()),
      "multiple_planets_ASC_ZODIAC_SIGN_PROXY":int((hit.sum(axis=1)>=2).sum())}
 for t in THRESHOLDS:
  label=str(int(t))
  extern=np.zeros(len(p),dtype=bool)
  for ix in EXTERNAL_NONLUM:
   extern|=(separation(p[:,ix],moon)<=t)|(separation(p[:,ix],mercury)<=t)
  sun=(separation(p[:,0],moon)<=t)|(separation(p[:,0],mercury)<=t)
  mutual=separation(moon,mercury)<=t
  for k,arr in [
   ("four_nonlum_externals",extern),
   ("including_Sun",extern|sun),
   ("including_Sun_and_mutual_Moon_Mercury",extern|sun|mutual),
  ]:
   out[f"fallback_{label}deg_{k}"]=int((first_none&arr).sum())
  out[f"fallback_{label}deg_mutual_Mercury_Moon_conjunction"]=int((first_none&mutual).sum())
  out[f"still_no_joined_candidate_{label}deg_inclusive_variant"]=int((first_none&~(extern|sun|mutual)).sum())
 return out

def run(west:Path,angles:Path,check_shas:bool=True):
 wp=json.loads((west/"plan.json").read_bytes());wm=json.loads((west/"verified_manifest.json").read_bytes())
 ap=json.loads((angles/"plan.json").read_bytes());am=json.loads((angles/"verified_manifest.json").read_bytes())
 n=initial.check_manifest(wp,wm,ap,am)
 if wm.get("plan_sha256")!=sha(west/"plan.json") or am.get("plan_sha256")!=sha(angles/"plan.json"):
  raise RuntimeError("Source manifest plan mismatch")
 count=Counter()
 for w,a in zip(wm["chunks"],am["shards"]):
  wfile=west/"chunks"/w["file"];afile=angles/"shards"/a["file"]
  k=w["count"]
  if wfile.stat().st_size!=k*64 or afile.stat().st_size!=k*136:
   raise RuntimeError("Source shard byte size mismatch")
  if check_shas and (sha(wfile)!=w["sha256"] or sha(afile)!=a["sha256"]):
   raise RuntimeError("Source shard SHA256 changed")
  p=np.memmap(wfile,dtype="<f8",mode="r",shape=(k,8))
  g=np.memmap(afile,dtype="<f8",mode="r",shape=(k,17))
  count.update(classify_source_proxy(p[:,:7],g[:,0]))
 if count["any_planet_in_ASC_ZODIAC_SIGN_PROXY"]+count["no_planet_in_ASC_ZODIAC_SIGN_PROXY"]!=n:
  raise RuntimeError("First branch source count does not partition grid")
 if count["any_planet_in_ASC_ZODIAC_SIGN_PROXY"]!=1428060:
  raise RuntimeError("Source changed relative to original Lilly source receipt")
 firstnone=count["no_planet_in_ASC_ZODIAC_SIGN_PROXY"]
 for t in THRESHOLDS:
  th=str(int(t))
  vals=[count[f"fallback_{th}deg_{k}"] for k in
     ("four_nonlum_externals","including_Sun","including_Sun_and_mutual_Moon_Mercury")]
  if vals!=sorted(vals):
   raise RuntimeError("Inclusive fallbacks violated subset arithmetic")
  if vals[-1]+count[f"still_no_joined_candidate_{th}deg_inclusive_variant"]!=firstnone:
   raise RuntimeError("Successive source-proxy branches fail to partition")
 return {
  "schema":"lilly_CVII_ASC_sign_proxy_and_Moon_Mercury_joined_candidate_sensitivity_v01",
  "status":"FIRST_TWO_GEOMETRIC_PROXIES_COMPLETE_FULL_CENTURY_MANNERS_SIGNIFICATOR_UNSELECTED",
  "source_uri":"https://cdn.astmd.gr/attachments/2023/11/29/williamlilly500-543.pdf",
  "original_author":"William Lilly, Christian Astrology Book III Ch.CVII pp.535-536",
  "full_grid_sample_count":n,
  "sample_interval_minutes":15,
  "source_horizon_utc":[wp["utc_start_inclusive"],wp["utc_end_exclusive"]],
  "source_manifest_sha256":{"planet":sha(west/"verified_manifest.json"),"angles":sha(angles/"verified_manifest.json")},
  "binary_source_shards_SHA256_rechecked":check_shas,
  "source_geometry_scope":ASCENT_SIGN_PROXY_NOTE,
  "angular_joining_thresholds_engineering_not_Lilly_source":list(THRESHOLDS),
  "source_planet_in_asc_house_or_intercepted_sign_COMPLETED":False,
  "source_actual_benefic_malefic_strength_and_dispositor_COMPLETED":False,
  "source_asc_ruler_and_its_dispositor_aspect_COMPLETED":False,
  "source_fallback_partile_aspect_and_dignity_COMPLETED":False,
  "source_fixed_stars_COMPLETED":False,
  "numerical_counts":dict(count),
  "cannot_assign_true_manners_significator":True,
  "human_behavior_score":None,
  "actual_person_predictive_accuracy":None,
  "no_private_natal_or_interview_input":True,
 }

def main():
 ar=argparse.ArgumentParser()
 ar.add_argument("--west",type=Path,required=True)
 ar.add_argument("--angles",type=Path,required=True)
 ar.add_argument("--out",type=Path,required=True)
 ar.add_argument("--skip-hashes",action="store_true")
 a=ar.parse_args()
 if a.out.exists():raise FileExistsError("Immutable original source grid receipt")
 out=run(a.west,a.angles,not a.skip_hashes)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":out["status"],"samples":out["full_grid_sample_count"],
                   "first_proxy_none":out["numerical_counts"]["no_planet_in_ASC_ZODIAC_SIGN_PROXY"],
                   "fallback_counts":{k:v for k,v in out["numerical_counts"].items() if "four_nonlum_externals" in k},
                   "original_shards_reverified":out["binary_source_shards_SHA256_rechecked"]},sort_keys=True))

if __name__=="__main__":main()
