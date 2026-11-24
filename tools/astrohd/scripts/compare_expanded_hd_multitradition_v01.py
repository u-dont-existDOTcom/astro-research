#!/usr/bin/env python3
"""Same-row separate-system dominance with new complete-catalogue HD scores.

Recompute the frozen non-HD primary arms for every original timestamp.
Keep compact, private full-grid joint-coding flags for later HD changes.
No rank-selected variant or full averaged-score ranking claim.
"""
from __future__ import annotations
import argparse,json,os
from collections import Counter,defaultdict
from datetime import timedelta
from pathlib import Path
import numpy as np
import compare_multitradition_intersections_v01 as m
import compare_multitradition_cross_coding_v01 as cc
import compare_hd_archetype_century_v01 as hd

GROUPS=m.PRIMARY
METRICS=("strict_any","strict_all","ge_any","ge_all")
COMBOS={"ptolemy":("ptolemy_blend",),"lilly":("lilly",),"both_west":("ptolemy_blend","lilly"),
 "ptolemy_eastern":("ptolemy_blend","vedic_union","chinese_union"),
 "lilly_eastern":("lilly","vedic_union","chinese_union"),"all_primary":GROUPS}

class Flags:
    def __init__(self,n):
        self.strict_any=np.zeros(n,bool);self.strict_all=np.ones(n,bool)
        self.ge_any=np.zeros(n,bool);self.ge_all=np.ones(n,bool);self.tags=set();self.known=np.ones(n,bool)
    def add(self,tag,x,y,known):
        if tag in self.tags or x.shape!=self.known.shape or y.shape!=x.shape or known.shape!=x.shape:raise ValueError("Arm alignment drift")
        self.tags.add(tag);self.known&=known
        gt=(x>m.EPS)&(y>m.EPS)&known;ge=(x>=-m.EPS)&(y>=-m.EPS)&known
        self.strict_any|=gt;self.strict_all&=gt;self.ge_any|=ge;self.ge_all&=ge

def western(lon,alt,cusp,profiles,flags):
    cond=m.c.all_conditions(lon,alt);r=np.arange(len(lon));ok=np.ones(len(lon),bool)
    signs=[m.g.vote_arrays(lon,q["hd_ev"]["western"]) for q in profiles]
    for tag,gm,pm,gl,pl in m.p.branches(lon,alt):
        im=np.maximum(gm,0);il=np.maximum(gl,0)
        sg=[m.b.family(np.where(gm>=0,ms[r,im],0),np.where(gl>=0,ls[r,il],0),ph,np.zeros(len(lon)))[0] for ms,ls,ph in signs]
        for pol in m.c.POLICIES:
            cc0=cond[pol];key=tag+"|"+pol
            mc=np.where(gm>=0,cc0[r,im],m.c.UNKNOWN);lc=np.where(gl>=0,cc0[r,il],m.c.UNKNOWN)
            z=[]
            for q,sign in zip(profiles,sg,strict=True):
                t=q["cond_table"]
                ch=(np.where(gm>=0,t[mc,0,im],0.)+np.where(gl>=0,t[lc,1,il],0.))/2
                z.append((ch+sign)/2-q["prior"]["condition"]["reference"][key]["scores"]["blend"])
            flags["ptolemy_blend"].add(key,*z,ok)
    for tag,st,sg,primary,sc,sp,outer in m.l.branches(lon,alt,cusp[:,0],cusp[:,1]):
        mask=m.lc.encode(primary)
        for arm in m.l.ARMS:
            z=[q["lilly_lut"][arm][mask]-q["prior"]["lilly"]["reference"][tag]["scores"][arm]["western"] for q in profiles]
            flags["lilly"].add(tag+"|"+arm,*z,ok)

