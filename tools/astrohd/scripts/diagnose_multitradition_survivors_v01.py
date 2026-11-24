#!/usr/bin/env python3
"""Audit frozen cross-system survivors and HD-ceiling-conditioned clock controls.

No fitted weights, new observations, real-person null population, or empirical
predictive validation. Private evidence and individual outputs stay private.
"""
from __future__ import annotations
import argparse,gzip,json,math,os
from collections import Counter,defaultdict
from datetime import timedelta
from pathlib import Path
import numpy as np
import compare_multitradition_intersections_v01 as m
import compare_multitradition_cross_coding_v01 as cc

SEED=20261124
CONTROL_N=64
DAY_ROWS=96
CORE=m.PRIMARY
EXTRA=tuple(k for k in m.GROUPS if k not in CORE)
KEY="ptolemy_blend + lilly + vedic_union + chinese_union"

class Capture(m.Extrema):
    def __init__(self,n,scale):
        super().__init__(n);self.values={};self.scale=scale
    def add(self,tag,delta,known):
        super().add(tag,delta,known)
        v=np.rint(delta*self.scale)
        if np.any(np.abs(v/self.scale-delta)>m.EPS/4) or np.any(np.abs(v)>np.iinfo(np.int32).max):
            raise ValueError("Exact rational representation failed")
        self.values[tag]=v.astype(np.int32)

def rational_scale(den):
    # Ptolemy blend has quarter faculty weights, sign has eighths;
    # Lilly means over up to seven principal planets.
    return math.lcm(8,*[4*n*k for n in den if n for k in range(1,8)])

def common_mask(lon,jds,bs,ls,cache):
    ok=np.ones(len(lon),bool)
    for _,mode in m.v.MODES:
        _,_,near,_=m.v.signs_and_graph(lon,jds,mode);ok&=~near
    for wall in (bs,ls):
        f=m.cal.features(bs,wall,cache);ok&=f["bazi_known"]&f["ziwei_known"]
    return ok

def collect(a,W,WM,A,AM,H,profiles,lookup,cache):
    start=m.g.timestamp(W["utc_start_inclusive"])
    jd0=m.swe.julday(start.year,start.month,start.day,start.hour+start.minute/60)
    lat,long=float(A["latitude"]),float(A["longitude"])
    chunks=defaultdict(list);processed=eligible=0
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not(wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):raise ValueError("Grid alignment drift")
        paths=(a.west/"chunks"/wi["file"],a.angles/"shards"/ai["file"],a.join/"shards"/hi["file"])
        for path,meta,size in zip(paths,(wi,ai,hi),(64,136,4),strict=True):
            if path.stat().st_size!=n*size or m.b.digest(path)!=meta["sha256"]:raise ValueError("Shard integrity drift")
        P=np.memmap(paths[0],dtype="<f8",mode="r",shape=(n,8));AA=np.memmap(paths[1],dtype="<f8",mode="r",shape=(n,17));ids=np.memmap(paths[2],dtype="<i4",mode="r",shape=(n,))
        if np.any(ids<-1) or np.any(ids>=m.g.HD_N):raise ValueError("Invalid HD index")
        good=ids>=0
        for q,h in zip(profiles,lookup,strict=True):good&=h[np.maximum(ids,0)]>=q["h0"]-m.EPS
        j=np.flatnonzero(good);eligible+=len(j)
        if len(j):
            bs,ls=m.cal.wall_arrays(start+timedelta(seconds=900*processed),n)
            idx=processed+j;jds=jd0+idx/96.
            lon=np.asarray(P[j,:7]);ok=common_mask(lon,jds,bs[j],ls[j],cache)
            j=j[ok];idx=idx[ok];jds=jds[ok];lon=lon[ok]
            cusp=np.array([m.swe.houses_ex(jd,lat,long,b"R")[0][:2] for jd in jds]).reshape(-1,2)
            if len(j) and np.max(np.abs((cusp[:,0]-AA[j,0]+180)%360-180))>0.0002:raise ValueError("ASC drift")
            for k,x in dict(lon=lon,alt=np.asarray(AA[j,4]),cusp=cusp,jds=jds,bs=bs[j],ls=ls[j],index=idx,states=np.asarray(ids[j])).items():
                chunks[k].append(x)
        processed+=n
    if processed!=m.g.N:raise ValueError("Incomplete source grid")
    return {k:np.concatenate(v,axis=0) for k,v in chunks.items()},eligible

def select(data,ix):return {k:v[ix] for k,v in data.items()}

