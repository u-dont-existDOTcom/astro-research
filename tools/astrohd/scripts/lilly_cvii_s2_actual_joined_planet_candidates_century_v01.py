#!/usr/bin/env python3
"""Original Lilly 1647 CVII p536 second-stage joined-planet candidate identity.

The first stage (S1) was genuinely computed and merged from original p535.
Only if NO S1 primary planet qualifies under one of three historically
disputed source geometries, original p536 asks which planets are joined
to Moon or Mercury. The p107 original printed planet-specific orb moieties
give two bounded alternative geometric conjunction thresholds; p536 DOES
NOT uniquely prescribe an exact orb or choose a lone final winner.

Here we find exact per-planet candidates, not just the prior yes/no S2,
and preserve MULTIPLE joined participants, possible joining to BOTH Moon
and Mercury, and the ambiguity of whether Sun and the mutual Moon-Mercury
contact may themselves qualify for this wording.

Three original first-stage source scopes (rising sign / Regiomontanus 1st
house / rising or fully intercepted sign) x two smaller/larger printed
orb envelopes x two classical candidate inclusion scopes (four external
nonluminary planets vs all OTHER classical planets) = 12 eligibility
scenarios. Their exact yes/no sample counts must equal the earlier
independent five-stage original whole-century S2 source calculation.

All 3,506,400 original UTC source rows and 108 SHA-pinned binary
planet/site/HD shards reverified; 288,908 HD structural intervals,
125 uncertain HD root crossings, 4,553 conditional Ptolemy four-mode
potential common-lord samples independently checked.

NO final historic manners ruler, strength arbitration or human behavior
claims are made. In particular all source-eligible S2 planets continue
to participate; if none S2 qualifies, proceed to S3. No private records.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import swisseph as swe

import lilly_cvii_ptolemy_same_instant_ordered_fallback_v02 as old
import lilly_cvii_s1_eligible_partial_strength_century_v01 as s1

N=3506400
HD_STATES=288908
MODES=s1.MODES
SCOPES=old.JOINS
ORB_OPTIONS=old.SOURCE_ORBS
PLANETS=old.PLANETS
STAGES=len(MODES)*len(ORB_OPTIONS)*len(SCOPES)


def candidates_joined_to_moon_or_mercury(planets,orbs,scope):
    """Planet-specific conjunction membership, not an astrological ruler."""
    p=np.asarray(planets,dtype=np.float64)
    o=np.asarray(orbs,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=7 or o.shape!=(7,) or scope not in SCOPES:
        raise ValueError("Seven source planets, source orb table, explicit joining scope")
    if not np.all(np.isfinite(p)) or not np.all(np.isfinite(o)):
        raise ValueError("Source values must be finite")
    if np.any((p<0)|(p>=360)) or np.any(o<=0):
        raise ValueError("Original tropical longitudes and source orb widths invalid")
    selected=(3,4,5,6) if scope==SCOPES[0] else tuple(range(7))
    Moon=np.zeros(p.shape,dtype=bool)
    Merc=np.zeros(p.shape,dtype=bool)
    for k in selected:
        if k!=1:Moon[:,k]=old.angle_distance(p[:,k],p[:,1])<=(o[k]+o[1])/2
        if k!=2:Merc[:,k]=old.angle_distance(p[:,k],p[:,2])<=(o[k]+o[2])/2
    both=Moon&Merc
    union=Moon|Merc
    prior=old.orb_join(p,o,scope=scope)
    if not np.array_equal(union.any(axis=1),prior["any_joined"]):
        raise RuntimeError("Original independent 1647 joining candidate witness disagrees")
    if not np.array_equal(both.any(axis=1),prior["both_same_planet"]):
        raise RuntimeError("Original independent joined-to-BOTH witness disagrees")
    return {"moon":Moon,"mercury":Merc,"both":both,"union":union}


def count_chunk(P,A,IDs,*,cusp1,cusp2,counts,hd_bits):
    n=len(P)
    p=np.asarray(P,dtype=np.float64)
    a=np.asarray(A,dtype=np.float64)
    source_ids=np.asarray(IDs,dtype=np.int32)
    if p.shape!=(n,8) or a.shape!=(n,17) or source_ids.shape!=(n,):
        raise ValueError("Original source columns and UTC row population changed")
    eligible=s1.first_stage_eligible(p[:,:7],cusp1,cusp2)
    census={mode:mask.any(axis=1) for mode,mask in eligible.items()}
    source_common=s1.base.es.src.PRIOR.ptolemy_source.conditional_all_four_common_leader(p,a[:,4])>=0
    known=source_ids>=0
    counts["sample_UTC_count"]+=n
    counts["HD_root_uncertain"]+=int((~known).sum())
    counts["ptolemy_conditional_four_mode_common"]+=int(source_common.sum())
    counts["ptolemy_HD_uncertain"]+=int((source_common&~known).sum())
    for mode in MODES:
        counts[mode+"|S1_present"]+=int(census[mode].sum())
        counts[mode+"|S1_empty"]+=int((~census[mode]).sum())
    for orbname,orbs in ORB_OPTIONS.items():
        for scope in SCOPES:
            joined=candidates_joined_to_moon_or_mercury(p[:,:7],orbs,scope)
            for mode in MODES:
                empty=~census[mode]
                m=joined["union"]&empty[:,None]
                k=m.sum(axis=1)
                no=empty&(k==0)
                sole=empty&(k==1)
                multi=empty&(k>1)
                tag="|".join((mode,orbname,scope))
                counts[tag+"|S2_zero_proceed_to_S3"]+=int(no.sum())
                counts[tag+"|S2_one_joined_planet"]+=int(sole.sum())
                counts[tag+"|S2_multiple_joined_planets"]+=int(multi.sum())
                counts[tag+"|S2_any"]+=int((sole|multi).sum())
                counts[tag+"|S2_joined_to_both_Moon_and_Mercury"]+=int((empty&joined["both"].any(axis=1)).sum())
                counts[tag+"|S2_moon_mercury_mutual_when_broad"]+=int((empty&m[:,1]&m[:,2]).sum())
                counts[tag+"|S2_nonluminary_candidate"]+=int((empty&m[:,2:7].any(axis=1)).sum())
                counts[tag+"|S2_luminary_candidate"]+=int((empty&m[:,:2].any(axis=1)).sum())
                counts[tag+"|S2_ptolemy_any"]+=int((source_common&(sole|multi)).sum())
                counts[tag+"|S2_ptolemy_sole"]+=int((source_common&sole).sum())
                counts[tag+"|S2_ptolemy_multi"]+=int((source_common&multi).sum())
                for i,name in enumerate(PLANETS):
                    counts[tag+"|candidate_"+name]+=int(m[:,i].sum())
                    counts[tag+"|sole_candidate_"+name]+=int((sole&m[:,i]).sum())
                    counts[tag+"|dual_joined_candidate_"+name]+=int((empty&joined["both"][:,i]).sum())
                for stage,mask in (("S2_any",sole|multi),
                                   ("S2_sole",sole),
                                   ("S2_multi",multi),
                                   ("S2_later_S3",no),
                                   ("S2_Ptolemy_any",source_common&(sole|multi))):
                    v=source_ids[mask&known]
                    if len(v):
                        hd_bits.setdefault(tag+"|"+stage,np.zeros(HD_STATES,dtype=bool))[v]=True


def run(west,angles,hd_cache,hd_join,verify_sha=True):
    if swe.version!="2.10.03":raise RuntimeError("Source Swiss engine changed")
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    pw=json.loads(wp.read_bytes());mw=json.loads(wm.read_bytes())
    pa=json.loads(ap.read_bytes());ma=json.loads(am.read_bytes())
    check=s1.base.es.src.PRIOR.base.reg.initial.check_manifest(pw,mw,pa,ma)
    if check!=N:raise RuntimeError("Original 1926-2026 UTC population changed")
    sha=s1.base.es.src.PRIOR.base.reg.initial.source_hash
    if mw["plan_sha256"]!=sha(wp) or ma["plan_sha256"]!=sha(ap):
        raise RuntimeError("Frozen source planet/site plan integrity changed")
    HD_proof=s1.base.es.src.PRIOR.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    hj=json.loads((hd_join/"manifest.json").read_bytes())
    if (hj["total_utc_grid_samples"]!=N or hj["total_hd_structural_intervals"]!=HD_STATES
        or hj["unresolved_near_boundary_samples"]!=125):
        raise RuntimeError("HD source time/structural population changed")
    prior=json.loads((Path(__file__).resolve().parents[1]/"reference/research/lilly_cvii_ptolemy_same_instant_ordered_fallback_public_v02.json").read_bytes())
    oldcounts=prior["counts"]
    jd=s1.base.es.src.PRIOR.base.reg.julian_from_utc(pw["utc_start_inclusive"])
    lat=float(pa["latitude"]);lon=float(pa["longitude"])
    c=Counter();bits={}
    first=0
    for w,a,h in zip(mw["chunks"],ma["shards"],hj["shards"],strict=True):
        k=w["count"]
        if not (w["first_index"]==first==a["first_index"]==h["index_first"] and h["count"]==k):
            raise RuntimeError("UTC time source shard index drift")
        pp=west/"chunks"/w["file"];apath=angles/"shards"/a["file"];hpath=hd_join/"shards"/h["file"]
        if pp.stat().st_size!=64*k or apath.stat().st_size!=136*k or hpath.stat().st_size!=4*k:
            raise RuntimeError("Source binary population byte sizes changed")
        if verify_sha:
            for path,meta in ((pp,w),(apath,a),(hpath,h)):
                if sha(path)!=meta["sha256"]:
                    raise RuntimeError("Original source shard SHA-256 mismatch")
        p=np.memmap(pp,dtype="<f8",mode="r",shape=(k,8))
        q=np.memmap(apath,dtype="<f8",mode="r",shape=(k,17))
        ids=np.memmap(hpath,dtype="<i4",mode="r",shape=(k,))
        c1=np.empty(k);c2=np.empty(k)
        for i in range(k):
            cu,_=swe.houses_ex(jd+(first+i)/96.,lat,lon,b"R")
            c1[i]=cu[0];c2[i]=cu[1]
        if np.max(np.abs((c1-q[:,0]+180)%360-180))>0.0002:
            raise RuntimeError("Original ascending degree disagrees with frozen source")
        count_chunk(p,q,ids,cusp1=c1,cusp2=c2,counts=c,hd_bits=bits)
        first+=k
    if (not verify_sha or first!=N or c["sample_UTC_count"]!=N or
        c["HD_root_uncertain"]!=125 or c["ptolemy_conditional_four_mode_common"]!=4553 or
        c["ptolemy_HD_uncertain"]!=0):
        raise RuntimeError("Full original source SHAs/HD/Ptolemy cohort not proven")
    expected={"ascending_sign":1428060,"regiomontanus_first_house":1409411,
              "ascending_sign_or_intercepted_sign":1516373}
    for mode in MODES:
        if c[mode+"|S1_present"]!=expected[mode] or c[mode+"|S1_empty"]!=N-expected[mode]:
            raise RuntimeError("Frozen first-stage source cohort differed")
        for orbname in ORB_OPTIONS:
            for scope in SCOPES:
                tag="|".join((mode,orbname,scope))
                oldtag="|".join((mode,orbname,scope,"dispositor_sign_ray","partile_Moon_or_Mercury"))
                any=c[tag+"|S2_any"]
                if any!=oldcounts[oldtag+"|S2"]:
                    raise RuntimeError("Historical earlier five-stage S2 source baseline mismatch")
                if c[tag+"|S2_ptolemy_any"]!=oldcounts["same_instant_Ptolemy_"+oldtag+"|S2"]:
                    raise RuntimeError("Historical earlier S2/Ptolemy joint source baseline mismatch")
                if (c[tag+"|S2_zero_proceed_to_S3"]+c[tag+"|S2_one_joined_planet"]+
                    c[tag+"|S2_multiple_joined_planets"]!=c[mode+"|S1_empty"]):
                    raise RuntimeError("S2 zero/single/multi source partition incomplete")
                if c[tag+"|S2_one_joined_planet"]+c[tag+"|S2_multiple_joined_planets"]!=any:
                    raise RuntimeError("S2 participants improperly deleted")
    return {
        "schema":"lilly_1647_CVII_S2_original_p536_joined_moon_mercury_source_century_v01",
        "status":"ORIGINAL_PRINTED_SECOND_STAGE_12_SOURCE_CONDITIONAL_MEMBERSHIP_VARIANTS_NO_FINAL_MANNERS_RULER",
        "original_source":"William Lilly Christian Astrology 1647 first printing pp535-536 and original printed p107 planetary moieties",
        "original_1647_p536_source_render_SHA256":"4cdd11d5cf468e20f38fed7889e42f2e6298540e05f7f196c9b916e28bb57b24",
        "source_horizon_UTC":[pw["utc_start_inclusive"],pw["utc_end_exclusive"]],
        "samples":N,"UTC_step_minutes":15,"fixed_research_site_count":1,
        "original_source_shard_SHA256_rechecked":verify_sha,
        "HD_source_audit":HD_proof,"HD_structural_interval_total":HD_STATES,
        "source_manifest_hashes":{"planet":sha(wm),"angles":sha(am),"HD_join":sha(hd_join/"manifest.json")},
        "source_conditions":{"S1_original_scope_variants":list(MODES),"original_1647_moiety_variant_bundles":{k:v.tolist() for k,v in ORB_OPTIONS.items()},
                             "joining_planet_inclusion_variants":list(SCOPES)},
        "source_sensitive_S2_eligibility_method_count":STAGES,
        "historical_second_stage_moon_mercury_mutual_status":"UNRESOLVED; broad alternative counts luminaries/Mercury as possible joined candidates, narrow four external planets does not",
        "original_if_one_planet_joined_both_moon_mercury":"SOURCE_SPECIAL_CASE; event and candidate identity counted, no unlicensed priority to this planet",
        "source_S2_missing_relative_planet_power":"COMPLETE_FULL_LILLY_PLANET_FORTITUDE_UNRESOLVED",
        "zero_S1_or_S2":"PROCEED_TO_SUBSEQUENT_DISPOSITOR_ASPECT_FALLBACK; NOT NEGATIVE_PERSONALITY",
        "counts":dict(c),
        "HD_distinct_structural_intervals_by_S2_condition":{k:int(b.sum()) for k,b in bits.items()},
        "S1_original_previous_results_unchanged":True,
        "actual_Lilly_CVII_manners_ruler_computed":False,
        "actual_Ptolemy_III13_soul_governor_computed":False,
        "independent_human_behavioral_validation":False,
        "private_user_thirdparty_natal_source_records_loaded":False
    }


def main():
    parser=argparse.ArgumentParser()
    for name in ("west","angles","hd-cache","hd-join","out"):
        parser.add_argument("--"+name,required=True,type=Path)
    z=parser.parse_args()
    if z.out.exists():raise FileExistsError("Original full century source result must be immutable")
    j=run(z.west,z.angles,z.hd_cache,z.hd_join)
    z.out.parent.mkdir(parents=True,exist_ok=True)
    z.out.write_text(json.dumps(j,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":j["status"],"samples":j["samples"],
       "source_methods":j["source_sensitive_S2_eligibility_method_count"]},sort_keys=True))
if __name__=="__main__":main()
