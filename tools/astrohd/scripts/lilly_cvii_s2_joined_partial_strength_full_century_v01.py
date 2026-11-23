#!/usr/bin/env python3
"""Lilly 1647 CVII p536: source-eligible S2 joined planets, then PARTIAL power.

A true full-century, source-hash-verified same-UTC join of the already
verified original S2 joining candidate identities and the prior partial
Lilly natal-body essential + house + motion scores. Original p536 is
entered only if first-stage p535 is EMPTY under the stated geometry.

3 p535 S1 place readings x 2 original 1647 p107 printed moiety envelopes
x 2 S2 candidate-body scopes = 12 qualifying S2 candidate-set variants;
each x 3 printed term tables x 4 reception/peregrine hypotheses x
2 historic house geometry policies x 3 modern station abstention bands =
864 transparent source-and-researcher-method conditional comparisons.

Original p536 permits a planet joined to Moon or Mercury and specifically
discusses a planet joined to BOTH. If multiple eligible planets exist,
retain all as manners candidates. The partial score arbitrates a stronger
candidate ONLY if its lower score bound exceeds all OTHER ELIGIBLE
joined planets' upper bounds; no ineligible global-strength champion may
be picked. A sole qualifying S2 body is a SOLE CONDITIONAL participant,
not a historically proven final manners ruler; original Moon/Mercury
mutual contact in broad candidate scope, luminary fortification, other
planet dignity and aspect strength remain disputed.

All original 3,506,400 15min UTC samples at ONE fixed research site.
Original 36 planet +36 site +36 HD source-index shards SHA-256 verified,
288,908 HD intervals, 125 HD root-margin unknown and 4,553 conditional
Ptolemy four-mode possible leaders preserved. Previous S2 12-source
zero/one/multi/HD-conditional results checked against frozen prior
aggregate, and old motion/house component reference bins checked.

NO natal persons, birth times, interview scores or humans evaluated.
NO original complete Lilly manners or Ptolemy soul governor selected.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import swisseph as swe

import lilly_cvii_s2_actual_joined_planet_candidates_century_v01 as s2
import lilly_cvii_s1_eligible_partial_strength_century_v01 as s1
import lilly_1647_integrated_partial_fortitude_full_century_v01 as partial

N=s2.N
HD_STATE_COUNT=s2.HD_STATES
MODES=s2.MODES
ORBS=s2.ORB_OPTIONS
SCOPES=s2.SCOPES
STATIONS=partial.STATIONS
ESSENTIAL_POLICIES=partial.ESSENTIAL_POLICIES
TERMS=partial.TERMS
HOUSES=partial.HOUSE_NAMES
PARTIAL_METHOD_COUNT=partial.NUM_SCENARIOS
SCENARIOS=s2.STAGES*PARTIAL_METHOD_COUNT


def select_joined_source_candidate(lower,upper,eligible,sect_known):
    """Original possible joining-set filtered provisional partial power.

    One qualifying S2 candidate is retained regardless of uncertain
    relative strength. Several candidates all remain historically
    participants, and a unique CONDITIONAL partial leader is chosen
    only when a strict bound dominates the other joined bodies.
    """
    return s1.select_conditional_principal(lower,upper,eligible,sect_known)


def scan_chunk(P,A,IDs,*,R,velocities,edges,counts,HD):
    p=np.asarray(P,dtype=np.float64)
    a=np.asarray(A,dtype=np.float64)
    ids=np.asarray(IDs,dtype=np.int32)
    r=np.asarray(R,dtype=np.float64)
    v=np.asarray(velocities,dtype=np.float64)
    n=len(p)
    if (p.shape!=(n,8) or a.shape!=(n,17) or ids.shape!=(n,)
        or r.shape!=(n,12) or v.shape!=(n,7)
        or np.asarray(edges,dtype=bool).shape!=(n,)):
        raise ValueError("Aligned original planet/site/HD and source speeds required")

    # First-stage source mode is a HARD prerequisite for S2.
    first=s1.first_stage_eligible(p[:,:7],r[:,0],r[:,1])
    empty={mode:~eligible.any(axis=1) for mode,eligible in first.items()}
    source_pt=s1.base.es.src.PRIOR.ptolemy_source.conditional_all_four_common_leader(p,a[:,4])
    pt_known=source_pt>=0
    HD_known=ids>=0
    sect=np.abs(a[:,4])>partial.es.SECT_EPS

    counts["original_UTC_clock_samples"]+=n
    counts["HD_root_unknown"]+=int((~HD_known).sum())
    counts["near_sun_horizon_sect_unknown"]+=int((~sect).sum())
    counts["ptolemy_conditional_fourmode_common"]+=int(pt_known.sum())
    counts["ptolemy_HD_root_unknown"]+=int((pt_known&~HD_known).sum())

    source_sets={}
    source_dual={}
    for orb,table in ORBS.items():
        for scope in SCOPES:
            qualifies=s2.candidates_joined_to_moon_or_mercury(p[:,:7],table,scope)
            for mode in MODES:
                k="|".join((mode,orb,scope))
                E=qualifies["union"]&empty[mode][:,None]
                source_sets[k]=E
                source_dual[k]=qualifies["both"]&E
                persons=E.sum(axis=1)
                zero=empty[mode]&(persons==0)
                sole=empty[mode]&(persons==1)
                multi=empty[mode]&(persons>1)
                counts[k+"|S2_empty_go_to_later"]+=int(zero.sum())
                counts[k+"|S2_sole"]+=int(sole.sum())
                counts[k+"|S2_multi"]+=int(multi.sum())
                counts[k+"|S2_any"]+=int((sole|multi).sum())
                counts[k+"|S2_ptolemy_any"]+=int(((sole|multi)&pt_known).sum())
                counts[k+"|S2_any_joins_both_Moon_and_Mercury"]+=int(
                    (source_dual[k].any(axis=1)).sum())

    house_scores={
       "Regiomontanus":partial.hs.HOUSE_POINTS[
          partial.hs.house_ids(p[:,:7],r)].astype(np.int16),
       "Placidus":partial.hs.HOUSE_POINTS[
          partial.hs.house_ids(p[:,:7],a[:,5:17])].astype(np.int16),
    }
    for mode in MODES:
        counts[mode+"|S1_empty"]+=int(empty[mode].sum())
    movement={t:partial.signed_motion_bounds(v,t,edges) for t in STATIONS}

    # Separate all-72 robust counters for each S2 eligibility set.
    stable={key:np.ones(n,dtype=bool) for key in source_sets}
    common={key:np.full(n,-2,dtype=np.int8) for key in source_sets}
    iteration=0
    for term in TERMS:
        strength=partial.essential_points(p[:,:7],a[:,4],term)
        for essential_policy in ESSENTIAL_POLICIES:
            essential=strength[essential_policy]
            for station in STATIONS:
                lower_motion,upper_motion=movement[station]
                for house in HOUSES:
                    label="|".join((term,essential_policy,house,f"station={station:.2f}"))
                    lower=essential+house_scores[house]+lower_motion
                    upper=essential+house_scores[house]+upper_motion
                    for key,E in source_sets.items():
                        sel,sole,multi=select_joined_source_candidate(lower,upper,E,sect)
                        qualified=sel>=0
                        counts[key+"|"+label+"|conditional_candidate"]+=int(qualified.sum())
                        counts[key+"|"+label+"|multi_partial_strict"]+=int((multi&qualified).sum())
                        counts[key+"|"+label+"|multi_unknown_strength"]+=int((multi&~qualified).sum())
                        counts[key+"|"+label+"|same_conditional_ptolemy"]+=int((qualified&(sel==source_pt)).sum())
                        counts[key+"|"+label+"|different_conditional_ptolemy"]+=int((qualified&pt_known&(sel!=source_pt)).sum())
                        # Do not accidentally interpret a missing S2 as a
                        # selected planet with a 0 score.
                        first_sel=common[key]
                        first_sel[:]=np.where(first_sel==-2,sel,first_sel)
                        stable[key]&=qualified&(first_sel==sel)
                    iteration+=1
    if iteration!=PARTIAL_METHOD_COUNT:
        raise RuntimeError("All 72 source-conditioned partial strength models must run")

    for key,E in source_sets.items():
        result=stable[key]&(common[key]>=0)
        n_eligible=E.sum(axis=1)
        zero=n_eligible==0
        single=n_eligible==1
        multi=n_eligible>1
        counts[key+"|stable_all72_sole"]+=int((result&single).sum())
        counts[key+"|stable_all72_multi_strict"]+=int((result&multi).sum())
        counts[key+"|stable_all72_any"]+=int(result.sum())
        counts[key+"|stable_all72_both_joined"]+=int(
            (result&source_dual[key][np.arange(n),np.maximum(common[key],0)]).sum())
        counts[key+"|stable_all72_Ptolemy_any"]+=int((result&pt_known).sum())
        counts[key+"|stable_all72_same_Ptolemy"]+=int((result&(common[key]==source_pt)).sum())
        if np.any(result&HD_known):
            HD[key][ids[result&HD_known]]=True
        if np.any(result&pt_known&HD_known):
            HD["Ptolemy_"+key][ids[result&pt_known&HD_known]]=True

    # Reconcile the *complete historical S2 uncertainty*, not cherry-picked
    # single place/orb; a candidate is universal only if all 12 eligibility
    # alternatives are each robust under all 72 strength policies.
    all_candidate=np.ones(n,dtype=bool)
    shared=np.full(n,-2,dtype=np.int8)
    for k in source_sets:
        all_candidate&=stable[k]
        shared[:]=np.where(shared==-2,common[k],shared)
        all_candidate&=(shared==common[k])
    counts["all_864_source_scenarios_same_strict_conditional_S2"]+=int(all_candidate.sum())
    counts["all_864_same_candidate_in_ptolemy_fourmode"]+=int((all_candidate&pt_known).sum())
    counts["all_864_same_candidate_same_as_ptolemy"]+=int((all_candidate&(shared==source_pt)).sum())
    if np.any(all_candidate&HD_known):
        HD["all_864_same"][ids[all_candidate&HD_known]]=True


def run(west,angles,hd_cache,hd_join,verify_sha=True):
    if swe.version!="2.10.03":raise RuntimeError("Frozen Swiss source engine drift")
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    wj=json.loads(wp.read_bytes());wjm=json.loads(wm.read_bytes())
    aj=json.loads(ap.read_bytes());ajm=json.loads(am.read_bytes())
    prior=s1.base.es.src.PRIOR
    N_original=prior.base.reg.initial.check_manifest(wj,wjm,aj,ajm)
    if N_original!=N or wj["step_minutes"]!=15:
        raise RuntimeError("Original century sample count changed")
    digest=prior.base.reg.initial.source_hash
    if wjm["plan_sha256"]!=digest(wp) or ajm["plan_sha256"]!=digest(ap):
        raise RuntimeError("Frozen original source plan drift")
    hdproof=prior.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    hj=json.loads((hd_join/"manifest.json").read_bytes())
    if (hj["total_utc_grid_samples"]!=N or hj["total_hd_structural_intervals"]!=HD_STATE_COUNT
        or hj["unresolved_near_boundary_samples"]!=125):
        raise RuntimeError("HD source structural cohort drift")
    last=json.loads((Path(__file__).resolve().parents[1]/"reference/research/lilly_cvii_s2_original_joining_full_century_public_v01.json").read_bytes())
    earlier=last["counts"]
    jd=prior.base.reg.julian_from_utc(wj["utc_start_inclusive"])
    lat=float(aj["latitude"]);lon=float(aj["longitude"])
    counts=Counter()
    hd_bits={key:np.zeros(HD_STATE_COUNT,dtype=bool) for key in
         [*("|".join((m,o,s)) for m in MODES for o in ORBS for s in SCOPES),
          *("Ptolemy_"+"|".join((m,o,s)) for m in MODES for o in ORBS for s in SCOPES),
          "all_864_same"]}
    cur=0
    for shard,(w,a,h) in enumerate(zip(wjm["chunks"],ajm["shards"],hj["shards"],strict=True)):
        n=w["count"]
        if not (w["first_index"]==cur==a["first_index"]==h["index_first"] and h["count"]==n):
            raise RuntimeError("Original source same UTC row shards misaligned")
        pp=west/"chunks"/w["file"];aa=angles/"shards"/a["file"];hh=hd_join/"shards"/h["file"]
        if pp.stat().st_size!=n*64 or aa.stat().st_size!=n*136 or hh.stat().st_size!=n*4:
            raise RuntimeError("Original binary source record size drift")
        if verify_sha:
            for path,meta in ((pp,w),(aa,a),(hh,h)):
                if digest(path)!=meta["sha256"]:
                    raise RuntimeError("One of 108 frozen source shard SHA-256 differs")
        P=np.memmap(pp,dtype="<f8",mode="r",shape=(n,8))
        A=np.memmap(aa,dtype="<f8",mode="r",shape=(n,17))
        IDs=np.memmap(hh,dtype="<i4",mode="r",shape=(n,))
        R=np.empty((n,12),dtype=np.float64)
        for i in range(n):
            cx,_=swe.houses_ex(jd+(cur+i)/96.,lat,lon,b"R")
            R[i]=cx
        if np.max(np.abs((R[:,0]-A[:,0]+180)%360-180))>0.0002:
            raise RuntimeError("Site Ascendant differs from original source geometry")
        pre=P[0,:7] if shard==0 else partial.mot._load_mmap(west,wjm["chunks"][shard-1])[-1,:7]
        nex=P[-1,:7] if shard==len(wjm["chunks"])-1 else partial.mot._load_mmap(west,wjm["chunks"][shard+1])[0,:7]
        prevs=np.concatenate((np.asarray(pre,dtype=float)[None,:],P[:-1,:7]),axis=0)
        nexts=np.concatenate((P[1:,:7],np.asarray(nex,dtype=float)[None,:]),axis=0)
        speed=partial.mot.wrapped_speed(prevs,nexts)
        speed[:,2]=P[:,7]  # original exact Mercury signed source speed
        edge=np.zeros(n,dtype=bool)
        if shard==0:edge[0]=True
        if shard==len(wjm["chunks"])-1:edge[-1]=True
        scan_chunk(P,A,IDs,R=R,velocities=speed,edges=edge,counts=counts,HD=hd_bits)
        cur+=n
    if not verify_sha or cur!=N or counts["original_UTC_clock_samples"]!=N:
        raise RuntimeError("Full original source grid not SHA-verified")
    if (counts["HD_root_unknown"]!=125 or counts["near_sun_horizon_sect_unknown"]!=5049
        or counts["ptolemy_conditional_fourmode_common"]!=4553 or counts["ptolemy_HD_root_unknown"]!=0):
        raise RuntimeError("Original HD, sect and Ptolemy common baseline changed")
    for mode in MODES:
        for orb in ORBS:
            for scope in SCOPES:
                k="|".join((mode,orb,scope))
                for old_suffix,new_suffix in (
                  ("S2_zero_proceed_to_S3","S2_empty_go_to_later"),
                  ("S2_one_joined_planet","S2_sole"),
                  ("S2_multiple_joined_planets","S2_multi"),
                  ("S2_any","S2_any"),
                  ("S2_ptolemy_any","S2_ptolemy_any")):
                    if counts[k+"|"+new_suffix]!=earlier[k+"|"+old_suffix]:
                        raise RuntimeError("Previously frozen S2 source stage disagrees: "+k+" "+old_suffix)
                if counts[k+"|stable_all72_sole"]!=earlier[k+"|S2_one_joined_planet"]:
                    raise RuntimeError("Sole joining body must remain sole through strength variants")
                if counts[k+"|stable_all72_multi_strict"]>earlier[k+"|S2_multiple_joined_planets"]:
                    raise RuntimeError("Multi source candidates cannot be invented")
                if counts[k+"|stable_all72_any"]!=counts[k+"|stable_all72_sole"]+counts[k+"|stable_all72_multi_strict"]:
                    raise RuntimeError("Unique partial candidate stage conservation failed")
                for term in TERMS:
                    for pol in ESSENTIAL_POLICIES:
                        for t in STATIONS:
                            for house in HOUSES:
                                label="|".join((term,pol,house,f"station={t:.2f}"))
                                if (counts[k+"|"+label+"|conditional_candidate"]+
                                    counts[k+"|"+label+"|multi_unknown_strength"]+
                                    counts[k+"|S2_empty_go_to_later"]!=
                                    earlier[mode+"|S1_empty"]):
                                    raise RuntimeError("Each source S2 method must cover S1-empty population")
    return {
        "schema":"lilly_1647_CVII_original_S2_joined_candidate_partial_strength_864_models_full_century_v01",
        "status":"ORIGINAL_S2_SOURCE_QUALIFIED_864_PARTIAL_MODELS_NO_HISTORICAL_FINAL_MANNERS_RULER",
        "samples":N,"step_minutes":15,
        "UTC_horizon":[wj["utc_start_inclusive"],wj["utc_end_exclusive"]],
        "one_fixed_research_location":True,
        "source_original_p536":"Lilly 1647 first printing p536 joins Mercury or Moon only when S1 empty; multiple-planet and dual-contact conditions distinct",
        "source_original_p535_p536_frozen_page_SHA256":{"535":"49efe26a167fcdd6d0f1f08d3c7a69faaf87939b41cab02341ef6dc2500f4708","536":"4cdd11d5cf468e20f38fed7889e42f2e6298540e05f7f196c9b916e28bb57b24"},
        "source_original_p107_two_moiety_tables":{k:v.tolist() for k,v in ORBS.items()},
        "source_manners_first_stage_geometry":list(MODES),
        "source_second_stage_candidate_scope":list(SCOPES),
        "partial_strength_variants": {
          "terms":list(TERMS),
          "reception_peregrine":list(ESSENTIAL_POLICIES),
          "houses":list(HOUSES),
          "station_numerical_not_source_authored":[float(x) for x in STATIONS]},
        "original_source_SHA256_shards_rechecked":verify_sha,
        "source_manifest_SHA256":{"planet":digest(wm),"site":digest(am),"HD":digest(hd_join/"manifest.json")},
        "HD_audit":hdproof,
        "HD_structural_intervals":HD_STATE_COUNT,
        "HD_transition_margin_unassigned":125,
        "S2_eligibility_policy_count":s2.STAGES,
        "partial_strength_policies":PARTIAL_METHOD_COUNT,
        "all_eligibility_x_partial_strength_policy_count":SCENARIOS,
        "conditional_Ptolemy_fourmode_common":4553,
        "partial_source_score_method":"For multiple qualifying S2 bodies, strict lower own-body positive/negative essential+house+motion points > highest upper of every other qualifying S2 candidate; unknown near station contributes [-5,+4]. A sole joined S2 body provisional regardless of uncertain sect, subject to original text caveats.",
        "counts":dict(counts),
        "distinct_HD_intervals_with_cross_method_stable_S2_candidate":{key:int(x.sum()) for key,x in hd_bits.items()},
        "same_original_S2_source_cohorts_independently_reproduced":True,
        "original_all_stage_Lilly_manners_ruler_computed":False,
        "original_Ptolemy_III13_soul_governor_computed":False,
        "individual_personality_predictive_accuracy_established":False,
        "private_natal_or_interview_data_loaded":False,
    }


def main():
    p=argparse.ArgumentParser()
    for arg in ("west","angles","hd-cache","hd-join","out"):
        p.add_argument("--"+arg,required=True,type=Path)
    args=p.parse_args()
    if args.out.exists():raise FileExistsError("Preserve original source receipt, use new version")
    j=run(args.west,args.angles,args.hd_cache,args.hd_join)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(j,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":j["status"],"samples":j["samples"],
      "all_source_model_count":j["all_eligibility_x_partial_strength_policy_count"]},sort_keys=True))
if __name__=="__main__":main()