def evaluate(data,profiles,registry,edges,cache,scales):
    n=len(data["index"]);lon,alt,cusp=data["lon"],data["alt"],data["cusp"]
    ext=[{k:Capture(n,scale) for k in m.GROUPS} for scale in scales]
    marginal=[defaultdict(lambda:defaultdict(Counter)) for _ in profiles]
    ones=[np.full(n,q["h0"]) for q in profiles];ok=np.ones(n,bool)
    m.western(lon,alt,cusp,ones,ok,profiles,ext,marginal)
    reg,prior,shared=registry
    for geom,mode in m.v.MODES:
        signs,graph,near,_=m.v.signs_and_graph(lon,data["jds"],mode)
        if np.any(near):raise ValueError("Unexpected Vedic boundary in common cohort")
        for q,ee in zip(profiles,ext,strict=True):
            tab,obs=q["vedic_tables"]
            for tag,bits in m.v.compute(signs,graph,reg,edges,tab).items():
                if not tag.endswith("|all_union"):continue
                key=geom+"|"+tag
                ee["vedic_union"].add(key,m.v.score(bits,obs)["score"]-q["prior"]["vedic"]["reference"][key]["score"],ok)
    for clock,wall in zip(m.cal.CLOCKS,(data["bs"],data["ls"]),strict=True):
        f=m.cal.features(data["bs"],wall,cache)
        for q,ee in zip(profiles,ext,strict=True):
            t=q["chinese_tables"]
            for tag,bits,good in m.z.models(f,t):
                if not tag.startswith("union|"):continue
                if not np.all(good):raise ValueError("Unexpected Chinese boundary in common cohort")
                key=clock+"|"+tag
                ee["chinese_union"].add(key,m.v.score(bits,t[2])["score"]-q["prior"]["chinese"]["reference"][key]["score"],good)
    mats={}
    for family,count in m.GROUPS.items():
        a,b=ext[0][family],ext[1][family];tags=sorted(a.values)
        if len(tags)!=count or set(tags)!=set(b.values) or not np.all(a.known&b.known):raise ValueError("Missing/unaligned score variants")
        mats[family]=(np.stack([a.values[k] for k in tags],axis=1),np.stack([b.values[k] for k in tags],axis=1))
    return mats

def join_matrix(mats,groups):
    return np.concatenate([v for k in groups for v in mats[k]],axis=1)

def dominating(matrix,target,initial=None):
    """Exact same-column comparison, cheap rejection before full comparisons.
    Column order affects runtime only; every column must pass.
    """
    ix=np.arange(len(matrix)) if initial is None else np.flatnonzero(initial)
    # First try the highest target differences, then every remaining column.
    order=np.argsort(-target,kind="stable")
    for off in range(0,len(order),24):
        cols=order[off:off+24]
        ix=ix[np.all(matrix[np.ix_(ix,cols)]>=target[cols],axis=1)]
        if not len(ix):break
    return ix

def rival_mask(mats):
    return np.logical_and.reduce([np.any((mats[k][0]>0)&(mats[k][1]>0),axis=1) for k in CORE])

def universal(mats,groups):
    return np.logical_and.reduce([np.all(v>=0,axis=1) for k in groups for v in mats[k]])

def update_controls(core,extra,control_core,control_extra,indices,controls,counts):
    for i,(a,b0,ix) in enumerate(zip(control_core,control_extra,controls,strict=True)):
        j=dominating(core,a)
        strict=np.any(core[j]>a,axis=1)
        far=np.abs(indices[j]-ix)>DAY_ROWS
        r=counts[i]
        r.update(core_weak=len(j),core_pareto=int(strict.sum()),core_weak_outside_24h=int(far.sum()),
                 core_pareto_outside_24h=int((strict&far).sum()))
        k=j[np.all(extra[j]>=b0,axis=1)]
        strict2=np.any(core[k]>a,axis=1)|np.any(extra[k]>b0,axis=1)
        far2=np.abs(indices[k]-ix)>DAY_ROWS
        r.update(all_weak=len(k),all_pareto=int(strict2.sum()),all_weak_outside_24h=int(far2.sum()),
                 all_pareto_outside_24h=int((strict2&far2).sum()))

