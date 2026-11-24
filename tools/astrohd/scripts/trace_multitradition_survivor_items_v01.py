#!/usr/bin/env python3
"""Decompose frozen primary scores for all shared-variant strict rivals.
Post-selection descriptive audit only: no new scores, fitted weights or
inference about actual people born at hypothetical timestamps.
"""
from __future__ import annotations
import argparse,json,os
from collections import defaultdict
from pathlib import Path
from itertools import product
import numpy as np
import diagnose_multitradition_survivors_v01 as d
import compare_multitradition_intersections_v01 as m
import compare_multitradition_cross_coding_v01 as cc

SIGN_SLOTS=("mercury_mode_testimony","moon_mode_testimony","moon_phase_testimony")

def item_weights(shared,obs,keys):
    weight=np.zeros(len(keys))
    for dom in m.p.DOMAINS:
        mask=np.array([k in shared["domains"][dom] for k in keys])
        n=sum(obs.get(k) is not None for k in shared["domains"][dom])
        if n:weight[mask]=.5/n
    return weight*np.array([obs.get(k) or 0 for k in keys])

def bits_items(bits,weights):
    p,n=bits
    masks=np.left_shift(np.uint64(1),np.arange(len(weights),dtype=np.uint64))
    return (((p[:,None]&masks)!=0).astype(np.int8)-((n[:,None]&masks)!=0).astype(np.int8))*weights

def verify_sum(items,score):
    if not np.allclose(items.sum(axis=1),score,rtol=0,atol=m.EPS/4):
        raise ValueError("Item contributions do not reproduce frozen score")

class Trace:
    def __init__(self,n,keys):
        self.keys=keys;self.wins=np.zeros(n,np.int16)
        self.gain=[np.zeros((n,len(keys)),bool) for _ in range(2)]
        self.loss=[a.copy() for a in self.gain]
        self.delta=[np.zeros((n,len(keys))) for _ in range(2)]
        self.positive=[np.zeros(len(keys),np.int64) for _ in range(2)]
        self.negative=[a.copy() for a in self.positive]
        self.tags=set()
    def add(self,tag,items,score,targets):
        if tag in self.tags:raise ValueError("Duplicate source variant")
        self.tags.add(tag);ds=[]
        for a,b0,t in zip(items,score,targets,strict=True):
            verify_sum(a,b0);m.close(b0[0],t)
            ds.append(a[1:]-a[:1])
        win=np.logical_and.reduce([np.sum(a,axis=1)>m.EPS for a in ds])
        self.wins+=win
        for i,a in enumerate(ds):
            p=(a>m.EPS)&win[:,None];n=(a<-m.EPS)&win[:,None]
            self.gain[i]|=p;self.loss[i]|=n
            self.delta[i]+=a*win[:,None]
            self.positive[i]+=p.sum(axis=0);self.negative[i]+=n.sum(axis=0)
    def finish(self):
        if np.any(self.wins<=0):raise ValueError("A previously certified rival failed shared strict variant replay")
        out=[]
        for i in range(2):
            mean=np.mean(self.delta[i]/self.wins[:,None],axis=0)
            out.append({k:{"rival_rows_gain_any":int(self.gain[i][:,j].sum()),"rival_rows_loss_any":int(self.loss[i][:,j].sum()),
                           "winning_arm_item_gains":int(self.positive[i][j]),"winning_arm_item_losses":int(self.negative[i][j]),
                           "mean_score_delta_per_rival":float(mean[j])} for j,k in enumerate(self.keys)})
        return {"variants":len(self.tags),"rivals":len(self.wins),
                "shared_winning_arm_count_histogram":{str(int(k)):int(v) for k,v in zip(*np.unique(self.wins,return_counts=True),strict=True)},
                "profiles":out}

def ptolemy_item_tables(reg,obs,keys):
    w=item_weights(reg,obs,keys)/2
    a=np.zeros((3,2,7,len(keys)))
    for r in reg["profiles"]:
        if r["bodies"][0]!=r["bodies"][1]:continue
        body=m.p.BODIES.index(r["bodies"][0])
        for ci,condition in enumerate(m.p.CONDITIONS):
            for di,dom in enumerate(m.p.DOMAINS):
                a[ci,di,body]=w*np.array([r[condition].get(k,0) if k in reg["domains"][dom] else 0 for k in keys])
    return a

def lilly_item_tables(reg,shared,obs,keys):
    w=item_weights(shared,obs,keys)
    a=np.zeros((2,7,len(keys)))
    for r in reg["profiles"]:
        body=m.l.BODIES.index(r["body"])
        for ci,condition in enumerate(m.l.CLAUSES):
            a[ci,body]=w*np.array([r[condition].get(k,0) for k in keys])
    return a

