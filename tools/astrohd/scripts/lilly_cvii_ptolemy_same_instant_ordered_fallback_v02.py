#!/usr/bin/env python3
"""William Lilly, original 1647 printed pages 106,107,110 and 535-536.

Full finite same-UTC century census, source-conditioned FIRST and FALLBACK
geometry only, never a uniquely source-determined manners significator.
The 1647 p107 printed orb TABLE includes author variants. Its two bounding
sets are carried as DISTINCT policies, not cherry-picked after reading natal
profiles; p106 describes a PARTILL aspect with matching numbered degrees
and p107 a PLATICK aspect within planetary MOIETIES (half sum of orbs).
The CVII p536 'joyned' does not specify which table row or priority to use.
Three rival first-stage interpretations stay independent. 'Behold' as sign
aspect vs ray within moiety and 'partile Moon or/and Mercury' also diverge.

Original source cached 7 classical tropical longitudes, ASC, site angles
and HD structural interval join; no respondent natal date or case loaded.
Original 36+36+36 source shard hashes checked; 125 HD-root instants abstain.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
import swisseph as swe
import ptolemy_lilly_same_instant_century_v01 as base
import ptolemy_lilly_hd_same_instant_century_v01 as hd_source
import ptolemy_iii13_latitude_certified_same_instant_century_v01 as ptolemy_source

PLANETS=("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn")
# planet index based on source column: Sun0, Moon1, Mercury2, Venus3,
# Mars4, Jupiter5, Saturn6. Original Lilly p107 tabular alternatives:
# Saturn 10/9, Jupiter 12/9, Mars 7.5/7, Sun17/15, Venus8/7,
# Mercury7, Moon12.5/12. These bundles are componentwise EXTREMES,
# not exhaustive choices or a modern orb rule asserted unique in CVII.
SOURCE_ORBS={
 "1647_table_smaller_orbs":np.array([15.,12.,7.,7.,7.,9.,9.]),
 "1647_table_larger_orbs":np.array([17.,12.5,7.,8.,7.5,12.,10.])
}
MODES=("ascending_sign","regiomontanus_first_house",
       "ascending_sign_or_intercepted_sign")
JOINS=("four_externals_only","all_other_classical_planets")
BEHOLDS=("dispositor_sign_ray","dispositor_orb_near_ray")
PARTILES=("partile_Moon_or_Mercury","partile_same_planet_Moon_and_Mercury")
ASPECTS=np.array([60.,90.,120.,180.,240.,270.,300.])
SEEING_SIGN_DELTAS=np.array([2,3,4,6,8,9,10])
TOTAL=3506400
HD_STATES=288908

def angle_distance(a,b):
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
    return np.abs((a-b+180.)%360.-180.)

def partile_numbered_ray(a,b):
    """Original p106 matching numbered zodiacal degrees, nonbody rays."""
    a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float)
    if a.shape!=b.shape:raise ValueError("partile arrays not aligned")
    sign_diff=(np.floor(a/30).astype(int)-np.floor(b/30).astype(int))%12
    is_ray=np.isin(sign_diff,SEEING_SIGN_DELTAS)
    degree_a=np.floor(a%30).astype(int)
    degree_b=np.floor(b%30).astype(int)
    return is_ray&(degree_a==degree_b)

def ray_residual(a,b):
    delta=(np.asarray(a,dtype=float)-np.asarray(b,dtype=float)+360.)%360.
    return np.min(np.abs((delta[...,None]-ASPECTS+180)%360-180),axis=-1)

def orb_join(p,orbs,*,scope):
    """Planet joined to Moon/Mercury by source-table orbital moieties."""
    x=np.asarray(p,dtype=float)
    if x.ndim!=2 or x.shape[1]!=7:raise ValueError("7 classical longitudes")
    if scope not in JOINS:raise ValueError("Source variant absent")
    included=(3,4,5,6) if scope==JOINS[0] else (0,3,4,5,6)
    witness_moon=np.zeros(len(x),dtype=bool)
    witness_mercury=np.zeros(len(x),dtype=bool)
    both_same_planet=np.zeros(len(x),dtype=bool)
    for k in included:
        m=angle_distance(x[:,k],x[:,1]) <= (orbs[k]+orbs[1])/2
        e=angle_distance(x[:,k],x[:,2]) <= (orbs[k]+orbs[2])/2
        witness_moon|=m;witness_mercury|=e
        both_same_planet|=m&e
    # All classical bodies option includes Moon-Mercury mutual contact,
    # potentially one reciprocal witness, but never automatically declares
    # an unfortified luminary a strong manners ruler.
    mutual=angle_distance(x[:,1],x[:,2])<=(orbs[1]+orbs[2])/2
    allw=witness_moon|witness_mercury
    if scope==JOINS[1]:allw|=mutual
    return {"any_joined":allw,"both_same_planet":both_same_planet,
            "Moon_Mercury_mutual":mutual}

def dispositor_see(p,asc,orbs):
    """ASC lord's domicile dispositor may aspect it. Self is UNKNOWN."""
    x=np.asarray(p,dtype=float);asc=np.asarray(asc,dtype=float)
    if x.ndim!=2 or x.shape[1]!=7 or asc.shape!=(len(x),):
        raise ValueError("Lilly dispositor arguments misaligned")
    idx=np.arange(len(x))
    rul=base.four.pt3.ptolemy2.DOMICILE[np.floor(asc/30).astype(int)]
    lord_lon=x[idx,rul]
    disp=base.four.pt3.ptolemy2.DOMICILE[np.floor(lord_lon/30).astype(int)]
    same=(disp==rul)
    disp_lon=x[idx,disp]
    sign_diff=(np.floor(lord_lon/30).astype(int)-
               np.floor(disp_lon/30).astype(int))%12
    raysign=(~same)&np.isin(sign_diff,SEEING_SIGN_DELTAS)
    near=(~same)&(ray_residual(lord_lon,disp_lon)<=
                 (orbs[rul]+orbs[disp])/2)
    return {"same_as_own_dispositor":same,"dispositor_sign_ray":raysign,
            "dispositor_orb_near_ray":near}