def hd_audit(a,profiles,data,rivals):
    """Missing-rule opportunity only, not scoring, no new personal answers."""
    rows=m.b.load_mapping(a.mapping_library)
    manifest=json.loads((a.hd_cache/"manifest.json").read_text())
    # prepare() already verifies every structural source row and digest.
    states=set(map(int,np.unique(data["states"])))
    lookup={};idx=0
    for shard in manifest["shards"]:
        for line in gzip.decompress((a.hd_cache/shard["filename"]).read_bytes()).splitlines():
            if idx in states:
                x=json.loads(line);lookup[idx]=m.g.source_hd_chart(x["chart_features"])
            idx+=1
    if idx!=m.g.HD_N or set(lookup)!=states:raise ValueError("HD structural trace missing")
    inv=json.loads(a.inventory.read_text());ref=next(q["chart_midpoint"]["HD"] for q in inv["comparison_units"] if q["private_id"]=="REFERENCE")
    result={"eligible_state_intervals":len(states),"distinct_structural_keys":len({(x["type"],x["profile"],tuple(sorted(x["defined_centers"]))) for x in lookup.values()}),
            "profile_counts":{},"rival_profile_counts":{},"known_rule_counts":[],"unobserved_predicate_groups":[]}
    ids=data["states"];rid=ids[np.isin(data["index"],rivals)]
    for k,ii in (("profile_counts",ids),("rival_profile_counts",rid)):
        counts=Counter()
        for s,n in zip(*np.unique(ii,return_counts=True),strict=True):counts[lookup[int(s)]["profile"]]+=int(n)
        result[k]=dict(counts)
    for q in profiles:
        obs=q["hd_ev"]["hd"]
        active=[r for r in rows if obs.get(r["mapping_id"]) is not None]
        result["known_rule_counts"].append({"admitted":len(rows),"observed":len(active),"clusters":sorted({r["dependency_cluster"] for r in active}),
                                         "observed_ids":[r["mapping_id"] for r in active]})
    # Group identical predicates (even if several question wordings refer to
    # them); rank opportunity by pairwise disagreement in entire tied cohort,
    # not by whether the reference would gain a point.
    groups=defaultdict(list)
    for r in rows:
        if all(q["hd_ev"]["hd"].get(r["mapping_id"]) is None for q in profiles):
            groups[json.dumps(r["chart_feature_predicate"],sort_keys=True)].append(r)
    for key,rs in groups.items():
        pred=rs[0]["chart_feature_predicate"]
        active={i:m.b.hd_active(ch,pred) for i,ch in lookup.items()}
        refval=m.b.hd_active(ref,pred)
        def count(ii):
            true=false=unknown=diff=0
            for k,n in zip(*np.unique(ii,return_counts=True),strict=True):
                v=active[int(k)];n=int(n)
                if v is True:true+=n
                elif v is False:false+=n
                else:unknown+=n
                if v is not None and refval is not None and v!=refval:diff+=n
            return {"true":true,"false":false,"unknown":unknown,"differs_from_reference":diff}
        allc=count(ids);rc=count(rid);n=allc["true"]+allc["false"]
        p=allc["true"]/n if n else 0.
        result["unobserved_predicate_groups"].append({"predicate":pred,"reference_carrier":refval,
           "mapping_ids":[r["mapping_id"] for r in rs],"question_ids":sorted(set(q for r in rs for q in r["question_ids"])),
           "behavior_statements":[r["behavioral_statement"] for r in rs],
           "dependency_clusters":sorted(set(r["dependency_cluster"] for r in rs)),
           "cohort":allc,"rivals":rc,"pair_disagreement":2*p*(1-p)})
    result["unobserved_predicate_groups"].sort(key=lambda r:(-r["pair_disagreement"],r["mapping_ids"]))
    return result

