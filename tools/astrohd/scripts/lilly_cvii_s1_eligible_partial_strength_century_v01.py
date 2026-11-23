#!/usr/bin/env python3
"""Original Lilly 1647 CVII p535 first-stage manners eligibility + partial strength.

This does NOT determine a full source-licensed manners significator.

Original first-print p535: if any planet occupies rising sign, or intercepted
sign, it is principal significator; if several are in the horoscope ALL
signify manners, with the most powerful lasting longer. Luminaries are said
to matter only in a general way unless exceptionally fortified; dignified
other planets participate even when not primary occupants.

Three independently labelled historical spatial interpretations:
 rising sign / actual Regiomontanus 1st quadrant house / rising sign OR
 fully intercepted sign in the actual first quadrant house.
 These are not interchangeable and none is source-determined as unique.

For each source S1 mode at every one of the original 3,506,400 finite 15-min
UTC samples: zero eligible occupant -> LATER STAGES NOT EVALUATED; one body ->
sole conditional S1 principal occupant, with luminary caveat; 2+ bodies ->
retain all as source participants; only source-scoped partial strength
comparison is possible, not the full old authorial 'most powerful' judgment.

Each multiple eligible body is compared using existing source-verified
partial strength points: original natal essential, natal house strength
under R/Placidus, signed motion p115; 72 disclosed variants =
3 printed term tables x4 reception/peregrine hypothetical policies
x2 house score divisions x3 engineering station-uncertainty windows.
Unknown motion becomes [-5,+4], and a strict unique conditional selection
requires winner's LOWER score > all eligible competitors' UPPER scores.
Uncertain sect blocks multiple-body comparison. A sole occupant remains a
sole geometric occupant independently of near-horizon sect unknown.

Scores for non-eligible classical planets are intentionally ignored; do not
silently pick the biggest all-seven-body natal strength as a CVII S1 ruler.
No reading or writing private natal/person evidence. All source SHA checks,
288,908 HD structural intervals, 125 root-margin abstentions and conditional
Ptolemy four-mode 4,553 sample reference remain intact.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import swisseph as swe

import lilly_1647_integrated_partial_fortitude_full_century_v01 as base
import ptolemy_lilly_same_instant_century_v01 as historical

N=base.N
HD_STATES=base.HD_STATE_COUNT
MODES=("ascending_sign","regiomontanus_first_house","ascending_sign_or_intercepted_sign")
PLANETS=base.PLANETS
SCENARIOS=base.NUM_SCENARIOS
TOTAL_SOURCE_INTERPRETATIONS=len(MODES)*SCENARIOS


def first_stage_eligible(planets,cusp1,cusp2):
    """S1 primary occupants, not later dignity-based indirect participants.

    Reuse the original source-defined source test for any-body presence; this
    routine obtains the seven planet-specific masks and verifies consistency.
    """
    p=np.asarray(planets,dtype=np.float64)
    c1=np.asarray(cusp1,dtype=np.float64)
    c2=np.asarray(cusp2,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or c1.shape!=(len(p),) or c2.shape!=c1.shape:
        raise ValueError("Seven source planets and aligned first/second house cusps required")
    if np.any(~np.isfinite(p)) or np.any(~np.isfinite(c1)) or np.any(~np.isfinite(c2)):
        raise ValueError("Finite source zodiac longitudes and cusps required")
    if np.any((p<0)|(p>=360)) or np.any((c1<0)|(c1>=360)) or np.any((c2<0)|(c2>=360)):
        raise ValueError("Source longitudes must be normalized 0..360 degrees")
    arc=(c2-c1)%360
    if np.any((arc<=0)|(arc>180)):
        raise ValueError("Invalid oriented original first-house quadrant")
    planet_signs=np.floor(p/30).astype(np.int8)
    asc_sign=np.floor(c1/30).astype(np.int8)
    sign=planet_signs==asc_sign[:,None]
    quadrant=((p-c1[:,None])%360)<arc[:,None]
    starts=np.arange(12,dtype=np.float64)*30.
    start_offset=(starts[None,:]-c1[:,None])%360.
    # Fully intercepted whole sign, neither its beginning nor its end
    # coincident with a first-house cusp (source tolerance is geometric).
    intercepted=(start_offset>1e-9)&(start_offset+30<arc[:,None]-1e-9)
    inside_intercepted=intercepted[np.arange(len(p))[:,None],planet_signs]
    sign_plus=sign|inside_intercepted
    result={"ascending_sign":sign,
            "regiomontanus_first_house":quadrant,
            "ascending_sign_or_intercepted_sign":sign_plus}
    original=historical.first_house_and_intercepted(p,c1,c2)
    for key,mask in result.items():
        if not np.array_equal(mask.any(axis=1),original[key]):
            raise RuntimeError("Original independent first-stage geometry baseline drift: "+key)
    return result


def select_conditional_principal(lower,upper,eligible,sect_known):
    """Sole occupant is a provisional principal; multi requires strict bounds.

    Return signed candidate ID (-1 if unresolved), and sole vs multi masks.
    A source first-stage EMPTY chart is *not* assigned a planet and must be
    passed onward to later historical manners-stage rules, not interpreted
    as negative astrological evidence.
    """
    l=np.asarray(lower,dtype=np.int16);h=np.asarray(upper,dtype=np.int16)
    e=np.asarray(eligible,dtype=bool);sect=np.asarray(sect_known,dtype=bool)
    if l.ndim!=2 or l.shape[1]!=7 or h.shape!=l.shape or e.shape!=l.shape or sect.shape!=(len(l),):
        raise ValueError("Aligned seven-body bounded source score and eligibility required")
    if np.any(l>h):raise ValueError("Original score lower bound exceeds upper")
    amount=e.sum(axis=1)
    sole=amount==1
    multi=amount>1
    sel=np.full(len(l),-1,dtype=np.int8)
    # Sole S1 body is source-defined regardless of as-yet undecided full
    # fortitude and solar sect; still conditional for luminaries.
    if np.any(sole):
        sel[sole]=np.argmax(e[sole],axis=1).astype(np.int8)
    if np.any(multi&sect):
        lo=np.where(e,l,np.int16(-32767))
        hi=np.where(e,h,np.int16(-32767))
        best=np.argmax(lo,axis=1)
        hi[np.arange(len(l)),best]=-32767
        other_hi=hi.max(axis=1)
        candidate=(multi&sect)&(lo[np.arange(len(l)),best]>other_hi)
        sel[candidate]=best[candidate].astype(np.int8)
    if np.any(sel[amount==0]>=0) or np.any((sel>=0)&~e[np.arange(len(l)),np.maximum(sel,0)]):
        raise RuntimeError("Noneligible body selected")
    return sel,sole,multi


def scan_chunk(P,A,IDs,*,R,velocities,edges,counts,HD_presence):
    p=np.asarray(P,dtype=np.float64);a=np.asarray(A,dtype=np.float64)
    h=np.asarray(IDs,dtype=np.int32);r=np.asarray(R,dtype=np.float64)
    v=np.asarray(velocities,dtype=np.float64)
    n=len(p)
    if p.shape!=(n,8) or a.shape!=(n,17) or h.shape!=(n,) or r.shape!=(n,12) or v.shape!=(n,7):
        raise ValueError("Source input shapes/clock alignment invalid")
    first=first_stage_eligible(p[:,:7],r[:,0],r[:,1])
    occupant_counts={key:mask.sum(axis=1) for key,mask in first.items()}
    known_sect=np.abs(a[:,4])>base.es.SECT_EPS
    known_HD=h>=0
    ptolemy=base.es.src.PRIOR.ptolemy_source.conditional_all_four_common_leader(p,a[:,4])
    ptolemy_known=ptolemy>=0
    counts["source_samples"]+=n
    counts["HD_root_margin_unassigned"]+=int((~known_HD).sum())
    counts["sect_horizon_uncertain"]+=int((~known_sect).sum())
    counts["conditional_ptolemy_4mode_sample"]+=int(ptolemy_known.sum())
    counts["conditional_ptolemy_HD_unknown"]+=int((ptolemy_known&~known_HD).sum())
    scorehouse={
      "Regiomontanus":base.hs.HOUSE_POINTS[base.hs.house_ids(p[:,:7],r)].astype(np.int16),
      "Placidus":base.hs.HOUSE_POINTS[base.hs.house_ids(p[:,:7],a[:,5:17])].astype(np.int16)
    }
    counts["original_house_component_any_body_disagree"]+=int(
         (base.hs.house_ids(p[:,:7],r)!=base.hs.house_ids(p[:,:7],a[:,5:17])).any(axis=1).sum())
    # One independent consensus accumulator per original S1 scope.
    agreement={m:np.full(n,-2,dtype=np.int8) for m in MODES}
    universal={m:np.ones(n,dtype=bool) for m in MODES}
    total_models=0
    for mode,elig in first.items():
        amount=occupant_counts[mode]
        zero=amount==0;one=amount==1;multi=amount>1
        counts[mode+"|empty_go_to_later_stages"]+=int(zero.sum())
        counts[mode+"|sole_primary_occupant"]+=int(one.sum())
        counts[mode+"|multiple_principal_occupants"]+=int(multi.sum())
        counts[mode+"|sole_luminary_qualifying_strength_unknown"]+=int(
             (one & elig[:,0:2].any(axis=1)).sum())
        counts[mode+"|multi_involving_luminary"]+=int(
             (multi & elig[:,0:2].any(axis=1)).sum())
        counts[mode+"|conditional_ptolemy_first_present"]+=int((~zero&ptolemy_known).sum())
        counts[mode+"|conditional_ptolemy_sole_occupant"]+=int((one&ptolemy_known).sum())
        for k,name in enumerate(PLANETS):
            counts[mode+"|occupant_"+name]+=int(elig[:,k].sum())
            counts[mode+"|sole_"+name]+=int((one&elig[:,k]).sum())
    motion={t:base.signed_motion_bounds(v,t,edges) for t in base.STATIONS}
    row=np.arange(n)
    for terms in base.TERMS:
        natal=base.essential_points(p[:,:7],a[:,4],terms)
        for interpretation in base.ESSENTIAL_POLICIES:
            essence=natal[interpretation]
            for station in base.STATIONS:
                low_motion,high_motion=motion[station]
                for house in base.HOUSE_NAMES:
                    prefix="|".join((terms,interpretation,house,f"station={station:.2f}"))
                    low=essence+scorehouse[house]+low_motion
                    high=essence+scorehouse[house]+high_motion
                    for mode in MODES:
                        elig=first[mode]
                        selected,sole,multi=select_conditional_principal(low,high,elig,known_sect)
                        candidate=selected>=0
                        single=sole&candidate
                        ranked=multi&candidate
                        counts[mode+"|"+prefix+"|conditional_candidate"]+=int(candidate.sum())
                        counts[mode+"|"+prefix+"|multi_strict_partial_candidate"]+=int(ranked.sum())
                        counts[mode+"|"+prefix+"|multi_unresolved"]+=int((multi&~candidate).sum())
                        counts[mode+"|"+prefix+"|same_ptolemy_body"]+=int((candidate&(selected==ptolemy)).sum())
                        counts[mode+"|"+prefix+"|different_ptolemy_body"]+=int((candidate&ptolemy_known&(selected!=ptolemy)).sum())
                        # Cross-all-72 stability PER original first-stage
                        # occupancy interpretation. A no-body candidate
                        # never becomes a selected pseudo ruler.
                        agg=agreement[mode]
                        agg[:]=np.where(agg==-2,selected,agg)
                        universal[mode]&=candidate&(agg==selected)
                    total_models+=1
    if total_models!=base.NUM_SCENARIOS:
        raise RuntimeError("All declared 72 source configurations must be evaluated")
    for mode in MODES:
        stable=universal[mode]&(agreement[mode]>=0)
        eligible_count=occupant_counts[mode]
        sole=eligible_count==1
        multi=eligible_count>1
        counts[mode+"|stable_all72_sole_occupant"]+=int((stable&sole).sum())
        counts[mode+"|stable_all72_multi_partial_candidate"]+=int((stable&multi).sum())
        counts[mode+"|stable_all72_any_conditional_candidate"]+=int(stable.sum())
        counts[mode+"|stable_all72_conditional_ptolemy_overlap"]+=int((stable&ptolemy_known).sum())
        counts[mode+"|stable_all72_same_conditional_ptolemy_planet"]+=int((stable&(agreement[mode]==ptolemy)).sum())
        counts[mode+"|stable_all72_diff_conditional_ptolemy_planet"]+=int((stable&ptolemy_known&(agreement[mode]!=ptolemy)).sum())
        ids=h[stable&known_HD]
        if len(ids):HD_presence[mode][ids]=True
        ids=h[stable&ptolemy_known&known_HD]
        if len(ids):HD_presence["Ptolemy_"+mode][ids]=True
    cross=universal[MODES[0]]&universal[MODES[1]]&universal[MODES[2]]
    first_id=agreement[MODES[0]]
    all_same=cross&(first_id==agreement[MODES[1]])&(first_id==agreement[MODES[2]])
    conflicting=cross&~all_same
    counts["S1_all_three_spatial_variants_each_stable_but_disagree"]+=int(conflicting.sum())
    counts["S1_all_three_spatial_variants_same_strict_candidate"]+=int(all_same.sum())
    counts["S1_all_three_spatial_variants_same_and_ptolemy"]+=int((all_same&ptolemy_known).sum())
    counts["S1_all_three_spatial_variants_same_body_as_conditional_ptolemy"]+=int((all_same&(first_id==ptolemy)).sum())
    if np.any(all_same&known_HD):HD_presence["all_three_same"][h[all_same&known_HD]]=True
    if np.any(all_same&ptolemy_known&known_HD):
        HD_presence["all_three_same_Ptolemy"][h[all_same&ptolemy_known&known_HD]]=True


def run(west,angles,hd_cache,hd_join,verify_sha=True):
    if swe.version!="2.10.03":raise RuntimeError("Swiss source version drift")
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    wj=json.loads(wp.read_bytes());wjm=json.loads(wm.read_bytes())
    aj=json.loads(ap.read_bytes());ajm=json.loads(am.read_bytes())
    n=base.es.src.PRIOR.base.reg.initial.check_manifest(wj,wjm,aj,ajm)
    if n!=N or wj["step_minutes"]!=15:
        raise RuntimeError("Original declared 3.5m clock changed")
    sourcehash=base.es.src.PRIOR.base.reg.initial.source_hash
    if wjm["plan_sha256"]!=sourcehash(wp) or ajm["plan_sha256"]!=sourcehash(ap):
        raise RuntimeError("Original planet/site manifest plan SHA mismatch")
    join_audit=base.es.src.PRIOR.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    hj=json.loads((hd_join/"manifest.json").read_bytes())
    if (hj["total_utc_grid_samples"]!=N or hj["total_hd_structural_intervals"]!=HD_STATES
        or hj["unresolved_near_boundary_samples"]!=125):
        raise RuntimeError("HD source proof population or root uncertainty drift")
    original_integrated=json.loads((Path(__file__).resolve().parents[1]/"reference/research/lilly_1647_integrated_partial_fortitude_full_century_public_v01.json").read_bytes())
    origcounts=original_integrated["counts"]
    jd0=base.es.src.PRIOR.base.reg.julian_from_utc(wj["utc_start_inclusive"])
    lat=float(aj["latitude"]);lon=float(aj["longitude"])
    counts=Counter()
    bits={k:np.zeros(HD_STATES,dtype=bool) for k in (*MODES,*(f"Ptolemy_{m}" for m in MODES),"all_three_same","all_three_same_Ptolemy")}
    curr=0
    for sh,(w,a,h) in enumerate(zip(wjm["chunks"],ajm["shards"],hj["shards"],strict=True)):
        k=w["count"]
        if not(w["first_index"]==curr==a["first_index"]==h["index_first"] and h["count"]==k):
            raise RuntimeError("Source UTC binary shards not aligned")
        wpbin=west/"chunks"/w["file"];apbin=angles/"shards"/a["file"];hpbin=hd_join/"shards"/h["file"]
        if wpbin.stat().st_size!=64*k or apbin.stat().st_size!=136*k or hpbin.stat().st_size!=4*k:
            raise RuntimeError("Original binary source shard sizes changed")
        if verify_sha:
            for path,entry in ((wpbin,w),(apbin,a),(hpbin,h)):
                if sourcehash(path)!=entry["sha256"]:
                    raise RuntimeError("Original source evidence SHA256 mismatch")
        P=np.memmap(wpbin,dtype="<f8",mode="r",shape=(k,8))
        A=np.memmap(apbin,dtype="<f8",mode="r",shape=(k,17))
        IDs=np.memmap(hpbin,dtype="<i4",mode="r",shape=(k,))
        R=np.empty((k,12),dtype=np.float64)
        for i in range(k):
            cusps,_=swe.houses_ex(jd0+(curr+i)/96.,lat,lon,b"R")
            R[i]=cusps
        if np.max(np.abs((R[:,0]-A[:,0]+180)%360-180))>0.0002:
            raise RuntimeError("Original source Ascendant clock mismatch")
        before=P[0,:7] if sh==0 else base.mot._load_mmap(west,wjm["chunks"][sh-1])[-1,:7]
        after=P[-1,:7] if sh==len(wjm["chunks"])-1 else base.mot._load_mmap(west,wjm["chunks"][sh+1])[0,:7]
        earlier=np.concatenate((np.asarray(before,dtype=float)[None,:],P[:-1,:7]),axis=0)
        following=np.concatenate((P[1:,:7],np.asarray(after,dtype=float)[None,:]),axis=0)
        velocities=base.mot.wrapped_speed(earlier,following)
        velocities[:,2]=P[:,7] # original exact Mercury source speed
        edge=np.zeros(k,dtype=bool)
        if sh==0:edge[0]=True
        if sh==len(wjm["chunks"])-1:edge[-1]=True
        scan_chunk(P,A,IDs,R=R,velocities=velocities,edges=edge,counts=counts,HD_presence=bits)
        curr+=k
    if not verify_sha or curr!=N or counts["source_samples"]!=N:
        raise RuntimeError("Source-audited entire UTC clock not completed")
    if (counts["HD_root_margin_unassigned"]!=125 or counts["sect_horizon_uncertain"]!=5049 or
        counts["conditional_ptolemy_4mode_sample"]!=4553 or counts["conditional_ptolemy_HD_unknown"]!=0):
        raise RuntimeError("Frozen historical century cohort/HD/sect drift")
    if counts["original_house_component_any_body_disagree"]!=origcounts["any_seven_body_house_assignment_differs"]:
        raise RuntimeError("Original full-house SHA source baseline drift")
    first_expected={"ascending_sign":1428060,"regiomontanus_first_house":1409411,"ascending_sign_or_intercepted_sign":1516373}
    first_pt_expected={"ascending_sign":1746,"regiomontanus_first_house":1920,"ascending_sign_or_intercepted_sign":1865}
    for mode in MODES:
        a=counts[mode+"|empty_go_to_later_stages"]
        b=counts[mode+"|sole_primary_occupant"]
        c=counts[mode+"|multiple_principal_occupants"]
        if a+b+c!=N or b+c!=first_expected[mode]:
            raise RuntimeError("Earlier source exact first-stage body-presence cohort drift: "+mode)
        if counts[mode+"|conditional_ptolemy_first_present"]!=first_pt_expected[mode]:
            raise RuntimeError("Same-UTC Ptolemy+Lilly first-stage baseline drift: "+mode)
        for name in PLANETS:
            if counts[mode+"|sole_"+name]>counts[mode+"|occupant_"+name]:
                raise RuntimeError("Impossible sole first occupant count")
        if counts[mode+"|stable_all72_sole_occupant"]!=b:
            raise RuntimeError("Exactly one source occupant must remain one across all partial-score variants")
        if counts[mode+"|stable_all72_multi_partial_candidate"]>c:
            raise RuntimeError("Conditional unique multi source candidate cannot exceed multi")
        for terms in base.TERMS:
            for es in base.ESSENTIAL_POLICIES:
                for station in base.STATIONS:
                    for place in base.HOUSE_NAMES:
                        k="|".join((mode,terms,es,place,f"station={station:.2f}"))
                        if (counts[k+"|conditional_candidate"]+
                            counts[k+"|multi_unresolved"]+a!=N):
                            raise RuntimeError("Every source S1 candidate must be accounted, including multi ambiguity")
    return {
      "schema":"lilly_1647_CVII_S1_original_primary_occupants_partial_strength_same_UTC_century_v01",
      "status":"ORIGINAL_PRINTED_CVII_FIRST_STAGE_SOURCE_CONDITIONED_216_POSSIBILITIES_NO_FINAL_MANNERS_RULER",
      "original_author_source":"William Lilly Christian Astrology first printing 1647 book III chapter CVII p535",
      "original_first_print_source_p535_image_sha256":"49efe26a167fcdd6d0f1f08d3c7a69faaf87939b41cab02341ef6dc2500f4708",
      "original_p535_source_scope":"Primary if occupies sign ascending or intercepted; all multiple horoscope occupants signify; most powerful more durable. Other planets dignified in principal's location participate; luminaries qualified.",
      "source_horizon_UTC":[wj["utc_start_inclusive"],wj["utc_end_exclusive"]],
      "source_UTC_samples":N,"step_minutes":15,"research_location_count":1,
      "original_source_shard_SHA256_rechecked":verify_sha,
      "source_manifest_hashes":{"planet":sourcehash(wm),"site_angles":sourcehash(am),"HD_lookup":sourcehash(hd_join/"manifest.json")},
      "same_UTC_HD_source_audit":join_audit,
      "HD_structural_interval_total":HD_STATES,
      "original_s1_eligibility_variant_names":list(MODES),
      "partial_natal_strength_model_variant_count":SCENARIOS,
      "source_sensitive_S1_x_partial_strength_policy_count":TOTAL_SOURCE_INTERPRETATIONS,
      "near_station_policy_original_source_status":"engineering source-uncertain numerical abstentions",
      "source_decision_sole":"one geometric primary occupant only, with luminary and other-dignity-participation caveats; not a complete historically qualified manner planet",
      "source_decision_multiple":"all eligible occupants retained as manners participants; a strict bounded partial maximum may be listed as researcher-conditioned possible more powerful body but is not a source-complete strength priority",
      "source_decision_empty":"later Lilly CVII joining/dispositor/partile/essential dignity branches OPEN, not negative personality finding",
      "source_decision_other_dignities":"planets with essential dignities in occupant's place participate; not assigned numerical behavior impact here",
      "counts":dict(counts),
      "HD_distinct_intervals_by_S1_scope_or_Ptolemy":{k:int(v.sum()) for k,v in bits.items()},
      "original_past_72_policy_results_unchanged":True,
      "historically_final_Lilly_manners_significator_computed":False,
      "independent_human_behavior_criterion_used":False,
      "owner_or_third_party_private_birth_records_loaded":False,
      "ptolemy_actual_soul_governor_not_computed":True
    }


def main():
    parser=argparse.ArgumentParser()
    for field in ("west","angles","hd-cache","hd-join","out"):
        parser.add_argument("--"+field,type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError("Historical original full-century source receipt must remain immutable")
    report=run(args.west,args.angles,args.hd_cache,args.hd_join)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":report["status"],"source_UTC_samples":report["source_UTC_samples"],"methods":report["source_sensitive_S1_x_partial_strength_policy_count"]},sort_keys=True))

if __name__=="__main__":main()
