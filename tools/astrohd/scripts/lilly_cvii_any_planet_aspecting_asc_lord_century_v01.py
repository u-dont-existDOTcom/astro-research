#!/usr/bin/env python3
"""Lilly 1647 CVII p536: broad "If no Planet aspect him" sensitivity.

P536 first says ASC lord may signify *provided its dispositor beholds it*.
It then says "If no Planet aspect him", which need not mean "if the
dispositor fails to aspect". A third case is now explicitly flagged:
another planet aspects the ASC lord but the dispositor does not. The
original text does NOT give that case an unambiguous manners significator.

This version retains the earlier frozen five-stage census exactly; it
splits the former stage 4/5 into (A) unresolved other-aspect blocker and
(B) actually eligible for the partile/final-dignity consideration.

Predeclared alternatives:
* 3 initial branches: ASC sign / real Regiomontanus house / rising-or-intercepted
* 2 Lilly original printed smaller/larger orb envelopes
* 2 joining inclusion scopes
* 2 ways a dispositor beholds the ASC lord: sign rays / moiety-to-ray
* 2 partile-reading alternatives: Moon OR Mercury / both same candidate
* 2 broad "any other planet" rules: rays-only / rays-or-bodily conjunction
= 96 source-conditioned separate interpretations. No rank or human profiles.

The original 3,506,400 fixed-place UTC 15-min source samples, original
36+36 western shards, 36 HD-index shards and independent 288,908-state HD
cache are hash-audited. 125 root-margin HD assignments remain abstentions.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
import swisseph as swe

import lilly_cvii_ptolemy_same_instant_ordered_fallback_v02 as prior

SOURCE_EPOCH="Lilly Christian Astrology 1647 p536"
CONTACT_CLASSES=("rays_only","rays_or_bodily")
HD_STATES=prior.HD_STATES
SAMPLE_COUNT=prior.TOTAL


def aspects_to_asc_lord(planets,asc,orbs):
    """Every OTHER classical planet, not only the lord's dispositor.

    An aspect by traditional nonconjunction ray is distinct from joining
    by body. Both are source-conditioned alternatives; no claim that
    Lilly's 'aspect him' unambiguously includes conjunctions.
    """
    p=np.asarray(planets,dtype=np.float64)
    a=np.asarray(asc,dtype=np.float64)
    o=np.asarray(orbs,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or a.shape!=(len(p),) or o.shape!=(7,):
        raise ValueError("seven-planet, aligned ASC and seven printed orbs required")
    if not (np.all(np.isfinite(p)) and np.all(np.isfinite(a)) and np.all(np.isfinite(o))):
        raise ValueError("finite astrology coordinates/orbs required")
    if np.any((p<0)|(p>=360)) or np.any((a<0)|(a>=360)) or np.any(o<=0):
        raise ValueError("normalized zodiac and positive orbital widths required")
    i=np.arange(len(p))
    lord_idx=prior.base.four.pt3.ptolemy2.DOMICILE[np.floor(a/30).astype(np.int8)]
    lord_lon=p[i,lord_idx]
    near_sign=np.zeros(len(p),dtype=bool)
    near_ray=np.zeros(len(p),dtype=bool)
    bodily=np.zeros(len(p),dtype=bool)
    for k in range(7):
        other=k!=lord_idx
        sep=(np.floor(p[:,k]/30).astype(np.int16)-
             np.floor(lord_lon/30).astype(np.int16))%12
        signray=np.isin(sep,prior.SEEING_SIGN_DELTAS)
        threshold=(o[k]+o[lord_idx])/2
        actual=prior.ray_residual(p[:,k],lord_lon)<=threshold
        conjunction=prior.angle_distance(p[:,k],lord_lon)<=threshold
        near_sign|=other&signray
        near_ray|=other&actual
        bodily|=other&conjunction
    return {
       "dispositor_sign_ray":{"rays_only":near_sign,
                             "rays_or_bodily":near_sign|bodily},
       "dispositor_orb_near_ray":{"rays_only":near_ray,
                                 "rays_or_bodily":near_ray|bodily}
    }


def split_six(first,joining,dispositor,any_planet_aspect,partile):
    """Five previous stages, split old R4/R5 when OTHER planet sees ASC lord.

    Ordered categories: S1 primary, S2 joined, S3 dispositor-sees-lord,
    SX *other* aspect but no dispositor (ABSTAIN), S4 forceful partile
    if literally NO planet aspects lord, S5 next dignity fallback.
    """
    arrays=[np.asarray(a,dtype=bool) for a in
            (first,joining,dispositor,any_planet_aspect,partile)]
    if len({a.shape for a in arrays})!=1 or arrays[0].ndim!=1:
        raise ValueError("Same-instant aligned 1D condition arrays required")
    f,j,d,anysee,part=arrays
    if np.any(d&~anysee):
        raise RuntimeError("Dispositor is a planet: its aspect must be included in all-planet set")
    rem=~f
    s2=rem&j
    rem&=~j
    s3=rem&d
    rem&=~d
    sx=rem&anysee
    rem&=~anysee
    s4=rem&part
    s5=rem&~part
    stages=(f,s2,s3,sx,s4,s5)
    if not np.all(sum(x.astype(np.int8) for x in stages)==1):
        raise RuntimeError("Six source-conditioned categories fail one-per-UTC-sample conservation")
    baseline=prior.stage_masks(f,j,d,part)
    if not all(np.array_equal(x,y) for x,y in zip(stages[:3],baseline[:3])):
        raise RuntimeError("Earlier Lilly source-stage order changed")
    if not np.array_equal(baseline[3],s4|(sx&part)):
        raise RuntimeError("Earlier partile-stage conservation broken")
    if not np.array_equal(baseline[4],s5|(sx&~part)):
        raise RuntimeError("Earlier remaining-dignity-stage conservation broken")
    return stages


def count_chunk(p,a,ids,*,jd0,first_index,lat,lon,counters,hd_presence):
    x=np.asarray(p,dtype=np.float64);q=np.asarray(a,dtype=np.float64)
    hd_ids=np.asarray(ids,dtype=np.int32)
    n=len(x)
    if x.shape!=(n,8) or q.shape!=(n,17) or hd_ids.shape!=(n,):
        raise ValueError("Earlier source binary matrix shape changed")
    cusps=np.empty((n,2),dtype=np.float64)
    for t in range(n):
        cc,_=swe.houses_ex(jd0+(first_index+t)/96.,lat,lon,b"R")
        cusps[t,0]=cc[0];cusps[t,1]=cc[1]
    if np.max(prior.angle_distance(cusps[:,0],q[:,0]))>0.0002:
        raise RuntimeError("New Regiomontanus ASC not bound to original source")
    classes=prior.base.first_house_and_intercepted(x[:,:7],cusps[:,0],cusps[:,1])
    part=prior.partile_candidates(x[:,:7])
    ptolemy=prior.ptolemy_source.conditional_all_four_common_leader(x,q[:,4])>=0
    known=hd_ids>=0
    counters["total_utc_samples"]+=n
    counters["HD_boundary_abstained"]+=int((~known).sum())
    counters["ptolemy_four_variant_robust_consensus"]+=int(ptolemy.sum())
    counters["ptolemy_consensus_boundary_unknown"]+=int((ptolemy&~known).sum())

    for orbname,orbs in prior.SOURCE_ORBS.items():
        disposer=prior.dispositor_see(x[:,:7],q[:,0],orbs)
        anyplanet=aspects_to_asc_lord(x[:,:7],q[:,0],orbs)
        for joinname in prior.JOINS:
            joined=prior.orb_join(x[:,:7],orbs,scope=joinname)
            for firststage in prior.MODES:
                for seen in prior.BEHOLDS:
                    for partname in prior.PARTILES:
                        basekey="|".join((firststage,orbname,joinname,seen,partname))
                        oldstage=prior.stage_masks(classes[firststage],
                                                  joined["any_joined"],
                                                  disposer[seen],part[partname])
                        for j,mask in enumerate(oldstage,1):
                            k=basekey+"|S"+str(j)
                            counters["earlier_"+k]+=int(mask.sum())
                            counters["earlier_Ptolemy_"+k]+=int((mask&ptolemy).sum())

                        for contact in CONTACT_CLASSES:
                            all_aspect=anyplanet[seen][contact]
                            new=split_six(classes[firststage],joined["any_joined"],
                                          disposer[seen],all_aspect,part[partname])
                            prefix=basekey+"|all="+contact
                            for stageid,mask in zip(("S1","S2","S3","SX","S4","S5"),new):
                                key=prefix+"|"+stageid
                                counters[key]+=int(mask.sum())
                                counters["Ptolemy_"+key]+=int((mask&ptolemy).sum())
                                a_ids=hd_ids[mask&known]
                                b_ids=hd_ids[mask&known&ptolemy]
                                if len(a_ids):
                                    arr=hd_presence.setdefault(key,np.zeros(HD_STATES,dtype=bool))
                                    arr[a_ids]=True
                                if len(b_ids):
                                    tag="Ptolemy_"+key
                                    arr=hd_presence.setdefault(tag,np.zeros(HD_STATES,dtype=bool))
                                    arr[b_ids]=True
                            blocker=new[3]
                            counters[prefix+"|blocked_partile"]+=int((blocker&part[partname]).sum())
                            counters[prefix+"|blocked_final_dignity"]+=int((blocker&~part[partname]).sum())


def run(west,angles,hd_cache,hd_join,verify_shards=True):
    if swe.version!="2.10.03":raise RuntimeError("Swiss ephemeris version changed")
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    wj=json.loads(wp.read_bytes());wjm=json.loads(wm.read_bytes())
    aj=json.loads(ap.read_bytes());ajm=json.loads(am.read_bytes())
    n=prior.base.reg.initial.check_manifest(wj,wjm,aj,ajm)
    if n!=SAMPLE_COUNT:raise RuntimeError("Wrong time universe")
    if (wjm["plan_sha256"]!=prior.base.reg.initial.source_hash(wp) or
        ajm["plan_sha256"]!=prior.base.reg.initial.source_hash(ap)):
        raise RuntimeError("Original source plans changed")
    proof=prior.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    hj=json.loads((hd_join/"manifest.json").read_bytes())
    if (hj["total_utc_grid_samples"]!=n or hj["unresolved_near_boundary_samples"]!=125
        or hj["total_hd_structural_intervals"]!=HD_STATES):
        raise RuntimeError("HD source universe, time population or root margin drift")
    jd=prior.base.reg.julian_from_utc(wj["utc_start_inclusive"])
    lat=float(aj["latitude"]);lon=float(aj["longitude"])
    counts=Counter();hp={}
    current=0
    for western,angleshard,hdpart in zip(wjm["chunks"],ajm["shards"],hj["shards"],strict=True):
        k=western["count"]
        if (western["first_index"]!=current or angleshard["first_index"]!=current
            or hdpart["index_first"]!=current or hdpart["count"]!=k):
            raise RuntimeError("Source shards lose same-UTC alignment")
        bp=west/"chunks"/western["file"]
        ba=angles/"shards"/angleshard["file"]
        bh=hd_join/"shards"/hdpart["file"]
        if (bp.stat().st_size!=k*64 or ba.stat().st_size!=k*136
            or bh.stat().st_size!=k*4):
            raise RuntimeError("Source binary shard byte size drift")
        if verify_shards and (
            prior.base.reg.initial.source_hash(bp)!=western["sha256"] or
            prior.base.reg.initial.source_hash(ba)!=angleshard["sha256"] or
            prior.base.reg.initial.source_hash(bh)!=hdpart["sha256"]):
            raise RuntimeError("Original source binary SHA256 changed")
        p=np.memmap(bp,dtype="<f8",mode="r",shape=(k,8))
        a=np.memmap(ba,dtype="<f8",mode="r",shape=(k,17))
        h=np.memmap(bh,dtype="<i4",mode="r",shape=(k,))
        count_chunk(p,a,h,jd0=jd,first_index=current,lat=lat,lon=lon,
                    counters=counts,hd_presence=hp)
        current+=k
    if (current!=SAMPLE_COUNT or counts["total_utc_samples"]!=SAMPLE_COUNT or
        counts["HD_boundary_abstained"]!=125 or
        counts["ptolemy_four_variant_robust_consensus"]!=4553 or
        counts["ptolemy_consensus_boundary_unknown"]!=0):
        raise RuntimeError("Frozen original population and Ptolemy counts changed")
    oldpath=Path(__file__).resolve().parents[1]/"reference/research/lilly_cvii_ptolemy_same_instant_ordered_fallback_public_v02.json"
    original=json.loads(oldpath.read_bytes())["counts"]
    for method in prior.MODES:
        for orb in prior.SOURCE_ORBS:
            for join in prior.JOINS:
                for behold in prior.BEHOLDS:
                    for partile in prior.PARTILES:
                        basekey="|".join((method,orb,join,behold,partile))
                        for i in range(1,6):
                            k=basekey+"|S"+str(i)
                            if counts["earlier_"+k]!=original[k]:
                                raise RuntimeError("Prior Lilly stage source-bound result differs: "+k)
                            if counts["earlier_Ptolemy_"+k]!=original["same_instant_Ptolemy_"+k]:
                                raise RuntimeError("Prior Ptolemy joint stage differs: "+k)
                        for contact in CONTACT_CLASSES:
                            prefix=basekey+"|all="+contact
                            keys=[prefix+"|"+x for x in ("S1","S2","S3","SX","S4","S5")]
                            if sum(counts[k] for k in keys)!=SAMPLE_COUNT:
                                raise RuntimeError("Broader Lilly stage conservation failure")
                            if sum(counts["Ptolemy_"+k] for k in keys)!=4553:
                                raise RuntimeError("Ptolemy/Lilly stage conservation failure")
                            if (counts[keys[0]]!=original[basekey+"|S1"] or
                                counts[keys[1]]!=original[basekey+"|S2"] or
                                counts[keys[2]]!=original[basekey+"|S3"]):
                                raise RuntimeError("Stage before gap changed in source comparison")
                            if (counts[keys[3]]+counts[keys[4]]+counts[keys[5]] !=
                                original[basekey+"|S4"]+original[basekey+"|S5"]):
                                raise RuntimeError("Source-gap invalidates conservation")
    return {
      "schema":"lilly_cvii_original_any_planet_aspects_asc_lord_source_gap_full_century_v01",
      "status":"COMPETING_HISTORICAL_OTHER_PLANET_RAY_AND_BODILY_SENSITIVITIES_NO_MANNERS_RULER",
      "source":["William Lilly, Christian Astrology 1647 original III CVII p536",
                "1647 original p106/107 general platick and moiety definitions; numeric variants historical and unresolved"],
      "no_human_prediction":True,"source_status":"SOURCE_CONDITIONED_GEOMETRIC_ONLY",
      "start_end_utc":[wj["utc_start_inclusive"],wj["utc_end_exclusive"]],
      "minutes_per_sample":15,"samples":SAMPLE_COUNT,"HD_states":HD_STATES,
      "original_all_source_shard_sha256_rechecked":verify_shards,
      "western_manifest_sha256":prior.base.reg.initial.source_hash(wm),
      "angle_manifest_sha256":prior.base.reg.initial.source_hash(am),
      "HD_join_manifest_sha256":prior.hd_source.hdverify.digest(hd_join/"manifest.json"),
      "HD_source_audit":proof,
      "historical_fork":"The original text conditions ASC lord on dispositor's aspect, then says if no planet aspect him. Other planets may aspect the lord even without dispositor. Those records are SX unresolved, NOT a chosen lord.",
      "six_stage_labels":{"S1":"ASC/first-house condition","S2":"planet joined Moon or Mercury",
                          "S3":"lord's dispositor beholds","SX":"other planet aspect blocks fallback but no source-licensed ruler",
                          "S4":"partile Moon/Mercury when NO planet aspects lord",
                          "S5":"essential dignities and fixed stars uncomputed"},
      "broad_contact_variants":list(CONTACT_CLASSES),
      "source_variants":{"first":list(prior.MODES),"orb_envelope":list(prior.SOURCE_ORBS),
                         "join":list(prior.JOINS),"dispositor":list(prior.BEHOLDS),
                         "partile":list(prior.PARTILES)},
      "counts":dict(counts),
      "HD_distinct_states_by_stage":{k:int(v.sum()) for k,v in hp.items()},
      "actual_Lilly_manners_significator_assigned":False,
      "actual_Ptolemy_soul_governor_assigned":False,
      "original_source_mixed_orb_variants_exhausted":False,
      "human_personal_birth_profile_inputs_used":False
    }

def main():
    p=argparse.ArgumentParser()
    for k in ("west","angles","hd-cache","hd-join","out"):
        p.add_argument("--"+k,required=True,type=Path)
    args=p.parse_args()
    if args.out.exists():raise FileExistsError("Never overwrite a historical source-bound receipt")
    result=run(args.west,args.angles,args.hd_cache,args.hd_join)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"samples":result["samples"],
                      "Ptolemy_shared_conditional":result["counts"]["ptolemy_four_variant_robust_consensus"]},
                     sort_keys=True))
if __name__=="__main__":main()