def partile_candidates(p):
    """Original p106 numbered-degree partile witness, source 'forcible' unknown."""
    x=np.asarray(p,dtype=float)
    if x.ndim!=2 or x.shape[1]!=7:raise ValueError("seven longitudes required")
    lunar=np.zeros(len(x),dtype=bool)
    merc=np.zeros(len(x),dtype=bool)
    both=np.zeros(len(x),dtype=bool)
    # Moon and Mercury cannot partile aspect THEMSELVES; Sun and other
    # traditional planets are separately eligible until fortification audit.
    for k in (0,3,4,5,6):
        m=partile_numbered_ray(x[:,k],x[:,1])
        e=partile_numbered_ray(x[:,k],x[:,2])
        lunar|=m;merc|=e;both|=(m&e)
    return {"partile_Moon_or_Mercury":lunar|merc,
            "partile_same_planet_Moon_and_Mercury":both,
            "partile_to_Moon":lunar,"partile_to_Mercury":merc}

def stage_masks(first,join,seeing,partile):
    """Mutually exclusive ordered GEOMETRIC path, strength unresolved."""
    f=np.asarray(first,dtype=bool)
    j=np.asarray(join,dtype=bool)
    see=np.asarray(seeing,dtype=bool)
    part=np.asarray(partile,dtype=bool)
    if not (f.shape==j.shape==see.shape==part.shape):
        raise ValueError("Same-UTC sample alignment required")
    residual=~f
    stage2=residual&j
    residual&=~j
    stage3=residual&see
    residual&=~see
    stage4=residual&part
    stage5=residual&~part
    result=(f,stage2,stage3,stage4,stage5)
    if not np.all(sum(z.astype(np.uint8) for z in result)==1):
        raise RuntimeError("Lilly fallback accounting failed")
    return result

