#!/usr/bin/env python3
"""Lilly CVII *first geometrical condition* across a finite Western UTC grid.

Only counts whether Sun/Moon and/or Mercury/Venus/Mars/Jupiter/Saturn occupy
the rising zodiacal SIGN. This is one partial condition from Lilly, not
the full Ascendant-house/interception rule and NOT a manners significator,
psychological score, source-verified claim about any person, or chart ranking.
External cache root must be authorized; the public code never embeds its path.

Sampling is at a 15-minute grid. This is not continuous birth-time coverage.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

PLANETS=("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn")
PLANET_RECORD=("<f8",8)
ANGLES_RECORD=("<f8",17)
CLAIM="LILLY-CVII-ASC-SIGN-PLANETS"


def source_hash(p:Path)->str:
    h=sha256()
    with p.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def classifications(asc, planets):
    """Classify source geom, not a psychological trait, vectorized on rows."""
    a=np.asarray(asc,dtype=np.float64)
    p=np.asarray(planets,dtype=np.float64)
    if a.ndim!=1 or p.ndim!=2 or p.shape!=(len(a),7):
        raise ValueError("Expected 1D asc and Nx7 classical planetary longitudes")
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(p)):
        raise ValueError("Nonfinite longitude")
    if np.any(a<0) or np.any(a>=360) or np.any(p<0) or np.any(p>=360):
        raise ValueError("Longitudes must be normalized 0<=longitude<360")
    signs=np.floor(p/30).astype(np.int8)
    asc_sign=np.floor(a/30).astype(np.int8)
    hit=signs==asc_sign[:,None]
    nonlum=hit[:,2:].sum(axis=1)
    lum=hit[:,:2].sum(axis=1)
    # Disjoint six classes, not judgment calls about strongest planets.
    return {
        "none_in_asc_sign": (nonlum==0)&(lum==0),
        "one_nonlum_only": (nonlum==1)&(lum==0),
        "multiple_nonlum_only": (nonlum>=2)&(lum==0),
        "luminaries_only": (nonlum==0)&(lum>=1),
        "nonlum_and_luminaries": (nonlum>=1)&(lum>=1),
        "rising_sign_planets": hit,
        "asc_sign":asc_sign,
    }


def check_manifest(wp,wm,ap,am):
    if wp.get("schema")!="western-source-neutral-utc-grid-float64-pilot-v1-NONCANONICAL":
        raise RuntimeError("Wrong Western source schema")
    if ap.get("schema")!="location-conditioned-western-angles-utc-grid-v1-NONCANONICAL":
        raise RuntimeError("Wrong angles source schema")
    if wp.get("record_order")!=list(PLANETS)+["Mercury_lon_speed"]:
        raise RuntimeError("Planet column order mismatch")
    if ap.get("cols",[])[0]!="asc":
        raise RuntimeError("First angles column not ASC")
    if (wp.get("record_bytes"),ap.get("record_bytes"))!=(64,136):
        raise RuntimeError("Unexpected f64 width")
    if wp["step_minutes"]!=15 or ap["step_minutes"]!=15:
        raise RuntimeError("This method requires the declared 15-minute grid")
    if wp.get("utc_start_inclusive")!=ap.get("utc_start") or wp.get("utc_end_exclusive")!=ap.get("utc_end_exclusive"):
        raise RuntimeError("UTC horizons differ")
    n=wp.get("total_samples")
    if n!=ap.get("sample_count") or n!=wm.get("total_samples") or n!=am.get("total_samples"):
        raise RuntimeError("Record count mismatch")
    w=wm.get("chunks",[])
    a=am.get("shards",[])
    if len(w)!=len(a) or not w:
        raise RuntimeError("Chunk count mismatch")
    start=0
    for x,y in zip(w,a):
        if x.get("count")!=y.get("count"):
            raise RuntimeError("Misaligned shard sample count")
        if x.get("first_index")!=start:
            raise RuntimeError("Missing or repeated Western grid index")
        start+=x["count"]
    if start!=n:raise RuntimeError("Incomplete sample coverage")
    return n


def survey(west:Path,angles:Path,verify_hashes=True)->dict:
    wp=json.loads((west/"plan.json").read_bytes())
    wm=json.loads((west/"verified_manifest.json").read_bytes())
    ap=json.loads((angles/"plan.json").read_bytes())
    am=json.loads((angles/"verified_manifest.json").read_bytes())
    n=check_manifest(wp,wm,ap,am)
    acc=Counter()
    signs=[0]*12
    for w,a in zip(wm["chunks"],am["shards"]):
        wp=west/"chunks"/w["file"]
        ap=angles/"shards"/a["file"]
        wc=w["count"]
        if wp.stat().st_size!=wc*64 or ap.stat().st_size!=wc*136:
            raise RuntimeError("Incomplete shard bytes")
        if verify_hashes and (source_hash(wp)!=w["sha256"] or source_hash(ap)!=a["sha256"]):
            raise RuntimeError("Shard SHA-256 binding mismatch")
        pv=np.memmap(wp,dtype="<f8",shape=(wc,8),mode="r")[:,:7]
        av=np.memmap(ap,dtype="<f8",shape=(wc,17),mode="r")[:,0]
        result=classifications(av,pv)
        for k in ("none_in_asc_sign","one_nonlum_only","multiple_nonlum_only","luminaries_only","nonlum_and_luminaries"):
            acc[k]+=int(result[k].sum())
        acc["multiple_planets_in_asc_sign"]+=int((result["rising_sign_planets"].sum(axis=1)>=2).sum())
        counts=np.bincount(result["asc_sign"].astype(np.int8),minlength=12)
        for i,num in enumerate(counts):signs[i]+=int(num)
    if sum(acc[k] for k in ("none_in_asc_sign","one_nonlum_only","multiple_nonlum_only","luminaries_only","nonlum_and_luminaries"))!=n:
        raise RuntimeError("Undistributed samples")
    if sum(signs)!=n:raise RuntimeError("Rising sign count mismatch")
    return {
        "schema":"lilly_cvii_first_geom_full_declared_utc_grid_v01",
        "status":"COMPLETE_MECHANICAL_GRID_FIRST_SOURCE_RUNG_ONLY",
        "source_claim_id":CLAIM,
        "model_result":"NO_MANNERS_PERSONALITY_SCORE",
        "sample_count":n,
        "sample_minutes":15,
        "horizon_utc":[
            json.loads((west/"plan.json").read_bytes())["utc_start_inclusive"],
            json.loads((west/"plan.json").read_bytes())["utc_end_exclusive"],
        ],
        "source_manifest_sha256":source_hash(west/"verified_manifest.json"),
        "angles_manifest_sha256":source_hash(angles/"verified_manifest.json"),
        "source_data_shards_sha256_reverified":verify_hashes,
        "categories":dict(acc),
        "asc_sign_counts":signs,
        "any_planet_in_asc_sign":n-acc["none_in_asc_sign"],
        "no_natal_referenced":True,
        "no_appropriate_personality_ranking":True,
        "intercepted_sign_or_house_rule_not_evaluated":True,
        "source_conditions_missing":["intercepted sign","multi-planet power","luminary special qualification","Mercury and Moon conjunction","Ascendant ruler fallback","partile aspects","fixed stars"],
        "caution":"No person-level validation; a fixed-location 15-minute grid not continuous chart interval coverage.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--west",type=Path,required=True)
    p.add_argument("--angles",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--skip-source-shard-hashes",action="store_true")
    args=p.parse_args()
    if args.out.exists():raise FileExistsError("Output immutable; choose a new versioned path")
    result=survey(args.west,args.angles,not args.skip_source_shard_hashes)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("LILLY_CVII_INITIAL_GEOMETRY",json.dumps({k:result[k] for k in ("status","sample_count","any_planet_in_asc_sign","source_data_shards_sha256_reverified")}))
if __name__=="__main__":main()
