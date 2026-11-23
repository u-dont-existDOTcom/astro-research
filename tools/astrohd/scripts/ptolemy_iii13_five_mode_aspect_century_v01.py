#!/usr/bin/env python3
"""Ptolemy III.2/3 + III.13: all-sample separate-place aspect fifth-mode sensitivity.

No authorial fixed orb or complete historical governor is claimed. Four
source-printed modes are reused. One fifth claim per distinct body and
place is conditional on an explicit geometric interpretation. Bodily
contact is an uncertain interval (no latitude assumed). A second interval
allows any still unresolved phase claim. The latter is deliberately broad,
not a claim that every planet can in fact satisfy the source's phase rule.
Moon/Mercury are evaluated independently: their provisional leaders may
differ. Sect and opposing-sect overcoming geometry remain separate flags,
not numerical strength or personality scores. No private natal inputs.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import numpy as np

import ptolemy_lilly_hd_same_instant_century_v01 as base

ROOT=Path(__file__).resolve().parents[3]
TASK="state/tasks/20261123-ptolemy-five-mode-aspect.json"
PUBLIC="tools/astrohd/reference/research/ptolemy_iii13_five_mode_aspect_century_public_v01.json"
N=3506400
HD_COUNT=288908
VARIANTS=base.VARIANTS
PLANETS=base.PLANET_NAMES
TOLS=(3.,15.)
MERCURY_POLICIES=("sign_rays","degree_near_rays")
SCOPES=("four_external","all_distinct_classical")
RAYS=np.array([60.,90.,120.,180.,240.,270.,300.])
SIGN_RAYS=(2,3,4,6,8,9,10)
# Source I.7 fixed planetary sect; Mercury varies with solar phase and
# is UNKNOWN here (rather than assuming an approximate elongation).
FIXED_SECT=np.array([1,-1,0,-1,-1,1,1],np.int8)
GEOMETRY_SCENARIOS=len(VARIANTS)*len(TOLS)*len(MERCURY_POLICIES)*len(SCOPES)


def aspect_bounds(positions,ref,tol,policy,scope):
    """Certain nonbodily ray, possible conjunction; one vote per body.

    'Certain' means geometric satisfaction under this selected model only.
    In sign-ray Mercury policy, sign relationship suffices for rays, whereas
    conjunction remains an optional near-degree bodily claim. Moon uses
    near-ray distance as a proxy for I.24's 'interval not great'. A close
    ray is allowed on either side of exactness (applying OR separating),
    and exact contact is tracked separately, not assigned a direction.
    """
    p=np.asarray(positions,float)
    if p.ndim!=2 or p.shape[1]!=7 or not np.isfinite(p).all() or np.any((p<0)|(p>=360)):
        raise ValueError("Seven finite normalized classical longitudes")
    if ref not in (1,2) or tol not in TOLS or policy not in MERCURY_POLICIES or scope not in SCOPES:
        raise ValueError("Explicit declared source sensitivity only")
    if ref==1 and policy!="degree_near_rays":
        raise ValueError("Lunar application/separation uses explicit closeness proxy")
    delta=(p-p[:,ref,None])%360
    near=np.full(delta.shape,180.,float)
    for ray in RAYS:
        residual=(delta-ray+180.)%360.-180.
        # Use signed nearest ray residual to classify lunar direction.
        near=np.where(np.abs(residual)<np.abs(near),residual,near)
    if policy=="sign_rays":
        sign=np.floor(p/30).astype(np.int8)
        mask=np.isin((sign-sign[:,ref,None])%12,SIGN_RAYS)
    else:
        mask=np.abs(near)<=tol
    body=(np.minimum(delta,360.-delta)<=tol)
    eligible=np.ones(7,bool) if scope=="all_distinct_classical" else np.array([0,0,0,1,1,1,1],bool)
    eligible[ref]=False
    certain=mask&eligible[None,:]
    possible=certain|(body&eligible[None,:])
    # Earlier zodiac longitude of Moon relative to selected ray is a
    # precedence/application proxy, not a physical exact-event solver.
    # Here residual is planet-minus-Moon, so positive -> Moon precedes ray.
    return certain,possible,near


def interval_leader(lower,upper,valid):
    """Strict guaranteed maximum and conservative possible top set.

    Upper/lower bounds are a product relaxation. Possible candidates need
    not be jointly realizable when missing evidence is correlated.
    """
    l=np.asarray(lower,np.int16);u=np.asarray(upper,np.int16);v=np.asarray(valid,bool)
    if l.ndim!=2 or l.shape[1]!=7 or u.shape!=l.shape or v.shape!=(len(l),):
        raise ValueError("Aligned seven-planet bounds required")
    if np.any((l<0)|(u>5)|(u<l)):
        raise ValueError("One source-mode vote per planet, maximum five")
    top=np.argmax(l,axis=1)
    competitor=u.copy()
    row=np.arange(len(l))
    competitor[row,top]=-1
    guaranteed=np.where(v&(l[row,top]>competitor.max(axis=1)),top,-1).astype(np.int8)
    possible=(u>=l.max(axis=1)[:,None])&v[:,None]
    if np.any((guaranteed>=0)&~possible[row,np.maximum(guaranteed,0)]):
        raise RuntimeError("Guaranteed leader outside possible set")
    return guaranteed,possible


def qualifier_flags(positions,alt,leader):
    """Separate direct own-domicile and fixed-sect relation/overcoming witness."""
    p=np.asarray(positions,float);alt=np.asarray(alt,float);sel=np.asarray(leader,np.int8)
    if p.shape!=(len(sel),7) or alt.shape!=(len(sel),) or np.any((sel<-1)|(sel>6)):
        raise ValueError("Aligned original provisional leader required")
    chosen=sel>=0;idx=np.maximum(sel,0);r=np.arange(len(sel))
    signs=np.floor(p/30).astype(np.int8)
    chosen_sect=FIXED_SECT[idx]
    diurnal=np.where(alt>base.SUN_ALT_UNCERTAINTY,1,np.where(alt<-base.SUN_ALT_UNCERTAINTY,-1,0))
    sect_known=chosen&(chosen_sect!=0)&(diurnal!=0)
    domicile=chosen&(base.four.pt3.ptolemy2.DOMICILE[signs[r,idx]]==idx)
    in_sect=sect_known&(chosen_sect==diurnal)
    contrary_sect=sect_known&(chosen_sect!=diurnal)
    # I.7 and III.13 + Robbins note 137/III.4 note 22. A particular
    # traditional preceding square is only one operational interpretation
    # of overcoming; no asserted universal historic priority.
    oppose=(FIXED_SECT[None,:]!=0)&(chosen_sect[:,None]!=0)&(FIXED_SECT[None,:]==-chosen_sect[:,None])
    preceding_square=((signs[r,idx,None]-signs)%12)==3
    opposition_witness=chosen&(oppose&preceding_square).any(axis=1)
    return {"own_domicile":domicile,"fixed_sect_matches_chart":in_sect,
            "fixed_sect_opposite_chart":contrary_sect,
            "fixed_sect_unknown":chosen&~sect_known,
            "opposite_fixed_sect_preceding_square_witness":opposition_witness}


def scan(P,A,ids,counts,hdsets):
    p=np.asarray(P,float);a=np.asarray(A,float);h=np.asarray(ids,np.int32)
    n=len(p)
    if p.shape!=(n,8) or a.shape!=(n,17) or h.shape!=(n,) or not np.isfinite(a[:,4]).all():
        raise ValueError("Aligned original Western, site and HD row shapes")
    lon=p[:,:7];alt=a[:,4];valid=np.abs(alt)>base.SUN_ALT_UNCERTAINTY
    hd_known=h>=0
    counts["original_UTC_rows"]+=n
    counts["near_horizon_sect_unknown"]+=int((~valid).sum())
    counts["HD_root_unknown"]+=int((~hd_known).sum())
    bounds={}
    for t in TOLS:
        for scope in SCOPES:
            L,U,lr=aspect_bounds(lon,1,t,"degree_near_rays",scope)
            bounds[(t,scope,1,"degree_near_rays")]=(L,U)
            counts[f"{t:g}|{scope}|lunar_ray_applying_precedence_body_events"]+=int((L&(lr>0)).sum())
            counts[f"{t:g}|{scope}|lunar_ray_separating_precedence_body_events"]+=int((L&(lr<0)).sum())
            counts[f"{t:g}|{scope}|lunar_ray_exact_no_direction_body_events"]+=int((L&(lr==0)).sum())
            for mer in MERCURY_POLICIES:
                L,U,_=aspect_bounds(lon,2,t,mer,scope)
                bounds[(t,scope,2,mer)]=(L,U)
    all_pair=np.ones(n,bool);all_phase_pair=np.ones(n,bool)
    first_mer=np.full(n,-2,np.int8);first_moon=first_mer.copy()
    first_pm=first_mer.copy();first_pl=first_mer.copy()
    base_all=np.ones(n,bool);base_first=first_mer.copy()
    base_pair=np.ones(n,bool);base_m=first_mer.copy();base_l=first_mer.copy()
    num=0
    for scheme,co in VARIANTS:
        bM=base.four_mode_votes(lon[:,2],alt,scheme,co).astype(np.int16)
        bL=base.four_mode_votes(lon[:,1],alt,scheme,co).astype(np.int16)
        k=scheme+"|"+("all_triplicity_corulers" if co else "principal_triplicity")
        M0,PM0=interval_leader(bM,bM,valid)
        L0,PL0=interval_leader(bL,bL,valid)
        rm,_=interval_leader(bM,bM+1,valid)
        rl,_=interval_leader(bL,bL+1,valid)
        stable=(rm>=0)&(rm==rl)
        base_first=np.where(base_first==-2,rm,base_first)
        base_all&=stable&(base_first==rm)
        base_m=np.where(base_m==-2,M0,base_m);base_l=np.where(base_l==-2,L0,base_l)
        base_pair&=(M0>=0)&(L0>=0)&(base_m==M0)&(base_l==L0)
        counts[k+"|four_mode_unique_both_places"]+=int(((M0>=0)&(L0>=0)).sum())
        for t in TOLS:
            for scope in SCOPES:
                lL,uL=bounds[(t,scope,1,"degree_near_rays")]
                for mer in MERCURY_POLICIES:
                    lM,uM=bounds[(t,scope,2,mer)]
                    tag=f"{k}|{t:g}deg|{mer}|{scope}"
                    # 4-mode and one possible geometric fifth claim.
                    M,PM=interval_leader(bM+lM,bM+uM,valid)
                    L,PL=interval_leader(bL+lL,bL+uL,valid)
                    # Additional unknown PHASE possibility anywhere (still
                    # only ONE vote in the fifth mode). Never a second vote.
                    pm,_=interval_leader(bM+lM,bM+1,valid)
                    pl,_=interval_leader(bL+lL,bL+1,valid)
                    mb=M>=0;lb=L>=0;both=mb&lb;common=both&(M==L)
                    counts[tag+"|mercury_unique"]+=int(mb.sum())
                    counts[tag+"|moon_unique"]+=int(lb.sum())
                    counts[tag+"|both_unique"]+=int(both.sum())
                    counts[tag+"|same_body"]+=int(common.sum())
                    counts[tag+"|different_bodies"]+=int((both&~common).sum())
                    counts[tag+"|neither_or_one_unresolved_including_sect"]+=int((~both).sum())
                    counts[tag+"|possible_common_top_body"]+=int((PM&PL).any(axis=1).sum())
                    counts[tag+"|phase_uncertainty_both_unique"]+=int(((pm>=0)&(pl>=0)).sum())
                    counts[tag+"|phase_uncertainty_same_body"]+=int(((pm>=0)&(pm==pl)).sum())
                    counts[tag+"|new_both_unique_where_four_mode_not"]+=int((both&~((M0>=0)&(L0>=0))).sum())
                    counts[tag+"|both_unique_changed_from_four_mode"]+=int((both&(M0>=0)&(L0>=0)&((M!=M0)|(L!=L0))).sum())
                    first_mer=np.where(first_mer==-2,M,first_mer);first_moon=np.where(first_moon==-2,L,first_moon)
                    first_pm=np.where(first_pm==-2,pm,first_pm);first_pl=np.where(first_pl==-2,pl,first_pl)
                    all_pair&=both&(M==first_mer)&(L==first_moon)
                    all_phase_pair&=(pm>=0)&(pl>=0)&(pm==first_pm)&(pl==first_pl)
                    num+=1
    if num!=GEOMETRY_SCENARIOS:
        raise RuntimeError("Incomplete historical/geometry policy cross-product")
    counts["prior_all_four_robust_common"]+=int(base_all.sum())
    counts["four_mode_all_variants_same_unique_pair"]+=int(base_pair.sum())
    for label,mask,mer,moon in (
      ("all32_geometry",all_pair,first_mer,first_moon),
      ("all32_with_unknown_phase",all_phase_pair,first_pm,first_pl)):
        same=mask&(mer==moon);different=mask&~same
        counts[label+"|unique_stable_pair"]+=int(mask.sum())
        counts[label+"|same_planet"]+=int(same.sum())
        counts[label+"|different_planets"]+=int(different.sum())
        counts[label+"|retains_prior_robust_common"]+=int((same&base_all&(mer==base_first)).sum())
        if np.any(mask&hd_known):
            hdsets[label+"|any"][h[mask&hd_known]]=True
        if np.any(same&hd_known):
            hdsets[label+"|same"][h[same&hd_known]]=True
        if np.any(different&hd_known):
            hdsets[label+"|different"][h[different&hd_known]]=True
        for ref,sel in (("Mercury",mer),("Moon",moon)):
            candidate=np.where(mask,sel,-1)
            for name,witness in qualifier_flags(lon,alt,candidate).items():
                counts[label+"|"+ref+"|"+name]+=int(witness.sum())
        for i,name in enumerate(PLANETS):
            counts[label+"|common_"+name]+=int((same&(mer==i)).sum())
    if np.any(base_all&(~all_phase_pair|(first_pm!=base_first)|(first_pl!=base_first))):
        raise RuntimeError("Old hypothetical fifth-vote robust common leaders lost")


def source_preflight():
    t=json.loads((ROOT/TASK).read_text())
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    if t["required_repo"]!="u-dont-existDOTcom/astro-research" or branch!=t["required_branch"] or not t["exclusive"]:
        raise RuntimeError("Wrong active source task worktree")
    if not t["parent_outcome"].startswith("OPEN") or not t["suspended_competing_sources"]:
        raise RuntimeError("Unjustified historical completion or competing scope")
    return t


def run(west,angles,hd_cache,hd_join):
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    W=json.loads(wp.read_bytes());WM=json.loads(wm.read_bytes())
    A=json.loads(ap.read_bytes());AM=json.loads(am.read_bytes())
    sha=base.reg.initial.source_hash
    if base.reg.initial.check_manifest(W,WM,A,AM)!=N or W["step_minutes"]!=15:
        raise RuntimeError("Original finite UTC source grid changed")
    if WM["plan_sha256"]!=sha(wp) or AM["plan_sha256"]!=sha(ap):
        raise RuntimeError("Original source plan hash changed")
    proof=base.hdverify.audit_join(west,hd_cache,hd_join)
    H=json.loads((hd_join/"manifest.json").read_bytes())
    if H["total_utc_grid_samples"]!=N or H["total_hd_structural_intervals"]!=HD_COUNT or H["unresolved_near_boundary_samples"]!=125:
        raise RuntimeError("Original HD source universe drift")
    counts=Counter()
    sets={a+"|"+b:np.zeros(HD_COUNT,bool) for a in ("all32_geometry","all32_with_unknown_phase") for b in ("any","same","different")}
    processed=0
    for w,a,h in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=w["count"]
        if not(w["first_index"]==processed==a["first_index"]==h["index_first"] and h["count"]==n):
            raise RuntimeError("Original UTC source row alignment changed")
        paths=(west/"chunks"/w["file"],angles/"shards"/a["file"],hd_join/"shards"/h["file"])
        for path,meta,size in zip(paths,(w,a,h),(64,136,4),strict=True):
            if path.stat().st_size!=n*size or sha(path)!=meta["sha256"]:
                raise RuntimeError("Original binary source SHA or size changed")
        P=np.memmap(paths[0],dtype="<f8",mode="r",shape=(n,8))
        Arows=np.memmap(paths[1],dtype="<f8",mode="r",shape=(n,17))
        ids=np.memmap(paths[2],dtype="<i4",mode="r",shape=(n,))
        scan(P,Arows,ids,counts,sets)
        processed+=n
    result={
       "schema":"ptolemy_III13_separate_Mercury_Moon_fifth_aspect_interval_full_sampled_century_v01",
       "status":"COMPLETE_DECLARED_32_GEOMETRIC_FIFTH_MODE_SENSITIVITIES_NOT_HISTORICAL_FULL_GOVERNOR",
       "source_passages":["Tetrabiblos III.2–3 (Loeb pp233–239)","III.13 (pp333–339), notes 135–138","I.7, I.13, I.23–24; III.4 note 22"],
       "source_sha_manifests":{"planet":sha(wm),"angles":sha(am),"HD":sha(hd_join/"manifest.json")},
       "UTC_horizon":[W["utc_start_inclusive"],W["utc_end_exclusive"]],
       "original_UTC_rows":processed,"resolution_minutes":15,"fixed_reference_location_count":1,
       "source_shard_SHA_rechecked":True,"HD_audit":proof,"HD_structural_intervals":HD_COUNT,
       "source_modes":len(VARIANTS),"orb_sensitivity_degrees":list(TOLS),
       "Mercury_aspect_policies":list(MERCURY_POLICIES),"fifth_claim_body_scopes":list(SCOPES),
       "geometry_scenarios":GEOMETRY_SCENARIOS,
       "phase_bound":"Under each aspect sensitivity any unestablished phase may add ONE fifth vote to any planet; lower=4+ray, upper=4+1. This is conservative algebra, not historical completeness.",
       "conjunction_bound":"Bodily conjunction possible, not verified for entire grid; lower excludes body-only claims, upper admits possible near conjunction, no actual longitude-latitude side assumption.",
       "sect_condition":"I.7 fixed sect; Mercury variable sect UNKNOWN. Opposing fixed sect preceding sign square is a separately labeled possible overcoming geometry, not authoritative strength arbitration.",
       "counts":dict(counts),"HD_distinct_intervals":{k:int(v.sum()) for k,v in sets.items()},
       "historically_complete_soul_governor":False,"independent_human_behavior_validation":False,
       "private_birth_or_interview_data_used":False
    }
    validate(result)
    return result


def validate(j):
    c=j["counts"]
    if (j["original_UTC_rows"]!=N or c["original_UTC_rows"]!=N or
        c["near_horizon_sect_unknown"]!=5049 or c["HD_root_unknown"]!=125 or
        c["prior_all_four_robust_common"]!=4553 or j["HD_structural_intervals"]!=HD_COUNT or
        j["geometry_scenarios"]!=32 or not j["source_shard_SHA_rechecked"]):
        raise RuntimeError("Frozen source denominator/prior 4553 agreement not reproduced")
    if j["historically_complete_soul_governor"] or j["independent_human_behavior_validation"] or j["private_birth_or_interview_data_used"]:
        raise RuntimeError("Unsupported historic/person claim")
    for k in ("all32_geometry","all32_with_unknown_phase"):
        if c[k+"|same_planet"]+c[k+"|different_planets"]!=c[k+"|unique_stable_pair"]:
            raise RuntimeError("Separate-place selection not partitioned")
        if c[k+"|retains_prior_robust_common"]!=4553:
            raise RuntimeError("Prior robust common subset not conserved")
    if c["all32_with_unknown_phase|unique_stable_pair"]>c["all32_geometry|unique_stable_pair"]:
        raise RuntimeError("Adding uncertainty cannot yield more guaranteed pairs")
    for scheme,co in VARIANTS:
        s=scheme+"|"+("all_triplicity_corulers" if co else "principal_triplicity")
        for t in TOLS:
            for scope in SCOPES:
                for mer in MERCURY_POLICIES:
                    k=f"{s}|{t:g}deg|{mer}|{scope}"
                    if c[k+"|same_body"]+c[k+"|different_bodies"]!=c[k+"|both_unique"] or c[k+"|both_unique"]+c[k+"|neither_or_one_unresolved_including_sect"]!=N:
                        raise RuntimeError("Incomplete conditional fifth-mode count")
                    if c[k+"|phase_uncertainty_both_unique"]>c[k+"|both_unique"]:
                        raise RuntimeError("Uncertain phase cannot add unique candidates")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--preflight",action="store_true")
    ap.add_argument("--audit",action="store_true")
    for x in ("west","angles","hd-cache","hd-join","out"):
        ap.add_argument("--"+x,type=Path)
    a=ap.parse_args()
    t=source_preflight()
    if a.preflight:
        print("PASS_SOURCE_TASK_PREFLIGHT")
        return
    if a.audit:
        for p in t["artifacts"]:
            if not (ROOT/p).is_file():raise RuntimeError("Missing original source task artifact: "+p)
        validate(json.loads((ROOT/PUBLIC).read_text()))
        print("PASS_DECLARED_PTOLEMY_32_FIFTH_MODE_SOURCE_CENSUS; PARENT OPEN")
        return
    if any(x is None for x in (a.west,a.angles,a.hd_cache,a.hd_join,a.out)):
        ap.error("full frozen source inputs and new output required")
    if a.out.exists():raise FileExistsError("Do not overwrite original source receipt")
    result=run(a.west,a.angles,a.hd_cache,a.hd_join)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"rows":result["original_UTC_rows"],"models":result["geometry_scenarios"],"status":result["status"]},sort_keys=True))

if __name__=="__main__":main()
