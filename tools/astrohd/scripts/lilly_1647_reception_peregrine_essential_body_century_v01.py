#!/usr/bin/env python3
"""Original Lilly 1647 p112 and p115: natal essential debility & reciprocal-dignity witnesses.

This is an INCOMPLETE natal-body essential condition comparator; it is NOT
Lilly's chapter CVII final dignity-at-Mercury-and-Moon place algorithm.

1647 first printing p112 defines a planet as peregrine if it has NO essential
dignity at the degree it occupies. Reception is defined between TWO planets
signifying a matter, in each other's essential dignities, even without aspect.
P115 gives +5 house/dom mutual reception, +4 exaltation reception, -5
detriment, -4 fall, -5 peregrine. "In own house OR mutual reception" is ONE
dignity channel, not double 5+5. Geometrically reciprocal house/exaltation
is testable; whether both bodies actually qualify as matter-significators
and whether reception removes peregrine status are NOT specified by our
generic natal charts, so all additional policies are explicitly hypothetical.

Preserve three independent source printed term tables (Lilly 1647, Robbins
1940 Ptolemaic and Egyptian) and compare:
 A five_positive_only (earlier basic subset);
 B five_positive_plus_negative_intrinsic_peregrine (no reception);
 C A + -5 detriment/-4 fall + house/exalt potential reciprocal reception,
   where reception clears the -5 peregrine penalty;
 D same as C, but peregrine tests INTRINSIC essential dignity only,
   and possible reception does not clear that penalty.

These are separate source-conditioned mathematical candidates, not
historically selected governors or empirical personality predictions.
Full 3,506,400 sampled source-clock values, one fixed location, all original
planet/site/HD SHA source shards rechecked; previous 4,553 conditional
Ptolemy candidate count and 125 HD root-margin abstentions preserved.
No private natal source, respondent or interview input.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np
import swisseph as swe

import lilly_cvii_original_essential_dignity_final_fallback_century_v01 as src

N=3506400
HD_STATES=288908
SECT_EPS=src.SECT_UNCERTAIN_DEG
PLANETS=src.PLANETS
POLICIES=(
  "five_positive_only",
  "plus_detriment_fall_peregrine_no_reception",
  "plus_mutual_house_exalt_reception_clears_peregrine",
  "plus_mutual_house_exalt_reception_retains_intrinsic_peregrine"
)
SOURCE_EDITS="Original 1647 first printing pp112,115, p104 term table; two independent 1940 Loeb printed term editions"


def potential_receptions(longs):
    """Pure natal zodiac GEOMETRY, NOT a true significator designation."""
    x=np.asarray(longs,dtype=np.float64)
    if x.ndim!=2 or x.shape[1]!=7 or np.any(~np.isfinite(x)):
        raise ValueError("Seven aligned classical geocentric longitudes required")
    if np.any((x<0)|(x>=360)):raise ValueError("Normalized zodiac required")
    ruler=src.FOUR.pt3.ptolemy2.DOMICILE
    exalt=src.FOUR.pt3.ptolemy2.EXALTATION
    signs=np.floor(x/30).astype(np.int8)
    n=len(x)
    house=np.zeros((n,7),dtype=bool)
    exalted=np.zeros((n,7),dtype=bool)
    # A and B need to occupy each other's SAME kind of dignity. Keep
    # mixed-mode and mere one-way dispositorship OUT of this strict test.
    for i in range(7):
        for j in range(i+1,7):
            hi=(ruler[signs[:,i]]==j)&(ruler[signs[:,j]]==i)
            ei=(exalt[signs[:,i]]==j)&(exalt[signs[:,j]]==i)
            house[:,i]|=hi
            house[:,j]|=hi
            exalted[:,i]|=ei
            exalted[:,j]|=ei
    return house,exalted


def positive_intrinsic(longs,solar_alt,terms_scheme):
    """One independent natal body at OWN longitude; no mutual reception."""
    p=np.asarray(longs,dtype=np.float64)
    alt=np.asarray(solar_alt,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or alt.shape!=(len(p),) or np.any(~np.isfinite(alt)):
        raise ValueError("N aligned natal bodies and sect altitudes required")
    if np.any(~np.isfinite(p)) or np.any((p<0)|(p>=360)):
        raise ValueError("Classic planets must have finite normalized longitude")
    signs=np.floor(p/30).astype(np.int8)
    days=alt>SECT_EPS
    nights=alt < -SECT_EPS
    n=len(p)
    pos=np.zeros((n,7),dtype=np.int16)
    ruler=src.FOUR.pt3.ptolemy2.DOMICILE
    exalt=src.FOUR.pt3.ptolemy2.EXALTATION
    for k in range(7):
        z=signs[:,k]
        x=p[:,k]
        # No double-counting the same dignity channel.
        pos[:,k]+=(ruler[z]==k).astype(np.int16)*5
        pos[:,k]+=(exalt[z]==k).astype(np.int16)*4
        trip=np.where(days,src.TRIP_DAY[z],np.where(nights,src.TRIP_NIGHT[z],-1))
        pos[:,k]+=(trip==k).astype(np.int16)*3
        term=src._terms(x,terms_scheme)
        pos[:,k]+=(term==k).astype(np.int16)*2
        decan=np.floor((x-30.0*z)/10).astype(np.int8)
        if np.any((decan<0)|(decan>2)):raise RuntimeError("Invalid actual zodiac face")
        pos[:,k]+=(src.FACES[z,decan]==k).astype(np.int16)
    if np.any((pos<0)|(pos>15)):raise RuntimeError("Positive essential score out of five-mode bound")
    return pos


def debility_masks(longs,positive,receives_house,receives_exalt):
    """Natal original p115 detriment/fall; two separate peregrine readings."""
    p=np.asarray(longs,dtype=np.float64)
    pos=np.asarray(positive,dtype=np.int16)
    rh=np.asarray(receives_house,dtype=bool)
    re=np.asarray(receives_exalt,dtype=bool)
    if p.ndim!=2 or p.shape[1]!=7 or pos.shape!=p.shape or rh.shape!=p.shape or re.shape!=p.shape:
        raise ValueError("Aligned seven classical bodies and positive source channels required")
    signs=np.floor(p/30).astype(np.int8)
    ruler=src.FOUR.pt3.ptolemy2.DOMICILE
    exalt=src.FOUR.pt3.ptolemy2.EXALTATION
    detr=np.zeros(p.shape,dtype=bool)
    fall=np.zeros(p.shape,dtype=bool)
    for k in range(7):
        detr[:,k]=ruler[(signs[:,k]+6)%12]==k
        fall[:,k]=exalt[(signs[:,k]+6)%12]==k
    intrinsic=pos==0
    possible_reception=(rh|re)
    clears=intrinsic&~possible_reception
    return detr,fall,intrinsic,clears


def candidate_models(longs,solar_alt):
    """Four complete, transparent candidate policies for each term witness.

    A strict unique maximum is just a PARTIAL SCORE winner. It is not Lilly's
    actual significator or a prediction of behavior. Sect uncertain -> -1.
    """
    p=np.asarray(longs,dtype=np.float64)
    alt=np.asarray(solar_alt,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or alt.shape!=(len(p),):
        raise ValueError("Source dimensions changed")
    known=np.abs(alt)>SECT_EPS
    rh,re=potential_receptions(p)
    winners={}
    attrs={}
    per_scheme={}
    # Reception by either house or exaltation is only geometrically
    # possible, never an automatic actual natal matter-significator.
    signs=np.floor(p/30).astype(np.int8)
    dom=src.FOUR.pt3.ptolemy2.DOMICILE
    ex=src.FOUR.pt3.ptolemy2.EXALTATION
    for scheme in src.TERMS:
        pos=positive_intrinsic(p,alt,scheme)
        detr,fall,peregrine_intrinsic,peregrine_after=debility_masks(p,pos,rh,re)
        per_scheme[scheme]={'detr':detr,'fall':fall,
                           'per':peregrine_intrinsic,'cleared':peregrine_after}
        base_deb=pos-5*detr.astype(np.int16)-4*fall.astype(np.int16)
        # "Own house OR mutual reception by house" should be one channel.
        # Do not add 5 on top of the same planet's own domicile, idem exalt.
        addrh=rh&~(dom[signs]==np.arange(7)[None,:])
        addre=re&~(ex[signs]==np.arange(7)[None,:])
        receipt_delta=5*addrh.astype(np.int16)+4*addre.astype(np.int16)
        values=(
            pos,
            base_deb-5*peregrine_intrinsic.astype(np.int16),
            base_deb+receipt_delta-5*peregrine_after.astype(np.int16),
            base_deb+receipt_delta-5*peregrine_intrinsic.astype(np.int16)
        )
        for policy,points in zip(POLICIES,values):
            top=points.max(axis=1)
            unique=(points==top[:,None]).sum(axis=1)==1
            chosen=np.argmax(points,axis=1).astype(np.int8)
            chosen[~unique|~known]=-1
            tag=scheme+"|"+policy
            winners[tag]=chosen
            attrs[tag]={
              "strict_unique":unique&known,
              "tied_or_unknown":~(unique&known),
              "sect_undetermined":~known,
              "highest_score_negative":unique&known&(top<0),
              "highest_score_zero":unique&known&(top==0),
            }
    stack=np.stack(tuple(winners.values()),axis=0)
    all_unique=(stack>=0).all(axis=0)
    full_agreement=all_unique&(stack==stack[0]).all(axis=0)
    return winners,attrs,np.where(full_agreement,stack[0],-1),{
      "potential_house_reception_planet_occurrences":rh.sum(axis=0),
      "potential_exaltation_reception_planet_occurrences":re.sum(axis=0),
      "all_sect_known":known,"per_scheme":per_scheme
    }


def run(west,angles,hd_cache,hd_join,verify_sha=True):
    if swe.version!="2.10.03":raise RuntimeError("Swiss version changed")
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    wj=json.loads(wp.read_bytes());wjm=json.loads(wm.read_bytes())
    aj=json.loads(ap.read_bytes());ajm=json.loads(am.read_bytes())
    n=src.PRIOR.base.reg.initial.check_manifest(wj,wjm,aj,ajm)
    if n!=N:raise RuntimeError("Frozen 3.5m century denominator drift")
    if wjm["plan_sha256"]!=src.PRIOR.base.reg.initial.source_hash(wp) or ajm["plan_sha256"]!=src.PRIOR.base.reg.initial.source_hash(ap):
        raise RuntimeError("Original input plan changed")
    hproof=src.PRIOR.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    hj=json.loads((hd_join/"manifest.json").read_bytes())
    if hj["total_utc_grid_samples"]!=N or hj["total_hd_structural_intervals"]!=HD_STATES or hj["unresolved_near_boundary_samples"]!=125:
        raise RuntimeError("Original HD clock/state changed")
    counts=Counter()
    consensus_HD=np.zeros(HD_STATES,dtype=bool)
    consensus_Ptolemy_HD=np.zeros(HD_STATES,dtype=bool)
    first=0
    for w,a,h in zip(wjm["chunks"],ajm["shards"],hj["shards"],strict=True):
        k=w["count"]
        if first!=w["first_index"] or first!=a["first_index"] or first!=h["index_first"] or h["count"]!=k:
            raise RuntimeError("Source alignment drift")
        bp=west/"chunks"/w["file"];ba=angles/"shards"/a["file"];bh=hd_join/"shards"/h["file"]
        if bp.stat().st_size!=k*64 or ba.stat().st_size!=k*136 or bh.stat().st_size!=k*4:
            raise RuntimeError("Original source binary length drift")
        if verify_sha and any(src.PRIOR.base.reg.initial.source_hash(p)!=meta["sha256"] for p,meta in ((bp,w),(ba,a),(bh,h))):
            raise RuntimeError("Original source SHAs altered")
        P=np.memmap(bp,dtype="<f8",shape=(k,8),mode="r")
        A=np.memmap(ba,dtype="<f8",shape=(k,17),mode="r")
        IDs=np.memmap(bh,dtype="<i4",shape=(k,),mode="r")
        alt=A[:,4]
        winn,attrs,consensus,recv=candidate_models(P[:,:7],alt)
        sector=np.abs(alt)>SECT_EPS
        knownHD=IDs>=0
        counts["clock_samples"]+=k
        counts["sect_uncertain_samples"]+=int((~sector).sum())
        counts["HD_transition_samples_abstained"]+=int((~knownHD).sum())
        cond=src.PRIOR.ptolemy_source.conditional_all_four_common_leader(P,alt)
        Pgood=cond>=0
        counts["prior_conditional_ptolemy_4mode_common"]+=int(Pgood.sum())
        counts["ptolemy_conditional_HD_unknown"]+=int((Pgood&~knownHD).sum())
        known=consensus>=0
        counts["12_policy_strict_same_unique_planet"]+=int(known.sum())
        counts["12_policy_common_in_ptolemy_conditional"]+=int((known&Pgood).sum())
        counts["12_policy_same_planet_as_conditional_ptolemy"]+=int((known&(consensus==cond)).sum())
        counts["12_policy_competing_with_conditional_ptolemy"]+=int((known&Pgood&(consensus!=cond)).sum())
        if np.any(known&knownHD):
            consensus_HD[IDs[known&knownHD]]=True
        if np.any(known&Pgood&knownHD):
            consensus_Ptolemy_HD[IDs[known&Pgood&knownHD]]=True
        for idx,name in enumerate(PLANETS):
            counts["potential_mutual_domicile_reception_"+name]+=int(recv["potential_house_reception_planet_occurrences"][idx])
            counts["potential_mutual_exaltation_reception_"+name]+=int(recv["potential_exaltation_reception_planet_occurrences"][idx])
        for scheme in src.TERMS:
            details=recv["per_scheme"][scheme]
            detr,fall,per,cleared=(details[key] for key in ("detr","fall","per","cleared"))
            for idx,name in enumerate(PLANETS):
                base=scheme+"|"+name
                counts[base+"|detriment"]+=int((detr[:,idx]&sector).sum())
                counts[base+"|fall"]+=int((fall[:,idx]&sector).sum())
                counts[base+"|intrinsically_peregrine"]+=int((per[:,idx]&sector).sum())
                counts[base+"|peregrine_even_after_geometric_reception"]+=int((cleared[:,idx]&sector).sum())
            simple=winn[scheme+"|"+POLICIES[0]]
            withneg=winn[scheme+"|"+POLICIES[1]]
            withrec=winn[scheme+"|"+POLICIES[2]]
            paired=(simple>=0)&(withneg>=0)
            counts[scheme+"|positive_to_neg_both_unique"]+=int(paired.sum())
            counts[scheme+"|positive_to_neg_changed"]+=int((paired&(simple!=withneg)).sum())
            paired2=(withneg>=0)&(withrec>=0)
            counts[scheme+"|neg_to_reception_both_unique"]+=int(paired2.sum())
            counts[scheme+"|neg_to_reception_changed"]+=int((paired2&(withneg!=withrec)).sum())
        for tag,chosen in winn.items():
            counts[tag+"|strict_unique"]+=int((chosen>=0).sum())
            counts[tag+"|tie_or_sect_unknown"]+=int((chosen<0).sum())
            counts[tag+"|same_as_conditional_ptolemy_candidate"]+=int(((chosen>=0)&(chosen==cond)).sum())
            for i,name in enumerate(PLANETS):
                counts[tag+"|leader_"+name]+=int((chosen==i).sum())
        first+=k
    if not verify_sha or first!=N or counts["clock_samples"]!=N or counts["HD_transition_samples_abstained"]!=125:
        raise RuntimeError("Full source century not source-verified")
    if counts["prior_conditional_ptolemy_4mode_common"]!=4553 or counts["ptolemy_conditional_HD_unknown"]!=0:
        raise RuntimeError("Frozen Ptolemy/HD cohort changed")
    if counts["12_policy_strict_same_unique_planet"]>N-counts["sect_uncertain_samples"]:
        raise RuntimeError("Consensus cannot include ambiguous sect")
    for tag in (sch+"|"+policy for sch in src.TERMS for policy in POLICIES):
        if counts[tag+"|strict_unique"]+counts[tag+"|tie_or_sect_unknown"]!=N:
            raise RuntimeError("All policy/sect winners must partition same frozen time grid")
    for sch in src.TERMS:
        for name in PLANETS:
            if counts[sch+"|"+name+"|peregrine_even_after_geometric_reception"]>counts[sch+"|"+name+"|intrinsically_peregrine"]:
                raise RuntimeError("Peregrine-clearability cannot exceed intrinsic missing dignity")
    return {
      "schema":"lilly_1647_original_p112_reception_peregrine_p115_essential_debility_full_century_v01",
      "status":"SOURCE_CONDITIONED_NATAL_PLANET_ESSENTIAL_COMPONENTS_ONLY_NO_HISTORIC_RULER",
      "horizon_UTC":[wj["utc_start_inclusive"],wj["utc_end_exclusive"]],
      "samples":N,
      "step_minutes":15,
      "fixed_research_location_only":True,
      "original_shard_108_sha256_verified":True,
      "original_source_manifest_SHA256":{
          "planet":src.PRIOR.base.reg.initial.source_hash(wm),
          "angles":src.PRIOR.base.reg.initial.source_hash(am),
          "HD":src.PRIOR.hd_source.hdverify.digest(hd_join/"manifest.json")},
      "HD_source_audit":hproof,
      "HD_intervals":HD_STATES,
      "historical_sources":SOURCE_EDITS,
      "historical_term_variants":list(src.TERMS),
      "geometric_policy_variants":list(POLICIES),
      "short_source_original_p112":"mutual reception and peregrine defined in terms of matter-significators and absence of self essential dignity",
      "mutual_reception_requires_actual_significator_in_the_historical_text":True,
      "candidate_mutual_receptions_are_geometry_only":True,
      "peregrine_reception_clears_penalty_status":"AMBIGUOUS_HISTORICALLY_PRESERVE_BOTH",
      "separate_place_based_Lilly_CVII_final_stage_not_replaced":True,
      "counts":dict(counts),
      "HD_intervals_with_strict_12_policy_same_candidate":int(consensus_HD.sum()),
      "HD_intervals_with_12_policy_same_candidate_in_conditional_Ptolemy_cohort":int(consensus_Ptolemy_HD.sum()),
      "complete_1647_essential_and_accidental_strength":False,
      "actual_Lilly_manners_significator_selected":False,
      "actual_Ptolemy_III13_governor_selected":False,
      "human_predictive_validation":False,
      "private_birth_interview_data_loaded":False,
    }


def main():
    p=argparse.ArgumentParser()
    for arg in ("west","angles","hd-cache","hd-join","out"):
        p.add_argument("--"+arg,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError("Immutable original-source computation must never overwrite earlier source receipt")
    z=run(a.west,a.angles,a.hd_cache,a.hd_join)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(z,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":z["status"],"samples":z["samples"],
                      "strict_all_variant_witness":z["counts"]["12_policy_strict_same_unique_planet"]},sort_keys=True))

if __name__=="__main__":main()