def eastern(lon,jds,bs,ls,profiles,registry,edges,cache,flags,err):
    reg,prior,shared=registry
    for geom,mode in m.v.MODES:
        signs,graph,near,e=m.v.signs_and_graph(lon,jds,mode);err[geom]=max(err.get(geom,0.),e)
        arms=[m.v.compute(signs,graph,reg,edges,q["vedic_tables"][0]) for q in profiles]
        for tag in arms[0]:
            if not tag.endswith("|all_union"):continue
            k=geom+"|"+tag
            z=[m.v.score(a[tag],q["vedic_tables"][1])["score"]-q["prior"]["vedic"]["reference"][k]["score"] for q,a in zip(profiles,arms,strict=True)]
            flags["vedic_union"].add(k,*z,~near)
    for clock,wall in zip(m.cal.CLOCKS,(bs,ls),strict=True):
        f=m.cal.features(bs,wall,cache)
        arms=[{k:(bits,good) for k,bits,good in m.z.models(f,q["chinese_tables"]) if k.startswith("union|")} for q in profiles]
        for tag in arms[0]:
            k=clock+"|"+tag
            z=[m.v.score(a[tag][0],q["chinese_tables"][2])["score"]-q["prior"]["chinese"]["reference"][k]["score"] for q,a in zip(profiles,arms,strict=True)]
            flags["chinese_union"].add(k,*z,arms[0][tag][1]&arms[1][tag][1])

def flag_bits(flags):
    n=len(next(iter(flags.values())).known);packed=np.zeros(n,np.uint16);known=np.ones(n,bool)
    for i,k in enumerate(GROUPS):
        f=flags[k]
        if len(f.tags)!=m.GROUPS[k]:raise ValueError("Incomplete frozen arm coverage")
        known&=f.known
        for j,v in enumerate(METRICS):packed|=getattr(f,v).astype(np.uint16)<<np.uint16(4*i+j)
    return packed,known

def get(packed,name,metric):
    return (packed&(1<<(4*GROUPS.index(name)+METRICS.index(metric))))!=0

def combo(packed,groups,metric):
    return np.logical_and.reduce([get(packed,g,metric) for g in groups])

def aggregate(packed,common,x,y):
    """HD scores are deltas for the same new arm under each evidence coding."""
    ge=common&(x>=-m.EPS)&(y>=-m.EPS)
    gt=common&(x>m.EPS)&(y>m.EPS)
    tie=common&(np.abs(x)<=m.EPS)&(np.abs(y)<=m.EPS)
    out={"HD_no_lower":int(ge.sum()),"HD_strict_both":int(gt.sum()),"HD_equal_both":int(tie.sum())}
    for key,groups in COMBOS.items():
        any_hi=combo(packed,groups,"strict_any");all_hi=combo(packed,groups,"strict_all")
        any_ge=combo(packed,groups,"ge_any");all_ge=combo(packed,groups,"ge_all")
        out[key]={"HD_strict_and_others_strict_any":int((gt&any_hi).sum()),
                  "HD_strict_and_others_strict_all":int((gt&all_hi).sum()),
                  "HD_no_lower_others_strict_any":int((ge&any_hi).sum()),
                  "HD_equal_others_strict_any":int((tie&any_hi).sum()),
                  "HD_no_lower_others_ge_any":int((ge&any_ge).sum()),
                  "HD_no_lower_others_ge_all":int((ge&all_ge).sum())}
    return out

def add_counts(a,b):
    for k,v in b.items():
        if isinstance(v,dict):add_counts(a.setdefault(k,{}),v)
        else:a[k]=a.get(k,0)+v