def trace_western(data,profiles,observations,keys,shared,out):
    lon,alt,cusp=data["lon"],data["alt"],data["cusp"];n=len(lon);rows=np.arange(n)
    cond=m.c.all_conditions(lon,alt)
    ptab=[ptolemy_item_tables(shared,o,keys) for o in observations]
    sv=[m.g.vote_arrays(lon,q["hd_ev"]["western"]) for q in profiles]
    for tag,gm,pm,gl,pl in m.p.branches(lon,alt):
        im=np.maximum(gm,0);il=np.maximum(gl,0)
        for pol in m.c.POLICIES:
            c=cond[pol];key=tag+"|"+pol
            mc=np.where(gm>=0,c[rows,im],m.c.UNKNOWN);lc=np.where(gl>=0,c[rows,il],m.c.UNKNOWN)
            items=[];scores=[];targets=[]
            for q,t,(ms,ls,ph) in zip(profiles,ptab,sv,strict=True):
                a=t[mc,0,im]+t[lc,1,il]
                sg=np.column_stack((np.where(gm>=0,ms[rows,im],0)*.25,np.where(gl>=0,ls[rows,il],0)*.125,ph*.125))
                items.append(np.column_stack((a,sg)))
                char=(np.where(gm>=0,q["cond_table"][mc,0,im],0.)+np.where(gl>=0,q["cond_table"][lc,1,il],0.))/2
                sign,_=m.b.family(np.where(gm>=0,ms[rows,im],0),np.where(gl>=0,ls[rows,il],0),ph,np.ones(n))
                scores.append((char+sign)/2);targets.append(q["prior"]["condition"]["reference"][key]["scores"]["blend"])
            out["ptolemy_blend"].add(key,items,scores,targets)
    lr,_=m.l.load_map();ltab=[lilly_item_tables(lr,shared,o,keys) for o in observations]
    for tag,status,single,primary,sc,sp,outer in m.l.branches(lon,alt,cusp[:,0],cusp[:,1]):
        mask=m.lc.encode(primary);cnt=primary.sum(axis=1)
        for ci,cl in enumerate(m.l.CLAUSES):
            for kind in ("single","mean"):
                arm=kind+"_"+cl;items=[];scores=[];targets=[]
                for q,t in zip(profiles,ltab,strict=True):
                    if kind=="single":
                        a=np.where((single>=0)[:,None],t[ci,np.maximum(single,0)],0.)
                    else:a=(primary@t[ci])/np.maximum(cnt,1)[:,None]
                    items.append(a);scores.append(q["lilly_lut"][arm][mask]);targets.append(q["prior"]["lilly"]["reference"][tag]["scores"][arm]["western"])
                out["lilly"].add(tag+"|"+arm,items,scores,targets)

def trace_eastern(data,profiles,observations,keys,registry,edges,cache,out):
    reg,prior,shared=registry;weights=[item_weights(shared,o,keys) for o in observations]
    for geom,mode in m.v.MODES:
        signs,graph,near,_=m.v.signs_and_graph(data["lon"],data["jds"],mode)
        if np.any(near):raise ValueError("Rival calendar unknown")
        arms=[m.v.compute(signs,graph,reg,edges,q["vedic_tables"][0]) for q in profiles]
        for tag in arms[0]:
            if not tag.endswith("|all_union"):continue
            key=geom+"|"+tag
            bits=[a[tag] for a in arms]
            out["vedic_union"].add(key,[bits_items(x,w) for x,w in zip(bits,weights,strict=True)],
                  [m.v.score(x,q["vedic_tables"][1])["score"] for x,q in zip(bits,profiles,strict=True)],
                  [q["prior"]["vedic"]["reference"][key]["score"] for q in profiles])
    for clock,wall in zip(m.cal.CLOCKS,(data["bs"],data["ls"]),strict=True):
        f=m.cal.features(data["bs"],wall,cache)
        arms=[{tag:(bits,good) for tag,bits,good in m.z.models(f,q["chinese_tables"]) if tag.startswith("union|")} for q in profiles]
        for tag in arms[0]:
            key=clock+"|"+tag;bits=[a[tag][0] for a in arms]
            if any(not np.all(a[tag][1]) for a in arms):raise ValueError("Rival Chinese calendar unknown")
            out["chinese_union"].add(key,[bits_items(x,w) for x,w in zip(bits,weights,strict=True)],
                [m.v.score(x,q["chinese_tables"][2])["score"] for x,q in zip(bits,profiles,strict=True)],
                [q["prior"]["chinese"]["reference"][key]["score"] for q in profiles])

