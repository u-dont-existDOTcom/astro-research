#!/usr/bin/env python3
"""One original 1647 accidental-strength component: natal house position.

Original Lilly 1647 first edition, printed p115: angular house 1/10 +5,
7/4/11 +4, 2/5 +3, 9 +2, 3 +1, 6/8 -2 and 12 -5.
It is a HOUSE-only single-component witness, NEVER full planetary strength.

Regiomontanus house geometry is retained as an original historical practice
candidate, but the 12 Placidus cusps in the frozen original source are also
computed INDEPENDENTLY to quantify exact house-convention ambiguity.
The historic source does not unambiguously authorize a single house engine.

All original 3,506,400 quarter-hour UTC samples, 36 planetary +36 site
source shards and 36 HD lookup source shards SHA-pinned. No personal natal,
interview, user location, behavior score or human #1 rank.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
import swisseph as swe

import lilly_cvii_ptolemy_same_instant_ordered_fallback_v02 as prev
from lilly_cvii_original_essential_dignity_final_fallback_century_v01 import PLANETS

SOURCE="Lilly 1647 original Christian Astrology first printing p115"
HOUSE_POINTS=np.array([5,3,1,4,3,-2,4,-2,2,5,4,-5],dtype=np.int8)
HOUSES=tuple(range(1,13))
N=3506400
HD_STATES=288908

def house_ids(planets,cusps):
    """Exact 12 disjoint ecliptic arcs cusp h inclusive to cusp h+1 exclusive."""
    p=np.asarray(planets,dtype=np.float64)
    c=np.asarray(cusps,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or c.shape!=(len(p),12):
        raise ValueError("Aligned Nx7 classical planets and 12 astronomical house cusps required")
    if not np.all(np.isfinite(p)) or not np.all(np.isfinite(c)):
        raise ValueError("Invalid nonfinite zodiac input")
    if np.any((p<0)|(p>=360)) or np.any((c<0)|(c>=360)):
        raise ValueError("Source longitudes and cusps must be in 0..360")
    ends=np.roll(c,-1,axis=1)
    widths=(ends-c)%360
    if np.any((widths<=0)|(widths>180)):
        raise ValueError("Twelve oriented quadrant house arcs must all be >0 and <=180")
    result=np.full(p.shape,-1,dtype=np.int8)
    for house in range(12):
        inside=((p-c[:,house,None])%360)<widths[:,house,None]
        if np.any(inside&(result!=-1)):
            raise RuntimeError("Planet assigned to overlapping houses")
        result[inside]=house
    if np.any(result<0):
        raise RuntimeError("Traditional planet lacks exactly one house assignment")
    if not np.all((result>=0)&(result<12)):
        raise RuntimeError("Invalid house assignment")
    return result

def local_house_winner(h):
    """Modern exact one-component maximum; no historical ruler assigned."""
    x=np.asarray(h,dtype=np.int8)
    if x.ndim!=2 or x.shape[1]!=7 or np.any((x<0)|(x>11)):
        raise ValueError("One of 12 houses for all seven classical planets required")
    scores=HOUSE_POINTS[x]
    top=scores.max(axis=1)
    unique=(scores==top[:,None]).sum(axis=1)==1
    leader=np.argmax(scores,axis=1).astype(np.int8)
    leader[~unique]=-1
    return scores,leader,unique

def scan_chunk(planets,site,hdids,*,jd_start,first_idx,lat,lon,counts,hdsets):
    p=np.asarray(planets,dtype=np.float64)
    a=np.asarray(site,dtype=np.float64)
    idx=np.asarray(hdids,dtype=np.int32)
    n=len(p)
    if p.shape!=(n,8) or a.shape!=(n,17) or idx.shape!=(n,):
        raise ValueError("Frozen original source shapes changed")
    P=a[:,5:17]
    R=np.empty((n,12),dtype=np.float64)
    for i in range(n):
        cusps,angles=swe.houses_ex(jd_start+(first_idx+i)/96.,lat,lon,b"R")
        R[i]=cusps
    delta=np.abs((R[:,0]-a[:,0]+180.)%360-180.)
    if np.max(delta)>0.0002:raise RuntimeError("Site/source Regiomontanus Ascendant mismatch")
    # Independently reconstruct original sample cached Placidus timing
    # at the source shard beginning, middle and end; full PDF SHAs checked
    # in run() and never claim source-binary R==P.
    for i in set((0,n//2,n-1)):
        source,_=swe.houses_ex(jd_start+(first_idx+i)/96.,lat,lon,b"P")
        if np.max(np.abs((np.asarray(source)-P[i]+180.)%360.-180.))>0.0002:
            raise RuntimeError("Original Placidus source clock/earth angle drift")
    regio=house_ids(p[:,:7],R)
    plac=house_ids(p[:,:7],P)
    rs,rw,ru=local_house_winner(regio)
    ps,pw,pu=local_house_winner(plac)
    same=ru&pu&(rw==pw)
    different=ru&pu&(rw!=pw)
    ptolemy=prev.ptolemy_source.conditional_all_four_common_leader(p,a[:,4])>=0
    known=idx>=0
    counts["total_utc_samples"]+=n
    counts["original_planet_house_assignments"]+=7*n
    counts["HD_boundary_unassigned"]+=int((~known).sum())
    counts["conditional_Ptolemy_fourmode_common"]+=int(ptolemy.sum())
    counts["conditional_Ptolemy_HD_unknown"]+=int((ptolemy&~known).sum())
    counts["Regiomontanus_first_house_any"]+=int((regio==0).any(axis=1).sum())
    counts["Placidus_first_house_any"]+=int((plac==0).any(axis=1).sum())
    counts["any_first_house_occupancy_disagrees"]+=int(((regio==0).any(axis=1)!=(plac==0).any(axis=1)).sum())
    counts["any_traditional_planet_differs_between_12house_systems"]+=int((regio!=plac).any(axis=1).sum())
    counts["regio_unique_house_only_maximum"]+=int(ru.sum())
    counts["placidus_unique_house_only_maximum"]+=int(pu.sum())
    counts["same_strictly_unique_house_only_winner"]+=int(same.sum())
    counts["different_strictly_unique_house_only_winner"]+=int(different.sum())
    counts["both_house_only_winner_tied_or_unresolved"]+=int((~(ru&pu)).sum())
    counts["same_house_only_winner_in_Ptolemy_conditional_set"]+=int((same&ptolemy).sum())
    counts["different_house_only_winner_in_Ptolemy_conditional_set"]+=int((different&ptolemy).sum())
    for planet_i,planet in enumerate(PLANETS):
        mismatch=regio[:,planet_i]!=plac[:,planet_i]
        counts["house_system_disagrees_"+planet]+=int(mismatch.sum())
        for h in range(12):
            counts[f"Regiomontanus_{planet}_house_{h+1}"]+=int((regio[:,planet_i]==h).sum())
            counts[f"Placidus_{planet}_house_{h+1}"]+=int((plac[:,planet_i]==h).sum())
        counts["same_unique_house_only_leader_"+planet]+=int((same&(rw==planet_i)).sum())
    for label,mask in (("same_unique_house_only",same),
                       ("different_unique_house_only",different),
                       ("same_house_only_with_Ptolemy_conditional",same&ptolemy),
                       ("different_house_only_with_Ptolemy_conditional",different&ptolemy)):
        selected=idx[mask&known]
        if len(selected):
            dest=hdsets.setdefault(label,np.zeros(HD_STATES,dtype=bool))
            dest[selected]=True

def run(west,angles,hd_cache,hd_join,verify_sha=True):
    if swe.version!="2.10.03":raise RuntimeError("Swiss source engine changed")
    wplan=west/"plan.json";wman=west/"verified_manifest.json"
    aplan=angles/"plan.json";aman=angles/"verified_manifest.json"
    wp=json.loads(wplan.read_bytes());wm=json.loads(wman.read_bytes())
    ap=json.loads(aplan.read_bytes());am=json.loads(aman.read_bytes())
    n=prev.base.reg.initial.check_manifest(wp,wm,ap,am)
    if n!=N or wp["step_minutes"]!=15:raise RuntimeError("Original exact UTC denominator changed")
    if wm["plan_sha256"]!=prev.base.reg.initial.source_hash(wplan) or am["plan_sha256"]!=prev.base.reg.initial.source_hash(aplan):
        raise RuntimeError("Original western or site plans differ from their source hashes")
    if ap["cols"][5:17]!=["placidus_cusp_"+str(i) for i in range(1,13)]:
        raise RuntimeError("Source cusps no longer Placidus")
    check=prev.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    hj=json.loads((hd_join/"manifest.json").read_bytes())
    if hj["total_utc_grid_samples"]!=N or hj["total_hd_structural_intervals"]!=HD_STATES or hj["unresolved_near_boundary_samples"]!=125:
        raise RuntimeError("Original HD state and boundary source drift")
    jd=prev.base.reg.julian_from_utc(wp["utc_start_inclusive"])
    lat=float(ap["latitude"]);lon=float(ap["longitude"])
    counts=Counter();hsets={}
    seen=0
    for w,a,h in zip(wm["chunks"],am["shards"],hj["shards"],strict=True):
        m=w["count"]
        if w["first_index"]!=seen or a["first_index"]!=seen or h["index_first"]!=seen or h["count"]!=m:
            raise RuntimeError("Same-UTC shard timeline mismatch")
        westbin=west/"chunks"/w["file"];anglebin=angles/"shards"/a["file"]
        hdbin=hd_join/"shards"/h["file"]
        if westbin.stat().st_size!=64*m or anglebin.stat().st_size!=136*m or hdbin.stat().st_size!=4*m:
            raise RuntimeError("Original binary shard byte length changed")
        if verify_sha and (prev.base.reg.initial.source_hash(westbin)!=w["sha256"] or
                           prev.base.reg.initial.source_hash(anglebin)!=a["sha256"] or
                           prev.base.reg.initial.source_hash(hdbin)!=h["sha256"]):
            raise RuntimeError("Original source SHA256 no longer matches")
        planets=np.memmap(westbin,dtype="<f8",mode="r",shape=(m,8))
        asc=np.memmap(anglebin,dtype="<f8",mode="r",shape=(m,17))
        ids=np.memmap(hdbin,dtype="<i4",mode="r",shape=(m,))
        scan_chunk(planets,asc,ids,jd_start=jd,first_idx=seen,
                   lat=lat,lon=lon,counts=counts,hdsets=hsets)
        seen+=m
    if not verify_sha:raise RuntimeError("Publication requires source-shard integrity")
    if seen!=N or counts["total_utc_samples"]!=N or counts["original_planet_house_assignments"]!=N*7:
        raise RuntimeError("Source sample or 7-body denominator altered")
    if counts["HD_boundary_unassigned"]!=125 or counts["conditional_Ptolemy_HD_unknown"]!=0 or counts["conditional_Ptolemy_fourmode_common"]!=4553:
        raise RuntimeError("Old source-neutral HD or Ptolemy baseline changed")
    if counts["Regiomontanus_first_house_any"]!=1409411:
        raise RuntimeError("Original verified first-house Regiomontanus source baseline changed")
    if counts["any_first_house_occupancy_disagrees"]!=84004:
        raise RuntimeError("Earlier source-reconciled Placidus vs Regiomontanus first-house diagnostic changed")
    if sum(counts[k] for k in ("same_strictly_unique_house_only_winner",
                              "different_strictly_unique_house_only_winner",
                              "both_house_only_winner_tied_or_unresolved"))!=N:
        raise RuntimeError("Complete house-winner sensitivity partition failed")
    for body in PLANETS:
        for method in ("Regiomontanus","Placidus"):
            if sum(counts[f"{method}_{body}_house_{j}"] for j in HOUSES)!=N:
                raise RuntimeError("Some traditional planet lacks an assigned house")
    return {
        "schema":"lilly_1647_original_p115_house_accidental_fortitude_same_UTC_century_v01",
        "status":"ORIGINAL_P115_HOUSE_ONLY_ACCIDENTAL_COMPONENT_FULL_CENTURY_NOT_FULL_RULER",
        "source":SOURCE,
        "historical_house_system_variants":["Regiomontanus","Placidus"],
        "published_under_no_personal_natal_data":True,
        "no_complete_accidental_strength_or_manners_ruler":True,
        "no_human_prediction_or_validated_rank":True,
        "house_1_to_12_source_points":HOUSE_POINTS.tolist(),
        "source_hour":"Original 1647 p115; house by ecliptic between quadrant cusps, exact cusp inclusive",
        "source_horizon":[wp["utc_start_inclusive"],wp["utc_end_exclusive"]],
        "fixed_location_research_only":True,"samples":N,"minutes_per_sample":15,
        "original_108_binary_source_shards_SHA256_rechecked":verify_sha,
        "HD_source_audit":check,
        "source_manifest_sha256":{"planets":prev.base.reg.initial.source_hash(wman),
                                   "angles":prev.base.reg.initial.source_hash(aman),
                                   "HD_join":prev.hd_source.hdverify.digest(hd_join/"manifest.json")},
        "HD_structural_intervals":HD_STATES,"HD_unassigned_margin_samples":125,
        "mechanical_counts":dict(counts),
        "HD_distinct_states_with_house_only_conditions":{key:int(bits.sum()) for key,bits in hsets.items()},
        "limits":["A one-component house fortitude of a natal planet is not Lilly's total fortitude or Lord of Geniture",
                  "Historical original quadrant house convention is not settled; Regiomontanus/Placidus treated separately",
                  "Mixed essential dignities including mutual reception and negatives, planetary velocities, motion conditions, fixed stars and aspects remain unknown",
                  "Ptolemy shared-fourmode 4,553 candidates remain conditional geometrical witnesses, not soul governors",
                  "No personal birth records, interviews or real-world trait scores entered this calculation."]
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("west","angles","hd-cache","hd-join","out"):
        p.add_argument("--"+name,required=True,type=Path)
    args=p.parse_args()
    if args.out.exists():raise FileExistsError("Original source-bound census immutable; choose versioned output")
    result=run(args.west,args.angles,args.hd_cache,args.hd_join)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"samples":result["samples"],
                       "source_checks":result["original_108_binary_source_shards_SHA256_rechecked"]},sort_keys=True))
if __name__=="__main__":main()
