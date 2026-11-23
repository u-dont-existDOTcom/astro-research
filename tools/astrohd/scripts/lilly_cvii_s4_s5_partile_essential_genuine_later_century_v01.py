#!/usr/bin/env python3
"""Lilly 1647 CVII p536: S4 partile candidates and S5 essential-at-place.

SOURCE-CRITICAL SCOPE:
  The original only says to examine a planet FORCIBLY partile-aspecting
  Moon/Mercury, then the most essential dignities at THEIR PLACES if
  none have partile. It does NOT uniquely operationalize 'forcibly',
  'and/or', full fortitude, or sum/max of Mercury and Moon place rights.
  Previous original-first-print source work retains:
     p106 partile = same numbered zodiacal degree in suitable aspect
     p104 domicile/exaltation/triplicity/terms/face 5/4/3/2/1
     original 1647 vs two printed 1940 Loeb term witnesses
     p536 last stage at Mercury and Luna places
  S4 is GEOMETRIC POSSIBILITY, not a source-certified forcible body.
  S5 only when no such geometrically possible partile contact exists
  under its chosen source policy. A positive five-mode S5 score alone
  does not establish actual historical manners governor.

Only run S4/S5 after source-qualified S1=EMPTY/S2=EMPTY,
S3 distinct dispositor DID NOT aspect ASC lord, AND no other
planet aspects ASC lord and the lord is NOT its own dispositor.
The new 2026-11-23 S3 census marked own-dispositor as SY and another
body/no distinct disposer as SX: both are source UNRESOLVED.
Do not silently promote either into S4 or S5.

48 stage variants = 3 original first-stage spatial ×2 p107 orb moiety
×2 S2 external/broad ×2 dispositor ray policy ×2 other-body aspect
policy, crossed with 2 original p106 p536 partile interpretations:
(1) a planet partile-aspects EITHER Moon or Mercury
(2) the SAME planet partile-aspects BOTH Moon and Mercury.
For genuine later-stage cases, 3 original/Loeb printed term tables x
2 openly RESEARCHER-DEFINED Mercury/Moon-place score aggregations
(plain sum / larger of the two) give 6 source-conditional S5 candidates.
Total 48*2*6=576 source/mechanical method comparisons.

All 3,506,400 original quarter-hour UTC source samples from 1926–2026
at one fixed research location, original 36 planet+36 site+36 HD lookup
shards individually SHA256 verified, 288,908 independent HD state
intervals, 125 near-root unresolved clock samples, and original 4,553
Ptolemy shared conditional 4-mode witnesses preserved. Exact original
96 six-stage frozen S4/S5 cohort counts reconciled with old SY split.

NO private natal, interviews or person-specific scores used or published.
NO empirically valid natal personality predictions or ranked #1 chart.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from collections import Counter
import numpy as np
import swisseph as swe
import lilly_cvii_s3_dispositor_other_aspect_self_gap_century_v01 as s3
import lilly_cvii_original_essential_dignity_final_fallback_century_v01 as es

N=s3.N
HD_STATES=s3.HD_STATES
MODES=s3.MODES
ORBS=s3.ORBS
JOINS=s3.JOIN_SCOPES
BEHOLDS=s3.BEHOLDS
CONTACTS=s3.CONTACTS
PARTILES=s3.old.PARTILES
S5_TERMS=tuple(es.TERMS)
S5_AGGREGATES=es.AGGREGATES
PLANETS=s3.PLANETS
STAGE_METHODS=s3.STAGE_COUNT
S4_S5_METHODS=STAGE_METHODS*len(PARTILES)
ALL_S5_SOURCE_POLICIES=S4_S5_METHODS*len(S5_TERMS)*len(S5_AGGREGATES)


def partile_body_candidates(planets):
    """Full seven-column candidates; five eligible other classical bodies.

    The original source p106 partile matching NUMBERED zodiac degree is
    not the same as a modern fixed <1 degree aspect orb.
    """
    p=np.asarray(planets,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or np.any(~np.isfinite(p)):
        raise ValueError("Aligned seven classical longitudes required")
    if np.any((p<0)|(p>=360)):raise ValueError("Normalized tropical zodiac")
    n=len(p)
    lunar=np.zeros((n,7),dtype=bool)
    mercury=np.zeros((n,7),dtype=bool)
    for k in (0,3,4,5,6):
        lunar[:,k]=s3.old.partile_numbered_ray(p[:,k],p[:,1])
        mercury[:,k]=s3.old.partile_numbered_ray(p[:,k],p[:,2])
    both=lunar&mercury
    union=lunar|mercury
    prior=s3.old.partile_candidates(p)
    if not np.array_equal(union.any(axis=1),prior[PARTILES[0]]):
        raise RuntimeError("Earlier p106 either-reference partile source cohort changed")
    if not np.array_equal(both.any(axis=1),prior[PARTILES[1]]):
        raise RuntimeError("Earlier same-planet both-reference partile source cohort changed")
    return {"moon":lunar,"mercury":mercury,
            "both":both,PARTILES[0]:union,PARTILES[1]:both}


def source_eligible_S4_S5(part_stage,partile_planets):
    """No original SX/SY can be pushed to subsequent fallback categories."""
    later=np.asarray(part_stage["LATER"],dtype=bool)
    part=np.asarray(partile_planets,dtype=bool)
    if part.ndim!=2 or part.shape!=(len(later),7):
        raise ValueError("Source stage and eligible partile planet mask misaligned")
    S4=later&part.any(axis=1)
    S5=later&~part.any(axis=1)
    if np.any(S4&S5) or not np.array_equal(S4|S5,later):
        raise RuntimeError("Only verified genuine LATER samples enter p536 S4/S5")
    if np.any(S4&(part_stage["SX"]|part_stage["SY"])) or np.any(S5&(part_stage["SX"]|part_stage["SY"])):
        raise RuntimeError("Historical SX/SY ambiguity laundered into last source stage")
    return S4,S5


def scan_chunk(P,A,IDs,*,cusp1,cusp2,counts,HD):
    p=np.asarray(P,dtype=np.float64)
    a=np.asarray(A,dtype=np.float64)
    hd=np.asarray(IDs,dtype=np.int32)
    n=len(p)
    if p.shape!=(n,8) or a.shape!=(n,17) or hd.shape!=(n,):
        raise ValueError("Original same UTC source binary shape changed")
    original_clock=hd>=0
    ptolemy=s3.s1.base.es.src.PRIOR.ptolemy_source.conditional_all_four_common_leader(p,a[:,4])
    pt_known=ptolemy>=0
    counts["UTC_clock_samples"]+=n
    counts["HD_root_margin_unknown"]+=int((~original_clock).sum())
    counts["conditional_Ptolemy_4mode_possible_common_lord"]+=int(pt_known.sum())
    counts["Ptolemy_common_HD_root_unknown"]+=int((pt_known&~original_clock).sum())

    original_S1=s3.s1.first_stage_eligible(p[:,:7],cusp1,cusp2)
    first={mode:mask.any(axis=1) for mode,mask in original_S1.items()}
    lord,dispositor=s3.asc_lord_dispositor_indices(p[:,:7],a[:,0])
    self_dispositor=lord==dispositor

    part=partile_body_candidates(p[:,:7])
    wins,score_meta,all6_consensus=es.candidate_score_winners(p[:,2],p[:,1],a[:,4])
    if len(wins)!=len(S5_TERMS)*len(S5_AGGREGATES):
        raise RuntimeError("All six printed source-S5 scoring alternatives missing")
    partial_S5_known=all6_consensus>=0
    row=np.arange(n)

    later_all48=np.ones(n,dtype=bool)
    all_source_branches=0
    for orbname,source_orbs in ORBS.items():
        seeing=s3.old.dispositor_see(p[:,:7],a[:,0],source_orbs)
        _,_,aspects=s3.individual_other_aspector_masks(p[:,:7],a[:,0],source_orbs)
        joins={scope:s3.s2.candidates_joined_to_moon_or_mercury(p[:,:7],source_orbs,scope)["union"].any(axis=1)
               for scope in JOINS}
        for mode in MODES:
            for join in JOINS:
                for behold in BEHOLDS:
                    disp=seeing[behold]
                    for contact in CONTACTS:
                        asp=aspects[behold][contact].any(axis=1)
                        stage=s3.source_s3_later_partitions(
                            first[mode],joins[join],disp,asp,self_dispositor)
                        base_tag="|".join((mode,orbname,join,behold,"all="+contact))
                        source_later=stage["LATER"]
                        sy_without_other=stage["SY"]&~asp
                        later_all48&=source_later
                        counts[base_tag+"|genuine_LATER"]+=int(source_later.sum())
                        counts[base_tag+"|SY_self_with_no_other"]+=int(sy_without_other.sum())
                        counts[base_tag+"|historical_source_SX_unknown"]+=int(stage["SX"].sum())
                        counts[base_tag+"|historical_source_SY_unknown"]+=int(stage["SY"].sum())
                        for policy in PARTILES:
                            eligible=part[policy]
                            stage_tag=base_tag+"|"+policy
                            S4,S5=source_eligible_S4_S5(stage,eligible)
                            counts[stage_tag+"|S4_GEOMETRIC_possible_forcible_unverified"]+=int(S4.sum())
                            counts[stage_tag+"|S5_NO_geometric_partile"]+=int(S5.sum())
                            counts[stage_tag+"|SY_with_geometric_partile_legacy"]+=int((sy_without_other&eligible.any(axis=1)).sum())
                            counts[stage_tag+"|SY_without_geometric_partile_legacy"]+=int((sy_without_other&~eligible.any(axis=1)).sum())
                            counts[stage_tag+"|Ptolemy_SY_with_geometric_partile_legacy"]+=int((sy_without_other&eligible.any(axis=1)&pt_known).sum())
                            counts[stage_tag+"|Ptolemy_SY_without_geometric_partile_legacy"]+=int((sy_without_other&~eligible.any(axis=1)&pt_known).sum())
                            counts[stage_tag+"|Ptolemy_S4_possible"]+=int((S4&pt_known).sum())
                            counts[stage_tag+"|Ptolemy_S5_no_partile"]+=int((S5&pt_known).sum())
                            count=eligible.sum(axis=1)
                            counts[stage_tag+"|S4_exactly_one_body"]+=int((S4&(count==1)).sum())
                            counts[stage_tag+"|S4_multiple_bodies"]+=int((S4&(count>1)).sum())
                            counts[stage_tag+"|S4_body_to_BOTH_Mercury_Moon"]+=int((S4&part["both"].any(axis=1)).sum())
                            for k,name in enumerate(PLANETS):
                                counts[stage_tag+"|S4_body_"+name]+=int((S4&eligible[:,k]).sum())
                                counts[stage_tag+"|S4_only_body_"+name]+=int((S4&(count==1)&eligible[:,k]).sum())
                                counts[stage_tag+"|S4_dual_reference_body_"+name]+=int((S4&part["both"][:,k]).sum())
                            counts[stage_tag+"|S5_six_source_same_unique_five_positive_lord"]+=int((S5&partial_S5_known).sum())
                            counts[stage_tag+"|S5_six_source_tied_or_sect_unknown"]+=int((S5&~partial_S5_known).sum())
                            counts[stage_tag+"|S5_Ptolemy_same_conditional_body"]+=int((S5&(all6_consensus==ptolemy)).sum())
                            for k,name in enumerate(PLANETS):
                                counts[stage_tag+"|S5_all6_source_winner_"+name]+=int((S5&(all6_consensus==k)).sum())
                            for source_tag,winner in wins.items():
                                chosen=S5&(winner>=0)
                                counts[stage_tag+"|S5_"+source_tag+"|unique_positive"]+=int(chosen.sum())
                                counts[stage_tag+"|S5_"+source_tag+"|tie_or_unknown"]+=int((S5&~(winner>=0)).sum())
                                counts[stage_tag+"|S5_"+source_tag+"|same_as_Ptolemy_conditional"]+=int((chosen&(winner==ptolemy)).sum())
                            for which,condition in (("S4",S4),("S5",S5),
                                                     ("S5_all6",S5&partial_S5_known)):
                                ids=hd[condition&original_clock]
                                if len(ids):
                                    key=stage_tag+"|"+which
                                    HD.setdefault(key,np.zeros(HD_STATES,dtype=bool))[ids]=True
                        all_source_branches+=1
    if all_source_branches!=STAGE_METHODS:
        raise RuntimeError("All 48 original stage interpretations not examined")

    anypart=part[PARTILES[0]].any(axis=1)
    bothpart=part[PARTILES[1]].any(axis=1)
    assert not np.any(bothpart&~anypart)
    cross={
       "all48_true_LATER":later_all48,
       "all48_true_LATER_S4_both_reference_same_planet":later_all48&bothpart,
       "all48_true_LATER_S4_either_only_policy_disagreement":later_all48&anypart&~bothpart,
       "all48_true_LATER_S5_no_geometric_partile_either_reference":later_all48&~anypart,
       "all48_true_LATER_S5_six_print_aggregation_agree":later_all48&~anypart&partial_S5_known
    }
    for tag,mask in cross.items():
        counts[tag]+=int(mask.sum())
        counts[tag+"|conditional_Ptolemy"]+=int((mask&pt_known).sum())
        if tag=="all48_true_LATER_S5_six_print_aggregation_agree":
            counts[tag+"|same_conditional_Ptolemy_body"]+=int((mask&(all6_consensus==ptolemy)).sum())
        ids=hd[mask&original_clock]
        if len(ids):
            HD.setdefault(tag,np.zeros(HD_STATES,dtype=bool))[ids]=True


def run(west,angles,hd_cache,hd_join,verify_sha=True):
    if swe.version!="2.10.03":raise RuntimeError("Original Swiss source version changed")
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    wj=json.loads(wp.read_bytes());wjm=json.loads(wm.read_bytes())
    aj=json.loads(ap.read_bytes());ajm=json.loads(am.read_bytes())
    original=s3.s1.base.es.src.PRIOR
    n=original.base.reg.initial.check_manifest(wj,wjm,aj,ajm)
    if n!=N or wj["step_minutes"]!=15:
        raise RuntimeError("Original full same-UTC source clock drift")
    digest=original.base.reg.initial.source_hash
    if wjm["plan_sha256"]!=digest(wp) or ajm["plan_sha256"]!=digest(ap):
        raise RuntimeError("Original planet/site plans differ from source SHA")
    proof=original.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    hj=json.loads((hd_join/"manifest.json").read_bytes())
    if (hj["total_utc_grid_samples"]!=N or hj["total_hd_structural_intervals"]!=HD_STATES
        or hj["unresolved_near_boundary_samples"]!=125):
        raise RuntimeError("Independent HD time/source manifest changed")
    prior_s3=json.loads((Path(__file__).resolve().parents[1]/"reference/research/lilly_cvii_s3_original_dispositor_self_other_aspect_full_century_public_v01.json").read_bytes())["counts"]
    original_96=json.loads((Path(__file__).resolve().parents[1]/"reference/research/lilly_cvii_all_other_planets_full_century_public_v01.json").read_bytes())["counts"]
    jd=s3.s1.base.es.src.PRIOR.base.reg.julian_from_utc(wj["utc_start_inclusive"])
    lat=float(aj["latitude"]);lon=float(aj["longitude"])
    counts=Counter();HD={}
    first=0
    for w,a,h in zip(wjm["chunks"],ajm["shards"],hj["shards"],strict=True):
        k=w["count"]
        if not(w["first_index"]==first==a["first_index"]==h["index_first"] and h["count"]==k):
            raise RuntimeError("Original same-UTC planet/site/HD source shards misaligned")
        pb=west/"chunks"/w["file"];ab=angles/"shards"/a["file"];hb=hd_join/"shards"/h["file"]
        if pb.stat().st_size!=64*k or ab.stat().st_size!=136*k or hb.stat().st_size!=4*k:
            raise RuntimeError("Original source binary record byte count changed")
        if verify_sha:
            for path,meta in ((pb,w),(ab,a),(hb,h)):
                if digest(path)!=meta["sha256"]:
                    raise RuntimeError("Frozen source SHA256 changed")
        P=np.memmap(pb,dtype="<f8",mode="r",shape=(k,8))
        A=np.memmap(ab,dtype="<f8",mode="r",shape=(k,17))
        IDs=np.memmap(hb,dtype="<i4",mode="r",shape=(k,))
        c1=np.empty(k);c2=np.empty(k)
        for i in range(k):
            cusps,_=swe.houses_ex(jd+(first+i)/96.,lat,lon,b"R")
            c1[i]=cusps[0];c2[i]=cusps[1]
        if np.max(np.abs((c1-A[:,0]+180)%360-180))>0.0002:
            raise RuntimeError("Frozen original source Ascendant mismatch")
        scan_chunk(P,A,IDs,cusp1=c1,cusp2=c2,counts=counts,HD=HD)
        first+=k
    if not verify_sha or first!=N or counts["UTC_clock_samples"]!=N:
        raise RuntimeError("Full original century not SHA256 source verified")
    if (counts["HD_root_margin_unknown"]!=125 or
        counts["conditional_Ptolemy_4mode_possible_common_lord"]!=4553 or
        counts["Ptolemy_common_HD_root_unknown"]!=0):
        raise RuntimeError("Original HD and Ptolemy conditional source cohort changed")
    for mode in MODES:
        for orb in ORBS:
            for join in JOINS:
                for behold in BEHOLDS:
                    for contact in CONTACTS:
                        key="|".join((mode,orb,join,behold,"all="+contact))
                        if counts[key+"|genuine_LATER"]!=prior_s3[key+"|LATER"]:
                            raise RuntimeError("Earlier 48-source S3 verified true LATER cohort changed")
                        if counts[key+"|SY_self_with_no_other"]!=prior_s3[key+"|SY_without_other_aspecting"]:
                            raise RuntimeError("Previously verified SY self aspect ambiguity changed")
                        for p in PARTILES:
                            tag=key+"|"+p
                            oldtag="|".join((mode,orb,join,behold,p,"all="+contact))
                            s4=counts[tag+"|S4_GEOMETRIC_possible_forcible_unverified"]
                            s5=counts[tag+"|S5_NO_geometric_partile"]
                            sy_part=counts[tag+"|SY_with_geometric_partile_legacy"]
                            sy_not=counts[tag+"|SY_without_geometric_partile_legacy"]
                            if s4+s5!=prior_s3[key+"|LATER"]:
                                raise RuntimeError("No SX/SY allowed to enter S4/S5")
                            if sy_part+sy_not!=prior_s3[key+"|SY_without_other_aspecting"]:
                                raise RuntimeError("Some self-dispositor case silently disappeared")
                            if s4+sy_part!=original_96[oldtag+"|S4"] or s5+sy_not!=original_96[oldtag+"|S5"]:
                                raise RuntimeError("Old original 96 source S4/S5 counts not fully reconstructed")
                            if (s4!=counts[tag+"|S4_exactly_one_body"]+counts[tag+"|S4_multiple_bodies"] or
                                s5!=counts[tag+"|S5_six_source_same_unique_five_positive_lord"]+
                                    counts[tag+"|S5_six_source_tied_or_sect_unknown"]):
                                raise RuntimeError("Each source later stage not partitioned by participants/witnesses")
                            if (counts[tag+"|S5_six_source_same_unique_five_positive_lord"]>
                                counts[tag+"|S5_NO_geometric_partile"]):
                                raise RuntimeError("A source six-score winner cannot exist outside last fallback")
                            for scheme in S5_TERMS:
                                for agg in S5_AGGREGATES:
                                    name=scheme+"|"+agg
                                    if (counts[tag+"|S5_"+name+"|unique_positive"]+
                                        counts[tag+"|S5_"+name+"|tie_or_unknown"]!=s5):
                                        raise RuntimeError("Source S5 printed rights six method accounting invalid")
                            if (counts[tag+"|Ptolemy_S4_possible"]+
                                counts[tag+"|Ptolemy_SY_with_geometric_partile_legacy"]!=
                                original_96["Ptolemy_"+oldtag+"|S4"] or
                                counts[tag+"|Ptolemy_S5_no_partile"]+
                                counts[tag+"|Ptolemy_SY_without_geometric_partile_legacy"]!=
                                original_96["Ptolemy_"+oldtag+"|S5"]):
                                raise RuntimeError("Previous original Ptolemy same-UTC S4/S5 sources not reconciled")
    return {
      "schema":"lilly_1647_CVII_original_S4_partile_S5_at_Mercury_Moon_places_genuine_later_source_v01",
      "status":"ORIGINAL_S4_PARTILE_GEOMETRIC_POSSIBLE_AND_S5_FIVE_POSITIVE_SOURCE_WITNESSES_NO_FINAL_MANNERS_RULER",
      "source_original":"Lilly Christian Astrology first London 1647 printing pp106-107, p535-536 and pp101-105",
      "source_original_p536_page_image_sha256":"4cdd11d5cf468e20f38fed7889e42f2e6298540e05f7f196c9b916e28bb57b24",
      "source_horizon_UTC":[wj["utc_start_inclusive"],wj["utc_end_exclusive"]],
      "samples":N,"step_minutes":15,"fixed_research_locations":1,
      "original_108_source_shard_SHA256_rechecked":verify_sha,
      "HD_source_audit":proof,"HD_structural_interval_total":HD_STATES,
      "source_manifest_SHA256":{"planet":digest(wm),"site":digest(am),"HD":digest(hd_join/"manifest.json")},
      "historically_disclosed_S1_space_variants":list(MODES),
      "original_printed_orb_variants":{key:val.tolist() for key,val in ORBS.items()},
      "S2_qualifying_planet_scopes":list(JOINS),
      "S3_dispositor_beholding_variants":list(BEHOLDS),
      "other_classical_aspect_to_lord_variants":list(CONTACTS),
      "p536_partile_scopes":list(PARTILES),
      "p536_S5_original_print_term_sources":list(S5_TERMS),
      "p536_S5_place_point_aggregation_options":list(S5_AGGREGATES),
      "original_source_stage_methods":STAGE_METHODS,
      "original_source_partile_S4_S5_eligibility_methods":S4_S5_METHODS,
      "S4_S5_eligibility_x_S5_source_candidate_scoring_methods":ALL_S5_SOURCE_POLICIES,
      "S4_forcible_aspect_historical_rule_adjudicated":False,
      "original_1647_CVII_S5_full_manners_ruler_selected":False,
      "p536_last_stage_positive_5_mode_place_score_is_not_full_fortitude":True,
      "S3_SX_SY_historical_source_gaps_retained":True,
      "old_96_source_S4_S5_and_new_48_S3_LATER_exactly_reconciled":True,
      "counts":dict(counts),
      "HD_distinct_structural_intervals_by_stage":{k:int(v.sum()) for k,v in HD.items()},
      "no_real_human_personality_prediction":True,
      "no_private_natal_birth_interview_or_person_source_evidence_used":True,
      "actual_Ptolemy_III13_soul_governor_computed":False
    }


def main():
    parser=argparse.ArgumentParser()
    for name in ("west","angles","hd-cache","hd-join","out"):
        parser.add_argument("--"+name,required=True,type=Path)
    a=parser.parse_args()
    if a.out.exists():raise FileExistsError("Source-bound original century receipt cannot be overwritten")
    j=run(a.west,a.angles,a.hd_cache,a.hd_join)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(j,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":j["status"],"samples":j["samples"],
                      "source_S4_S5_options":j["S4_S5_eligibility_x_S5_source_candidate_scoring_methods"]},sort_keys=True))

if __name__=="__main__":main()