def reference_data(a):
    inv=json.loads(a.inventory.read_text());ref=next(x["chart_midpoint"] for x in inv["comparison_units"] if x["private_id"]=="REFERENCE")
    at=m.g.timestamp(ref["utc"]);lon,alt,c1,c2=m.l.chart(ref)
    jd=m.swe.julday(at.year,at.month,at.day,at.hour+at.minute/60+at.second/3600+at.microsecond/3.6e9)
    return {"lon":lon,"alt":alt,"cusp":np.column_stack((c1,c2)),"jds":np.array([jd]),
        "bs":np.array([m.cal.wall_seconds(at.astimezone(m.cal.BEIJING))]),
        "ls":np.array([m.cal.wall_seconds(at.astimezone(m.cal.ZoneInfo(m.cal.SITE_ZONE)))])}

def run(a):
    files=[a.west,a.angles,a.hd_cache,a.join,a.ephemeris,a.calendar,a.inventory,a.mapping_library,a.output,a.overlap,a.cross_coding,*a.evidence,*a.hd_evidence,*[getattr(a,k) for k in m.RECEIPTS]]
    if any(x.resolve().is_relative_to(m.b.ROOT) for x in files) or a.output.exists():raise ValueError("Private immutable inputs required")
    W,WM,A,AM,H,proof=m.g.verify_inputs(a)
    ov=json.loads(a.overlap.read_text());cross=json.loads(a.cross_coding.read_text())
    if ov["runner_sha256"]!=m.b.digest(m.__file__) or cross["runner_sha256"]!=m.b.digest(cc.__file__) or cross["full_overlap_sha256"]!=m.b.digest(a.overlap):raise ValueError("Prior result drift")
    for k in m.RECEIPTS:
        if ov["prior_receipt_sha256"][k]!=m.b.digest(getattr(a,k)):raise ValueError("Prior receipt changed")
    for name,sha in W["ephe_sha256"].items():
        if m.b.digest(a.ephemeris/name)!=sha:raise ValueError("Ephemeris drift")
    m.swe.set_ephe_path(str(a.ephemeris));m.cal.witnesses()
    with np.load(a.calendar,allow_pickle=False) as f:cache={k:f[k] for k in f.files}
    receipts={k:json.loads(getattr(a,k).read_text()) for k in m.RECEIPTS}
    if receipts["chinese"]["calendar_sha256"]!=m.b.digest(a.calendar):raise ValueError("Chinese calendar changed")
    profiles,lookup,registry,edges=m.prepare(a,W,A,cache,receipts)
    data,eligible=d.collect(a,W,WM,A,AM,H,profiles,lookup,cache)
    rivals=np.array(cross["strict_survivor_indices"][d.KEY+"|strict_any"])
    keep=np.searchsorted(data["index"],rivals)
    if not np.array_equal(data["index"][keep],rivals):raise ValueError("Rival rows not present in common cohort")
    selected=d.select(data,keep);ref=reference_data(a)
    joined={k:np.concatenate((v,selected[k]),axis=0) for k,v in ref.items()}
    shared=registry[2];keys=tuple(k for dom in m.p.DOMAINS for k in shared["domains"][dom])
    observations=[json.loads(p.read_text())["observations"] for p in a.evidence]
    out={k:Trace(len(rivals),keys+SIGN_SLOTS if k=="ptolemy_blend" else keys) for k in m.PRIMARY}
    trace_western(joined,profiles,observations,keys,shared,out)
    trace_eastern(joined,profiles,observations,keys,registry,edges,cache,out)
    if any(len(t.tags)!=m.GROUPS[k] for k,t in out.items()):raise ValueError("Missing primary arm traces")
    result={"status":"EXECUTED_SHARED_WINNING_ARM_ITEM_TRACE_NOT_VALIDATION","families":{k:t.finish() for k,t in out.items()},
            "cross_coding_sha256":m.b.digest(a.cross_coding),"runner_sha256":m.b.digest(__file__)}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("Item trace complete; every decomposed score and reference reconciled.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","ephemeris","calendar","inventory","mapping-library","output","overlap","cross-coding",*m.RECEIPTS):
        p.add_argument("--"+k,type=Path,required=True)
    for k in ("evidence","hd-evidence"):p.add_argument("--"+k,type=Path,action="append",required=True)
    run(p.parse_args())
if __name__=="__main__":main()
