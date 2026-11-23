#!/usr/bin/env python3
"""Full ORDERED source-conditioned Lilly CVII 1647 manners-stage COVERAGE.

End-to-end S1, S2, S3, SX, SY, S4, S5 at every original frozen
quarter-hour UTC sample, 1926-11-19..2026-11-19 exclusive. Original
first printing pp535-536, p106 partile/p104 essential rights, original
printed p107 moiety sensitivity, all prior source variant registers.
Not a completed historical manners ruler; not human prediction.

3 initial S1 geometry ×2 original p107 moiety envelopes ×2 S2 inclusion
×2 S3 dispositing aspect ×2 all-other aspect ×2 S4 partile policies
= 96 different source-condition stage paths. S5 has 3 historically
printed term schemes ×2 explicitly RESEARCHER-DEFINED combine-two-place
scores = 6 source-sensitive last-stage candidate tests.

This program does NOT choose strength leaders among multiple S1/S2 primary
participants, does NOT treat an S4 geometric partile as historically
'forcible', and does NOT invent a ruler for self-dispositor SY or
another-aspector-without-dispositor SX. A unique S1 or S2 primary
occupant, the historically source-conditional S3 ASC domicile ruler,
or SIX-way consistent positive-only S5 place-score candidate is a
PROVISIONAL single-primary candidate; source p535 still allows other
dignity-bearing participants, and complete planetary fortitude remains
missing. All source unknowns are actual statuses, never negative
personality predictions.

Unlike isolated previous S1/S2/S3/S4/S5 source census artifacts, this
executes ONE STRICT stage-ordered per-UTC candidate classification across
ALL source alternatives, computes same-personal-planet candidate IDs ONLY
for source-limited single-primary paths, cross-method robustness and HD
intervals, with exact 96 earlier frozen S4/S5 stage-count reconciliation.

All 3,506,400 original UTC rows, 36 planet+36 site+36 HD binary SHA
sources checked individually, 288,908 HD intervals, 125 HD boundary
unknowns, conditional Ptolemy 4,553 common 4-mode subset frozen.
No private natal, interviews, response data or personal chart scores.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
import swisseph as swe

import lilly_cvii_s4_s5_partile_essential_genuine_later_century_v01 as old

N=3506400
HD_TOTAL=288908
MODES=old.MODES
ORBS=old.ORBS
JOINS=old.JOINS
BEHOLDS=old.BEHOLDS
CONTACTS=old.CONTACTS
PARTILES=old.PARTILES
STAGES=old.S4_S5_METHODS
PLANETS=old.PLANETS

# Codes are invented status labels, NOT actual authored Lilly numbers.
CODES={
 "S1_one_primary":1,
 "S1_multiple_primaries":2,
 "S2_one_joined":3,
 "S2_multiple_joined":4,
 "S3_asc_lord":5,
 "SY_self_dispositor_source_unknown":6,
 "SX_other_aspector_no_dispositor_source_unknown":7,
 "S4_partile_possible_one_force_unknown":8,
 "S4_partile_possible_multiple_force_unknown":9,
 "S5_positive_place_same_unique_six_models":10,
 "S5_positive_place_tied_or_unknown":11
}
LABELS={code:name for name,code in CODES.items()}
PROVISIONAL_SINGLE={1,3,5,10}
NOT_FULL_HISTORICAL_STRENGTH={2,4,6,7,8,9,11}
LATER_LABELS={8,9,10,11}


def stage_status(first_eligible,second_eligible,third_stage,partile_eligible,sex_five_consensus,asc_lord):
    """Classify one original 1647 chronological S1..S5 source alternative."""
    f=np.asarray(first_eligible,dtype=bool)
    j=np.asarray(second_eligible,dtype=bool)
    part=np.asarray(partile_eligible,dtype=bool)
    stage=third_stage
    n=len(f)
    if (f.shape!=(n,7) or j.shape!=(n,7) or part.shape!=(n,7)
        or np.asarray(sex_five_consensus).shape!=(n,)
        or np.asarray(asc_lord).shape!=(n,)):
        raise ValueError("Same-clock traditional seven-body source eligibility required")
    masksets={name:np.asarray(stage[name],dtype=bool) for name in ("S1","S2","S3","SY","SX","LATER")}
    if any(z.shape!=(n,) for z in masksets.values()):
        raise ValueError("Source third stage not aligned to original time")
    fc=f.sum(axis=1);jc=j.sum(axis=1);pc=part.sum(axis=1)
    if not np.array_equal(fc>0,masksets["S1"]):
        raise RuntimeError("Chronological S1 candidates differ from source stage")
    if not np.array_equal(masksets["S2"],(fc==0)&(jc>0)):
        raise RuntimeError("Chronological S2 candidates differ from source stage")
    out=np.zeros(n,dtype=np.int8)
    who=np.full(n,-1,dtype=np.int8)
    rows=np.arange(n)
    one=masksets["S1"]&(fc==1)
    many=masksets["S1"]&(fc>1)
    out[one]=CODES["S1_one_primary"]
    out[many]=CODES["S1_multiple_primaries"]
    who[one]=np.argmax(f[one],axis=1).astype(np.int8)
    one=masksets["S2"]&(jc==1)
    many=masksets["S2"]&(jc>1)
    out[one]=CODES["S2_one_joined"]
    out[many]=CODES["S2_multiple_joined"]
    who[one]=np.argmax(j[one],axis=1).astype(np.int8)
    out[masksets["S3"]]=CODES["S3_asc_lord"]
    who[masksets["S3"]]=np.asarray(asc_lord,dtype=np.int8)[masksets["S3"]]
    out[masksets["SY"]]=CODES["SY_self_dispositor_source_unknown"]
    out[masksets["SX"]]=CODES["SX_other_aspector_no_dispositor_source_unknown"]
    later=masksets["LATER"]
    one=later&(pc==1)
    many=later&(pc>1)
    out[one]=CODES["S4_partile_possible_one_force_unknown"]
    out[many]=CODES["S4_partile_possible_multiple_force_unknown"]
    part_none=later&(pc==0)
    positive=part_none&(np.asarray(sex_five_consensus,dtype=np.int8)>=0)
    uncertain=part_none&~positive
    out[positive]=CODES["S5_positive_place_same_unique_six_models"]
    out[uncertain]=CODES["S5_positive_place_tied_or_unknown"]
    who[positive]=np.asarray(sex_five_consensus,dtype=np.int8)[positive]
    if np.any(out==0):
        raise RuntimeError("Source-conditional ordered stage dropped a UTC clock sample")
    if np.any((who>=0)&~np.isin(out,list(PROVISIONAL_SINGLE))):
        raise RuntimeError("Ambiguous/multiple S1/S2 or unfortified S4 assigned a fake source ruler")
    return out,who


def scan_chunk(P,A,IDs,*,cusp1,cusp2,counts,HD):
    x=np.asarray(P,dtype=np.float64)
    a=np.asarray(A,dtype=np.float64)
    ids=np.asarray(IDs,dtype=np.int32)
    n=len(x)
    if x.shape!=(n,8) or a.shape!=(n,17) or ids.shape!=(n,) or cusp1.shape!=(n,) or cusp2.shape!=(n,):
        raise ValueError("Original frozen input 8 western +17 site +1 HD and 2 house cusps")
    pt=old.s3.s1.base.es.src.PRIOR.ptolemy_source.conditional_all_four_common_leader(x,a[:,4])
    pt_valid=pt>=0
    knownHD=ids>=0
    counts["UTC_original_samples"]+=n
    counts["HD_root_margin_unassigned"]+=int((~knownHD).sum())
    counts["Ptolemy_conditional_fourmode_common"]+=int(pt_valid.sum())
    counts["Ptolemy_HD_boundary_unknown"]+=int((pt_valid&~knownHD).sum())
    S1=old.s3.s1.first_stage_eligible(x[:,:7],cusp1,cusp2)
    first={m:e.any(axis=1) for m,e in S1.items()}
    asc_lord,dispositor=old.s3.asc_lord_dispositor_indices(x[:,:7],a[:,0])
    same=asc_lord==dispositor
    partile=old.partile_body_candidates(x[:,:7])
    _,_,six_stable=old.es.candidate_score_winners(x[:,2],x[:,1],a[:,4])
    stage_agree=np.ones(n,dtype=bool)
    first_stage=None
    candidate_agree=np.ones(n,dtype=bool)
    first_candidate=None
    source_method_count=0
    for orb_name,orbs in ORBS.items():
        disposition=old.s3.old.dispositor_see(x[:,:7],a[:,0],orbs)
        _,_,other_see=old.s3.individual_other_aspector_masks(x[:,:7],a[:,0],orbs)
        joins={scope:old.s3.s2.candidates_joined_to_moon_or_mercury(x[:,:7],orbs,scope)["union"] for scope in JOINS}
        for mode in MODES:
            initial=S1[mode]
            for join_scope in JOINS:
                j=joins[join_scope]&(~first[mode])[:,None]
                for behold in BEHOLDS:
                    disp=disposition[behold]
                    for contact in CONTACTS:
                        other_seen=other_see[behold][contact].any(axis=1)
                        stage=old.s3.source_s3_later_partitions(
                            first[mode],j.any(axis=1),disp,other_seen,same)
                        base="|".join((mode,orb_name,join_scope,behold,"all="+contact))
                        for partpol in PARTILES:
                            key=base+"|"+partpol
                            possible=partile[partpol]
                            status,candidate=stage_status(initial,j,stage,possible,six_stable,asc_lord)
                            if first_stage is None:
                                first_stage=status.copy()
                                first_candidate=candidate.copy()
                            else:
                                stage_agree&=(status==first_stage)
                                candidate_agree&=(candidate>=0)&(candidate==first_candidate)
                            for value,label in LABELS.items():
                                mask=status==value
                                counts[key+"|"+label]+=int(mask.sum())
                                counts["Ptolemy_"+key+"|"+label]+=int((mask&pt_valid).sum())
                                if value in PROVISIONAL_SINGLE:
                                    counts[key+"|"+label+"|same_conditional_Ptolemy_body"]+=int((mask&(candidate==pt)).sum())
                            counts[key+"|source_primary_conditional_candidate"]+=int((candidate>=0).sum())
                            counts[key+"|historical_strength_or_rule_not_unique"]+=int((candidate<0).sum())
                            counts[key+"|source_qualified_genuine_LATER"]+=int(stage["LATER"].sum())
                            # exact original source cohort checks happen in run
                            source_method_count+=1
    if source_method_count!=STAGES:
        raise RuntimeError("96 original stage alternative policies not fully computed")
    for name,label in CODES.items():
        stable=stage_agree&(first_stage==label)
        counts["cross96_same_stage_"+name]+=int(stable.sum())
        counts["cross96_same_stage_"+name+"|Ptolemy"]+=int((stable&pt_valid).sum())
        if np.any(stable&knownHD):
            HD.setdefault("cross96_same_stage_"+name,np.zeros(HD_TOTAL,dtype=bool))[ids[stable&knownHD]]=True
        if label in PROVISIONAL_SINGLE:
            agreed_body=stable&candidate_agree&(first_candidate>=0)
            different_body=stable&~agreed_body
            counts["cross96_same_stage_"+name+"|same_primary_body"]+=int(agreed_body.sum())
            counts["cross96_same_stage_"+name+"|different_primary_body"]+=int(different_body.sum())
            if np.any(agreed_body&knownHD):
                HD.setdefault("cross96_same_stage_"+name+"|same_primary_body",np.zeros(HD_TOTAL,dtype=bool))[ids[agreed_body&knownHD]]=True
    full=stage_agree&candidate_agree&(first_candidate>=0)
    # Only unique source-conditioned primary occupant / S3 lord / S5
    # positive-place rights count, without S4 forcible assumption.
    counts["cross96_same_provisional_primary_candidate"]+=int(full.sum())
    counts["cross96_same_provisional_primary_candidate|Ptolemy"]+=int((full&pt_valid).sum())
    counts["cross96_same_provisional_primary_candidate|same_Ptolemy_body"]+=int((full&(first_candidate==pt)).sum())
    if np.any(full&knownHD):
        HD.setdefault("cross96_same_provisional_primary_candidate",np.zeros(HD_TOTAL,dtype=bool))[ids[full&knownHD]]=True
    # Unstable interpretation or stable nonunanimous historical participation
    counts["cross96_stages_disagree"]+=int((~stage_agree).sum())
    counts["cross96_stage_agrees_but_no_single_provisional_body"]+=int((stage_agree&~full).sum())


def run(west,site,hd_cache,hd_join,verify_sha=True):
    if swe.version!="2.10.03":raise RuntimeError("Frozen Swiss Ephemeris source changed")
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=site/"plan.json";am=site/"verified_manifest.json"
    wpj=json.loads(wp.read_bytes());wmj=json.loads(wm.read_bytes())
    apj=json.loads(ap.read_bytes());amj=json.loads(am.read_bytes())
    prior=old.s3.s1.base.es.src.PRIOR
    actual=prior.base.reg.initial.check_manifest(wpj,wmj,apj,amj)
    if actual!=N or wpj["step_minutes"]!=15:
        raise RuntimeError("Original full source clock changed")
    sha=prior.base.reg.initial.source_hash
    if wmj["plan_sha256"]!=sha(wp) or amj["plan_sha256"]!=sha(ap):
        raise RuntimeError("Original chart source plan SHA drift")
    proof=prior.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    H=json.loads((hd_join/"manifest.json").read_bytes())
    if (H["total_utc_grid_samples"]!=N or H["total_hd_structural_intervals"]!=HD_TOTAL
        or H["unresolved_near_boundary_samples"]!=125):
        raise RuntimeError("Original HD structural source drift")
    oldS3=json.loads((Path(__file__).resolve().parents[1]/"reference/research/lilly_cvii_s3_original_dispositor_self_other_aspect_full_century_public_v01.json").read_bytes())["counts"]
    oldS4=json.loads((Path(__file__).resolve().parents[1]/"reference/research/lilly_cvii_s4_s5_genuine_later_full_century_public_v01.json").read_bytes())["counts"]
    jd=prior.base.reg.julian_from_utc(wpj["utc_start_inclusive"])
    lat=float(apj["latitude"]);lon=float(apj["longitude"])
    c=Counter();HD={};first=0
    for w,a,h in zip(wmj["chunks"],amj["shards"],H["shards"],strict=True):
        n=w["count"]
        if not(w["first_index"]==first==a["first_index"]==h["index_first"] and h["count"]==n):
            raise RuntimeError("Original same-UTC 108 shards misaligned")
        pp=west/"chunks"/w["file"];aa=site/"shards"/a["file"];hh=hd_join/"shards"/h["file"]
        if pp.stat().st_size!=n*64 or aa.stat().st_size!=n*136 or hh.stat().st_size!=n*4:
            raise RuntimeError("Original source shard byte size drift")
        if verify_sha:
            for path,meta in ((pp,w),(aa,a),(hh,h)):
                if sha(path)!=meta["sha256"]:
                    raise RuntimeError("Original 108 shard integrity changed")
        P=np.memmap(pp,dtype="<f8",mode="r",shape=(n,8))
        A=np.memmap(aa,dtype="<f8",mode="r",shape=(n,17))
        IDs=np.memmap(hh,dtype="<i4",mode="r",shape=(n,))
        cusp1=np.empty(n);cusp2=np.empty(n)
        for i in range(n):
            cu,_=swe.houses_ex(jd+(first+i)/96.,lat,lon,b"R")
            cusp1[i]=cu[0];cusp2[i]=cu[1]
        if np.max(np.abs((cusp1-A[:,0]+180)%360-180))>0.0002:
            raise RuntimeError("Exact original ascending longitude changed")
        scan_chunk(P,A,IDs,cusp1=cusp1,cusp2=cusp2,counts=c,HD=HD)
        first+=n
    if not verify_sha or first!=N or c["UTC_original_samples"]!=N:
        raise RuntimeError("Complete original sampled century was not source SHA verified")
    if (c["HD_root_margin_unassigned"]!=125 or
        c["Ptolemy_conditional_fourmode_common"]!=4553 or
        c["Ptolemy_HD_boundary_unknown"]!=0):
        raise RuntimeError("Original frozen Ptolemy/HD source coverage changed")
    for mode in MODES:
        for orb in ORBS:
            for join in JOINS:
                for behold in BEHOLDS:
                    for contact in CONTACTS:
                        base="|".join((mode,orb,join,behold,"all="+contact))
                        trueold=oldS3[base+"|LATER"]
                        if c[base+"|"+PARTILES[0]+"|source_qualified_genuine_LATER"]!=trueold:
                            raise RuntimeError("Previous S3 true LATER count changed")
                        for part in PARTILES:
                            key=base+"|"+part
                            if sum(c[key+"|"+k] for k in CODES)!=N:
                                raise RuntimeError("All 96 source variants must partition 3.5m UTC")
                            for state,one,many in (
                                ("S1","S1_one_primary","S1_multiple_primaries"),
                                ("S2","S2_one_joined","S2_multiple_joined")
                            ):
                                if c[key+"|"+one]+c[key+"|"+many]!=oldS3[base+"|"+state]:
                                    raise RuntimeError("Original stage S1/S2 candidate counts shifted")
                            if c[key+"|S3_asc_lord"]!=oldS3[base+"|S3"]:
                                raise RuntimeError("Original S3 ASC lord source cohort changed")
                            if c[key+"|SY_self_dispositor_source_unknown"]!=oldS3[base+"|SY"]:
                                raise RuntimeError("Original self-dispositor source gap dropped")
                            if c[key+"|SX_other_aspector_no_dispositor_source_unknown"]!=oldS3[base+"|SX"]:
                                raise RuntimeError("Original other planet aspect source gap dropped")
                            if (c[key+"|S4_partile_possible_one_force_unknown"]+
                                c[key+"|S4_partile_possible_multiple_force_unknown"]!=
                                oldS4[key+"|S4_GEOMETRIC_possible_forcible_unverified"]):
                                raise RuntimeError("Original p536 geometric S4 possible source drift")
                            if (c[key+"|S5_positive_place_same_unique_six_models"]+
                                c[key+"|S5_positive_place_tied_or_unknown"]!=
                                oldS4[key+"|S5_NO_geometric_partile"]):
                                raise RuntimeError("Original S5 positive place scoring cohort changed")
                            if c[key+"|S5_positive_place_same_unique_six_models"]!=oldS4[key+"|S5_six_source_same_unique_five_positive_lord"]:
                                raise RuntimeError("Frozen six-source S5 mathematical candidate drift")
                            if (c[key+"|source_primary_conditional_candidate"]+
                                c[key+"|historical_strength_or_rule_not_unique"]!=N):
                                raise RuntimeError("Source provisional status not accounted")
    if (c["cross96_same_provisional_primary_candidate"]+
        c["cross96_stage_agrees_but_no_single_provisional_body"]+
        c["cross96_stages_disagree"]!=N):
        raise RuntimeError("Consensus/stage agreement partition incomplete")
    if sum(c["cross96_same_stage_"+LABELS[k]+"|same_primary_body"] for k in PROVISIONAL_SINGLE)!=c["cross96_same_provisional_primary_candidate"]:
        raise RuntimeError("Original source-variant stage/body consistency broken")
    for code in PROVISIONAL_SINGLE:
        key="cross96_same_stage_"+LABELS[code]
        if c[key+"|same_primary_body"]+c[key+"|different_primary_body"]!=c[key]:
            raise RuntimeError("One source-conditional primary stage disagreement not disclosed")
    for code in (CODES["S3_asc_lord"],CODES["S5_positive_place_same_unique_six_models"]):
        key="cross96_same_stage_"+LABELS[code]
        if c[key+"|different_primary_body"]!=0:
            raise RuntimeError("S3 ASC lord/S5 same positive source body drifted between historical variants")
    return {
       "schema":"lilly_1647_CVII_original_ordered_stage_source_conditional_96x6_full_century_v01",
       "status":"ORIGINAL_1647_ALL_ORDERED_MANNERS_STAGE_COVERAGE_BUT_COMPLETE_HISTORICAL_RULER_AND_HUMAN_VALIDITY_OPEN",
       "source":"Lilly Christian Astrology original 1647 first print pp535-536; source p104, p106 and p107",
       "source_horizon_UTC":[wpj["utc_start_inclusive"],wpj["utc_end_exclusive"]],
       "samples":N,"sample_step_minutes":15,"fixed_source_neutral_research_locations":1,
       "original_sha_source_shards_verified":verify_sha,
       "original_source_manifest_SHA256":{"planet":sha(wm),"angles":sha(am),"HD":sha(hd_join/"manifest.json")},
       "HD_original_source_audit":proof,"HD_structural_intervals":HD_TOTAL,
       "source_S1_spatial_variants":list(MODES),
       "source_p107_orb_envelopes":list(ORBS),
       "source_S2_body_inclusion_variants":list(JOINS),
       "source_dispositor_seeing_variants":list(BEHOLDS),
       "source_other_aspecting_lord_variants":list(CONTACTS),
       "source_partile_either_or_same_both_variants":list(PARTILES),
       "original_96_stage_path_scenarios":STAGES,
       "source_conditional_S5_printed_and_scoring_policies":6,
       "status_codes":CODES,
       "provisional_single_primary_stage_status_codes":sorted(PROVISIONAL_SINGLE),
       "full_Lilly_complete_planetary_fortitude":False,
       "forcible_partile_1647_original_still_unadjudicated":True,
       "source_p535_other_secondary_dignity_based_manners_significators_included":False,
       "source_unknown_SX_SY_states_retained":True,
       "same_natal_candidate_across_all_96_is_not_human_predictive_validation":True,
       "old_source_S3_S4_S5_counts_all96_reproduced_exactly":True,
       "counts":dict(c),
       "HD_distinct_intervals_for_all96_stable_stage_or_candidate":{key:int(bit.sum()) for key,bit in HD.items()},
       "historically_selected_single_final_manners_ruler":False,
       "Ptolemy_III13_actual_source_complete_soul_governor":False,
       "independent_human_personality_accuracy":False,
       "private_natal_interview_ratings_used":False
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("west","site","hd-cache","hd-join","out"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError("Original source science receipts append-only")
    j=run(a.west,a.site,a.hd_cache,a.hd_join)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(j,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":j["status"],"sampled_UTC":j["samples"],
       "all96_conditional_same_primary":j["counts"]["cross96_same_provisional_primary_candidate"]},sort_keys=True))

if __name__=="__main__":main()
