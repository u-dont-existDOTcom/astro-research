#!/usr/bin/env python3
"""Lilly 1647 original CVII p536 third-stage Ascendant lord/dispositor.

Only after neither p535 first-stage primary occupant nor p536 second-stage
joined-to-Moon/Mercury planet is eligible (source-conditional).

Original 1647 p536 'then take the Lord of the ascendant ... but so as his
Dispositor behold him with some aspect' and 'If no Planet aspect him'
leave two explicitly unassigned situations:
 SX: another classical planet aspects the ASC lord, but its domicile
     dispositor does NOT; source text does not appoint a unique ruler.
 SY: ASC lord is in its OWN domicile and therefore is its OWN dispositor,
     so historical aspecting oneself is not clarified.

Source-only method partitions 3 first-stage sign/house variants x
2 original printed lower/larger 1647 moiety envelopes x
2 Moon/Mercury joining candidate scopes x2 dispositing aspect geometries
(sign-based ray vs orb-close to traditional nonconjunction rays) x
2 any-other-planet aspect classes (rays-only vs rays plus bodily)
= 48 historical SOURCE-CONDITIONAL cases.

Explicitly identify the classical ASC lord, its natal domicile dispositor,
and every other classical planet geometrically aspecting it. No full
historical manners ruler, psychological predictions or individual natal
input. Old original 96 six-stage counts are preserved and mathematically
reconciled: new SY is an UNASSIGNED split of old SX and old S4/S5 buckets,
never a rewrite of the earlier historical numerical artifact.

All 3,506,400 original 15-minute source UTC samples 1926-2026 at ONE
fixed source-neutral research location; original 36 planetary, 36 site
and 36 HD-index binary SHA shards independently reverified, original
288,908 HD intervals and 125 root-margin unknown samples, 4,553
conditional source Ptolemy four-mode possible common leaders preserved.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
import swisseph as swe

import lilly_cvii_s1_eligible_partial_strength_century_v01 as s1
import lilly_cvii_s2_actual_joined_planet_candidates_century_v01 as s2
import lilly_cvii_ptolemy_same_instant_ordered_fallback_v02 as old
import lilly_cvii_any_planet_aspecting_asc_lord_century_v01 as other

N=3506400
HD_STATES=288908
MODES=s1.MODES
ORBS=old.SOURCE_ORBS
JOIN_SCOPES=old.JOINS
BEHOLDS=old.BEHOLDS
CONTACTS=other.CONTACT_CLASSES
STAGE_COUNT=len(MODES)*len(ORBS)*len(JOIN_SCOPES)*len(BEHOLDS)*len(CONTACTS)
PLANETS=old.PLANETS

def asc_lord_dispositor_indices(planets,asc):
    p=np.asarray(planets,dtype=np.float64)
    a=np.asarray(asc,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or a.shape!=(len(p),):
        raise ValueError("Seven traditional bodies and aligned actual ASC degree required")
    if not np.all(np.isfinite(p)) or not np.all(np.isfinite(a)):
        raise ValueError("Nonfinite source zodiac")
    if np.any((p<0)|(p>=360)) or np.any((a<0)|(a>=360)):
        raise ValueError("Unnormalized original source longitudes")
    rul=old.base.four.pt3.ptolemy2.DOMICILE
    lord=rul[np.floor(a/30).astype(np.int8)].astype(np.int8)
    row=np.arange(len(a))
    disp=rul[np.floor(p[row,lord]/30).astype(np.int8)].astype(np.int8)
    return lord,disp


def individual_other_aspector_masks(planets,asc,orbs):
    """Which *other* seven traditional planets geometrically aspect ASC lord.

    Preserves orbital-ray vs sign-ray and nonconjunction vs bodily.
    Source conditional, not necessarily historical qualifying fortitude.
    Each per-planet mask is independently checked against prior frozen
    original whole-planet yes/no source classifier.
    """
    p=np.asarray(planets,dtype=np.float64)
    a=np.asarray(asc,dtype=np.float64)
    o=np.asarray(orbs,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or a.shape!=(len(p),) or o.shape!=(7,):
        raise ValueError("Seven source longitudes/orbs and ASC required")
    lord,disp=asc_lord_dispositor_indices(p,a)
    n=len(p);idx=np.arange(n)
    lord_lon=p[idx,lord]
    zlord=np.floor(lord_lon/30).astype(np.int16)
    out={behold:{contact:np.zeros((n,7),dtype=bool) for contact in CONTACTS} for behold in BEHOLDS}
    for k in range(7):
        notlord=(lord!=k)
        sep=(np.floor(p[:,k]/30).astype(np.int16)-zlord)%12
        signray=np.isin(sep,old.SEEING_SIGN_DELTAS)
        threshold=(o[k]+o[lord])/2
        near=old.ray_residual(p[:,k],lord_lon)<=threshold
        body=old.angle_distance(p[:,k],lord_lon)<=threshold
        for source,ray in ((BEHOLDS[0],signray),(BEHOLDS[1],near)):
            out[source][CONTACTS[0]][:,k]=notlord&ray
            out[source][CONTACTS[1]][:,k]=notlord&(ray|body)
    prior=other.aspects_to_asc_lord(p,a,o)
    for source in BEHOLDS:
        for contact in CONTACTS:
            if not np.array_equal(out[source][contact].any(axis=1),prior[source][contact]):
                raise RuntimeError("Source other-planets original aspect any flag drift")
    return lord,disp,out


def source_s3_later_partitions(first_present,join_present,dispositor_ray,other_aspect,self_dispositor):
    """Six exhaustive source-state conditions; no final appointed ruler.

    S1 first, then S2, then S3 if distinct dispositor beholds lord,
    SY (own domicile) prior source-UNASSIGNED, SX other aspects lord but
    dispositor does not, then later S4/S5 possible when no contact.
    """
    f=np.asarray(first_present,dtype=bool)
    j=np.asarray(join_present,dtype=bool)
    d=np.asarray(dispositor_ray,dtype=bool)
    a=np.asarray(other_aspect,dtype=bool)
    own=np.asarray(self_dispositor,dtype=bool)
    if len({x.shape for x in (f,j,d,a,own)})!=1 or f.ndim!=1:
        raise ValueError("All original time-same stage conditions must be 1D aligned")
    if np.any(d&~a):raise RuntimeError("Dispositor aspect must be included in any-other aspect")
    if np.any(own&d):raise RuntimeError("Self as own dispositor cannot source-behold himself")
    S1=f
    rest=~f
    S2=rest&j
    rest&=~j
    S3=rest&d
    SY=rest&own
    SX=rest&~d&~own&a
    LATER=rest&~d&~own&~a
    values={"S1":S1,"S2":S2,"S3":S3,"SY":SY,"SX":SX,"LATER":LATER}
    if not np.all(sum(x.astype(np.uint8) for x in values.values())==1):
        raise RuntimeError("Source six distinct conservative stage classification not exhaustive")
    return values


def scan_chunk(P,A,IDs,*,cusp1,cusp2,counts,hd):
    p=np.asarray(P,dtype=np.float64)
    a=np.asarray(A,dtype=np.float64)
    source_ids=np.asarray(IDs,dtype=np.int32)
    n=len(p)
    if p.shape!=(n,8) or a.shape!=(n,17) or source_ids.shape!=(n,):
        raise ValueError("Source original planets, angles and HD not aligned")
    masks=s1.first_stage_eligible(p[:,:7],cusp1,cusp2)
    first={k:v.any(axis=1) for k,v in masks.items()}
    known_hd=source_ids>=0
    Ptolemy=s1.base.es.src.PRIOR.ptolemy_source.conditional_all_four_common_leader(p,a[:,4])
    pt_known=Ptolemy>=0
    counts["original_UTC_sample_count"]+=n
    counts["HD_root_margin_unknown"]+=int((~known_hd).sum())
    counts["conditional_Ptolemy_fourmode_common"]+=int(pt_known.sum())
    counts["Ptolemy_in_HD_unknown"]+=int((pt_known&~known_hd).sum())
    lord,disp=asc_lord_dispositor_indices(p[:,:7],a[:,0])
    self_as_dispositor=lord==disp
    row=np.arange(n)
    for k,name in enumerate(PLANETS):
        counts["all_clock_ASC_lord_"+name]+=int((lord==k).sum())
        counts["all_clock_ASC_lord_own_domicile_"+name]+=int(((lord==k)&self_as_dispositor).sum())

    all48_S3=np.ones(n,dtype=bool)
    all48_SY=np.ones(n,dtype=bool)
    all48_SX=np.ones(n,dtype=bool)
    all48_LATER=np.ones(n,dtype=bool)
    count_models=0
    for orb,moiety in ORBS.items():
        info=old.dispositor_see(p[:,:7],a[:,0],moiety)
        _,_,source_aspect=individual_other_aspector_masks(p[:,:7],a[:,0],moiety)
        if not np.array_equal(self_as_dispositor,info["same_as_own_dispositor"]):
            raise RuntimeError("Original self-dispositor source encoding changed")
        joined={scope:s2.candidates_joined_to_moon_or_mercury(p[:,:7],moiety,scope)["union"].any(axis=1)
                for scope in JOIN_SCOPES}
        for mode in MODES:
            for scope in JOIN_SCOPES:
                for behold in BEHOLDS:
                    d=info[behold]
                    for contact in CONTACTS:
                        source_tag="|".join((mode,orb,scope,behold,"all="+contact))
                        asp=source_aspect[behold][contact]
                        any_other=asp.any(axis=1)
                        parts=source_s3_later_partitions(first[mode],joined[scope],d,any_other,self_as_dispositor)
                        counts[source_tag+"|SY_with_other_aspecting"]+=int((parts["SY"]&any_other).sum())
                        counts[source_tag+"|SY_without_other_aspecting"]+=int((parts["SY"]&~any_other).sum())
                        counts["Ptolemy_"+source_tag+"|SY_with_other_aspecting"]+=int((parts["SY"]&any_other&pt_known).sum())
                        counts["Ptolemy_"+source_tag+"|SY_without_other_aspecting"]+=int((parts["SY"]&~any_other&pt_known).sum())
                        counts[source_tag+"|SX_exactly_one_other_aspector"]+=int((parts["SX"]&(asp.sum(axis=1)==1)).sum())
                        counts[source_tag+"|SX_multiple_other_aspectors"]+=int((parts["SX"]&(asp.sum(axis=1)>1)).sum())
                        for state,mask in parts.items():
                            counts[source_tag+"|"+state]+=int(mask.sum())
                            counts["Ptolemy_"+source_tag+"|"+state]+=int((pt_known&mask).sum())
                            if state in ("S3","SY","SX","LATER"):
                                for k,name in enumerate(PLANETS):
                                    counts[source_tag+"|"+state+"_ASC_lord_"+name]+=int((mask&(lord==k)).sum())
                        for k,name in enumerate(PLANETS):
                            counts[source_tag+"|S3_dispositor_"+name]+=int((parts["S3"]&(disp==k)).sum())
                            counts[source_tag+"|SX_other_aspector_"+name]+=int((parts["SX"]&asp[:,k]).sum())
                            counts[source_tag+"|SY_other_aspector_"+name]+=int((parts["SY"]&asp[:,k]).sum())
                        counts[source_tag+"|S3_same_conditional_Ptolemy_lord"]+=int((parts["S3"]&(lord==Ptolemy)).sum())
                        all48_S3&=parts["S3"]
                        all48_SY&=parts["SY"]
                        all48_SX&=parts["SX"]
                        all48_LATER&=parts["LATER"]
                        if np.any(parts["SY"]&known_hd):
                            arr=hd.setdefault(source_tag+"|SY",np.zeros(HD_STATES,dtype=bool))
                            arr[source_ids[parts["SY"]&known_hd]]=True
                        count_models+=1
    if count_models!=STAGE_COUNT:
        raise RuntimeError("Source 48 original S1/S2/S3/SX branches incomplete")
    statuses={"S3":all48_S3,"SY":all48_SY,"SX":all48_SX,"LATER":all48_LATER}
    for state,mask in statuses.items():
        counts["all48_same_"+state]+=int(mask.sum())
        counts["all48_same_"+state+"_conditional_Ptolemy"]+=int((mask&pt_known).sum())
        if state=="S3":
            counts["all48_S3_same_ASC_lord_as_Ptolemy"]+=int((mask&(lord==Ptolemy)).sum())
        if np.any(mask&known_hd):
            arr=hd.setdefault("all48_"+state,np.zeros(HD_STATES,dtype=bool))
            arr[source_ids[mask&known_hd]]=True


def run(west,angles,hd_cache,hd_join,verify_sha=True):
    if swe.version!="2.10.03":raise RuntimeError("Frozen source Swiss 2.10.03 changed")
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    wj=json.loads(wp.read_bytes());wjm=json.loads(wm.read_bytes())
    aj=json.loads(ap.read_bytes());ajm=json.loads(am.read_bytes())
    prev=s1.base.es.src.PRIOR
    population=prev.base.reg.initial.check_manifest(wj,wjm,aj,ajm)
    if population!=N:raise RuntimeError("Source prior finite 3.5m UTC samples changed")
    sha=prev.base.reg.initial.source_hash
    if wjm["plan_sha256"]!=sha(wp) or ajm["plan_sha256"]!=sha(ap):
        raise RuntimeError("Original source data plans changed")
    hdproof=prev.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    hj=json.loads((hd_join/"manifest.json").read_bytes())
    if (hj["total_utc_grid_samples"]!=N or hj["total_hd_structural_intervals"]!=HD_STATES
        or hj["unresolved_near_boundary_samples"]!=125):
        raise RuntimeError("Original HD structural source changed")
    earlier=json.loads((Path(__file__).resolve().parents[1]/"reference/research/lilly_cvii_all_other_planets_full_century_public_v01.json").read_bytes())["counts"]
    jd=prev.base.reg.julian_from_utc(wj["utc_start_inclusive"])
    lat=float(aj["latitude"]);lon=float(aj["longitude"])
    counter=Counter();H={}
    first=0
    for w,a,h in zip(wjm["chunks"],ajm["shards"],hj["shards"],strict=True):
        n=w["count"]
        if not (w["first_index"]==first==a["first_index"]==h["index_first"] and h["count"]==n):
            raise RuntimeError("Original source shard UTC clock misalignment")
        pp=west/"chunks"/w["file"];aa=angles/"shards"/a["file"];hh=hd_join/"shards"/h["file"]
        if pp.stat().st_size!=n*64 or aa.stat().st_size!=n*136 or hh.stat().st_size!=n*4:
            raise RuntimeError("Original 108 binary shard size invalid")
        if verify_sha:
            for p,record in ((pp,w),(aa,a),(hh,h)):
                if sha(p)!=record["sha256"]:
                    raise RuntimeError("Frozen original primary source shard SHA mismatch")
        P=np.memmap(pp,dtype="<f8",mode="r",shape=(n,8))
        A=np.memmap(aa,dtype="<f8",mode="r",shape=(n,17))
        IDs=np.memmap(hh,dtype="<i4",mode="r",shape=(n,))
        C1=np.empty(n);C2=np.empty(n)
        for i in range(n):
            cc,_=swe.houses_ex(jd+(first+i)/96.,lat,lon,b"R")
            C1[i]=cc[0];C2[i]=cc[1]
        if np.max(np.abs((C1-A[:,0]+180)%360-180))>0.0002:
            raise RuntimeError("Original ASC site source drift")
        scan_chunk(P,A,IDs,cusp1=C1,cusp2=C2,counts=counter,hd=H)
        first+=n
    if not verify_sha or first!=N or counter["original_UTC_sample_count"]!=N:
        raise RuntimeError("Actual source entire declared century not audited")
    if (counter["HD_root_margin_unknown"]!=125 or counter["conditional_Ptolemy_fourmode_common"]!=4553
        or counter["Ptolemy_in_HD_unknown"]!=0):
        raise RuntimeError("Frozen source Ptolemy/HD population changed")
    for mode in MODES:
        for orb in ORBS:
            for scope in JOIN_SCOPES:
                for behold in BEHOLDS:
                    for contact in CONTACTS:
                        key="|".join((mode,orb,scope,behold,"all="+contact))
                        for partile in old.PARTILES:
                            earlier_key="|".join((mode,orb,scope,behold,partile,"all="+contact))
                            if (counter[key+"|S1"]!=earlier[earlier_key+"|S1"] or
                                counter[key+"|S2"]!=earlier[earlier_key+"|S2"] or
                                counter[key+"|S3"]!=earlier[earlier_key+"|S3"]):
                                raise RuntimeError("Prior original S1/S2/S3 stage evidence changed")
                            if (counter[key+"|SX"]+counter[key+"|SY_with_other_aspecting"]!=
                                earlier[earlier_key+"|SX"]):
                                raise RuntimeError("Older source SX must include unknown self-dispositor-with-another-aspect")
                            if (counter[key+"|LATER"]+counter[key+"|SY_without_other_aspecting"]!=
                                earlier[earlier_key+"|S4"]+earlier[earlier_key+"|S5"]):
                                raise RuntimeError("Older S4/S5 must include self-as-dispositor-without-other-aspect")
                            if (counter["Ptolemy_"+key+"|S3"]!=earlier["Ptolemy_"+earlier_key+"|S3"] or
                                counter["Ptolemy_"+key+"|SX"]+
                                counter["Ptolemy_"+key+"|SY_with_other_aspecting"]!=
                                earlier["Ptolemy_"+earlier_key+"|SX"]):
                                raise RuntimeError("Previously frozen conditional Ptolemy third stage source changed")
                            if (counter["Ptolemy_"+key+"|LATER"]+
                                counter["Ptolemy_"+key+"|SY_without_other_aspecting"]!=
                                earlier["Ptolemy_"+earlier_key+"|S4"]+
                                earlier["Ptolemy_"+earlier_key+"|S5"]):
                                raise RuntimeError("Previously frozen Ptolemy later stage conditional census changed")
                        if sum(counter[key+"|"+name] for name in ("S1","S2","S3","SY","SX","LATER"))!=N:
                            raise RuntimeError("Missing original source sample/duplicate stage")
                        if counter[key+"|SY_with_other_aspecting"]+counter[key+"|SY_without_other_aspecting"]!=counter[key+"|SY"]:
                            raise RuntimeError("One self-dispositor status not assigned")
                        if counter[key+"|SX_exactly_one_other_aspector"]+counter[key+"|SX_multiple_other_aspectors"]!=counter[key+"|SX"]:
                            raise RuntimeError("Another-planet source aspector identities incomplete")
    return {
      "schema":"lilly_1647_CVII_S3_original_ASC_lord_dispositor_and_other_aspect_self_gap_century_v01",
      "status":"ORIGINAL_S3_SX_SELF_DISPOSITOR_SOURCE_CONDITIONAL_ONLY_HISTORICAL_RULER_OPEN",
      "source_original":"Lilly Christian Astrology 1647 first printing CVII pp535-536 and original p107 planet moiety bounds",
      "original_p536_render_SHA256":"4cdd11d5cf468e20f38fed7889e42f2e6298540e05f7f196c9b916e28bb57b24",
      "source_horizon_UTC":[wj["utc_start_inclusive"],wj["utc_end_exclusive"]],
      "samples":N,"one_fixed_research_location":True,"step_minutes":15,
      "original_planet_site_HD_shard_SHA256_rechecked":verify_sha,
      "HD_source_audit":hdproof,"HD_structural_intervals":HD_STATES,
      "source_manifest_SHA256":{"planet":sha(wm),"site":sha(am),"HD":sha(hd_join/"manifest.json")},
      "source_p535_S1_place_variants":list(MODES),
      "source_p107_moiety_variants":{k:v.tolist() for k,v in ORBS.items()},
      "source_p536_S2_joining_candidate_scope_variants":list(JOIN_SCOPES),
      "source_S3_dispositor_beholding_variants":list(BEHOLDS),
      "source_other_aspector_modes":list(CONTACTS),
      "number_source_S3_SX_self_interpretations":STAGE_COUNT,
      "S3_source_provisional_manners_planet":"ASC_lord (domicile ruler of original rising sign), if a DISTINCT domicile dispositor beholds it under the declared ray policy; source conditional only",
      "SY_source_ambiguity":"ASC lord occupies OWN domicile, therefore is own dispositor; original 'dispositor behold him' cannot be literally evaluated as a different-planet aspect; conservatively abstain rather than force original S4/S5",
      "SX_source_ambiguity":"Some OTHER classical planet aspects ASC lord but its different domicile dispositor does NOT; no unique historical next rule appointed by p536 wording",
      "LATER_source_condition":"No S1, S2, distinct dispositor aspect, self-as-dispositor or any other classical planet aspect under declared ray/body scope; later partile and essential dignity rules OPEN",
      "counts":dict(counter),
      "HD_distinct_intervals_per_source_category":{key:int(arr.sum()) for key,arr in H.items()},
      "original_96_variant_S1_S2_S3_SX_S4_S5_count_reconciliation":True,
      "historically_actual_complete_Lilly_manners_ruler":False,
      "historically_actual_complete_Ptolemy_soul_governor":False,
      "independently_validated_human_personality_accuracy":False,
      "private_owner_or_thirdparty_natal_case_source_used":False,
    }


def main():
    parser=argparse.ArgumentParser()
    for arg in ("west","angles","hd-cache","hd-join","out"):
        parser.add_argument("--"+arg,type=Path,required=True)
    a=parser.parse_args()
    if a.out.exists():raise FileExistsError("Do not overwrite immutable original century source receipt")
    j=run(a.west,a.angles,a.hd_cache,a.hd_join)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(j,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":j["status"],"sample_count":j["samples"],
      "source_policy_count":j["number_source_S3_SX_self_interpretations"]},sort_keys=True))

if __name__=="__main__":main()