def calc_chunk(p,a,ids,*,jd0,index_first,lat,lon,counts,hd_sets):
    x=np.asarray(p,dtype=float);q=np.asarray(a,dtype=float)
    ids=np.asarray(ids,dtype=np.int32)
    n=len(x)
    if x.shape!=(n,8) or q.shape!=(n,17) or ids.shape!=(n,):
        raise ValueError("Source indexes not aligned")
    cusps=np.empty((n,2))
    for i in range(n):
        r,arms=swe.houses_ex(jd0+(index_first+i)/96,lat,lon,b'R')
        cusps[i]=r[:2]
    if np.max(angle_distance(cusps[:,0],q[:,0]))>0.0002:
        raise RuntimeError("Regiomontanus ASC does not match source")
    classes=base.first_house_and_intercepted(x[:,:7],cusps[:,0],cusps[:,1])
    part=partile_candidates(x[:,:7])
    known=ids>=0
    ptolemy_common=ptolemy_source.conditional_all_four_common_leader(x,q[:,4])>=0
    counts["ptolemy_robust_all_four_variant_common"]+=int(ptolemy_common.sum())
    counts["ptolemy_robust_common_HD_unknown"]+=int((ptolemy_common&~known).sum())
    counts["rows"]+=n
    counts["HD_boundary_abstentions"]+=int((~known).sum())
    for mode in MODES:
        counts["first_"+mode]+=int(classes[mode].sum())
    for orbname,orbs in SOURCE_ORBS.items():
        see=dispositor_see(x[:,:7],q[:,0],orbs)
        counts["self_dispositor_"+orbname]+=int(see["same_as_own_dispositor"].sum())
        for joinname in JOINS:
            joined=orb_join(x[:,:7],orbs,scope=joinname)
            counts["joined_both_"+orbname+"_"+joinname]+=int(joined["both_same_planet"].sum())
            for mode in MODES:
                for seeingname in BEHOLDS:
                    for partname in PARTILES:
                        tag="|".join((mode,orbname,joinname,seeingname,partname))
                        stages=stage_masks(classes[mode],joined["any_joined"],
                                see[seeingname],part[partname])
                        for number,mask in enumerate(stages,1):
                            key=tag+"|S"+str(number)
                            counts[key]+=int(mask.sum())
                            counts["same_instant_Ptolemy_"+key]+=int((mask&ptolemy_common).sum())
                            joint=ids[mask&ptolemy_common&known]
                            if len(joint):
                                ptkey="same_instant_Ptolemy_"+key
                                hd_sets.setdefault(ptkey,np.zeros(HD_STATES,dtype=bool))[joint]=True
                            selected=ids[mask&known]
                            if len(selected):
                                # True same-instant linkage to HD *state* IDs,
                                # never a natal personality or participant score.
                                dest=hd_sets.setdefault(key,np.zeros(HD_STATES,dtype=bool))
                                dest[selected]=True
    return counts

