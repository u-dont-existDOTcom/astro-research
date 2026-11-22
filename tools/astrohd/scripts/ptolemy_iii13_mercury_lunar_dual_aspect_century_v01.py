#!/usr/bin/env python3
"""Ptolemy III.13 'two places at once' FOUR-LORD source-aspect witness.

The *source text* explicitly separates:
  Mercury's reason/mind condition;
  Moon's sensory condition and applying/separating configurations;
  governors whose Mercury aspect AND lunar relation both qualify.
III.13, Robbins 1940 pp. 333-339 (textual positions 23-31 online).

This counts a STRICT SUBSET of possible geometric double configurations:
a non-Mercury, non-luminary lord [Venus, Mars, Jupiter, Saturn] who
 - is a common D/E/triplicity/term candidate for Mercury and Moon;
 - is near a natal traditional configuration to Mercury;
 - is near a natal traditional configuration to the Moon;
 - has a definite sampled Moon/planet approaching or separating
   angular trajectory across neighboring quarter-hour samples.

SOURCE/LIMITS: Ptolemy I.24 does NOT supply one numeric orb, nor does he
demand this filter as a necessary condition for all Ptolemaic characters.
We calculate EXPLICIT ENGINEERING angular-distance sensitivity [1,3,5,10,15]
DEGREES (not days), not original historical qualifiers. We give a
LOWER-BOUND witness excluding bodily conjunctions, for which the cached
planetary grid lacks latitude, and a POSSIBLE UPPER-SCOPE including all
conjunctions without checking required same-ecliptic-side condition.

Mercury cannot meaningfully aspect itself; excluding it prevents spurious
self-'configuration'. All excluded paths remain UNKNOWN, not falsified.
This is a full historical *astronomical grid* scan, NOT a human natal
prediction, Ptolemy's definitive ruler choice, or validated psychology.
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
_sp=importlib.util.spec_from_file_location(
    "fourterms",HERE/"ptolemy_four_modes_source_terms_century_v01.py")
four=importlib.util.module_from_spec(_sp);_sp.loader.exec_module(four)
pt3=four.pt3
PTOLEMY= "ptolemy_printed_1940"
EGYPTIAN="egyptian_printed_1940"
SCHEMES=(PTOLEMY,EGYPTIAN)
# All five conventional aspect classes; duplicate oriented targets are
# included so both sides of conjunction/opposition/trine etc are measured.
ASPECTS_NONBODY=(60.,90.,120.,180.,240.,270.,300.)
ASPECTS_WITH_BODY=(0.,)+ASPECTS_NONBODY
THRESHOLDS=(1.,3.,5.,10.,15.)
# Sources speak of 5 nonluminaries; this deliberately avoids the Mercury
# self-relation and cannot interpret it, so j=3..6 only.
EXTERNAL_GOVERNORS={"Venus":3,"Mars":4,"Jupiter":5,"Saturn":6}
CHUNK_RECORD_BYTES=64
ANGLE_RECORD_BYTES=136


def sha(path:Path)->str:
    return four.sha(path)


def nearest_residual(lon_a,lon_b,targets):
    a=np.asarray(lon_a,dtype=np.float64)
    b=np.asarray(lon_b,dtype=np.float64)
    if a.shape!=b.shape or a.ndim!=1 or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError("Aligned finite longitude series required")
    if np.any((a<0)|(a>=360)) or np.any((b<0)|(b>=360)):
        raise ValueError("Unnormalized celestial longitude")
    delta=a-b
    residuals=np.stack([((delta-k+180.)%360.-180.) for k in targets],axis=0)
    nearest=np.argmin(np.abs(residuals),axis=0)
    return np.take_along_axis(residuals,nearest[np.newaxis,:],axis=0)[0]


def lunar_radial_trend(moon,planet):
    """Central-difference sign of angular approach/recession, edges UNKNOWN.

    Source array contains longitudes only, not actual speed for all planets.
    Difference of wrapped relative longitude over 30 minutes approximates the
    local daily derivative. The two edges of EACH source shard remain unknown.
    Do not promote these estimates to actual exact-root historical directions.
    """
    moon=np.asarray(moon,dtype=np.float64)
    p=np.asarray(planet,dtype=np.float64)
    if moon.shape!=p.shape or moon.ndim!=1 or len(moon)<3:
        raise ValueError("Need aligned sample sequence of >=3 instants")
    if np.any(~np.isfinite(moon)) or np.any(~np.isfinite(p)):
        raise ValueError("Nonfinite longitude")
    if np.any((moon<0)|(moon>=360)) or np.any((p<0)|(p>=360)):
        raise ValueError("Longitude outside normalized range")
    rel=((moon-p+180.)%360.-180.)
    vel=np.full_like(rel,np.nan)
    vel[1:-1]=((rel[2:]-rel[:-2]+180.)%360.-180.)*(24./0.5)
    return vel


def source_common_lord_bits(mercury,moon,sun_altitude,scheme):
    """4 modes => possible common lords. NOT actual III.13 governor."""
    m=np.asarray(mercury,dtype=np.float64)
    l=np.asarray(moon,dtype=np.float64)
    alt=np.asarray(sun_altitude,dtype=np.float64)
    if m.shape!=l.shape or m.shape!=alt.shape:
        raise ValueError("Longitude / sect arrays mismatch")
    ms=four.prior_sign(m);ls=four.prior_sign(l)
    mb=pt3.mask_for_ruler_modes(ms,alt,all_triplicity_members=True)
    lb=pt3.mask_for_ruler_modes(ls,alt,all_triplicity_members=True)
    mt=four.term_lords(m,scheme);lt=four.term_lords(l,scheme)
    mb|=(np.uint16(1)<<mt.astype(np.uint16))
    lb|=(np.uint16(1)<<lt.astype(np.uint16))
    common=mb&lb
    # Do not call remaining two source modes definite without sect and the
    # omitted historical application/phase rule.
    return common,np.abs(alt)<=0.1


def scan_chunk(planet_rows:np.ndarray,angle_rows:np.ndarray)->dict:
    p=np.asarray(planet_rows,dtype=np.float64)
    a=np.asarray(angle_rows,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=8 or a.shape!=(len(p),17):
        raise ValueError("Wrong fixed source record shapes")
    if len(p)<3:raise ValueError("Need central neighbors for Moon speed")
    n=len(p)
    moon=p[:,1]
    mercury=p[:,2]
    sun_alt=a[:,4]
    unknown=np.zeros(n,dtype=bool)
    unknown[0]=True;unknown[-1]=True
    near_sect=np.abs(sun_alt)<=0.1
    unknown|=near_sect
    schemes={}
    for name in SCHEMES:
        candidate,_=source_common_lord_bits(mercury,moon,sun_alt,name)
        schemes[name]=candidate
    # Threshold cohorts are cumulative across non-self external rulers.
    # Source-based common candidate alone remains a *broad* astronomical fact.
    results={name:{
        "near_horizon_unknown":int(near_sect.sum()),
        "shard_edge_derivative_unknown":2,
        "source_candidate_external_nonmercury":int(
            (((common&(0b1111000))!=0)&~near_sect).sum()),
        "thresholds":{str(int(t)):{"nonbody_only":np.zeros(n,dtype=bool),
                                   "including_uncertified_conjunctions":np.zeros(n,dtype=bool),
                                   "applying_nonbody_only":np.zeros(n,dtype=bool),
                                   "separating_nonbody_only":np.zeros(n,dtype=bool)}
                      for t in THRESHOLDS}
    } for name,common in schemes.items()}
    # Angular distance: the same external planet must qualify in BOTH places;
    # self-Mercury is absent by construction.
    for planet_name,index in EXTERNAL_GOVERNORS.items():
        planet=p[:,index]
        dm=nearest_residual(planet,mercury,ASPECTS_NONBODY)
        dl=nearest_residual(moon,planet,ASPECTS_NONBODY)
        um=nearest_residual(planet,mercury,ASPECTS_WITH_BODY)
        ul=nearest_residual(moon,planet,ASPECTS_WITH_BODY)
        v=lunar_radial_trend(moon,planet)
        applying=np.isfinite(v)&(v*dl < 0)
        separating=np.isfinite(v)&(v*dl > 0)
        # Rare exact aspect (<1e-12) is unresolved about approach vs parting.
        # Retain count in upper generic witness but never invent polarity.
        for name,common in schemes.items():
            eligible=((common&(1<<index))!=0)&~unknown
            for t in THRESHOLDS:
                ts=results[name]["thresholds"][str(int(t))]
                nb=eligible&(np.abs(dm)<=t)&(np.abs(dl)<=t)
                ub=eligible&(np.abs(um)<=t)&(np.abs(ul)<=t)
                ts["nonbody_only"]|=nb
                ts["including_uncertified_conjunctions"]|=ub
                ts["applying_nonbody_only"]|=nb&applying
                ts["separating_nonbody_only"]|=nb&separating
    flat={}
    for name,entry in results.items():
        flat[name+"_candidate_external_nonmercury"] = entry["source_candidate_external_nonmercury"]
        flat[name+"_near_horizon_unknown"]=entry["near_horizon_unknown"]
        for th,sub in entry["thresholds"].items():
            for label,mask in sub.items():
                flat[f"{name}_{th}deg_{label}"]=int(mask.sum())
    for t in THRESHOLDS:
        th=str(int(t))
        for key in ("nonbody_only","including_uncertified_conjunctions"):
            a=results[PTOLEMY]["thresholds"][th][key]
            b=results[EGYPTIAN]["thresholds"][th][key]
            flat[f"{th}deg_scheme_disagreement_{key}"]=int((a!=b).sum())
    flat["screened_interior_source_samples"]=n-2-int(near_sect[1:-1].sum())
    flat["shard_derivative_unknown_samples"]=2
    return flat


def run(west:Path,angles:Path,verify_shards=True):
    wp=west/"plan.json"; wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    plan=json.loads(wp.read_bytes());wmj=json.loads(wm.read_bytes())
    plan_a=json.loads(ap.read_bytes());amj=json.loads(am.read_bytes())
    n=pt3.check_two_cache_manifests(plan,wmj,plan_a,amj)
    if wmj["plan_sha256"]!=sha(wp) or amj["plan_sha256"]!=sha(ap):
        raise RuntimeError("Source manifest does not match original plan")
    c=Counter()
    for w,a in zip(wmj["chunks"],amj["shards"]):
        bp=west/"chunks"/w["file"]
        ba=angles/"shards"/a["file"]
        k=w["count"]
        if bp.stat().st_size!=k*CHUNK_RECORD_BYTES or ba.stat().st_size!=k*ANGLE_RECORD_BYTES:
            raise RuntimeError("Source file byte size changed")
        if verify_shards and (sha(bp)!=w["sha256"] or sha(ba)!=a["sha256"]):
            raise RuntimeError("Source SHA256 failed to match per-shard manifest")
        rows=np.memmap(bp,dtype="<f8",shape=(k,8),mode="r")
        places=np.memmap(ba,dtype="<f8",shape=(k,17),mode="r")
        c.update(scan_chunk(rows,places))
    if c["shard_derivative_unknown_samples"]!=2*len(wmj["chunks"]):
        raise RuntimeError("Shards not counted")
    if c["screened_interior_source_samples"]<n-10000:
        raise RuntimeError("Unexpectedly little source coverage")
    for name in SCHEMES:
        for t in THRESHOLDS:
            ts=str(int(t))
            l=c[f"{name}_{ts}deg_nonbody_only"]
            h=c[f"{name}_{ts}deg_including_uncertified_conjunctions"]
            if not (0<=l<=h<=n):
                raise RuntimeError("Lower/upper source-screen ordering failed")
            if c[f"{name}_{ts}deg_applying_nonbody_only"]>l:
                raise RuntimeError("Applying witness exceeds total")
    return {
      "schema":"ptolemy_III13_double_config_to_Mercury_and_Moon_angular_sensitivity_v01",
      "status":"FULL_DECLARED_CENTURY_GEOMETRIC_WITNESS_SENSITIVITY_NOT_HISTORICAL_ORB_OR_SOUL_GOVERNOR",
      "utc_grid_window":[plan["utc_start_inclusive"],plan["utc_end_exclusive"]],
      "total_grid_samples":n,
      "15minute_source_clock_samples":True,
      "angle_source_manifests_sha256":{"planet":sha(wm),"Sun_altitude":sha(am)},
      "all_original_binary_shards_sha256_verified":verify_shards,
      "source_schemes":list(SCHEMES),
      "angular_thresholds_engineering_not_source_degrees":list(THRESHOLDS),
      "historical_source":"Ptolemy Tetrabiblos I.24 and III.13 opening; Robbins 1940",
      "original_source_explicit_conditions":["mercury_configuration","lunar_application_or_separation","ruler_correspondence_and_conditions"],
      "screened_governor_subset":list(EXTERNAL_GOVERNORS),
      "excluded_mercury_self_relation_not_evidence_against_source":True,
      "conjunction_latitude_source_unavailable_so_upper_only":True,
      "moon_relative_motion_estimate":"central_15minute_longitude_difference_on_each_binary_shard; first and last shard record abstain",
      "source_neutral_samples_not_human_birth_cohort":True,
      "cumulative_counts":dict(c),
      "original_first_four_mode_candidate_baseline_file":"ptolemy_iii13_four_mode_terms_aggregate_v01.json",
      "does_not_complete_fifth_domination_mode":True,
      "does_not_apply_source_defined_orb":True,
      "does_not_score_personality_or_unique_natal_rank":True,
      "validated_human_predictions":0,
    }


def main():
    ar=argparse.ArgumentParser()
    ar.add_argument("--west",required=True,type=Path)
    ar.add_argument("--angles",required=True,type=Path)
    ar.add_argument("--out",required=True,type=Path)
    ar.add_argument("--skip-shard-hashes",action="store_true")
    a=ar.parse_args()
    if a.out.exists():
        raise FileExistsError("Immutable source-bound result exists")
    res=run(a.west,a.angles,not a.skip_shard_hashes)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(res,sort_keys=True,indent=2)+"\n")
    keys=[f"{PTOLEMY}_{i}deg_nonbody_only" for i in (1,3,5,10,15)]
    print(json.dumps({
      "status":res["status"],"sample_count":res["total_grid_samples"],
      "source_hashes_checked":res["all_original_binary_shards_sha256_verified"],
      "ptolemy_threshold_witness_counts":{k:res["cumulative_counts"][k] for k in keys},
      "human_validation":res["validated_human_predictions"]
    },sort_keys=True))

if __name__=="__main__":
    main()
