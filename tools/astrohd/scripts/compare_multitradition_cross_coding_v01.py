#!/usr/bin/env python3
"""Same-variant, both-coding check on the complete HD-no-lower intersection.

Logical filtering on HD dominance is exact for the stated Pareto question.
No average-score ranking over the full grid is claimed by this extra pass.
"""
from __future__ import annotations
import argparse,json,os
from collections import Counter,defaultdict
from pathlib import Path
from datetime import timedelta
import numpy as np
import compare_multitradition_intersections_v01 as m

class Store(m.Extrema):
    def __init__(self,n):
        super().__init__(n);self.arms={}
    def add(self,tag,delta,known):
        super().add(tag,delta,known)
        # Losslessly classify each score relative to the frozen EPS.
        self.arms[tag]=(np.where(delta>m.EPS,1,np.where(delta<-m.EPS,-1,0)).astype(np.int8),known.copy())

def both(a,b):
    """Min of the two per-arm sign classifications BEFORE family extrema."""
    if set(a.arms)!=set(b.arms):raise ValueError("Variant alignment drift")
    x=m.Extrema(len(a.lo));ties=np.zeros(len(a.lo),bool)
    for k,(v,known) in a.arms.items():
        w,ok=b.arms[k]
        # For strict/weak both-coding dominance, min is the exact
        # classification. For exact ties, both values must be zero.
        x.add(k,np.minimum(v,w).astype(float),known&ok)
        ties|=known&ok&(v==0)&(w==0)
    x.any_tie=ties
    return x

def compare(ext,known,ids,counts,indices):
    boths={k:both(a,b) for k,a,b in ((k,ext[0][k],ext[1][k]) for k in m.PRIMARY)}
    west=m.group_options(boths)
    groups={**boths,"western_alternatives":west}
    common=known.copy()
    for a in groups.values():common&=a.known
    counts["coverage"].update(common=int(common.sum()),unknown=int((~common).sum()),rows=len(common))
    for k,a in groups.items():
        counts[k].update(rows=int(common.sum()),strict_any=int((common&(a.hi>m.EPS)).sum()),
            strict_all=int((common&(a.lo>m.EPS)).sum()),ge_any=int((common&(a.hi>=-m.EPS)).sum()),
            ge_all=int((common&(a.lo>=-m.EPS)).sum()))
    combos=[("ptolemy_blend","vedic_union","chinese_union"),("lilly","vedic_union","chinese_union"),
            ("western_alternatives","vedic_union","chinese_union"),
            ("ptolemy_blend","lilly","vedic_union","chinese_union")]
    for names in combos:
        x=[groups[k] for k in names];key=" + ".join(names)
        for label,arr in (("any",[a.hi for a in x]),("all",[a.lo for a in x])):
            strict=common&np.logical_and.reduce([a>m.EPS for a in arr])
            weak=common&np.logical_and.reduce([a>=-m.EPS for a in arr])
            # At least one strict in BOTH codings is a deliberately stronger
            # criterion than separate Pareto improvements in distinct families.
            robust=weak&np.logical_or.reduce([a>m.EPS for a in arr])
            counts[key].update({"strict_"+label:int(strict.sum()),"weak_"+label:int(weak.sum()),
                                "weak_with_shared_strict_"+label:int(robust.sum())})
            indices[key+"|strict_"+label].extend(ids[strict].tolist())