def run(west,angles,hd_cache,hd_join,hashes=True):
    if swe.version!="2.10.03":raise RuntimeError("Swiss version changed")
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    pw=json.loads(wp.read_bytes());mw=json.loads(wm.read_bytes())
    pa=json.loads(ap.read_bytes());ma=json.loads(am.read_bytes())
    total=base.reg.initial.check_manifest(pw,mw,pa,ma)
    if total!=TOTAL:raise RuntimeError("Not the previously frozen century")
    if mw["plan_sha256"]!=base.reg.initial.source_hash(wp) or ma["plan_sha256"]!=base.reg.initial.source_hash(ap):
        raise RuntimeError("Frozen planetary/angle plan altered")
    proof=hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    hm=json.loads((hd_join/"manifest.json").read_bytes())
    if (hm["total_utc_grid_samples"]!=total or hm["unresolved_near_boundary_samples"]!=125 or
        hm["total_hd_structural_intervals"]!=HD_STATES):
        raise RuntimeError("HD join timeline or boundary uncertainty changed")
    jj=base.reg.julian_from_utc(pw["utc_start_inclusive"])
    lat=float(pa["latitude"]);lon=float(pa["longitude"])
    c=Counter(); states={}
    index=0
    for w,a,h in zip(mw["chunks"],ma["shards"],hm["shards"],strict=True):
        k=w["count"]
        if w["first_index"]!=index or a["first_index"]!=index or h["index_first"]!=index or h["count"]!=k:
            raise RuntimeError("UTC shard indices not identical")
        bp=west/"chunks"/w["file"];ba=angles/"shards"/a["file"]
        if bp.stat().st_size!=k*64 or ba.stat().st_size!=k*136:
            raise RuntimeError("Original source binary length changed")
        if hashes and (base.reg.initial.source_hash(bp)!=w["sha256"] or
           base.reg.initial.source_hash(ba)!=a["sha256"]):
            raise RuntimeError("Original source SHA256 mismatch")
        p=np.memmap(bp,dtype="<f8",shape=(k,8),mode="r")
        q=np.memmap(ba,dtype="<f8",shape=(k,17),mode="r")
        ids=np.memmap(hd_join/"shards"/h["file"],dtype="<i4",shape=(k,),mode="r")
        calc_chunk(p,q,ids,jd0=jj,index_first=index,lat=lat,lon=lon,
                   counts=c,hd_sets=states)
        index+=k
    if index!=TOTAL or c["rows"]!=TOTAL or c["HD_boundary_abstentions"]!=125:
        raise RuntimeError("Sample population/boundary conservation failed")
    if c["ptolemy_robust_all_four_variant_common"]!=4553 or c["ptolemy_robust_common_HD_unknown"]!=0:
        raise RuntimeError("Prior same-instant Ptolemy source baseline drift")
    for m,v in (("ascending_sign",1428060),("regiomontanus_first_house",1409411),
                ("ascending_sign_or_intercepted_sign",1516373)):
        if c["first_"+m]!=v:raise RuntimeError("Original first-stage baseline drift")
    for orbname in SOURCE_ORBS:
        for joinname in JOINS:
            for mode in MODES:
                for see in BEHOLDS:
                    for part in PARTILES:
                        prefix="|".join((mode,orbname,joinname,see,part))
                        if sum(c[prefix+"|S"+str(n)] for n in range(1,6))!=TOTAL:
                            raise RuntimeError("Not all 5 original-stage labels covered")
                        if sum(c["same_instant_Ptolemy_"+prefix+"|S"+str(n)] for n in range(1,6))!=4553:
                            raise RuntimeError("Joint Ptolemy/Lilly stages fail conservation")
                        expected_first={"ascending_sign":1746,"regiomontanus_first_house":1920,
                                        "ascending_sign_or_intercepted_sign":1865}[mode]
                        if c["same_instant_Ptolemy_"+prefix+"|S1"]!=expected_first:
                            raise RuntimeError("Earlier Ptolemy+Lilly first-stage check differs")
    return {
      "schema":"lilly_CVII_1647_Ptolemy_consensus_ordered_fallback_full_UTC_century_v02",
      "status":"SOURCE_CONDITIONED_FIVE_STAGE_CENSUS_NO_FINAL_MANNERS_SIGNIFICATOR",
      "UTC_horizon":[pw["utc_start_inclusive"],pw["utc_end_exclusive"]],
      "original_UTC_grid_samples":TOTAL,"minute_step":15,
      "source_first_print":"Lilly 1647 pp106-107,110 and 535-536 photographed original; historical orbs vary explicitly",
      "orb_source_variants":{key:dict(zip(PLANETS,value.tolist())) for key,value in SOURCE_ORBS.items()},
      "first_rules":list(MODES),"joined_rules":list(JOINS),
      "dispositor_seeing_rules":list(BEHOLDS),"partile_fallback_rules":list(PARTILES),
      "interpretation_of_partile":"same-numbered degree within zodiac signs separated by traditional ray; not exact continuous angular residual",
      "source_status":"Lilly's strength, dispositors, appropriateness of unfortified luminary, joining orbs in CVII, and final dignities cannot be source-uniquely adjudicated",
      "full_source_Sha256_rechecked":hashes,
      "hd_source_join":proof,
      "original_planet_manifest_sha256":base.reg.initial.source_hash(wm),
      "original_angles_manifest_sha256":base.reg.initial.source_hash(am),
      "original_HD_join_manifest_sha256":hd_source.hdverify.digest(hd_join/"manifest.json"),
      "counts":dict(c),
      "HD_interval_counts":{k:int(v.sum()) for k,v in states.items()},
      "missing_effect_size_and_human_accuracy":True,
      "personal_natal_interview_inputs_loaded":False,
      "same_instant_ptolemy_screen":"4,553 source-conditional robust four-mode common leader across four terms/triplicity choices, not actual soul governor or human prediction",
      "actual_manners_significator_selected":False
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("west","angles","hd-cache","hd-join","out"):
        p.add_argument("--"+name,type=Path,required=True)
    z=p.parse_args()
    if z.out.exists():raise FileExistsError("Versioned source receipt must be immutable")
    result=run(z.west,z.angles,z.hd_cache,z.hd_join)
    z.out.parent.mkdir(parents=True,exist_ok=True)
    z.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"rows":result["original_UTC_grid_samples"],
                      "scope":["source-only","no personality rank"]},sort_keys=True))
if __name__=="__main__":main()
