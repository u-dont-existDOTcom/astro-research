#!/usr/bin/env python3
"""Lilly 1647 original p115 direct +4, retrograde -5: source-bound motion.

Five traditional planets Mercury/Venus/Mars/Jupiter/Saturn are classified by
direct/retrograde from the signed geocentric longitude time derivative.
Sun and Moon are exempt, per original p115 ("Sun and Moon are always so,
as to them this is voyd"). This is a motion COMPONENT, NOT a complete
planetary fortitude, temperament or human natal-prediction score.

Original 3,506,400 quarter-hour UTC samples at one research place,
36 original SHA-verified planet shards + site angle and HD index, 288,908
HD state intervals, 125 transition-margin unknowns. Finite differences
are centered across shard edges. Absolute first/last samples abstain.
Near station where |speed| <= 0.01 / 0.02 / 0.05 degrees/day (research
uncertainty, NOT Lilly-defined historical thresholds) also abstain.

Independent controls recompute pinned 2.10.03 Swiss ephemeris FLG_SPEED at
deterministic grid indices across all shards. Mercury's original exact
speed column serves as a 3.5m-row cross-check against the derivative.
This is not a reconstruction of "swift"/"slow" historical thresholds.
No user natal/interview records accepted.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np
import swisseph as swe

import lilly_cvii_ptolemy_same_instant_ordered_fallback_v02 as previous

N=3506400
STATE_TOTAL=288908
EPHE_VER="2.10.03"
SEPL_HASH="9f057b316b1890a7f9340d0bf92db96edbab4939dbcc54762b62f6a70a059eb0"
SEMO_HASH="1ca07bd67c24374d77226180c20a4f9996cba013697894810518e7eb582ca4f7"
THRESHOLDS=(0.01,0.02,0.05)
MOVING=(2,3,4,5,6)
PLANET_NAMES=("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn")

def wrapped_speed(prior_row,next_row):
    """Centered quarter-hour 2-tick finite difference in degrees/day."""
    a=np.asarray(prior_row,dtype=np.float64)
    b=np.asarray(next_row,dtype=np.float64)
    if a.shape!=b.shape or a.ndim!=2 or a.shape[1]!=7:
        raise ValueError("Aligned seven-body geocentric longitudes required")
    if np.any(~np.isfinite(a)) or np.any(~np.isfinite(b)):
        raise ValueError("Nonfinite source")
    if np.any((a<0)|(a>=360)) or np.any((b<0)|(b>=360)):
        raise ValueError("Unnormalized zodiac")
    return ((b-a+180.0)%360.-180.0)*48.0

def status(speed,epsilon,global_first_last=None):
    """(direct, retrograde, unknown): disjoint/complete for each body and time."""
    x=np.asarray(speed,dtype=np.float64)
    if x.ndim!=1 or epsilon<=0 or epsilon>0.1:
        raise ValueError("1D positive bounded engineering threshold required")
    unk=~np.isfinite(x)|(np.abs(x)<=epsilon)
    if global_first_last is not None:
        edges=np.asarray(global_first_last,dtype=bool)
        if edges.shape!=x.shape:raise ValueError("Absolute edges not aligned")
        unk|=edges
    direct=~unk&(x>0)
    retro=~unk&(x<0)
    if np.any(direct&retro) or not np.all(direct|retro|unk):
        raise RuntimeError("Motion classification overlap/missing state")
    return direct,retro,unk

def _load_mmap(root,chunk):
    p=root/"chunks"/chunk["file"]
    if p.stat().st_size!=chunk["count"]*64:
        raise RuntimeError("Frozen original planet data size changed")
    return np.memmap(p,dtype="<f8",mode="r",shape=(chunk["count"],8))

def scan(west,angles,hd_cache,hd_join,ephe,verify_shards=True):
    if swe.version!=EPHE_VER:raise RuntimeError("Swiss source engine changed")
    for name,digest in (("sepl_18.se1",SEPL_HASH),("semo_18.se1",SEMO_HASH)):
        if previous.base.reg.initial.source_hash(ephe/name)!=digest:
            raise RuntimeError("Planetary source binary SHA drift: "+name)
    swe.set_ephe_path(str(ephe))
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    wj=json.loads(wp.read_bytes());wjm=json.loads(wm.read_bytes())
    aj=json.loads(ap.read_bytes());ajm=json.loads(am.read_bytes())
    n=previous.base.reg.initial.check_manifest(wj,wjm,aj,ajm)
    if n!=N or wj["step_minutes"]!=15:raise RuntimeError("Frozen century clock changed")
    if (wjm["plan_sha256"]!=previous.base.reg.initial.source_hash(wp) or
        ajm["plan_sha256"]!=previous.base.reg.initial.source_hash(ap)):
        raise RuntimeError("Original source plan SHA drift")
    proof=previous.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    hj=json.loads((hd_join/"manifest.json").read_bytes())
    if hj["total_utc_grid_samples"]!=N or hj["total_hd_structural_intervals"]!=STATE_TOTAL or hj["unresolved_near_boundary_samples"]!=125:
        raise RuntimeError("Independent HD state or source clock changed")
    counter=Counter()
    HDsets={name:np.zeros(STATE_TOTAL,dtype=bool) for name in PLANET_NAMES[2:]}
    jd0=previous.base.reg.julian_from_utc(wj["utc_start_inclusive"])
    first=0
    largest_speed_difference=0.
    largest_lon_difference=0.
    for sh,(w,a,h) in enumerate(zip(wjm["chunks"],ajm["shards"],hj["shards"],strict=True)):
        m=w["count"]
        if first!=w["first_index"] or first!=a["first_index"] or first!=h["index_first"] or h["count"]!=m:
            raise RuntimeError("Source original UTC row offsets shifted")
        pth=west/"chunks"/w["file"];apth=angles/"shards"/a["file"];hpth=hd_join/"shards"/h["file"]
        if apth.stat().st_size!=136*m or hpth.stat().st_size!=4*m:raise RuntimeError("Source binary length drift")
        if verify_shards:
            for f,row in ((pth,w),(apth,a),(hpth,h)):
                if previous.base.reg.initial.source_hash(f)!=row["sha256"]:
                    raise RuntimeError("Source binary shard hash changed")
        X=_load_mmap(west,w)
        # Valid source-control inputs include original site and HD shards.
        A=np.memmap(apth,dtype="<f8",mode="r",shape=(m,17))
        ids=np.memmap(hpth,dtype="<i4",mode="r",shape=(m,))
        counter["samples"]+=m
        known=ids>=0
        counter["HD_transition_margin_unknown"]+=int((~known).sum())
        ptolemy=previous.ptolemy_source.conditional_all_four_common_leader(X,A[:,4])>=0
        counter["prior_conditional_ptolemy_common"]+=int(ptolemy.sum())
        counter["ptolemy_HD_unknown"]+=int((ptolemy&~known).sum())

        prev_row=X[0,:7] if sh==0 else _load_mmap(west,wjm["chunks"][sh-1])[-1,:7]
        next_row=X[-1,:7] if sh==len(wjm["chunks"])-1 else _load_mmap(west,wjm["chunks"][sh+1])[0,:7]
        prevs=np.concatenate((np.asarray(prev_row,dtype=float).reshape(1,7),X[:-1,:7]),axis=0)
        nexts=np.concatenate((X[1:,:7],np.asarray(next_row,dtype=float).reshape(1,7)),axis=0)
        deriv=wrapped_speed(prevs,nexts)
        edge=np.zeros(m,dtype=bool)
        if sh==0:edge[0]=True
        if sh==len(wjm["chunks"])-1:edge[-1]=True
        # Cached Mercury speed is exact original source speed, independent
        # of finite differencing; keep source audit differences explicit.
        nonedge=~edge
        delta=np.abs(deriv[nonedge,2]-X[nonedge,7])
        if len(delta):
            largest_speed_difference=max(largest_speed_difference,float(delta.max()))
            counter["mercury_cached_speed_comparison_samples"]+=int(len(delta))
            for t in THRESHOLDS:
                d1,r1,_=status(deriv[:,2],t,edge)
                d2,r2,_=status(X[:,7],t,edge)
                conflict=int((d1&r2|r1&d2).sum())
                counter[f"Mercury_exact_vs_finite_sign_conflict_{t}"]+=conflict
        for idx in MOVING:
            name=PLANET_NAMES[idx]
            # Original Western cache already contains Mercury's Swiss
            # longitude speed as column 7; use that actual source value
            # instead of a finite-difference approximation for Mercury.
            vel=X[:,7] if idx==2 else deriv[:,idx]
            for t in THRESHOLDS:
                d,r,u=status(vel,t,edge)
                key=f"{name}|threshold={t:.2f}|"
                counter[key+"direct"]+=int(d.sum())
                counter[key+"retrograde"]+=int(r.sum())
                counter[key+"unknown"]+=int(u.sum())
                counter[key+"conditional_ptolemy_direct"]+=int((d&ptolemy).sum())
                counter[key+"conditional_ptolemy_retrograde"]+=int((r&ptolemy).sum())
                counter[key+"conditional_ptolemy_unknown"]+=int((u&ptolemy).sum())
                if t==0.02:
                    sel=ids[r&known]
                    if len(sel):HDsets[name][sel]=True
        # Independent Swiss ephemeris exact speed controls across all
        # traditional nonluminary planets, not only cached Mercury speed.
        controls=sorted(set((0,1,m//9,m//3,m//2,2*m//3,8*m//9,m-2,m-1)))
        for i in controls:
            jd=jd0+(first+i)/96.
            for idx in MOVING:
                actual,flag=swe.calc_ut(jd,idx,swe.FLG_SWIEPH|swe.FLG_SPEED)
                ephem_kind=flag&(swe.FLG_JPLEPH|swe.FLG_SWIEPH|swe.FLG_MOSEPH)
                if ephem_kind!=swe.FLG_SWIEPH:
                    raise RuntimeError("Swiss silently substituted another ephemeris source")
                lon_diff=abs((actual[0]-X[i,idx]+180)%360-180)
                largest_lon_difference=max(largest_lon_difference,lon_diff)
                if lon_diff>0.0002:
                    raise RuntimeError("Exact Swiss control source longitude not same original grid")
                if not edge[i]:
                    vd=abs(actual[3]-deriv[i,idx])
                    largest_speed_difference=max(largest_speed_difference,vd)
                    # Derivative is a numerical approximation; these
                    # controls catch material sign errors, not fake exactness.
                    if vd>0.01:raise RuntimeError("Geocentric speed derivative drift outside engineering tolerance")
                    for t in THRESHOLDS:
                        if (abs(actual[3])>t and abs(deriv[i,idx])>t
                            and (actual[3]>0)!=(deriv[i,idx]>0)):
                            raise RuntimeError("Pausable direct/retrograde source speed sign conflict")
                counter["Swiss_verified_frozen_longitude_and_speed_controls"]+=1
        first+=m
    if not verify_shards:raise RuntimeError("Cannot publish unverified source data")
    if first!=N or counter["samples"]!=N or counter["HD_transition_margin_unknown"]!=125 or counter["prior_conditional_ptolemy_common"]!=4553:
        raise RuntimeError("Original same-UTC and HD source denominator changed")
    if counter["ptolemy_HD_unknown"]!=0:raise RuntimeError("Previously known Ptolemy/HD root case drift")
    if counter["mercury_cached_speed_comparison_samples"]!=N-2:
        raise RuntimeError("Full-century exact Mercury speed comparison incomplete")
    for name in PLANET_NAMES[2:]:
        for t in THRESHOLDS:
            prefix=f"{name}|threshold={t:.2f}|"
            if sum(counter[prefix+kind] for kind in ("direct","retrograde","unknown"))!=N:
                raise RuntimeError("Motion statuses must partition entire original full source clock")
            if sum(counter[prefix+"conditional_ptolemy_"+kind] for kind in ("direct","retrograde","unknown"))!=4553:
                raise RuntimeError("Motion statuses must partition original conditional Ptolemy set")
            if counter[prefix+"unknown"]<2:
                raise RuntimeError("Two absolute clock endpoints cannot have central derivative")
    for t in THRESHOLDS:
        if counter[f"Mercury_exact_vs_finite_sign_conflict_{t}"]!=0:
            raise RuntimeError("Source Mercury signed speed and derivative disagree outside station range")
    return {
      "schema":"lilly_1647_p115_direct_retrograde_partial_original_century_v01",
      "status":"ORIGINAL_DIRECT_RETROGRADE_SOURCE_COMPONENT_CENTURY_WITH_FINITE_SPEED_ABSTENTIONS",
      "source":"William Lilly, Christian Astrology, original first printing 1647 p115 direct +4, retrograde -5; Sun/Moon always-direct grade void",
      "source_page_115_sha256":"fe75468d8eaf129a1f643d6d652455e81eb95b0aedd3016091e3ce7c204e4aab",
      "strict_new_source_Swiss_version":EPHE_VER,
      "strict_planetary_ephemeris_SHA256":{"sepl_18.se1":SEPL_HASH,"semo_18.se1":SEMO_HASH},
      "longitude_source_rebound_max_deg":largest_lon_difference,
      "signed_speed_finite_diff_vs_cached_or_rebound_max_deg_per_day":largest_speed_difference,
      "source_original_input_shard_sha256_verified":verify_shards,
      "source_hd_verified_audit":proof,
      "source_horizon_UTC":[wj["utc_start_inclusive"],wj["utc_end_exclusive"]],
      "samples":N,"step_minutes":15,"HD_structural_intervals":STATE_TOTAL,
      "source_planetary_positions":["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"],
      "Sun_Moon_direct_retrograde_table_grade":"EXCLUDED_BY_LILLY_ORIGINAL_P115_PARENTHESES",
      "station_tolerance_deg_per_day":list(THRESHOLDS),
      "station_uncertainty_is_engineering_not_historic_orb":True,
      "speed_method":"Exact source Swiss Mercury speed column for all samples; original 15-minute centered geocentric finite differences for Venus/Mars/Jupiter/Saturn with 2 absolute clock-edge abstentions; exact Swiss controls across all five planets",
      "counts":dict(counter),
      "HD_distinct_intervals_with_retrograde_0p02_by_planet":{name:int(bits.sum()) for name,bits in HDsets.items()},
      "complete_historic_accidental_strength":False,
      "Lilly_actual_manners_significator_calculated":False,
      "Ptolemy_actual_soul_governor_calculated":False,
      "human_predictive_validity_established":False,
      "personal_natal_interview_data_used":False
    }

def main():
    parser=argparse.ArgumentParser()
    for name in ("west","angles","hd-cache","hd-join","ephe","out"):
        parser.add_argument("--"+name,type=Path,required=True)
    a=parser.parse_args()
    if a.out.exists():raise FileExistsError("Source-bound original run must not overwrite earlier evidence")
    j=scan(a.west,a.angles,a.hd_cache,a.hd_join,a.ephe)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(j,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":j["status"],"samples":j["samples"],
                      "control_count":j["counts"]["Swiss_verified_frozen_longitude_and_speed_controls"]},sort_keys=True))
if __name__=="__main__":main()