def run(a):
    paths=[a.west,a.angles,a.hd_cache,a.join,a.ephemeris,a.calendar,a.inventory,a.mapping_library,a.overlap,a.cross_coding,a.output,*a.evidence,*a.hd_evidence,*[getattr(a,k) for k in m.RECEIPTS]]
    if any(p.resolve().is_relative_to(m.b.ROOT) for p in paths) or a.output.exists():raise ValueError("Private immutable files outside checkout required")
    W,WM,A,AM,H,proof=m.g.verify_inputs(a)
    ov=json.loads(a.overlap.read_text());cross=json.loads(a.cross_coding.read_text())
    if ov["runner_sha256"]!=m.b.digest(m.__file__) or cross["runner_sha256"]!=m.b.digest(cc.__file__) or cross["full_overlap_sha256"]!=m.b.digest(a.overlap):raise ValueError("Previous overlap binding drift")
    for k in m.RECEIPTS:
        if ov["prior_receipt_sha256"][k]!=m.b.digest(getattr(a,k)):raise ValueError("Frozen prior receipt drift")
    for name,sha in W["ephe_sha256"].items():
        if m.b.digest(a.ephemeris/name)!=sha:raise ValueError("Ephemeris drift")
    m.swe.set_ephe_path(str(a.ephemeris));m.cal.witnesses()
    with np.load(a.calendar,allow_pickle=False) as f:cache={k:f[k] for k in f.files}
    receipts={k:json.loads(getattr(a,k).read_text()) for k in m.RECEIPTS}
    if receipts["chinese"]["calendar_sha256"]!=m.b.digest(a.calendar):raise ValueError("Calendar drift")
    profiles,lookup,registry,edges=m.prepare(a,W,A,cache,receipts)
    if any(q["h0"]!=1. for q in profiles):raise ValueError("Frozen ceiling needed for complete reduction")
    scales=[rational_scale(q["prior"]["condition"]["observed_domains"]) for q in profiles]
    data,eligible=collect(a,W,WM,A,AM,H,profiles,lookup,cache)
    n=len(data["index"])
    if eligible!=cross["HD_eligible_both_codings"] or n!=cross["counts"]["coverage"]["common"]:raise ValueError("Previous HD cohort mismatch")
    controls=np.sort(np.random.default_rng(SEED).choice(n,size=CONTROL_N,replace=False))
    cm=evaluate(select(data,controls),profiles,registry,edges,cache,scales)
    cc0=join_matrix(cm,CORE);ce=join_matrix(cm,EXTRA)
    results=[Counter() for i in controls];rivals=[];weak_core=[];weak_full=[];strict_full=[];stats=defaultdict(Counter)
    for off in range(0,n,4000):
        batch=select(data,slice(off,min(n,off+4000)));idx=batch["index"]
        mats=evaluate(batch,profiles,registry,edges,cache,scales)
        r=rival_mask(mats);wc=universal(mats,CORE);wf=wc&universal(mats,EXTRA)
        core=join_matrix(mats,CORE);extra=join_matrix(mats,EXTRA)
        rivals.extend(idx[r].tolist());weak_core.extend(idx[wc].tolist());weak_full.extend(idx[wf].tolist())
        strict_full.extend(idx[wf&(np.any(core>0,axis=1)|np.any(extra>0,axis=1))].tolist())
        for group,(u,v) in mats.items():
            strict=(u>0)&(v>0);ge=(u>=0)&(v>=0)
            stats[group].update(rows=len(idx),strict_any=int(np.any(strict,axis=1).sum()),
                    strict_all=int(np.all(strict,axis=1).sum()),ge_all=int(np.all(ge,axis=1).sum()),
                    rival_shared_strict_arms=int(strict[r].sum()),rival_shared_nonstrict_arms=int(ge[r].sum()),
                    rival_rows=len(idx[r]),near_core_lower_arms=int((~ge[wc]).sum()))
        update_controls(core,extra,cc0,ce,idx,data["index"][controls],results)
        if (off//4000)%10==0:print("Survivor diagnostic:",min(n,off+len(idx)),"/",n,flush=True)
    expected=cross["strict_survivor_indices"][KEY+"|strict_any"]
    wkey=KEY+"|HD_tie_all_others_ge_all"
    old=sorted(set(ov["profiles"][0]["survivor_grid_indices"][wkey])&set(ov["profiles"][1]["survivor_grid_indices"][wkey]))
    if rivals!=expected or weak_core!=old or len(weak_core)!=cross["counts"][KEY]["weak_all"]:raise ValueError("Core survivors did not replay")
    if not set(weak_full)<=set(weak_core):raise ValueError("Extended comparison subset drift")
    if any(r["core_weak"]<1 or r["all_weak"]<1 or r["all_weak"]>r["core_weak"] for r in results):raise ValueError("Clock control failed self-comparison")
    audit=hd_audit(a,profiles,data,rivals)
    out={"status":"EXECUTED_FROZEN_SURVIVOR_DIAGNOSTICS_NOT_VALIDATION","grid_rows":m.g.N,
         "HD_eligible":eligible,"common":n,"scales":scales,
         "weak_core_indices":weak_core,"weak_all_included_indices":weak_full,"pareto_all_included_indices":strict_full,
         "strict_rivals":len(rivals),"rival_group_diagnostics":dict(stats),
         "HD_audit":audit,"clock_controls":{"seed":SEED,"controls":[{"grid_index":int(data["index"][k]),**r} for k,r in zip(controls,results,strict=True)],"scope":"HD_MAXIMAL_COMMON_ROWS_FIXED_EVIDENCE_NOT_HUMAN_NULL"},
         "prior_overlap_sha256":m.b.digest(a.overlap),"prior_cross_coding_sha256":m.b.digest(a.cross_coding),"runner_sha256":m.b.digest(__file__)}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("Survivor diagnostics complete; frozen core survivors reproduced.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","ephemeris","calendar","inventory","mapping-library","output","overlap","cross-coding",*m.RECEIPTS):
        p.add_argument("--"+k,type=Path,required=True)
    for k in ("evidence","hd-evidence"):p.add_argument("--"+k,type=Path,action="append",required=True)
    run(p.parse_args())
if __name__=="__main__":main()
