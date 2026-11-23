#!/usr/bin/env python3
"""Exhaustively apply the frozen PR36 development rubric on the PR35 finite grid.
No personal scores or observations go to stdout or to the public checkout.
The reference is an exact-time private chart; ranks count grid rows, not people.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import os
import numpy as np
import compare_bounded_behavior_v01 as b
import ptolemy_iii13_five_mode_aspect_century_v01 as src

ROOT=b.ROOT
N=src.N
HD_N=src.HD_COUNT
HD_MANIFEST="a7bec3c4e855d286bbdb93737a58043119cd11ae908c36e73ee118d7d467c746"
HD_ROWS="73370f9d898ce43d6e497850236694cd6777d62f4fff3766d20200885e40eaa9"
EPS=1e-12
SCHEMES=list(product(src.VARIANTS,src.TOLS,src.MERCURY_POLICIES,src.SCOPES))

def timestamp(s):
    x=datetime.fromisoformat(s.replace("Z","+00:00"))
    if x.utcoffset() is None or x.utcoffset().total_seconds()!=0:
        raise ValueError("Explicit UTC required")
    return x

def source_hd_chart(f):
    return {"type": f["type"].replace("_"," ").title(),
            "profile":f["profile"],"defined_centers":[
                {"heart_ego":"Heart","solar_plexus":"Solar Plexus","g":"G"}.get(c,c.replace("_"," ").title())
                for c in f["defined_centers"]]}

def load_hd_scores(root, mappings, evidence, at, ref):
    mf=root/"manifest.json";m=json.loads(mf.read_text())
    if b.digest(mf)!=HD_MANIFEST or m["canonical_rows_sha256"]!=HD_ROWS:
        raise ValueError("HD source manifest or rows changed")
    scores=[[] for e in evidence]; seen={};rawhash=sha256();prev=None
    refhits=0;refindex=None
    for shard in m["shards"]:
        fp=root/shard["filename"]
        raw_compressed=fp.read_bytes()
        if sha256(raw_compressed).hexdigest()!=shard["sha256"]:
            raise ValueError("HD source shard SHA drift")
        raw=gzip.decompress(raw_compressed)
        if len(raw)!=shard["uncompressed_bytes"]:
            raise ValueError("HD source byte count drift")
        rawhash.update(raw);count=0
        for line in raw.splitlines():
            x=json.loads(line);start,end=map(timestamp,(x["start_utc"],x["end_utc"]))
            if (prev is not None and start!=prev) or end<=start:
                raise ValueError("HD state gap or overlap")
            prev=end;count+=1
            f=source_hd_chart(x["chart_features"])
            key=(f["type"],f["profile"],tuple(sorted(f["defined_centers"])))
            if key not in seen:
                seen[key]=[b.hd_score(f,mappings,e["hd"])["score"] for e in evidence]
            val=seen[key]
            if start<=at<end:
                refhits+=1;refindex=len(scores[0])
                if any(b.hd_active(f,r["chart_feature_predicate"])!=b.hd_active(ref,r["chart_feature_predicate"]) for r in mappings):
                    raise ValueError("Exact reference HD state mismatch on admitted predicates")
            for a,v in zip(scores,val,strict=True):a.append(v)
        if count!=shard["state_count"]:
            raise ValueError("HD source shard state count drift")
    if rawhash.hexdigest()!=HD_ROWS or any(len(x)!=HD_N for x in scores) or refhits!=1:
        raise ValueError("HD logical hash/count or reference binding failed")
    return [np.asarray(x) for x in scores],refindex,len(seen)

def vote_arrays(lon, obs):
    signs=np.floor(lon/30).astype(np.int8)
    if not np.isfinite(lon).all() or np.any((signs<0)|(signs>11)):
        raise ValueError("Invalid longitude")
    vals={}
    for name in b.PLACES:
        table=np.array([b.vote(obs,f"{name}_{m}") for m in b.MODES],np.int8)
        vals[name]=table[signs]
    d=(lon[:,1]-lon[:,0])%360
    phase=np.where((d>0)&(d<180),b.vote(obs,"moon_waxing_frankness"),
        np.where((d>180)&(d<360),b.vote(obs,"moon_waning_caution"),0)).astype(np.int8)
    return vals["mercury"],vals["moon"],phase

def place_values(votes, leader, possible):
    if votes.shape!=possible.shape or leader.shape!=(len(votes),):
        raise ValueError("Aligned place score and candidate arrays required")
    r=np.arange(len(votes));g=np.where(leader>=0,votes[r,np.maximum(leader,0)],0)
    anyp=possible.any(axis=1)
    lo=np.where(anyp,np.where(possible,votes,2).min(axis=1),0)
    hi=np.where(anyp,np.where(possible,votes,-2).max(axis=1),0)
    return g,lo,hi

def exact_counts(v,target,known):
    return Counter(higher=int((known&(v>target+EPS)).sum()),
                   tied=int((known&(np.abs(v-target)<=EPS)).sum()),
                   lower=int((known&(v<target-EPS)).sum()))

def bound_counts(lo,hi,target,known):
    tl,th=target
    return Counter(certainly_higher=int((known&(lo>th+EPS)).sum()),
                   could_equal_or_exceed=int((known&(hi>=tl-EPS)).sum()),
                   certainly_lower=int((known&(hi<tl-EPS)).sum()))

def scenario_scores(h, mv, lv, phase, target, known):
    mg,ml,mh=mv;lg,ll,lh=lv
    w,j=b.family(mg,lg,phase,h)
    _,pl=b.family(ml,ll,phase,h);_,ph=b.family(mh,lh,phase,h)
    wl,cl=b.family(np.minimum(0,ml),np.minimum(0,ll),np.minimum(0,phase),h)
    wh,ch=b.family(np.maximum(0,mh),np.maximum(0,lh),np.maximum(0,phase),h)
    return {"strict_joint":exact_counts(j,target["joint_strict"],known),
            "possible_joint":bound_counts(pl,ph,target["joint_possible"],known),
            "conservative_joint":bound_counts(cl,ch,target["joint_conservative"],known),
            "conservative_western":bound_counts(wl,wh,target["western_conservative"],known)},j

def scan_chunk(lon,alt,ids,hdlookup,evidence,refs,counts):
    known=ids>=0
    if np.any(ids < -1) or np.any(ids>=len(hdlookup[0])):
        raise ValueError("HD lookup index out of range")
    valid=np.abs(alt)>b.base.SUN_ALT_UNCERTAINTY
    vs=[vote_arrays(lon,e["western"]) for e in evidence]
    hs=[lookup[np.maximum(ids,0)] for lookup in hdlookup]
    higher_all=[known.copy() for _ in evidence];higher_any=[np.zeros(len(ids),bool) for _ in evidence]
    tied_all=[known.copy() for _ in evidence]
    for k,(h,(m,l,ph),target) in enumerate(zip(hs,vs,refs,strict=True)):
        r=target["cases"]["REFERENCE"]
        w,j=b.family(m[:,2],l[:,1],ph,h)
        out=counts[k]
        out["HD_direct"].update(exact_counts(h,r["hd"]["score"],known))
        out["Western_direct"].update(exact_counts(w,r["western_direct"],known))
        out["joint_direct"].update(exact_counts(j,r["joint_direct"],known))
        out["coverage"].update({"rows":len(ids),"known":int(known.sum()),
                                "unknown_HD":int((~known).sum()),"unknown_sect":int((~valid).sum())})
    # Cache independent lunar/mercurial aspects, exactly the PR35 choices.
    aspects={}
    for tol,scope in product(src.TOLS,src.SCOPES):
        for ref,policies in ((1,("degree_near_rays",)),(2,src.MERCURY_POLICIES)):
            for policy in policies:
                lo,hi,_=src.aspect_bounds(lon,ref,tol,policy,scope)
                aspects[ref,tol,policy,scope]=(lo,hi)
    for scheme,co in src.VARIANTS:
        baseM=b.base.four_mode_votes(lon[:,2],alt,scheme,co).astype(np.int16)
        baseL=b.base.four_mode_votes(lon[:,1],alt,scheme,co).astype(np.int16)
        for tol,scope in product(src.TOLS,src.SCOPES):
            llo,lhi=aspects[1,tol,"degree_near_rays",scope]
            lunar={}
            for label,upper in (("geometry",lhi),("phase_envelope",1)):
                leader,possible=src.interval_leader(baseL+llo,baseL+upper,valid)
                lunar[label]=[place_values(l,leader,possible) for m,l,p in vs]
            for policy in src.MERCURY_POLICIES:
                mlo,mhi=aspects[2,tol,policy,scope]
                for label,upper in (("geometry",mhi),("phase_envelope",1)):
                    tag=f"{scheme}|{co}|{tol}|{policy}|{scope}|{label}"
                    leader,possible=src.interval_leader(baseM+mlo,baseM+upper,valid)
                    for k,(h,(m,l,ph),target) in enumerate(zip(hs,vs,refs,strict=True)):
                        mv=place_values(m,leader,possible);lv=lunar[label][k]
                        tc=target["scenarios"][tag]["cases"]["REFERENCE"]
                        add,j=scenario_scores(h,mv,lv,ph,tc,known)
                        for metric,v in add.items():
                            counts[k][tag+"|"+metric].update(v)
                        higher=known&(j>tc["joint_strict"]+EPS)
                        tied=known&(np.abs(j-tc["joint_strict"])<=EPS)
                        higher_all[k]&=higher;higher_any[k]|=higher;tied_all[k]&=tied
    for k in range(len(evidence)):
        counts[k]["across_scenarios"].update({"strictly_higher_every_scenario":int(higher_all[k].sum()),
                "strictly_higher_any_scenario":int(higher_any[k].sum()),
                "tied_every_scenario":int(tied_all[k].sum())})

def verify_inputs(a):
    prior=json.loads((ROOT/"tools/astrohd/reference/research/ptolemy_iii13_five_mode_aspect_century_public_v01.json").read_text())
    Wm=a.west/"verified_manifest.json";Am=a.angles/"verified_manifest.json";Hm=a.join/"manifest.json"
    for p,key in ((Wm,"planet"),(Am,"angles"),(Hm,"HD")):
        if b.digest(p)!=prior["source_sha_manifests"][key]:
            raise ValueError("Original PR35 grid SHA drift")
    W=json.loads((a.west/"plan.json").read_text());WM=json.loads(Wm.read_text())
    A=json.loads((a.angles/"plan.json").read_text());AM=json.loads(Am.read_text())
    if WM["plan_sha256"]!=b.digest(a.west/"plan.json") or AM["plan_sha256"]!=b.digest(a.angles/"plan.json"):
        raise ValueError("Original source plan hash drift")
    if b.base.reg.initial.check_manifest(W,WM,A,AM)!=N or W["step_minutes"]!=15:
        raise ValueError("Original source clock coverage drift")
    proof=b.base.hdverify.audit_join(a.west,a.hd_cache,a.join)
    if proof["sample_count"]!=N or proof["HD_structural_intervals"]!=HD_N or proof["unresolved_HD_transition_near_samples"]!=125:
        raise ValueError("Original joined source count drift")
    return W,WM,A,AM,json.loads(Hm.read_text()),proof

def run(a):
    allpaths=[a.west,a.angles,a.hd_cache,a.join,a.mapping_library,a.inventory,a.output,*a.evidence,*a.prior_receipt]
    if any(x.resolve().is_relative_to(ROOT) for x in allpaths):
        raise ValueError("Private inputs and outputs must remain outside the public checkout")
    if a.output.exists():
        raise FileExistsError("Private output is immutable")
    if len(a.evidence)!=len(a.prior_receipt) or not a.evidence:
        raise ValueError("One prior PR36 receipt per evidence coding")
    W,WM,A,AM,H,proof=verify_inputs(a)
    mappings=b.load_mapping(a.mapping_library)
    inv=json.loads(a.inventory.read_text())
    units=inv["comparison_units"]
    ref=next(u for u in units if u["private_id"]=="REFERENCE")
    c=ref["chart_midpoint"];w=c["Western"]["source_witness"]
    if any(float(w["site"][k])!=float(A[k]) for k in ("latitude","longitude","elevation_m")):
        raise ValueError("Reference and grid site differ; no cross-site rank")
    at=timestamp(c["utc"])
    if at!=timestamp(w["UTC"]):
        raise ValueError("Reference chart time not aligned")
    evidence=[];refs=[]
    for epath,rpath in zip(a.evidence,a.prior_receipt,strict=True):
        e=json.loads(epath.read_text());r=json.loads(rpath.read_text())
        if (e["inventory_sha256"]!=b.digest(a.inventory) or r["input_digests"]["evidence"]!=b.digest(epath)
            or r["input_digests"]["inventory"]!=b.digest(a.inventory)
            or r["input_digests"]["mapping"]!=b.digest(a.mapping_library)
            or r["input_digests"]["scorer"]!=b.digest(b.__file__)):
            raise ValueError("Frozen PR36 input/receipt/scorer binding changed")
        fresh=b.compare(units,mappings,e["hd"],e["western"])
        if fresh["cases"]!=r["cases"] or fresh["scenarios"]!=r["scenarios"] or fresh["direct_ranks"]!=r["direct_ranks"]:
            raise ValueError("Prior full panel score replay mismatch")
        evidence.append(e);refs.append(r)
    hdlookup,refindex,n_signatures=load_hd_scores(a.hd_cache,mappings,evidence,at,c["HD"])
    for lookup,r in zip(hdlookup,refs,strict=True):
        if lookup[refindex]!=r["cases"]["REFERENCE"]["hd"]["score"]:
            raise ValueError("Reference HD score replay mismatch")
    from collections import defaultdict
    counts=[defaultdict(Counter) for e in evidence]
    processed=0
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not (wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):
            raise ValueError("Grid shard row alignment drift")
        paths=(a.west/"chunks"/wi["file"],a.angles/"shards"/ai["file"],a.join/"shards"/hi["file"])
        for p,meta,size in zip(paths,(wi,ai,hi),(64,136,4),strict=True):
            if p.stat().st_size!=n*size or b.digest(p)!=meta["sha256"]:
                raise ValueError("Grid shard size or SHA drift")
        P=np.memmap(paths[0],dtype="<f8",mode="r",shape=(n,8));Arows=np.memmap(paths[1],dtype="<f8",mode="r",shape=(n,17))
        ids=np.memmap(paths[2],dtype="<i4",mode="r",shape=(n,))
        scan_chunk(np.asarray(P[:,:7]),np.asarray(Arows[:,4]),ids,hdlookup,evidence,refs,counts)
        processed+=n
        if processed%500000==0 or processed==N:
            print("Verified and scored",processed,"of",N,"grid rows",flush=True)
    if processed!=N:
        raise ValueError("Incomplete full-grid scoring")
    for row in counts:
        known=row["coverage"]["known"]
        if row["coverage"]!={"rows":N,"known":N-125,"unknown_HD":125,"unknown_sect":5049}:
            raise ValueError("Source count drift")
        strict=[k for k in row if k.endswith("|strict_joint")]
        if len(strict)!=64 or any(sum(row[k].values())!=known for k in strict+["HD_direct","Western_direct","joint_direct"]):
            raise ValueError("Missing score rows or scenarios")
    start=timestamp(W["utc_start_inclusive"])
    grid_offset=(at-start).total_seconds()/900
    result={"status":"EXHAUSTIVE_FROZEN_RUBRIC_FINITE_GRID_DEVELOPMENT_NOT_VALIDATION",
            "grid_rows":N,"ranked_rows":N-125,"unranked_HD_boundary":125,
            "reference_in_grid":grid_offset==int(grid_offset),"same_site_verified":True,
            "grid_source_proof":proof,"HD_unique_structural_score_keys":n_signatures,
            "frozen_source_hashes":{"scorer":b.digest(b.__file__),"runner":b.digest(__file__),
             "mapping":b.digest(a.mapping_library),"inventory":b.digest(a.inventory)},
            "profiles":[{"evidence_sha256":b.digest(ep),"prior_receipt_sha256":b.digest(rp),
                         "reference_direct_scores":{key:rr["cases"]["REFERENCE"][key] for key in ("western_direct","joint_direct")},
                         "reference_HD_score":rr["cases"]["REFERENCE"]["hd"]["score"],
                         "counts":dict(co)} for ep,rp,rr,co in zip(a.evidence,a.prior_receipt,refs,counts,strict=True)]}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("Completed private result:",len(evidence),"frozen evidence codings; 64 scenarios each.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("west","angles","hd-cache","join","mapping-library","inventory","output"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--evidence",type=Path,action="append",required=True)
    p.add_argument("--prior-receipt",type=Path,action="append",required=True)
    run(p.parse_args())

if __name__=="__main__":main()
