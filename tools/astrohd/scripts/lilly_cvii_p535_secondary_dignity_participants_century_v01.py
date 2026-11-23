#!/usr/bin/env python3
"""Lilly 1647 CVII p535: non-occupant dignity-bearing participants in manners.

Original first-print p535: a planet in the ascending or intercepted sign is a
PRINCIPAL significator of manners, BUT another planet having essential dignity
IN THE PLACE OF that principal ALSO PARTICIPATES. Multiple S1 occupants all
remain principal. We do NOT collapse participating secondary to coequal
governor, a unique strongest body, or a psychological trait claim.

The original source gives five essential dignity modes at a PLACE (1647
p104): domicile, exaltation, sect triplicity, terms and face.
Three printed historical terms witnesses independently preserved:
 original Lilly first printing, 1940 Ptolemaic, 1940 Egyptian.

For each original S1 mode:
  1. identify ALL 7 traditional planets actually in the S1 place;
  2. for EACH primary planet's exact zodiacal longitude, identify ALL
     classical bodies holding >= 1 positive dignity at that PLACE;
  3. add nonoccupant holders as SECONDARY participants only, while keeping
     original primary/secondary roles distinct.

When sect near horizon is uncertain (±0.1° source engineering boundary),
report guaranteed/intersection of day/night positive rights versus
possible/union, never assume no triplicity or invent a daytime chart.
This is one explicit original source participant rule only. It does not
prove other dignity-bearing bodies actually govern personality without
the original benevolent/malevolent, aspect and strength qualification.

Three competing first-stage spatial rules x three printed term traditions
= 9 source/interpretation combinations at all original 3,506,400
quarter-hour UTC samples at ONE fixed source-neutral research location.
All 36 original planet +36 site/angle +36 HD-index binary SHA-256 checks,
288,908 independent HD structural intervals, 125 HD root uncertainties,
5,049 sect uncertainty and 4,553 conditional four-mode Ptolemy reference
source clock rows independently checked. NO personal natal/interview data.

NOT full Lilly CVII manners ruler or Ptolemy III.13 governor;
NOT a behavioral validation or any universal natal chart ranking.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
import swisseph as swe

import lilly_cvii_s1_eligible_partial_strength_century_v01 as s1
import lilly_cvii_original_essential_dignity_final_fallback_century_v01 as essential

N=3506400
HD_STATE_COUNT=288908
MODES=s1.MODES
TERMS=tuple(essential.TERMS)
PLANETS=s1.PLANETS
METHODS=len(MODES)*len(TERMS)


def participant_rights_at_primary_places(planets,solar_alt,primary_masks):
    """Source-positive own primary PLACE rights, with honest sect intervals.

    Return two nested masks (certain, possible) of SECONDARY participants
    per source mode/printed term, excluding all actual primary occupants.
    Source term variants are not retrospectively chosen from human reports.
    """
    P=np.asarray(planets,dtype=np.float64)
    alt=np.asarray(solar_alt,dtype=np.float64)
    if P.ndim!=2 or P.shape[1]!=7 or alt.shape!=(len(P),):
        raise ValueError("Seven aligned classical planet longitude columns and solar altitude required")
    if (np.any(~np.isfinite(P)) or np.any(~np.isfinite(alt)) or
        np.any((P<0)|(P>=360))):
        raise ValueError("Nonfinite/un-normalized actual classical source input")
    if set(primary_masks)!=set(MODES):
        raise ValueError("All three original S1 spatial variants needed")
    for key,mask in primary_masks.items():
        z=np.asarray(mask)
        if z.shape!=P.shape or z.dtype!=np.bool_:
            raise ValueError("Aligned boolean primary occupant sets required for "+key)
    n=len(P)
    near_horizon=np.abs(alt)<=essential.SECT_UNCERTAIN_DEG
    certain={(mode,term):np.zeros((n,7),dtype=bool) for mode in MODES for term in TERMS}
    possible={(mode,term):np.zeros((n,7),dtype=bool) for mode in MODES for term in TERMS}
    for i in range(7):
        any_primary=np.logical_or.reduce([primary_masks[m][:,i] for m in MODES])
        idx=np.flatnonzero(any_primary)
        if not len(idx):continue
        z=P[idx,i]
        sectors=alt[idx]
        for term in TERMS:
            guaranteed=essential.dignity_scores_at_place(z,sectors,term)>0
            can=guaranteed.copy()
            unknown=near_horizon[idx]
            if np.any(unknown):
                n_unknown=int(unknown.sum())
                day=essential.dignity_scores_at_place(
                    z[unknown],np.ones(n_unknown,dtype=float),term)>0
                night=essential.dignity_scores_at_place(
                    z[unknown],-np.ones(n_unknown,dtype=float),term)>0
                guaranteed[unknown]=day&night
                can[unknown]=day|night
            for mode in MODES:
                used=primary_masks[mode][idx,i]
                if not np.any(used):continue
                chosen=idx[used]
                certain[(mode,term)][chosen]|=guaranteed[used]
                possible[(mode,term)][chosen]|=can[used]
    for mode in MODES:
        for term in TERMS:
            k=(mode,term)
            # An original first-stage occupant is already a PRIMARY.
            # Essential claims at another occupant's place do not make
            # it an additional independent secondary person/planet.
            certain[k]&=~primary_masks[mode]
            possible[k]&=~primary_masks[mode]
            if np.any(certain[k]&~possible[k]):
                raise RuntimeError("Source certainly dignified secondary is not possibly dignified")
            if np.any(certain[k]&primary_masks[mode]) or np.any(possible[k]&primary_masks[mode]):
                raise RuntimeError("Primary S1 occupant was demoted into secondary")
            if np.any((possible[k].any(axis=1))&(~primary_masks[mode].any(axis=1))):
                raise RuntimeError("Source cannot attach secondary participant when no primary exists")
    return certain,possible


def scan_chunk(P,A,HDids,*,cusp1,cusp2,counts,HDsets):
    p=np.asarray(P,dtype=np.float64)
    a=np.asarray(A,dtype=np.float64)
    ids=np.asarray(HDids,dtype=np.int32)
    n=len(p)
    if p.shape!=(n,8) or a.shape!=(n,17) or ids.shape!=(n,) or (
        np.asarray(cusp1).shape!=(n,) or np.asarray(cusp2).shape!=(n,)):
        raise ValueError("Original planet/site/HD and quadrant cusp sample shapes changed")
    original=s1.first_stage_eligible(p[:,:7],cusp1,cusp2)
    certainly,possibly=participant_rights_at_primary_places(p[:,:7],a[:,4],original)
    known_HD=ids>=0
    conditional=s1.base.es.src.PRIOR.ptolemy_source.conditional_all_four_common_leader(p,a[:,4])>=0
    counts["original_UTC_samples"]+=n
    counts["original_HD_margin_unknown"]+=int((~known_HD).sum())
    counts["original_sector_uncertain"]+=int((np.abs(a[:,4])<=essential.SECT_UNCERTAIN_DEG).sum())
    counts["original_Ptolemy_fourmode_common_conditional"]+=int(conditional.sum())
    counts["original_Ptolemy_conditional_HD_unknown"]+=int((conditional&~known_HD).sum())

    participants={(mode,term):original[mode]|certainly[(mode,term)]
                  for mode in MODES for term in TERMS}
    participant_can={(mode,term):original[mode]|possibly[(mode,term)]
                     for mode in MODES for term in TERMS}
    for mode in MODES:
        E=original[mode]
        n_primaries=E.sum(axis=1)
        none=n_primaries==0
        sole=n_primaries==1
        multi=n_primaries>1
        counts[mode+"|source_S1_no_primary"]+=int(none.sum())
        counts[mode+"|source_S1_sole_primary"]+=int(sole.sum())
        counts[mode+"|source_S1_multiple_primary"]+=int(multi.sum())
        for term in TERMS:
            k=(mode,term)
            C=certainly[k]
            U=possibly[k]
            any_c=C.any(axis=1)
            any_u=U.any(axis=1)
            uncertain=np.any(U!=C,axis=1)
            certain_total=participants[k].sum(axis=1)
            possible_total=participant_can[k].sum(axis=1)
            stem=mode+"|"+term+"|"
            counts[stem+"extra_secondary_certain_any"]+=int(any_c.sum())
            counts[stem+"extra_secondary_possible_any"]+=int(any_u.sum())
            counts[stem+"extra_secondary_no_possible"]+=int(((~any_u)&~none).sum())
            counts[stem+"extra_secondary_sector_unknown_any"]+=int(uncertain.sum())
            counts[stem+"primary_sole_with_certain_secondary"]+=int((sole&any_c).sum())
            counts[stem+"primary_sole_with_possible_secondary"]+=int((sole&any_u).sum())
            counts[stem+"primary_multi_with_certain_secondary"]+=int((multi&any_c).sum())
            counts[stem+"participant_certain_two_or_more"]+=int((certain_total>=2).sum())
            counts[stem+"participant_possible_two_or_more"]+=int((possible_total>=2).sum())
            counts[stem+"total_secondary_planet_occurrences"]+=int(C.sum())
            counts[stem+"possible_secondary_planet_occurrences"]+=int(U.sum())
            counts[stem+"conditional_Ptolemy_extra_secondary_certain"]+=int((conditional&any_c).sum())
            for idx,name in enumerate(PLANETS):
                counts[stem+"certain_secondary_"+name]+=int(C[:,idx].sum())
                counts[stem+"possible_secondary_"+name]+=int(U[:,idx].sum())
            for label,mask in (("S1_extra_certain",any_c),
                               ("S1_extra_possible",any_u)):
                if np.any(mask&known_HD):
                    HDsets.setdefault(stem+label,np.zeros(HD_STATE_COUNT,dtype=bool))[ids[mask&known_HD]]=True
        # Requiring same participant-set AND no uncertain sector rights
        # across all three historical printed terms witnesses.
        candidate=original[mode].any(axis=1)
        ref=participants[(mode,TERMS[0])]
        for term in TERMS:
            k=(mode,term)
            candidate&=np.all(participants[k]==ref,axis=1)
            candidate&=np.all(participants[k]==participant_can[k],axis=1)
        counts[mode+"|all_three_printed_terms_exact_full_participant_set"]+=int(candidate.sum())
        counts[mode+"|all_three_printed_terms_with_extra_secondary"]+=int(
            (candidate&certainly[(mode,TERMS[0])].any(axis=1)).sum())
        if np.any(candidate&known_HD):
            HDsets.setdefault(mode+"|all_three_terms_exact_participant_set",np.zeros(HD_STATE_COUNT,dtype=bool))[ids[candidate&known_HD]]=True

    # Original "sign" versus quadrant-house source disagreement can even
    # distinguish which planets are PRINCIPAL despite equal all-participant
    # membership. Keep candidate identity and participant *roles* separate.
    all_primary_present=np.logical_and.reduce([original[m].any(axis=1) for m in MODES])
    firstprimary=original[MODES[0]]
    same_primary=all_primary_present.copy()
    for mode in MODES:
        same_primary&=np.all(firstprimary==original[mode],axis=1)
    first_set=participants[(MODES[0],TERMS[0])]
    stable_all_participants=all_primary_present.copy()
    for mode in MODES:
        for term in TERMS:
            key=(mode,term)
            stable_all_participants&=np.all(participants[key]==first_set,axis=1)
            stable_all_participants&=np.all(participants[key]==participant_can[key],axis=1)
    same_role_and_set=stable_all_participants&same_primary
    counts["all_three_geometries_same_exact_primary_set"]+=int(same_primary.sum())
    counts["all_nine_geometries_terms_same_exact_total_participant_set"]+=int(stable_all_participants.sum())
    counts["all_nine_same_original_primary_ROLE_and_secondary_participants"]+=int(same_role_and_set.sum())
    counts["all_nine_same_roles_and_extra_secondary"]+=int(
        (same_role_and_set&certainly[(MODES[0],TERMS[0])].any(axis=1)).sum())
    counts["all_nine_same_roles_and_conditional_Ptolemy"]+=int((same_role_and_set&conditional).sum())
    for label,mask in (("all_nine_same_roles_and_participants",same_role_and_set),
                       ("all_nine_same_roles_and_Ptolemy",same_role_and_set&conditional)):
        if np.any(mask&known_HD):
            HDsets.setdefault(label,np.zeros(HD_STATE_COUNT,dtype=bool))[ids[mask&known_HD]]=True


def run(west,angles,hd_cache,hd_join,verify_sha=True):
    if swe.version!="2.10.03":raise RuntimeError("Original Swiss engine version changed")
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    W=json.loads(wp.read_bytes());WM=json.loads(wm.read_bytes())
    A=json.loads(ap.read_bytes());AM=json.loads(am.read_bytes())
    previous=s1.base.es.src.PRIOR
    if previous.base.reg.initial.check_manifest(W,WM,A,AM)!=N or W["step_minutes"]!=15:
        raise RuntimeError("Original century UTC sample count changed")
    sha=previous.base.reg.initial.source_hash
    if WM["plan_sha256"]!=sha(wp) or AM["plan_sha256"]!=sha(ap):
        raise RuntimeError("Source planet/site manifests disagree with source plan SHA")
    proof=previous.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    HDJOIN=json.loads((hd_join/"manifest.json").read_bytes())
    if (HDJOIN["total_utc_grid_samples"]!=N or
        HDJOIN["total_hd_structural_intervals"]!=HD_STATE_COUNT or
        HDJOIN["unresolved_near_boundary_samples"]!=125):
        raise RuntimeError("Original HD source structural corpus changed")
    original=json.loads((Path(__file__).resolve().parents[1]/"reference/research/lilly_cvii_s1_eligible_partial_strength_full_century_public_v01.json").read_bytes())
    old=original["counts"]
    counts=Counter()
    hdsets={}
    jd=previous.base.reg.julian_from_utc(W["utc_start_inclusive"])
    lat=float(A["latitude"]);lon=float(A["longitude"])
    offset=0
    for westchunk,angchunk,hdchunk in zip(WM["chunks"],AM["shards"],HDJOIN["shards"],strict=True):
        n=westchunk["count"]
        if not (westchunk["first_index"]==offset==angchunk["first_index"]==hdchunk["index_first"]
                and hdchunk["count"]==n):
            raise RuntimeError("Original Western, site and HD UTC row offsets changed")
        Pfile=west/"chunks"/westchunk["file"]
        Afile=angles/"shards"/angchunk["file"]
        Hfile=hd_join/"shards"/hdchunk["file"]
        if Pfile.stat().st_size!=n*64 or Afile.stat().st_size!=n*136 or Hfile.stat().st_size!=n*4:
            raise RuntimeError("Original binary source shard size changed")
        if verify_sha:
            for p,meta in ((Pfile,westchunk),(Afile,angchunk),(Hfile,hdchunk)):
                if sha(p)!=meta["sha256"]:
                    raise RuntimeError("Input SHA256 differs from recorded original source")
        P=np.memmap(Pfile,dtype="<f8",mode="r",shape=(n,8))
        Ang=np.memmap(Afile,dtype="<f8",mode="r",shape=(n,17))
        IDs=np.memmap(Hfile,dtype="<i4",mode="r",shape=(n,))
        first=np.empty(n,dtype=float);second=np.empty(n,dtype=float)
        for i in range(n):
            cusps,_=swe.houses_ex(jd+(offset+i)/96.,lat,lon,b"R")
            first[i]=cusps[0];second[i]=cusps[1]
        if np.max(np.abs((first-Ang[:,0]+180.)%360-180.))>0.0002:
            raise RuntimeError("Original source ASC differs from independent quadrant source")
        scan_chunk(P,Ang,IDs,cusp1=first,cusp2=second,counts=counts,HDsets=hdsets)
        offset+=n
    if not verify_sha or offset!=N or counts["original_UTC_samples"]!=N:
        raise RuntimeError("Actual original complete source-hash-checked century not run")
    if (counts["original_HD_margin_unknown"]!=125 or
        counts["original_sector_uncertain"]!=5049 or
        counts["original_Ptolemy_fourmode_common_conditional"]!=4553 or
        counts["original_Ptolemy_conditional_HD_unknown"]!=0):
        raise RuntimeError("Original HD, sect and Ptolemy exact-source denominator drift")
    for mode in MODES:
        if (counts[mode+"|source_S1_no_primary"]!=old[mode+"|empty_go_to_later_stages"] or
            counts[mode+"|source_S1_sole_primary"]!=old[mode+"|sole_primary_occupant"] or
            counts[mode+"|source_S1_multiple_primary"]!=old[mode+"|multiple_principal_occupants"]):
            raise RuntimeError("Previously source-verified S1 occupant original counts changed")
        for term in TERMS:
            stem=mode+"|"+term+"|"
            if not (0<=counts[stem+"extra_secondary_certain_any"]<=
                    counts[stem+"extra_secondary_possible_any"]<=
                    N-counts[mode+"|source_S1_no_primary"]):
                raise RuntimeError("Source secondary holder inclusion outside eligible S1 or impossible interval")
            if (counts[stem+"primary_sole_with_certain_secondary"]+
                counts[stem+"primary_multi_with_certain_secondary"]!=
                counts[stem+"extra_secondary_certain_any"]):
                raise RuntimeError("Source secondary must be attached to precisely one S1 presence class")
            if sum(counts[stem+"certain_secondary_"+name] for name in PLANETS)!=counts[stem+"total_secondary_planet_occurrences"]:
                raise RuntimeError("Source classical secondary-holder count missed body")
    return {
        "schema":"lilly_1647_CVII_p535_secondary_nonoccupant_dignities_at_primary_places_full_century_v01",
        "status":"SOURCE_1647_S1_SECONDARY_DIGNITY_PARTICIPANTS_9_POLICIES_NOT_FULL_MANNERS_GOVERNOR",
        "source":"Lilly Christian Astrology first printing 1647 Book III CVII p535; original p104 essential dignities at each PRINCIPAL's place and original printed terms alternatives",
        "original_p535_render_sha256":"49efe26a167fcdd6d0f1f08d3c7a69faaf87939b41cab02341ef6dc2500f4708",
        "source_horizon_UTC":[W["utc_start_inclusive"],W["utc_end_exclusive"]],
        "sample_UTC_count":N,"step_minutes":15,"fixed_research_location_count":1,
        "original_108_planet_site_HD_binary_shards_sha256_rechecked":verify_sha,
        "source_sha256_manifests":{"Western":sha(wm),"site":sha(am),"HD":sha(hd_join/"manifest.json")},
        "original_HD_audit":proof,"original_HD_structural_intervals":HD_STATE_COUNT,
        "S1_spatial_source_variants":list(MODES),
        "historically_independent_printed_terms_sources":list(TERMS),
        "source_method_count":METHODS,
        "source_p535_roles":"First-stage occupants remain PRINCIPAL; bodies with positive essential dignity at ANY primary occupant's exact zodiac place are SECONDARY participants if not already primary. No automatic coequal governor or unique strongest.",
        "sect_uncertainty_policy":"Day/night uncertain source altitude <= 0.1°: CERTAIN rights must be present by both day and night; POSSIBLE rights by either. No invented sect or silent negative.",
        "secondary_aspective_qualifications_missing":"Original p535 benevolent/malevolent, strength, dispositorship and aspects influence manners; these are not entirely source-qualified here.",
        "counts":dict(counts),
        "HD_distinct_source_intervals_by_condition":{key:int(mask.sum()) for key,mask in hdsets.items()},
        "prior_S1_source_cohorts_reproduced":True,
        "historically_complete_Lilly_manners_ruler_computed":False,
        "complete_Ptolemy_III13_soul_governor_computed":False,
        "independent_human_behavior_validation":False,
        "private_natal_or_interview_evidence_used":False
    }


def main():
    parser=argparse.ArgumentParser()
    for arg in ("west","angles","hd-cache","hd-join","out"):
        parser.add_argument("--"+arg,required=True,type=Path)
    args=parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Original source-bound census receipt cannot overwrite previous source evidence")
    result=run(args.west,args.angles,args.hd_cache,args.hd_join)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"samples":result["sample_UTC_count"],
                      "methods":result["source_method_count"]},sort_keys=True))

if __name__=="__main__":main()