def run(a):
    files=[a.west,a.angles,a.hd_cache,a.join,a.ephemeris,a.calendar,a.inventory,a.mapping_library,a.output,a.overlap,*a.evidence,*a.hd_evidence,*[getattr(a,k) for k in m.RECEIPTS]]
    if any(x.resolve().is_relative_to(m.b.ROOT) for x in files) or a.output.exists():raise ValueError("External immutable inputs required")
    W,WM,A,AM,H,proof=m.g.verify_inputs(a)
    overlap=json.loads(a.overlap.read_text())
    if overlap["grid_rows"]!=m.g.N or overlap["runner_sha256"]!=m.b.digest(m.__file__):raise ValueError("Full-grid overlap receipt drift")
    for k in m.RECEIPTS:
        if overlap["prior_receipt_sha256"][k]!=m.b.digest(getattr(a,k)):raise ValueError("Prior receipt changed")
    for name,sha in W["ephe_sha256"].items():
        if m.b.digest(a.ephemeris/name)!=sha:raise ValueError("Ephemeris drift")
    m.swe.set_ephe_path(str(a.ephemeris));m.cal.witnesses()
    with np.load(a.calendar,allow_pickle=False) as f:cache={k:f[k] for k in f.files}
    if str(cache["runner_sha256"])!=m.b.digest(m.cal.__file__) or str(cache["grid_plan_sha256"])!=m.b.digest(a.west/"plan.json"):raise ValueError("Calendar cache drift")
    receipts={k:json.loads(getattr(a,k).read_text()) for k in m.RECEIPTS}
    if receipts["chinese"]["calendar_sha256"]!=m.b.digest(a.calendar):raise ValueError("Chinese cache changed")
    profiles,lookup,registry,edges=m.prepare(a,W,A,cache,receipts)
    for q in profiles:
        if q["h0"]!=1.:raise ValueError("This specific reduction requires the frozen maximum HD target")
    start=m.g.timestamp(W["utc_start_inclusive"]);jd0=m.swe.julday(start.year,start.month,start.day,start.hour+start.minute/60)
    lat=float(A["latitude"]);long=float(A["longitude"])
    counts=defaultdict(Counter);indices=defaultdict(list);processed=0;hd_eligible=0;err={}
    reg,prior,shared=registry
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not(wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):raise ValueError("Grid alignment drift")
        pp=(a.west/"chunks"/wi["file"],a.angles/"shards"/ai["file"],a.join/"shards"/hi["file"])
        for path,meta,size in zip(pp,(wi,ai,hi),(64,136,4),strict=True):
            if path.stat().st_size!=n*size or m.b.digest(path)!=meta["sha256"]:raise ValueError("Grid shard drift")
        P=np.memmap(pp[0],dtype="<f8",mode="r",shape=(n,8));AA=np.memmap(pp[1],dtype="<f8",mode="r",shape=(n,17));ids=np.memmap(pp[2],dtype="<i4",mode="r",shape=(n,))
        if np.any(ids<-1) or np.any(ids>=m.g.HD_N):raise ValueError("Invalid HD index")
        h=[x[np.maximum(ids,0)] for x in lookup]
        # Check the complete grid for the exact necessary condition.
        eligible=(ids>=0)&(h[0]>=profiles[0]["h0"]-m.EPS)&(h[1]>=profiles[1]["h0"]-m.EPS)
        ix=np.flatnonzero(eligible)
        hd_eligible+=len(ix)
        if len(ix):
            bs,ls=m.cal.wall_arrays(start+timedelta(seconds=900*processed),n)
            for off in range(0,len(ix),4000):
                j=ix[off:off+4000];nn=len(j);global_index=processed+j
                lon=np.asarray(P[j,:7]);alt=np.asarray(AA[j,4]);hh=[x[j] for x in h];ok=np.ones(nn,bool)
                jds=jd0+global_index/96.
                cusp=np.array([m.swe.houses_ex(jd,lat,long,b"R")[0][:2] for jd in jds])
                if np.max(np.abs((cusp[:,0]-AA[j,0]+180)%360-180))>0.0002:raise ValueError("ASC drift")
                # Store only primary arms; secondary Western sensitivities
                # are recomputed unchanged but need not retain row matrices.
                ext=[{k:(Store(nn) if k in m.PRIMARY else m.Extrema(nn)) for k in m.GROUPS} for q in profiles]
                marg=[defaultdict(lambda:defaultdict(Counter)) for q in profiles]
                m.western(lon,alt,cusp,hh,ok,profiles,ext,marg)
                for geom,mode in m.v.MODES:
                    signs,graph,near,e=m.v.signs_and_graph(lon,jds,mode);err[geom]=max(err.get(geom,0.),e)
                    for q,ee in zip(profiles,ext,strict=True):
                        tab,obs=q["vedic_tables"]
                        for tag,bits in m.v.compute(signs,graph,reg,edges,tab).items():
                            if not tag.endswith("|all_union"):continue
                            key=geom+"|"+tag;r=q["prior"]["vedic"]["reference"][key]
                            ee["vedic_union"].add(key,m.v.score(bits,obs)["score"]-r["score"],~near)
                for clock,wall in zip(m.cal.CLOCKS,(bs[j],ls[j]),strict=True):
                    f=m.cal.features(bs[j],wall,cache)
                    for q,ee in zip(profiles,ext,strict=True):
                        t=q["chinese_tables"]
                        for tag,bits,good in m.z.models(f,t):
                            if not tag.startswith("union|"):continue
                            key=clock+"|"+tag;r=q["prior"]["chinese"]["reference"][key]
                            ee["chinese_union"].add(key,m.v.score(bits,t[2])["score"]-r["score"],good)
                for ee in ext:
                    if any(len(ee[k].tags)!=m.GROUPS[k] for k in m.GROUPS):raise ValueError("Incomplete same-variant pass")
                compare(ext,ok,global_index,counts,indices)
        processed+=n
    if processed!=m.g.N or counts["coverage"]["rows"]!=hd_eligible:raise ValueError("Incomplete HD dominance cohort")
    # Every same-variant strict survivor must belong to both previously
    # computed independent-coding existential sets.
    for k,idx in indices.items():
        name,kind=k.rsplit("|",1)
        oldkey=name+"|HD_tie_all_others_"+kind
        old=[set(p["survivor_grid_indices"][oldkey]) for p in overlap["profiles"]]
        if not set(idx)<=old[0]&old[1] or len(idx)!=counts[name][kind]:raise ValueError("Cross-coding subset reconciliation failed")
        if kind=="strict_all" and set(idx)!=old[0]&old[1]:raise ValueError("Universal cross-coding intersection drift")
    result={"status":"EXECUTED_COMPLETE_HD_DOMINANCE_COHORT_SAME_VARIANT_BOTH_CODINGS_NOT_VALIDATION","grid_rows":processed,
       "HD_eligible_both_codings":hd_eligible,"counts":dict(counts),"strict_survivor_indices":dict(indices),
       "full_overlap_sha256":m.b.digest(a.overlap),"runner_sha256":m.b.digest(__file__),"sidereal_sample_max_error_degrees":err}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("Same-variant both-coding dominance receipt completed.",flush=True)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","ephemeris","calendar","inventory","mapping-library","output","overlap",*m.RECEIPTS):ap.add_argument("--"+k,type=Path,required=True)
    for k in ("evidence","hd-evidence"):ap.add_argument("--"+k,type=Path,action="append",required=True)
    run(ap.parse_args())
if __name__=="__main__":main()
