#!/usr/bin/env python3
"""Full declared century census: four-mode consensus + optional I.24 ecliptic latitude.

Scope: source-only astronomy, NOT a uniquely Ptolemaic personality governor.
A separate, pinned Swiss ephemeris provides latitudes absent from the original
quarter-hour cache. No private natal/chart/profile/survey data are accepted.
The older edition-specific four-mode common-lord witness remains CONDITIONAL.
Ptolemy I.24: bodily app/sep require bodies on same side of ecliptic, unlike rays.
I.24's western-before/eastern-after source criterion is compared separately
with the older relative-velocity sign, never conflated with exact event roots.
"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import json
import numpy as np
import swisseph as swe
import ptolemy_lilly_hd_same_instant_century_v01 as prior

FOUR=prior.four
DUAL=prior.dual
REG=prior.reg
HD=prior.hdverify
SAMPLES=3506400
SWISS_VERSION="2.10.03"
SEPL_SHA="9f057b316b1890a7f9340d0bf92db96edbab4939dbcc54762b62f6a70a059eb0"
SEMO_SHA="1ca07bd67c24374d77226180c20a4f9996cba013697894810518e7eb582ca4f7"
TOLERANCES=(1.,3.,5.,10.,15.)
# A numerical rebind tolerance for old cache longitude vs pinned later Swiss
# planetary source. This is NOT a Ptolemaic orb or ecliptic latitude threshold.
LONGITUDE_REBIND_MAX_DEG=0.0002
LAT_ZERO_UNCERTAINTY_DEG=0.000001

def same_ecliptic_side(a,b,eps=LAT_ZERO_UNCERTAINTY_DEG):
    """Treat exactly/nearly-on-ecliptic inputs as unknown, never affirmative."""
    a=np.asarray(a,dtype=np.float64);b=np.asarray(b,dtype=np.float64)
    if a.shape!=b.shape:raise ValueError("Latitude pair not aligned")
    return (np.isfinite(a)&np.isfinite(b)&(np.abs(a)>eps)&
            (np.abs(b)>eps)&((a>0)==(b>0)))

def conditional_all_four_common_leader(planet_rows,solar_altitude):
    """Exact prior consensus algebra; keep all four historical variants."""
    p=np.asarray(planet_rows,dtype=np.float64)
    alt=np.asarray(solar_altitude,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=8 or alt.shape!=(len(p),):
        raise ValueError("Aligned source longitudes and altitude required")
    source_branches=[]
    sect=np.abs(alt)>prior.SUN_ALT_UNCERTAINTY
    for scheme,corulers in prior.VARIANTS:
        mercury=prior.four_mode_votes(p[:,2],alt,scheme,corulers)
        moon=prior.four_mode_votes(p[:,1],alt,scheme,corulers)
        m,_,mr,_=prior.rank_state(mercury)
        l,_,lr,_=prior.rank_state(moon)
        source_branches.append(np.where(
            sect & mr & lr & (m>=0)&(m==l),m,-1))
    stack=np.stack(source_branches,axis=0)
    joint=(stack>=0).all(axis=0)&(stack==stack[0]).all(axis=0)
    return np.where(joint,stack[0],-1)

def classify_dual(eligible,mray,lray,mbody,lbody,m_lat_ok,l_lat_ok,v,t):
    """Deterministic candidate masks for one engineering distance threshold."""
    arrays=[np.asarray(x) for x in (eligible,mray,lray,mbody,lbody,m_lat_ok,l_lat_ok,v)]
    if len({x.shape for x in arrays})!=1 or arrays[0].ndim!=1:
        raise ValueError("Same-length 1D geometry required")
    if t<=0 or t>30:raise ValueError("Only explicit bounded sensitivity thresholds")
    e,mr,lr,mb,lb,ml,ll,rv=arrays
    mr_ok=np.abs(mr)<=t;lr_ok=np.abs(lr)<=t
    mb_ok=np.abs(mb)<=t;lb_ok=np.abs(lb)<=t
    nonbody=e&mr_ok&lr_ok
    possible=e&(mr_ok|mb_ok)&(lr_ok|lb_ok)
    verified=e&(mr_ok|(mb_ok&ml))&(lr_ok|(lb_ok&ll))
    lunar=np.where(lr_ok,lr,lb)
    # For bodies with uncertain latitude, no directional classification.
    # Orientation is between Moon and selected planet ray.
    apply_ecliptic=verified&(lunar<0)
    separate_ecliptic=verified&(lunar>0)
    apply_velocity=verified&(rv*lunar<0)&np.isfinite(rv)
    separate_velocity=verified&(rv*lunar>0)&np.isfinite(rv)
    return {
        "nonbody":nonbody,"possible":possible,"verified":verified,
        "apply_by_zodiacal_precedence":apply_ecliptic,
        "separate_by_zodiacal_precedence":separate_ecliptic,
        "apply_by_relative_velocity_proxy":apply_velocity,
        "separate_by_relative_velocity_proxy":separate_velocity,
        "direction_disagreement":verified&np.isfinite(rv)&(lunar!=0)&
             (apply_ecliptic!=apply_velocity),
        "exactly_on_ray_direction_unresolved":verified&(lunar==0),
        "body_latitude_unsupported_or_opposite":possible&~verified
    }

def run(west:Path,angles:Path,hd_cache:Path,hd_join:Path,ephe:Path,sha_check=True):
    if swe.version!=SWISS_VERSION:raise RuntimeError("Wrong Swiss ephemeris version")
    required={"sepl_18.se1":SEPL_SHA,"semo_18.se1":SEMO_SHA}
    for file,digest in required.items():
        if REG.initial.source_hash(ephe/file)!=digest:
            raise RuntimeError("Pinned strict Swiss source file SHA256 mismatch: "+file)
    swe.set_ephe_path(str(ephe))
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    pw=json.loads(wp.read_bytes());mw=json.loads(wm.read_bytes())
    pa=json.loads(ap.read_bytes());ma=json.loads(am.read_bytes())
    n=REG.initial.check_manifest(pw,mw,pa,ma)
    if n!=SAMPLES:raise RuntimeError("Wrong full-century population")
    if mw["plan_sha256"]!=REG.initial.source_hash(wp) or ma["plan_sha256"]!=REG.initial.source_hash(ap):
        raise RuntimeError("Changed original plan")
    hproof=HD.audit_join(west,hd_cache,hd_join)
    hj=json.loads((hd_join/"manifest.json").read_bytes())
    if hj["unresolved_near_boundary_samples"]!=125 or len(hj["shards"])!=36:
        raise RuntimeError("HD source incongruent")
    start_jd=REG.julian_from_utc(pw["utc_start_inclusive"])
    counts=Counter()
    hd_set={t:set() for t in TOLERANCES}
    max_drift=0.
    processed=0
    for w,a,h in zip(mw["chunks"],ma["shards"],hj["shards"],strict=True):
        k=w["count"]
        if (w["first_index"]!=processed or a["first_index"]!=processed or
                h["index_first"]!=processed or h["count"]!=k):
            raise RuntimeError("Misaligned chronological shards")
        sourcep=west/"chunks"/w["file"]
        sourcea=angles/"shards"/a["file"]
        if sourcep.stat().st_size!=k*64 or sourcea.stat().st_size!=k*136:
            raise RuntimeError("Original binary size changed")
        if sha_check and (REG.initial.source_hash(sourcep)!=w["sha256"] or
          REG.initial.source_hash(sourcea)!=a["sha256"]):
            raise RuntimeError("Original source shard hash changed")
        p=np.memmap(sourcep,dtype="<f8",shape=(k,8),mode="r")
        q=np.memmap(sourcea,dtype="<f8",shape=(k,17),mode="r")
        ids=np.memmap(hd_join/"shards"/h["file"],dtype="<i4",shape=(k,),mode="r")
        common=conditional_all_four_common_leader(p,q[:,4])
        counts["all_four_robust_consensus"]+=int((common>=0).sum())
        no_motion=np.zeros(k,dtype=bool);no_motion[0]=True;no_motion[-1]=True
        for planet in DUAL.EXTERNAL_GOVERNORS.values():
            selected=(common==planet)&~no_motion
            if not selected.any():continue
            mray=DUAL.nearest_residual(p[:,planet],p[:,2],DUAL.ASPECTS_NONBODY)
            lray=DUAL.nearest_residual(p[:,1],p[:,planet],DUAL.ASPECTS_NONBODY)
            mbody=DUAL.nearest_residual(p[:,planet],p[:,2],(0.,))
            lbody=DUAL.nearest_residual(p[:,1],p[:,planet],(0.,))
            v=DUAL.lunar_radial_trend(p[:,1],p[:,planet])
            mlat=np.zeros(k,dtype=bool)
            llat=np.zeros(k,dtype=bool)
            # Only compute strict Swiss latitudes when a bodily ray can
            # change the largest t=15 candidate result.
            maybe=selected&( (np.abs(mray)<=15)|(np.abs(mbody)<=15) )&(
                    (np.abs(lray)<=15)|(np.abs(lbody)<=15))
            need=np.flatnonzero(maybe&( (np.abs(mbody)<=15)|(np.abs(lbody)<=15) ))
            for i in need:
                jd=start_jd+(processed+int(i))/96.
                bodies={}
                for body in (1,2,planet):
                    xx,flag=swe.calc_ut(jd,body,swe.FLG_SWIEPH|swe.FLG_SPEED)
                    if (flag & (swe.FLG_JPLEPH|swe.FLG_SWIEPH|swe.FLG_MOSEPH))!=swe.FLG_SWIEPH:
                        raise RuntimeError("Swiss silently changed ephemeris to fallback")
                    delta=abs((xx[0]-p[i,body]+180)%360-180)
                    max_drift=max(max_drift,delta)
                    if delta>LONGITUDE_REBIND_MAX_DEG:
                        raise RuntimeError("Current Swiss longitude differs from original source grid")
                    bodies[body]=xx[1]
                mlat[i]=bool(same_ecliptic_side(
                    np.array([bodies[2]]),np.array([bodies[planet]]))[0])
                llat[i]=bool(same_ecliptic_side(
                    np.array([bodies[1]]),np.array([bodies[planet]]))[0])
            counts["swiss_exact_latitude_timestamps_examined"]+=len(need)
            for t in TOLERANCES:
                tag=str(int(t))+"deg_"
                c=classify_dual(selected,mray,lray,mbody,lbody,mlat,llat,v,t)
                for metric,mask in c.items():
                    counts[tag+metric]+=int(mask.sum())
                eligible=c["verified"]&(ids>=0)
                counts[tag+"hd_valid"]+=int(eligible.sum())
                counts[tag+"hd_unresolved"]+=int((c["verified"]&(ids<0)).sum())
                hd_set[t].update(ids[eligible].tolist())
        processed+=k
    if processed!=n:raise RuntimeError("Grid incompletely traversed")
    if counts["all_four_robust_consensus"]!=4553:
        raise RuntimeError("Frozen original all-variant consensus baseline shifted")
    for t in TOLERANCES:
        tag=str(int(t))+"deg_"
        if counts[tag+"nonbody"]>counts[tag+"verified"] or counts[tag+"verified"]>counts[tag+"possible"]:
            raise RuntimeError("Ecliptic latitude qualification ordering failed")
    return {
      "schema":"ptolemy_i24_dual_contact_latitude_verified_finite_century_v01",
      "status":"PINNED_SWISS_BODILY_LATITUDE_CHECK_SOURCE_GEOMETRY_ONLY",
      "sample_count":n,"step_minutes":15,
      "UTC_start":pw["utc_start_inclusive"],"UTC_end_exclusive":pw["utc_end_exclusive"],
      "original_72_source_shards_SHA256_verified":sha_check,
      "original_west_manifest_SHA256":REG.initial.source_hash(wm),
      "original_angle_manifest_SHA256":REG.initial.source_hash(am),
      "HD_join_audit":hproof,
      "strict_new_ephe_SHA256":required,
      "Swiss_version":swe.version,
      "largest_rebound_longitude_deviation_deg":max_drift,
      "source_ephemeris_version_not_original_grid_binary":True,
      "source_numeric_orbs_historically_authored":False,
      "engineering_tolerances_deg":list(TOLERANCES),
      "conditional_consensus_four_mode_only":True,
      "moon_velocity_direction_not_equated_to_original_source":True,
      "longitude_source_original_plus_later_ephemeris_latitude_pinned":True,
      "counts":dict(counts),
      "HD_interval_counts":{str(int(t)):len(hd_set[t]) for t in TOLERANCES},
      "human_predictions_validated":False,
      "actual_ptolemy_soul_governor_selected":False,
      "private_natal_or_interview_loaded":False
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("west","angles","hd-cache","hd-join","ephe","out"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError("Immutable source-bound output already exists")
    z=run(a.west,a.angles,a.hd_cache,a.hd_join,a.ephe)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(z,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":z["status"],"count":z["sample_count"],
                      "scan":z["counts"],"HD_intervals":z["HD_interval_counts"]},sort_keys=True))

if __name__=="__main__":main()