def run(a):
    paths=[a.west,a.angles,a.hd_cache,a.join,a.ephemeris,a.calendar,a.inventory,a.mapping_library,a.output,a.flag_output,a.hd_result,a.state_input,a.overlap,a.cross_coding,a.context,*a.evidence,*a.hd_evidence,*[getattr(a,k) for k in m.RECEIPTS]]
    if any(x.resolve().is_relative_to(m.b.ROOT) for x in paths) or a.output.exists() or a.flag_output.exists():raise ValueError("Private immutable paths required")
    W,WM,A,AM,H,proof=m.g.verify_inputs(a)
    hr=json.loads(a.hd_result.read_text());ov=json.loads(a.overlap.read_text());cross=json.loads(a.cross_coding.read_text());context=json.loads(a.context.read_text())
    if hr["runner_sha256"]!=m.b.digest(hd.__file__) or hr["map_sha256"]!=hd.MAP_SHA or hr["state_output_sha256"]!=m.b.digest(a.state_input):
        raise ValueError("Expanded HD receipt drift")
    for k,pa in (("prior_overlap_sha256",a.overlap),("prior_cross_coding_sha256",a.cross_coding),("prior_context_sha256",a.context)):
        if hr[k]!=m.b.digest(pa):raise ValueError("Earlier reference result changed")
    if ov["runner_sha256"]!=m.b.digest(m.__file__) or cross["runner_sha256"]!=m.b.digest(cc.__file__) or cross["full_overlap_sha256"]!=m.b.digest(a.overlap):raise ValueError("Earlier intersection drift")
    if hr["evidence_sha256"]!=[m.b.digest(p) for p in a.evidence] or hr["HD_evidence_sha256"]!=[m.b.digest(p) for p in a.hd_evidence]:raise ValueError("Frozen evidence drift")
    for k in m.RECEIPTS:
        if ov["prior_receipt_sha256"][k]!=m.b.digest(getattr(a,k)):raise ValueError("Prior score receipt changed")
    if m.swe.version!=W["swisseph_version"]:raise ValueError("Ephemeris version changed")
    for name,sha in W["ephe_sha256"].items():
        if m.b.digest(a.ephemeris/name)!=sha:raise ValueError("Ephemeris SHA drift")
    m.swe.set_ephe_path(str(a.ephemeris));m.cal.witnesses()
    with np.load(a.calendar,allow_pickle=False) as f:cache={k:f[k] for k in f.files}
    receipts={k:json.loads(getattr(a,k).read_text()) for k in m.RECEIPTS}
    if receipts["chinese"]["calendar_sha256"]!=m.b.digest(a.calendar):raise ValueError("Calendar changed")
    profiles,lookup,registry,edges=m.prepare(a,W,A,cache,receipts)
    with np.load(a.state_input,allow_pickle=False) as f:
        delta=f["delta"];base=f["base_delta"]
        if tuple(f["arms"].tolist())!=hd.SCORES or str(f["map_sha256"])!=hd.MAP_SHA or str(f["runner_sha256"])!=hr["runner_sha256"]:raise ValueError("HD state arm drift")
    if delta.shape!=(3,len(hd.SCORES),m.g.HD_N) or base.shape!=(3,m.g.HD_N) or not np.all(np.isfinite(delta)) or not np.all(np.isfinite(base)):raise ValueError("HD state matrix shape/value drift")
    for i,h in enumerate(lookup):
        if not np.allclose(base[i],h-profiles[i]["h0"],rtol=0,atol=m.EPS/4):raise ValueError("HD baseline delta replay drift")
    start=m.g.timestamp(W["utc_start_inclusive"]);jd0=m.swe.julday(start.year,start.month,start.day,start.hour+start.minute/60)
    lat,long=float(A["latitude"]),float(A["longitude"])
    all_flags=np.zeros(m.g.N,np.uint16);all_known=np.zeros(m.g.N,bool)
    counts={label:{k:{} for k in ("baseline",*hd.SCORES)} for label in ("original_pair","context_pair")}
    old_indices={k:[] for k in ("ptolemy_eastern","lilly_eastern","either_eastern","all_primary","universal")}
    ctx_indices={k:[] for k in old_indices};processed=0;err={};known_HD=0
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not(wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):raise ValueError("Shard alignment drift")
        pp=(a.west/"chunks"/wi["file"],a.angles/"shards"/ai["file"],a.join/"shards"/hi["file"])
        for path,meta,size in zip(pp,(wi,ai,hi),(64,136,4),strict=True):
            if path.stat().st_size!=n*size or m.b.digest(path)!=meta["sha256"]:raise ValueError("Source shard drift")
        P=np.memmap(pp[0],dtype="<f8",mode="r",shape=(n,8));AA=np.memmap(pp[1],dtype="<f8",mode="r",shape=(n,17));ids=np.memmap(pp[2],dtype="<i4",mode="r",shape=(n,))
        if np.any(ids<-1) or np.any(ids>=m.g.HD_N):raise ValueError("HD index drift")
        known_HD+=int((ids>=0).sum())
        for off in range(0,n,25000):
            stop=min(n,off+25000);I=processed+off;nn=stop-off
            lon=np.asarray(P[off:stop,:7]);alt=np.asarray(AA[off:stop,4]);ii=np.asarray(ids[off:stop]);idx=np.maximum(ii,0)
            jds=jd0+(I+np.arange(nn,dtype=float))/96.
            cusp=np.array([m.swe.houses_ex(jd,lat,long,b"R")[0][:2] for jd in jds])
            if np.max(np.abs((cusp[:,0]-AA[off:stop,0]+180)%360-180))>0.0002:raise ValueError("ASC drift")
            bs,ls=m.cal.wall_arrays(start+timedelta(seconds=900*I),nn)
            flags={k:Flags(nn) for k in GROUPS}
            western(lon,alt,cusp,profiles,flags)
            eastern(lon,jds,bs,ls,profiles,registry,edges,cache,flags,err)
            packed,good=flag_bits(flags);common=(ii>=0)&good
            all_flags[I:I+nn]=packed;all_known[I:I+nn]=common
            for i,label,store in ((0,"original_pair",old_indices),(2,"context_pair",ctx_indices)):
                xx=base[i,idx];yy=base[1,idx];old=common&(xx>=-m.EPS)&(yy>=-m.EPS)
                add_counts(counts[label]["baseline"],aggregate(packed,common,xx,yy))
                p=combo(packed,COMBOS["ptolemy_eastern"],"strict_any")
                l=combo(packed,COMBOS["lilly_eastern"],"strict_any")
                for k,mask in (("ptolemy_eastern",p),("lilly_eastern",l),("either_eastern",p|l),("all_primary",p&l),("universal",combo(packed,GROUPS,"ge_all"))):
                    store[k].extend((I+np.flatnonzero(old&mask)).tolist())
                for k,tag in enumerate(hd.SCORES):
                    add_counts(counts[label][tag],aggregate(packed,common,delta[i,k,idx],delta[1,k,idx]))
        processed+=n
        if processed%500000==0 or processed==m.g.N:print("Expanded-HD cross-system grid:",processed,"/",m.g.N,flush=True)
    if processed!=m.g.N or known_HD!=m.g.N-125 or int(all_known.sum())!=ov["profiles"][0]["counts"]["coverage"]["common"]:raise ValueError("Common grid denominator drift")
    combos={"ptolemy_eastern":"ptolemy_blend + vedic_union + chinese_union|strict_any","lilly_eastern":"lilly + vedic_union + chinese_union|strict_any",
            "either_eastern":"western_alternatives + vedic_union + chinese_union|strict_any","all_primary":"ptolemy_blend + lilly + vedic_union + chinese_union|strict_any"}
    for k,tag in combos.items():
        if old_indices[k]!=cross["strict_survivor_indices"][tag] or ctx_indices[k]!=context["new_survivor_indices"][tag]:raise ValueError("Exact prior survivor identity replay drift")
    wk="ptolemy_blend + lilly + vedic_union + chinese_union|HD_tie_all_others_ge_all"
    if old_indices["universal"]!=sorted(set(ov["profiles"][0]["survivor_grid_indices"][wk])&set(ov["profiles"][1]["survivor_grid_indices"][wk])) or ctx_indices["universal"]!=context["new_survivor_indices"]["universal_all_included"]:
        raise ValueError("Prior universal weak identity drift")
    os.umask(0o077)
    with a.flag_output.open("xb") as f:
        np.savez_compressed(f,flags=all_flags,known=all_known,groups=np.asarray(GROUPS),metrics=np.asarray(METRICS),runner_sha256=m.b.digest(__file__),overlap_sha256=m.b.digest(a.overlap))
    result={"status":"EXECUTED_EXPANDED_HD_FROZEN_NON_HD_FULL_GRID_DOMINANCE_NOT_VALIDATION","grid_rows":processed,
        "common_rows":int(all_known.sum()),"counts":counts,"arms":len(hd.SCORES),"runner_sha256":m.b.digest(__file__),
        "hd_result_sha256":m.b.digest(a.hd_result),"state_input_sha256":m.b.digest(a.state_input),"flag_output_sha256":m.b.digest(a.flag_output),
        "prior_overlap_sha256":m.b.digest(a.overlap),"prior_cross_coding_sha256":m.b.digest(a.cross_coding),"prior_context_sha256":m.b.digest(a.context),"sidereal_sample_max_error_degrees":err}
    with a.output.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("Expanded HD and frozen primary non-HD full-grid dominance complete; old survivor identities replayed.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","ephemeris","calendar","inventory","mapping-library","output","flag-output","hd-result","state-input","overlap","cross-coding","context",*m.RECEIPTS):
        p.add_argument("--"+k,type=Path,required=True)
    for k in ("evidence","hd-evidence"):p.add_argument("--"+k,type=Path,action="append",required=True)
    run(p.parse_args())
if __name__=="__main__":main()
