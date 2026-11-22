#!/usr/bin/env python3
"""Same-instant, full-grid historical SOURCE-QUALIFICATION audit (NO personality scores).

Ptolemy III.2-3 and III.13: count the FOUR already sourced domination
modes at Mercury/Moon separately. Both printed term traditions and
primary/all triplicity variants are kept independently. One hypothetical
uncomputed fifth mode could add at most one vote per planet: margin >= 2
makes a *four-mode leader* mathematically stable against THAT bounded
extension. The fifth mode and qualitative planetary strength/contrary
testimony are NOT numerically settled, so no actual soul governor selected.

Lilly CVII p.535 literally says "Sign ascending, or which is intercepted".
The sign-only proxy and Regiomontanus first HOUSE are competing readings,
not a source-authorized replacement of one by the other. A sign-or-fully-
intercepted-sign interpretation is tested as a THIRD explicit sensitivity.
No manners significator is chosen.

Only anonymous, fixed-place 1926-2026 sampled UTC geometry; private natal,
survey, interview, and target score data are NEVER read or output.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
import swisseph as swe

import ptolemy_four_modes_source_terms_century_v01 as four
import lilly_cvii_regiomontanus_house_century_v01 as reg
import ptolemy_iii13_mercury_lunar_dual_aspect_century_v01 as dual
import verify_western_hd_join_index as hdverify

SCHEMES=tuple(four.TABLES)
VARIANTS=tuple((scheme, co) for scheme in SCHEMES for co in (False,True))
PLANET_NAMES=tuple(four.PLANETS)
SUN_ALT_UNCERTAINTY=0.1
SWISS_VERSION="2.10.03"


def four_mode_votes(place_longitude, solar_altitude, scheme, all_corulers):
    """One vote *per distinct mode per planet*; not the historical full ruler."""
    lng=np.asarray(place_longitude,dtype=np.float64)
    alt=np.asarray(solar_altitude,dtype=np.float64)
    if lng.ndim!=1 or lng.shape!=alt.shape or np.any(~np.isfinite(alt)):
        raise ValueError("Aligned longitude and altitude required")
    s=four.prior_sign(lng)
    n=len(lng)
    rows=np.arange(n)
    out=np.zeros((n,7),dtype=np.uint8)
    out[rows,four.pt3.ptolemy2.DOMICILE[s]]+=1
    exalt=four.pt3.ptolemy2.EXALTATION[s]
    ok=exalt>=0
    out[rows[ok],exalt[ok]]+=1
    # Co-ruler branches count each source-listed co-ruler ONCE in the
    # triplicity mode, never two votes for the same ruler.
    if all_corulers:
        daybits=four.pt3.CO_DAY[s]
        nightbits=four.pt3.CO_NIGHT[s]
    else:
        daybits=(np.uint16(1)<<four.pt3.PRIMARY_DAY[s].astype(np.uint16))
        nightbits=(np.uint16(1)<<four.pt3.PRIMARY_NIGHT[s].astype(np.uint16))
    tripbits=np.where(alt>SUN_ALT_UNCERTAINTY,daybits,
                      np.where(alt< -SUN_ALT_UNCERTAINTY,nightbits,np.uint16(0)))
    for i in range(7):
        out[:,i]+=((tripbits>>i)&1).astype(np.uint8)
    term=four.term_lords(lng,scheme)
    out[rows,term]+=1
    if np.max(out)>4:raise RuntimeError("One of the four modes voted twice")
    return out


def rank_state(votes):
    """Top lord, tie and conditional 1-vote fifth-mode robustness."""
    v=np.asarray(votes,dtype=np.uint8)
    if v.ndim!=2 or v.shape[1]!=7 or not len(v) or np.max(v)>4:
        raise ValueError("N x 7 four-mode votes required")
    top_value=v.max(axis=1)
    tied=(v==top_value[:,None]).sum(axis=1)>1
    winner=np.argmax(v,axis=1).astype(np.int8)
    runner_up=np.partition(v,-2,axis=1)[:,-2]
    margin=top_value.astype(np.int16)-runner_up.astype(np.int16)
    winner[tied]=-1
    robust=(~tied)&(margin>=2)
    return winner,tied,robust,margin


def first_house_and_intercepted(planets,cusp1,cusp2):
    """Actual first-house bodies; fully contained whole signs distinct."""
    p=np.asarray(planets,dtype=np.float64)
    c1=np.asarray(cusp1,dtype=np.float64)
    c2=np.asarray(cusp2,dtype=np.float64)
    inside=reg.cusp_member(p,c1,c2).any(axis=1)
    arc=(c2-c1)%360
    starts=np.arange(12,dtype=np.float64)*30.
    offsets=(starts[None,:]-c1[:,None])%360.
    # A fully intercepted sign has neither beginning nor end on a cusp.
    # It must have both boundaries strictly inside the arc.
    intercepted=(offsets>1e-9)&(offsets+30<arc[:,None]-1e-9)
    psigns=np.floor(p/30).astype(np.int8)
    planet_intercepted=intercepted[np.arange(len(p))[:,None],psigns].any(axis=1)
    asc_sign=np.floor(c1/30).astype(np.int8)
    sign_any=(psigns==asc_sign[:,None]).any(axis=1)
    sign_plus=sign_any|planet_intercepted
    return {
      "regiomontanus_first_house":inside,
      "ascending_sign":sign_any,
      "ascending_sign_or_intercepted_sign":sign_plus,
      "intercepted_first_house_sign_exists":intercepted.any(axis=1),
      "planet_in_intercepted_first_house_sign":planet_intercepted
    }


def chunk_compute(planets,angles,*,start_jd,first_index,latitude,longitude,hd_ids,hd_sets):
    p=np.asarray(planets,dtype=np.float64)
    a=np.asarray(angles,dtype=np.float64)
    n=len(p)
    hd_ids=np.asarray(hd_ids,dtype=np.int32)
    if hd_ids.shape!=(n,) or np.any(hd_ids < -1):
        raise ValueError("One verified signed HD structural index per UTC sample required")
    hv=hd_ids>=0
    if p.ndim!=2 or p.shape[1]!=8 or a.shape!=(n,17):
        raise ValueError("Source matrix columns changed")
    asc=a[:,0]
    if np.any(~np.isfinite(p)) or np.any((p[:,:7]<0)|(p[:,:7]>=360)):
        raise ValueError("Source planet longitude invalid")
    c1=np.empty(n,dtype=np.float64)
    c2=np.empty(n,dtype=np.float64)
    for i in range(n):
        cusps,arms=swe.houses_ex(start_jd+(first_index+i)/96.,
                                 latitude,longitude,b'R')
        c1[i]=cusps[0];c2[i]=cusps[1]
    if np.any(np.abs((c1-asc+180)%360-180)>0.0002):
        raise RuntimeError("Original ASC/source-day/Regiomontanus site mismatch")
    classes=first_house_and_intercepted(p[:,:7],c1,c2)
    out=Counter()
    valid=np.abs(a[:,4])>SUN_ALT_UNCERTAINTY
    out["total_samples"]=n
    out["hd_join_known_same_instant"]=int(hv.sum())
    out["hd_join_boundary_abstain_same_instant"]=int((~hv).sum())
    out["sect_known"]=int(valid.sum())
    out["sect_ambiguous"]=int((~valid).sum())
    for key,mask in classes.items():
        out["lilly_"+key+"_all"]=int(mask.sum())
        eligible=mask&hv
        out["hd_same_instant_lilly_"+key+"_known"]=int(eligible.sum())
        hd_sets.setdefault("lilly_"+key,set()).update(hd_ids[eligible].tolist())
    for k in ("ascending_sign","ascending_sign_or_intercepted_sign"):
        m=classes[k];h=classes["regiomontanus_first_house"]
        out["lilly_"+k+"_only_vs_house"]=int((m&~h).sum())
        out["lilly_house_only_vs_"+k]=int((h&~m).sum())
    for t in (1.,3.,5.,10.):
        joined=reg.house.joined_4_externals(p[:,:7],t)
        for mode in ("ascending_sign","regiomontanus_first_house",
                     "ascending_sign_or_intercepted_sign"):
            out["lilly_"+str(int(t))+"deg_joined_if_"+mode+"_empty"]=int(
                (joined&~classes[mode]).sum())
    joint_unique_by_variant={}
    joint_robust_by_variant={}
    for scheme,co in VARIANTS:
        tag=scheme+("_corulers" if co else "_principal")
        merc=four_mode_votes(p[:,2],a[:,4],scheme,co)
        moon=four_mode_votes(p[:,1],a[:,4],scheme,co)
        mw,mt,mr,mm=rank_state(merc)
        lw,lt,lr,lm=rank_state(moon)
        joint=(mw>=0)&(lw>=0)&(mw==lw)
        joint_robust=joint&mr&lr&valid
        good=joint_robust&hv
        out["hd_same_instant_"+tag+"_robust_common_known"]=int(good.sum())
        hd_sets.setdefault("ptolemy_"+tag+"_robust",set()).update(hd_ids[good].tolist())
        joint_unique_by_variant[tag]=np.where(joint&valid,mw,-1)
        joint_robust_by_variant[tag]=np.where(joint_robust,mw,-1)
        out["ptolemy_"+tag+"_unique_Mercury_fourmode"]=int(((~mt)&valid).sum())
        out["ptolemy_"+tag+"_unique_Moon_fourmode"]=int(((~lt)&valid).sum())
        out["ptolemy_"+tag+"_Mercury_fourmode_robust_to_one_fifth_vote"]=int((mr&valid).sum())
        out["ptolemy_"+tag+"_Moon_fourmode_robust_to_one_fifth_vote"]=int((lr&valid).sum())
        out["ptolemy_"+tag+"_same_unique_fourmode_leader_both"]=int((joint&valid).sum())
        out["ptolemy_"+tag+"_same_robust_fourmode_leader_both"]=int(joint_robust.sum())
        for planet_i,planet in enumerate(PLANET_NAMES):
            out["ptolemy_"+tag+"_same_robust_fourmode_"+planet]=int(
                 (joint_robust&(mw==planet_i)).sum())
        for mode in ("ascending_sign","regiomontanus_first_house",
                     "ascending_sign_or_intercepted_sign"):
            out["joint_"+tag+"_robust_common_ptolemy_with_lilly_"+mode]=int(
                (joint_robust&classes[mode]).sum())
            out["joint_"+tag+"_robust_common_ptolemy_lilly_"+mode+"_empty"]=int(
                (joint_robust&~classes[mode]).sum())
    # Exact same-UTC-time source VARIANT consensus is stricter than counting
    # each historically contested variant separately. Refuse to pool branches.
    for label,store in (("unique",joint_unique_by_variant),
                        ("robust",joint_robust_by_variant)):
        stack=np.stack(list(store.values()),axis=0)
        present=stack>=0
        all_present=present.all(axis=0)
        any_present=present.any(axis=0)
        unanimous=all_present&(stack==stack[0]).all(axis=0)
        conflict=all_present&~unanimous
        out["ptolemy_at_least_one_variant_"+label+"_common"]=int(any_present.sum())
        out["ptolemy_all_four_variants_"+label+"_common"]=int(all_present.sum())
        out["ptolemy_all_four_variants_same_"+label+"_common_lord"]=int(unanimous.sum())
        out["ptolemy_all_four_variants_conflicting_"+label+"_lords"]=int(conflict.sum())
        eligible_unanimous=unanimous&hv
        out["hd_same_instant_unanimous_"+label+"_known"]=int(eligible_unanimous.sum())
        hd_sets.setdefault("ptolemy_unanimous_"+label,set()).update(
            hd_ids[eligible_unanimous].tolist())
        for mode in ("ascending_sign","regiomontanus_first_house",
                     "ascending_sign_or_intercepted_sign"):
            same=unanimous&classes[mode]
            out["joint_unanimous_four_variants_"+label+"_common_lord_lilly_"+mode]=int(same.sum())
            eligible=same&hv
            out["hd_same_instant_joint_unanimous_"+label+"_lilly_"+mode]=int(eligible.sum())
            hd_sets.setdefault("joint_unanimous_"+label+"_lilly_"+mode,set()).update(
                hd_ids[eligible].tolist())
        if label=="robust":
            # This is a further geometric CONDITION on already robust common
            # four-mode leaders, NOT itself an original Ptolemy fifth vote.
            # Source I.24 permits rays and bodily conjunctions and gives no
            # numeric orb; near-exact bodily contacts require latitude data
            # absent from frozen longitude cache. Only non-bodily rays are
            # counted as definite geometry; conjunctions upper-bound POSSIBLE.
            unanimous_planet=np.where(unanimous,stack[0],-1)
            unknown=np.zeros(n,dtype=bool)
            unknown[0]=True;unknown[-1]=True
            unknown|=~valid
            candidates={t:{k:np.zeros(n,dtype=bool) for k in
                    ("lower","upper","applying","separating")}
                    for t in dual.THRESHOLDS}
            for pidx in dual.EXTERNAL_GOVERNORS.values():
                candidate=unanimous_planet==pidx
                if not candidate.any():continue
                # Compute each planetary lunar and Mercury geometry ONCE,
                # independent of five downstream angular sensitivities.
                m_ray=dual.nearest_residual(p[:,pidx],p[:,2],dual.ASPECTS_NONBODY)
                l_ray=dual.nearest_residual(p[:,1],p[:,pidx],dual.ASPECTS_NONBODY)
                m_all=dual.nearest_residual(p[:,pidx],p[:,2],dual.ASPECTS_WITH_BODY)
                l_all=dual.nearest_residual(p[:,1],p[:,pidx],dual.ASPECTS_WITH_BODY)
                v=dual.lunar_radial_trend(p[:,1],p[:,pidx])
                for t,acc in candidates.items():
                    ray=candidate&~unknown&(np.abs(m_ray)<=t)&(np.abs(l_ray)<=t)
                    possible=candidate&~unknown&(np.abs(m_all)<=t)&(np.abs(l_all)<=t)
                    acc["lower"]|=ray
                    acc["upper"]|=possible
                    acc["applying"]|=ray&(v*l_ray<0)
                    acc["separating"]|=ray&(v*l_ray>0)
            for t,acc in candidates.items():
                stem="ptolemy_all4_robust_consensus_dual_"+str(int(t))+"deg_"
                out[stem+"nonconjunction_ray_witness"]=int(acc["lower"].sum())
                eligible=acc["lower"]&hv
                out["hd_same_instant_"+stem+"nonconjunction_ray_witness"]=int(eligible.sum())
                hd_sets.setdefault("phase_dual_"+str(int(t))+"deg",set()).update(
                    hd_ids[eligible].tolist())
                out[stem+"uncertified_bodily_inclusive_scope"]=int(acc["upper"].sum())
                out[stem+"applying_nonconjunction_ray_witness"]=int(acc["applying"].sum())
                out[stem+"separating_nonconjunction_ray_witness"]=int(acc["separating"].sum())
                for mode in ("ascending_sign","regiomontanus_first_house",
                             "ascending_sign_or_intercepted_sign"):
                    out[stem+"nonconjunction_ray_and_lilly_"+mode]=int(
                        (acc["lower"]&classes[mode]).sum())
    # Terms and triplicity variants are independent historically; never
    # silently pick whichever makes an individual comparison look best.
    return out


def run(west,angles,hd_cache,hd_join,verify_hashes=True):
    if swe.version!=SWISS_VERSION:
        raise RuntimeError("Wrong Swiss calculation version")
    wp=west/"plan.json"; wm=west/"verified_manifest.json"
    ap=angles/"plan.json"; am=angles/"verified_manifest.json"
    pw=json.loads(wp.read_bytes());mw=json.loads(wm.read_bytes())
    pa=json.loads(ap.read_bytes());ma=json.loads(am.read_bytes())
    n=reg.initial.check_manifest(pw,mw,pa,ma)
    if mw["plan_sha256"]!=reg.initial.source_hash(wp) or ma["plan_sha256"]!=reg.initial.source_hash(ap):
        raise RuntimeError("Input plans changed since source froze")
    if pa.get("cols",[])[5:7]!=["placidus_cusp_1","placidus_cusp_2"]:
        raise RuntimeError("Angle-column provenance mismatch")
    if pa.get("swisseph_version")!=SWISS_VERSION:raise RuntimeError("Angle source Swiss changed")
    hdproof=hdverify.audit_join(west,hd_cache,hd_join)
    hdmeta=json.loads((hd_join/"manifest.json").read_bytes())
    if hdmeta["total_utc_grid_samples"]!=n or hdmeta["step_minutes"]!=15:
        raise RuntimeError("HD structural index has wrong temporal population")
    if hdmeta["unresolved_near_boundary_samples"]!=125:
        raise RuntimeError("Original HD boundary uncertainty changed")
    jd0=reg.julian_from_utc(pw["utc_start_inclusive"])
    lat=float(pa["latitude"]);lon=float(pa["longitude"])
    counts=Counter()
    hd_sets={}
    for w,a,h in zip(mw["chunks"],ma["shards"],hdmeta["shards"],strict=True):
        bp=west/"chunks"/w["file"];ba=angles/"shards"/a["file"]
        k=w["count"]
        if bp.stat().st_size!=64*k or ba.stat().st_size!=136*k:
            raise RuntimeError("Source shard size drift")
        if verify_hashes and (reg.initial.source_hash(bp)!=w["sha256"] or
              reg.initial.source_hash(ba)!=a["sha256"]):
            raise RuntimeError("Source SHA256 mismatch")
        if h["index_first"]!=w["first_index"] or h["count"]!=k:
            raise RuntimeError("HD and planetary sample offsets differ")
        p=np.memmap(bp,dtype="<f8",shape=(k,8),mode="r")
        q=np.memmap(ba,dtype="<f8",shape=(k,17),mode="r")
        hid=np.memmap(hd_join/"shards"/h["file"],dtype="<i4",shape=(k,),mode="r")
        counts.update(chunk_compute(p,q,start_jd=jd0,first_index=w["first_index"],
                                    latitude=lat,longitude=lon,hd_ids=hid,hd_sets=hd_sets))
    if counts["total_samples"]!=n or n!=3506400:raise RuntimeError("Unexpected source census denominator")
    if counts["hd_join_boundary_abstain_same_instant"]!=125:raise RuntimeError("Unresolved original HD boundary drift")
    if counts["lilly_ascending_sign_all"]!=1428060:raise RuntimeError("Old sign source baseline changed")
    if counts["lilly_regiomontanus_first_house_all"]!=1409411:raise RuntimeError("Old house source baseline changed")
    for scheme,co in VARIANTS:
        tag=scheme+("_corulers" if co else "_principal")
        if counts["ptolemy_"+tag+"_same_robust_fourmode_leader_both"]>counts[
          "ptolemy_"+tag+"_same_unique_fourmode_leader_both"]:
            raise RuntimeError("Robust subset cannot exceed unique")
    return {
      "schema":"ptolemy_iii13_lilly_cvii_hd_same_instant_public_structural_census_v01",
      "status":"ORIGINAL_SOURCE_CONDITIONED_MECHANICS_ONLY_NO_FULL_GOVERNOR_OR_PERSONALITY_RANK",
      "source_horizon":[pw["utc_start_inclusive"],pw["utc_end_exclusive"]],
      "step_minutes":15,"data_samples":n,"fixed_location_not_participant":True,
      "ptolemy_variant_definitions":[{"terms":s,"triplicity":"corulers" if co else "principal"} for s,co in VARIANTS],
      "four_mode_fifth_vote_margin_rule":"A strictly unique 4-mode winner with lead >=2 cannot be tied by any single extra vote to another candidate, ONLY under a bounded one-vote-per-candidate interpretation. This does not adjudicate actual historical phase, strength or testimony.",
      "lilly_geometry_branches":["ascending_sign","regiomontanus_first_house","ascending_sign_or_intercepted_sign"],
      "lilly_1647_original_facsimile_collated":False,
      "original_72_source_binary_shards_sha256_rechecked":verify_hashes,
      "original_source_manifest_sha256":{"planet":reg.initial.source_hash(wm),
                "angles":reg.initial.source_hash(am)},
      "sample_counts":dict(counts),
      "unique_HD_structural_intervals_by_same_instant_condition":{
          key:len(value) for key,value in sorted(hd_sets.items())},
      "HD_independent_join_source_audit":hdproof,
      "HD_original_join_manifest_sha256":hdverify.digest(hd_join/"manifest.json"),
      "HD_original_source_manifest_sha256":hdverify.digest(hd_cache/"manifest.json"),
      "HD_structural_intervals_total":hdmeta["total_hd_structural_intervals"],
      "HD_boundary_near_instants_abstained":hdmeta["unresolved_near_boundary_samples"],
      "unknown":["Ptolemy phase/aspect original scope and orbs","planetary strengths, sect/angles and conflicting testimony",
                 "whether a voting count alone can select governors","Lilly ascendant sign/house grammatical precedence",
                 "Lilly full strength/dispositor/partile/fixed star rules",
                 "Human Design whole-chart behavioral scoring","original respondent-blind predictive evaluation"],
      "human_natal_scores_computed":False,"human_predictive_validation":False,
      "personal_birth_records_loaded":False,
      "full_same_instant_geometry_only":True,
      "all_four_historical_variant_consensus_requires_same_planet_and_eligibility_on_same_sample":True,
      "nonbody_ray_screen_is_fifth_mode_sensitivity_not_a_historically_authorized_extra_vote":True,
      "engineering_angular_thresholds_degrees":[1,3,5,10,15],
      "shard_endpoint_moon_motion_abstentions":72
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--west",required=True,type=Path)
    p.add_argument("--angles",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--hd-cache",required=True,type=Path)
    p.add_argument("--hd-join",required=True,type=Path)
    p.add_argument("--skip-shard-hashes",action="store_true")
    args=p.parse_args()
    if args.out.exists():raise FileExistsError("Output immutable; choose new version")
    result=run(args.west,args.angles,args.hd_cache,args.hd_join,not args.skip_shard_hashes)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"total":result["data_samples"],
                      "source_hashes":result["original_72_source_binary_shards_sha256_rechecked"],
                      "counts":result["sample_counts"]},sort_keys=True))
if __name__=="__main__":main()
