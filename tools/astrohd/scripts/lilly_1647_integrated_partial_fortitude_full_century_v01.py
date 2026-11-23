#!/usr/bin/env python3
"""Lilly 1647 source-scoped PARTIAL natal-body essential+house+motion comparison.

A real original finite 3,506,400 UTC row scan at the one existing fixed
research site; not a full Lilly CVII "manners" or Ptolemy III.13 governor,
and not an independently validated human behavioral model.

The original 1647 printed p104/p112/p115 direct source witnesses yield:
  3 terms tables (Lilly1647, Loeb Ptolemaic, Loeb Egyptian);
  4 separate possible intrinsic debility/reception conventions (original
    natal essential code, including potential strict reciprocal reception);
  2 HOUSES (Regiomontanus, cached Placidus);
  3 source-UNSPECIFIED engineering station uncertainty thresholds
    (0.01,0.02,0.05 degree/day) for 4-body numerical finite velocities.

12 natal essential source policies x two house methods x three uncertainty
ranges = 72 scored historical/mechanical scenarios. These combine independent
original table POINT components to compare *source sensitivity*, but do NOT
license a unique historical ruler: the topic's valid significators, other
receptions, aspects, fixed stars, solar condition, planetary visibility,
'fortitude' semantics, and all CVII stages remain historically open.

Uncertain velocity status -> true bounded score interval [-5,+4], not a
made-up midpoint. A candidate is strict unique ONLY if its score lower bound
exceeds the UPPER bounds of every other classical planet. All sect-uncertain
timestamps abstain. Absence of original source-unique cross-variant candidate
is unknown, NOT proof of bad natal fit.

Identical UTC source manifest and 36 planet+36 site+36 HD index binary shard
SHA checks; independent HD cache 288,908 interval proofs; 125 HD near-root
IDs unassigned. 1,620 prior independent Swiss source-speed controls were
performed in the frozen motion sub-study, which this code reconciles by
exact motion counts before publishing. No private birth or case data input.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np
import swisseph as swe

import lilly_1647_reception_peregrine_essential_body_century_v01 as es
import lilly_1647_house_accidental_fortitude_century_v01 as hs
import lilly_1647_source_direct_retro_motion_century_v01 as mot

N=3506400
HD_STATE_COUNT=288908
HOUSE_NAMES=("Regiomontanus","Placidus")
TERMS=tuple(es.src.TERMS)
ESSENTIAL_POLICIES=es.POLICIES
STATIONS=mot.THRESHOLDS
MOVING=mot.MOVING
PLANETS=es.PLANETS
NUM_SCENARIOS=len(TERMS)*len(ESSENTIAL_POLICIES)*2*len(STATIONS)


def essential_points(longs,alt,scheme):
    """Reusable original source code, no self-picked numeric trait factors."""
    p=np.asarray(longs,dtype=np.float64)
    alt=np.asarray(alt,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or alt.shape!=(len(p),):
        raise ValueError("Seven classical natal longitudes and aligned altitude required")
    z=es.positive_intrinsic(p,alt,scheme)
    rec_dom,rec_ex=es.potential_receptions(p)
    detr,fall,per,notcleared=es.debility_masks(p,z,rec_dom,rec_ex)
    # Original p115 uses 'own house OR mutual reception', not twice 5/4.
    signs=np.floor(p/30).astype(np.int8)
    dom=es.src.FOUR.pt3.ptolemy2.DOMICILE
    exalt=es.src.FOUR.pt3.ptolemy2.EXALTATION
    bodyindex=np.arange(7)
    possible_extra_house=rec_dom&~(dom[signs]==bodyindex[None,:])
    possible_extra_exalt=rec_ex&~(exalt[signs]==bodyindex[None,:])
    positive_extras=5*possible_extra_house.astype(np.int16)+4*possible_extra_exalt.astype(np.int16)
    deb=z-5*detr.astype(np.int16)-4*fall.astype(np.int16)
    result=(
        z,
        deb-5*per.astype(np.int16),
        deb+positive_extras-5*notcleared.astype(np.int16),
        deb+positive_extras-5*per.astype(np.int16)
    )
    for x in result:
        if x.shape!=p.shape or x.dtype!=np.int16:
            raise RuntimeError("Numeric source candidate score type or shape changed")
    return dict(zip(ESSENTIAL_POLICIES,result,strict=True))


def signed_motion_bounds(speed,eps,absolute_edges):
    """Motion source p115: direct +4 / retro -5 / uncertain [-5,+4]."""
    s=np.asarray(speed,dtype=np.float64)
    edges=np.asarray(absolute_edges,dtype=bool)
    if s.ndim!=2 or s.shape[1]!=7 or edges.shape!=(len(s),):
        raise ValueError("Motion velocity source and exact UTC boundaries not aligned")
    low=np.zeros(s.shape,dtype=np.int16)
    high=np.zeros(s.shape,dtype=np.int16)
    for k in MOVING:
        d,r,u=mot.status(s[:,k],eps,edges)
        low[:,k]=np.where(d,4,-5).astype(np.int16)
        high[:,k]=np.where(r,-5,4).astype(np.int16)
        if not np.all((d|r|u)):raise RuntimeError("Motion status partition missing rows")
    return low,high


def interval_unique_winner(low,high,sect_known):
    """A winner must beat EVERY competitor even at their score upper bound."""
    l=np.asarray(low,dtype=np.int16)
    h=np.asarray(high,dtype=np.int16)
    known=np.asarray(sect_known,dtype=bool)
    if l.ndim!=2 or l.shape[1]!=7 or h.shape!=l.shape or known.shape!=(len(l),):
        raise ValueError("Seven-body comparable scores and sect required")
    if np.any(l>h):raise ValueError("Lower strength interval exceeds upper")
    n=len(l)
    choice=np.argmax(l,axis=1).astype(np.int8)
    maxima=h.copy()
    maxima[np.arange(n),choice]=-32767
    strong=(l[np.arange(n),choice]>np.max(maxima,axis=1))&known
    choice[~strong]=-1
    return choice


def process_chunk(P,A,IDs,*,R,velocities,edges,totals,HD):
    """Compute all scenarios only on fixed original SHA-bound UTC sample rows."""
    n=len(P)
    if P.shape!=(n,8) or A.shape!=(n,17) or IDs.shape!=(n,) or R.shape!=(n,12) or velocities.shape!=(n,7):
        raise ValueError("Source input, site and same UTC arrays are not aligned")
    all_known=np.abs(A[:,4])>es.SECT_EPS
    any_HD=IDs>=0
    prior_pt=es.src.PRIOR.ptolemy_source.conditional_all_four_common_leader(P,A[:,4])
    ptolemy=prior_pt>=0
    house_maps={
        "Regiomontanus":hs.house_ids(P[:,:7],R),
        "Placidus":hs.house_ids(P[:,:7],A[:,5:17])
    }
    house_scores={k:hs.HOUSE_POINTS[v].astype(np.int16) for k,v in house_maps.items()}
    totals["total_UTC_clock"]+=n
    totals["HD_transition_unknown"]+=int((~any_HD).sum())
    totals["near_horizon_sect_abstentions"]+=int((~all_known).sum())
    totals["conditional_ptolemy_4mode_common"]+=int(ptolemy.sum())
    totals["conditional_ptolemy_HD_unknown"]+=int((ptolemy&~any_HD).sum())
    totals["any_seven_body_house_assignment_differs"]+=int((house_maps["Regiomontanus"]!=house_maps["Placidus"]).any(axis=1).sum())
    check=np.full(n,-2,dtype=np.int8)
    compatible=np.ones(n,dtype=bool)
    all_consensus_count=0
    movement={t:signed_motion_bounds(velocities,t,edges) for t in STATIONS}
    for term in TERMS:
        essential=essential_points(P[:,:7],A[:,4],term)
        for policy in ESSENTIAL_POLICIES:
            body=essential[policy]
            for t in STATIONS:
                ml,mh=movement[t]
                across={}
                for place in HOUSE_NAMES:
                    group="|".join((term,policy,place,f"station={t:.2f}"))
                    low=body+house_scores[place]+ml
                    high=body+house_scores[place]+mh
                    chosen=interval_unique_winner(low,high,all_known)
                    eligible=chosen>=0
                    totals[group+"|strict_unique"]+=int(eligible.sum())
                    totals[group+"|uncertain_or_tied"]+=int((~eligible).sum())
                    totals[group+"|ptolemy_conditional_unique"]+=int((eligible&ptolemy).sum())
                    totals[group+"|same_as_ptolemy_conditional_body"]+=int((eligible&(chosen==prior_pt)).sum())
                    across[place]=chosen
                    compatible&=eligible
                    check=np.where(check==-2,chosen,check)
                    compatible&=(check==chosen)
                    all_consensus_count+=1
                reg=across["Regiomontanus"]
                plac=across["Placidus"]
                both=(reg>=0)&(plac>=0)
                pref="|".join((term,policy,f"station={t:.2f}"))
                totals[pref+"|both_house_systems_unique"]+=int(both.sum())
                totals[pref+"|same_unique_between_houses"]+=int((both&(reg==plac)).sum())
                totals[pref+"|different_unique_between_houses"]+=int((both&(reg!=plac)).sum())
    if all_consensus_count!=NUM_SCENARIOS:
        raise RuntimeError("Full comparison universe not examined")
    stable=compatible&(check>=0)
    totals["cross_72_source_method_same_unique_partial_winner"]+=int(stable.sum())
    totals["cross_72_same_unique_and_conditional_ptolemy"]+=int((stable&ptolemy).sum())
    totals["cross_72_strict_same_planet_as_conditional_ptolemy"]+=int((stable&(check==prior_pt)).sum())
    totals["cross_72_different_planet_from_conditional_ptolemy"]+=int((stable&ptolemy&(check!=prior_pt)).sum())
    if np.any(stable&any_HD):
        HD["same_unique_partial_source"] [IDs[stable&any_HD]]=True
    if np.any(stable&ptolemy&any_HD):
        HD["same_unique_partial_and_ptolemy"] [IDs[stable&ptolemy&any_HD]]=True


def run(west,angles,hd_cache,hd_join,verify_shards=True):
    if swe.version!="2.10.03":raise RuntimeError("Source Swiss version altered")
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    wj=json.loads(wp.read_bytes());wjm=json.loads(wm.read_bytes())
    aj=json.loads(ap.read_bytes());ajm=json.loads(am.read_bytes())
    n=es.src.PRIOR.base.reg.initial.check_manifest(wj,wjm,aj,ajm)
    if n!=N or wj["step_minutes"]!=15:raise RuntimeError("Source century denominator altered")
    hashit=es.src.PRIOR.base.reg.initial.source_hash
    if wjm["plan_sha256"]!=hashit(wp) or ajm["plan_sha256"]!=hashit(ap):
        raise RuntimeError("Source plan identity drift")
    proof=es.src.PRIOR.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    hj=json.loads((hd_join/"manifest.json").read_bytes())
    if hj["total_utc_grid_samples"]!=n or hj["total_hd_structural_intervals"]!=HD_STATE_COUNT or hj["unresolved_near_boundary_samples"]!=125:
        raise RuntimeError("HD structural source or UTC grid changed")
    # Prior independently executed original house/motion full century source
    # audits are immutable receipt checks, not fabricated hosted CI passes.
    original_house=json.loads((Path(__file__).resolve().parents[1]/"reference/research/lilly_1647_house_accidental_fortitude_full_century_public_v01.json").read_bytes())
    original_motion=json.loads((Path(__file__).resolve().parents[1]/"reference/research/lilly_1647_direct_retrograde_full_century_public_v01.json").read_bytes())
    M=original_motion["counts"];H=original_house["mechanical_counts"]
    jd=es.src.PRIOR.base.reg.julian_from_utc(wj["utc_start_inclusive"])
    lat=float(aj["latitude"]);lon=float(aj["longitude"])
    totals=Counter()
    HD={"same_unique_partial_source":np.zeros(HD_STATE_COUNT,dtype=bool),
        "same_unique_partial_and_ptolemy":np.zeros(HD_STATE_COUNT,dtype=bool)}
    first=0
    for shard,(w,a,h) in enumerate(zip(wjm["chunks"],ajm["shards"],hj["shards"],strict=True)):
        k=w["count"]
        if first!=w["first_index"] or first!=a["first_index"] or first!=h["index_first"] or h["count"]!=k:
            raise RuntimeError("Same-UTC source shard alignment drift")
        bp=west/"chunks"/w["file"];ba=angles/"shards"/a["file"];bh=hd_join/"shards"/h["file"]
        if bp.stat().st_size!=k*64 or ba.stat().st_size!=k*136 or bh.stat().st_size!=k*4:
            raise RuntimeError("Original source binary size changed")
        if verify_shards and (hashit(bp)!=w["sha256"] or hashit(ba)!=a["sha256"] or hashit(bh)!=h["sha256"]):
            raise RuntimeError("Original source SHA-256 differs from frozen manifest")
        P=np.memmap(bp,dtype="<f8",mode="r",shape=(k,8))
        A=np.memmap(ba,dtype="<f8",mode="r",shape=(k,17))
        IDs=np.memmap(bh,dtype="<i4",mode="r",shape=(k,))
        R=np.empty((k,12),dtype=np.float64)
        for i in range(k):
            cu,arms=swe.houses_ex(jd+(first+i)/96.,lat,lon,b"R")
            R[i]=cu
        if np.max(np.abs((R[:,0]-A[:,0]+180.)%360.-180.))>0.0002:
            raise RuntimeError("Original fixed-location ASC drift")
        # Frozen prior original source motion uses both absolute endpoints
        # as unknown across Mercury and other moving classical bodies.
        before=P[0,:7] if shard==0 else mot._load_mmap(west,wjm["chunks"][shard-1])[-1,:7]
        after=P[-1,:7] if shard==len(wjm["chunks"])-1 else mot._load_mmap(west,wjm["chunks"][shard+1])[0,:7]
        previous=np.concatenate((np.asarray(before,dtype=float)[None,:],P[:-1,:7]),axis=0)
        following=np.concatenate((P[1:,:7],np.asarray(after,dtype=float)[None,:]),axis=0)
        v=mot.wrapped_speed(previous,following)
        v[:,2]=P[:,7] # original source actual Mercury geocentric speed
        edge=np.zeros(k,dtype=bool)
        if shard==0:edge[0]=True
        if shard==len(wjm["chunks"])-1:edge[-1]=True
        for idx in mot.MOVING:
            for t in STATIONS:
                direct,retro,unknown=mot.status(v[:,idx],t,edge)
                label=mot.PLANET_NAMES[idx]+f"|threshold={t:.2f}|"
                for state,mask in (("direct",direct),("retrograde",retro),("unknown",unknown)):
                    totals["source_motion_"+label+state]+=int(mask.sum())
        process_chunk(P,A,IDs,R=R,velocities=v,edges=edge,totals=totals,HD=HD)
        first+=k
    if not verify_shards:raise RuntimeError("Source check required for public output")
    if totals["total_UTC_clock"]!=N or totals["HD_transition_unknown"]!=125 or totals["conditional_ptolemy_4mode_common"]!=4553 or totals["conditional_ptolemy_HD_unknown"]!=0:
        raise RuntimeError("Prior exact UTC/HD/Ptolemy source population drift")
    if totals["any_seven_body_house_assignment_differs"]!=H["any_traditional_planet_differs_between_12house_systems"]:
        raise RuntimeError("Original house source result does not reproduce")
    if totals["near_horizon_sect_abstentions"]!=5049:raise RuntimeError("Frozen original sect limit count shifted")
    for k in mot.MOVING:
        for t in STATIONS:
            label=mot.PLANET_NAMES[k]+f"|threshold={t:.2f}|"
            for state in ("direct","retrograde","unknown"):
                if totals["source_motion_"+label+state]!=M[label+state]:
                    raise RuntimeError("Frozen original motion source mismatch "+label+state)
    for term in TERMS:
        for ep in ESSENTIAL_POLICIES:
            for t in STATIONS:
                pref="|".join((term,ep,f"station={t:.2f}"))
                if (totals[pref+"|both_house_systems_unique"]!=totals[pref+"|same_unique_between_houses"]+
                    totals[pref+"|different_unique_between_houses"]):
                    raise RuntimeError("House-only comparative partial source partition broken")
                for place in HOUSE_NAMES:
                    group="|".join((term,ep,place,f"station={t:.2f}"))
                    if totals[group+"|strict_unique"]+totals[group+"|uncertain_or_tied"]!=N:
                        raise RuntimeError("One partial source model not scored over entire UTC population")
    return {
      "schema":"lilly_1647_integrated_essential_house_motion_partial_source_century_v01",
      "status":"ALL_72_SOURCE_CONDITIONAL_MODELS_PARTIAL_ASTRO_PLANET_STRENGTH_NOT_MANNERS_RULER",
      "original_source":"Lilly Christian Astrology 1647 pp104,112,115; three printed terms traditions independent",
      "source_horizon":[wj["utc_start_inclusive"],wj["utc_end_exclusive"]],
      "samples":N,"step_minutes":15,"one_fixed_research_location":True,
      "source_SHA256_shards_verified":True,
      "source_HD_audit":proof,
      "HD_structural_interval_count":HD_STATE_COUNT,
      "sources":{"west_manifest":hashit(wm),"angle_manifest":hashit(am),
                 "HD_join_manifest":hashit(hd_join/"manifest.json")},
      "all_model_sensitivity_variants":{"printed_terms":list(TERMS),"reception_peregrine":list(ESSENTIAL_POLICIES),
        "house":list(HOUSE_NAMES),"station_deg_per_day":list(STATIONS)},
      "source_stated_essential_house_motion_component_weights":True,
      "historic_source_authorized_unique_total_or_manners_ruler":False,
      "station_thresholds_historically_specified":False,
      "reception_actual_significator_condition_verified":False,
      "unmodeled_original_point_conditions":["all other benefic/malefic aspects","Sun orientation/visibility",
        "swift/slow motion source threshold","nodes","fixed stars","besieging",
        "full Lilly CVII stage eligibility and strength","Ptolemy III13 fifth phase/aspect testimony"],
      "experimental_source_combination_model_count":NUM_SCENARIOS,
      "numerical_candidate_strictness":"lower bound of winner greater than ALL other upper bounds under known source policy; near station ranges [-5,+4] not forced into one state; no human behavior assigned",
      "counts":dict(totals),
      "HD_distinct_states_with_strict_all_72_agreement":int(HD["same_unique_partial_source"].sum()),
      "HD_distinct_states_with_strict_72_agreement_and_conditional_ptolemy":int(HD["same_unique_partial_and_ptolemy"].sum()),
      "not_independently_validated_human_personality":True,
      "private_natal_interview_or_personal_criterion_used":False
    }


def main():
    ap=argparse.ArgumentParser()
    for key in ("west","angles","hd-cache","hd-join","out"):
        ap.add_argument("--"+key,type=Path,required=True)
    args=ap.parse_args()
    if args.out.exists():raise FileExistsError("Do not replace an original source-bound century result")
    result=run(args.west,args.angles,args.hd_cache,args.hd_join)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"samples":result["samples"],
      "all_source_variant_agreement":result["counts"]["cross_72_source_method_same_unique_partial_winner"]},sort_keys=True))
if __name__=="__main__":main()
