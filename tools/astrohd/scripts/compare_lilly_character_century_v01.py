#!/usr/bin/env python3
"""Finite-grid extension of the frozen Lilly CVII/CVIII primary-character pilot.
Histograms are sufficient statistics for the unchanged mask-based score.
All participant inputs and individual results remain private.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import numpy as np
import swisseph as swe
import compare_lilly_character_panel_v01 as l
import compare_bounded_behavior_v01 as b
import compare_planet_character_century_v01 as pc
import compare_full_grid_behavior_v01 as g

ROOT=b.ROOT
MASKS=(np.arange(128)[:,None] & (1<<np.arange(7)))!=0
BITS=1<<np.arange(7,dtype=np.int64)
PRIOR=pc.MAP.parent/"lilly_cvii_ordered_stage_coverage_full_century_public_v01.json"
CATEGORIES=np.minimum(MASKS.sum(axis=1),2)

def encode(mask):
    if mask.ndim!=2 or mask.shape[1]!=7:
        raise ValueError("Seven-body mask required")
    return (mask*BITS).sum(axis=1)

def lookup(vals,hd_values):
    n=MASKS.sum(axis=1)
    single=np.where(n==1,np.argmax(MASKS,axis=1),-1)
    z=l.score(MASKS,single,MASKS,vals,np.zeros(128))
    out={}
    for arm in l.ARMS:
        w=np.broadcast_to(z[arm]["western"],(len(hd_values),128))
        out[arm]={"western":w.ravel(),"joint":((hd_values[:,None]+w)/2).ravel()}
    lo=np.broadcast_to(z["envelope"]["western_lo"],(len(hd_values),128))
    hi=np.broadcast_to(z["envelope"]["western_hi"],(len(hd_values),128))
    out["envelope"]={"western_lo":lo.ravel(),"western_hi":hi.ravel(),
                    "joint_lo":((hd_values[:,None]+lo)/2).ravel(),
                    "joint_hi":((hd_values[:,None]+hi)/2).ravel()}
    return out

def exact(v,t,hist):
    return Counter(higher=int(hist[v>t+g.EPS].sum()),
                   tied=int(hist[np.abs(v-t)<=g.EPS].sum()),
                   lower=int(hist[v<t-g.EPS].sum()))

def bounds(lo,hi,tlo,thi,hist):
    return Counter(certainly_higher=int(hist[lo>thi+g.EPS].sum()),
                   certainly_lower=int(hist[hi<tlo-g.EPS].sum()),
                   could_equal_or_exceed=int(hist[hi>=tlo-g.EPS].sum()))

def compare_hist(ph,oh,table,target,ref_primary_count):
    res={}
    match=np.tile(MASKS.sum(axis=1)==ref_primary_count,len(ph)//128)
    for arm in l.ARMS:
        for kind in ("western","joint"):
            v=table[arm][kind];t=target[arm][kind]
            res[arm+"|"+kind]=exact(v,t,ph)
            if kind=="joint":
                res[arm+"|matched_primary_count"]=exact(v,t,ph*match)
    for kind in ("western","joint"):
        a=table["envelope"];t=target["envelope"]
        res["envelope|"+kind]=bounds(a[kind+"_lo"],a[kind+"_hi"],t[kind+"_lo"],t[kind+"_hi"],oh)
    return res

def scan_chunk(lon,alt,cusp,ids,codes,n_codes,stage_counts,histograms,coverage):
    known=ids>=0
    if np.any(ids < -1) or np.any(ids>=g.HD_N):
        raise ValueError("Invalid HD indices")
    hcodes=[c[np.maximum(ids,0)][known]*128 for c in codes]
    coverage.update({"rows":len(ids),"ranked":int(known.sum()),"unknown_HD":int((~known).sum())})
    seen=set()
    for tag,status,single,primary,sc,sp,outer in l.branches(lon,alt,cusp[:,0],cusp[:,1]):
        if tag in seen:raise ValueError("Duplicate historical scenario")
        seen.add(tag)
        status_hist=np.bincount(status,minlength=12)
        for i,label in l.stage.LABELS.items():
            stage_counts[tag+"|"+label]+=int(status_hist[i])
        pn=primary.sum(axis=1)
        if np.any((pn==1)!=(single>=0)) or np.any(primary&~outer) or np.any(sc&~sp) or np.any(sp&primary):
            raise ValueError("Primary/secondary source mask mismatch")
        pm=encode(primary)[known];om=encode(outer)[known]
        for code,size,out in zip(hcodes,n_codes,histograms,strict=True):
            ph=np.bincount(code+pm,minlength=128*size)
            oh=np.bincount(code+om,minlength=128*size)
            if tag not in out:
                out[tag]=[ph,oh,Counter()]
            else:
                out[tag][0]+=ph;out[tag][1]+=oh
            out[tag][2].update({"secondary_possible":int((known&sp.any(axis=1)).sum()),
                                "secondary_certain":int((known&sc.any(axis=1)).sum())})
    if len(seen)!=96:raise ValueError("Missing historical scenarios")

def finalize(hists,table,refs,ranked):
    out={}
    if set(hists)!=set(refs):raise ValueError("Reference/scenario mismatch")
    for tag,(ph,oh,other) in hists.items():
        if int(ph.sum())!=ranked or int(oh.sum())!=ranked:
            raise ValueError("Histogram row accounting failed")
        r=refs[tag]
        mask_counts=ph.reshape(-1,128).sum(axis=0)
        cats=np.bincount(CATEGORIES,weights=mask_counts,minlength=3)
        cov={"ranked":ranked,"unknown_primary":int(cats[0]),"single_primary":int(cats[1]),
             "multiple_primary":int(cats[2]),**other,
             "matched_primary_count":int(mask_counts[MASKS.sum(axis=1)==len(r["primary"])].sum())}
        ans=compare_hist(ph,oh,table,r["scores"],len(r["primary"]))
        for arm in l.ARMS:
            for k in ("western","joint"):
                if sum(ans[arm+"|"+k].values())!=ranked:raise ValueError("Exact count drift")
            if sum(ans[arm+"|matched_primary_count"].values())!=cov["matched_primary_count"]:
                raise ValueError("Matched count drift")
        for k in ("western","joint"):
            z=ans["envelope|"+k]
            if z["certainly_lower"]+z["could_equal_or_exceed"]!=ranked or z["certainly_higher"]>z["could_equal_or_exceed"]:
                raise ValueError("Bound count drift")
        out[tag]={**ans,"coverage":cov}
    return out

def run(a):
    inputs=[a.west,a.angles,a.hd_cache,a.join,a.mapping_library,a.inventory,*a.evidence,*a.hd_evidence,*a.prior_panel]
    if any(p.resolve().is_relative_to(ROOT) for p in inputs+[a.output]):
        raise ValueError("Private inputs and output must stay outside public checkout")
    if a.output.exists() or any(len(x)!=2 for x in (a.evidence,a.hd_evidence,a.prior_panel)):
        raise ValueError("Two immutable observation versions and new output required")
    W,WM,A,AM,H,proof=g.verify_inputs(a)
    if swe.version!="2.10.03":raise ValueError("Original Swiss Ephemeris version changed")
    inv=json.loads(a.inventory.read_text());units=inv["comparison_units"]
    ref=next(u["chart_midpoint"] for u in units if u["private_id"]=="REFERENCE")
    w=ref["Western"]["source_witness"];at=g.timestamp(ref["utc"])
    if at!=g.timestamp(w["UTC"]) or any(float(w["site"][k])!=float(A[k]) for k in ("latitude","longitude","elevation_m")):
        raise ValueError("Reference site/time mismatch")
    mappings=b.load_mapping(a.mapping_library);reg,shared=l.load_map()
    hd_ev=[];tables=[];refs=[];prov=[]
    for hp,ep,pp in zip(a.hd_evidence,a.evidence,a.prior_panel,strict=True):
        h=json.loads(hp.read_text());e=json.loads(ep.read_text());p=json.loads(pp.read_text())
        if h["inventory_sha256"]!=b.digest(a.inventory) or e["map_sha256"]!=pc.MAP_SHA or e["hd_evidence_sha256"]!=b.digest(hp) or p["map_sha256"]!=l.MAP_SHA or p["runner_sha256"]!=b.digest(l.__file__):
            raise ValueError("Frozen map, observation or panel scorer drift")
        for k,path in (("inventory",a.inventory),("mapping_library",a.mapping_library),("hd_evidence",hp),("evidence",ep)):
            if p["source_hashes"][k]!=b.digest(path):raise ValueError("Prior pilot input mismatch")
        fresh=l.compare(units,mappings,h["hd"],e["observations"])
        if fresh["cases"]!=p["cases"] or fresh["ranks"]!=p["ranks"]:
            raise ValueError("Prior panel score replay mismatch")
        vals,den,_=l.table(reg,shared,e["observations"])
        tables.append(vals);refs.append(fresh["cases"]["REFERENCE"]);hd_ev.append(h)
        prov.append({"HD_evidence_sha256":b.digest(hp),"evidence_sha256":b.digest(ep),"prior_panel_sha256":b.digest(pp),"observed_domains":den})
    hlookups,idx,_=g.load_hd_scores(a.hd_cache,mappings,hd_ev,at,ref["HD"])
    codes=[];n_codes=[];lookups=[]
    for h,t,e in zip(hlookups,tables,hd_ev,strict=True):
        if h[idx]!=b.hd_score(ref["HD"],mappings,e["hd"])["score"]:
            raise ValueError("Reference HD replay mismatch")
        values,code=np.unique(h,return_inverse=True)
        codes.append(code);n_codes.append(len(values));lookups.append(lookup(t,values))
    source=Counter();histograms=[{},{}];coverage=Counter()
    jd=l.stage.old.s3.s1.base.es.src.PRIOR.base.reg.julian_from_utc(W["utc_start_inclusive"])
    lat=float(A["latitude"]);lon=float(A["longitude"]);processed=0
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not (wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):
            raise ValueError("Source shard alignment drift")
        paths=(a.west/"chunks"/wi["file"],a.angles/"shards"/ai["file"],a.join/"shards"/hi["file"])
        for p,meta,size in zip(paths,(wi,ai,hi),(64,136,4),strict=True):
            if p.stat().st_size!=n*size or b.digest(p)!=meta["sha256"]:raise ValueError("Source shard SHA drift")
        P=np.memmap(paths[0],dtype="<f8",mode="r",shape=(n,8))
        AA=np.memmap(paths[1],dtype="<f8",mode="r",shape=(n,17))
        ids=np.memmap(paths[2],dtype="<i4",mode="r",shape=(n,))
        cusp=np.array([swe.houses_ex(jd+(processed+i)/96.,lat,lon,b"R")[0][:2] for i in range(n)])
        if np.max(np.abs((cusp[:,0]-AA[:,0]+180)%360-180))>0.0002:
            raise ValueError("Original ascending longitude drift")
        scan_chunk(np.asarray(P[:,:7]),np.asarray(AA[:,4]),cusp,ids,codes,n_codes,source,histograms,coverage)
        processed+=n
        if processed%500000==0 or processed==g.N:print("Lilly character scoring:",processed,"/",g.N,flush=True)
    if processed!=g.N or coverage!={"rows":g.N,"ranked":g.N-125,"unknown_HD":125}:
        raise ValueError("Grid accounting drift")
    old=json.loads(PRIOR.read_text())["counts"]
    if len(source)!=96*11 or any(v!=old[k] for k,v in source.items()):
        raise ValueError("Original 96-stage count reconciliation failed")
    profiles=[{**p,"reference":r,"scenarios":finalize(h,t,r,g.N-125)}
              for p,r,h,t in zip(prov,refs,histograms,lookups,strict=True)]
    result={"status":"EXECUTED_FULL_FINITE_GRID_LILLY_PRIMARY_CHARACTER_NOT_VALIDATION","grid_rows":processed,
            "ranked_rows":processed-125,"source_stage_counts_reproduced":True,"historical_branches":96,
            "arms":list(l.ARMS),"map_sha256":l.MAP_SHA,"runner_sha256":b.digest(__file__),"grid_proof":proof,
            "source_census_sha256":b.digest(PRIOR),"profiles":profiles}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("Private Lilly full-grid result complete; all prior stage counts and panel scores reconciled.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","mapping-library","inventory","output"):
        p.add_argument("--"+k,type=Path,required=True)
    for k in ("evidence","hd-evidence","prior-panel"):
        p.add_argument("--"+k,type=Path,action="append",required=True)
    run(p.parse_args())
if __name__=="__main__":main()
