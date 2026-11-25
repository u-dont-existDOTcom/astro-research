#!/usr/bin/env python3
"""Source-specific HD behavioral block and exact cached same-row comparison.

The old model is immutable. All new score/weight choices are experimental.
Non-HD flags encode paired same-interpretation outcomes, not actual people.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
import numpy as np
import compare_hd_archetype_century_v01 as h
import compare_expanded_hd_multitradition_v01 as c
import audit_expanded_hd_arm_robustness_v01 as rb

b=h.b;g=h.g;s=h.s
MAP=h.MAP.parent/"hd_specific_observable_block_v01.json"
MAP_SHA="c9daf6b7f6cf0648719ca4bd7a1c0f4ecffdc7fd22dcf1d0c65547b27f5234ae"
KINDS=("specific","specific_structural","shared_specific","extended_blend")
PAIRS=((0,"original_pair"),(2,"context_pair"))
DOMAINS=("communication","work","motivation","relationship")

def load_map(prior_groups):
    if b.digest(MAP)!=MAP_SHA:raise ValueError("Specific map digest drift")
    reg=json.loads(MAP.read_text())
    if reg["schema"]!="hd_specific_observable_block_v01" or reg["prior_map_sha256"]!=h.MAP_SHA or tuple(reg["domains"])!=DOMAINS:raise ValueError("Map registry drift")
    keys=tuple(i["id"] for i in reg["items"]);domains={i["id"]:i["domain"] for i in reg["items"]}
    if len(set(keys))!=len(keys) or not 0<len(keys)<=64 or set(domains.values())!=set(DOMAINS):raise ValueError("Observable vocabulary drift")
    rows={(v["kind"],v["id"]):v for v in reg["carriers"]}
    if len(rows)!=len(reg["carriers"]):raise ValueError("Duplicate carrier")
    groups={}
    for kind,old in prior_groups.items():
        groups[kind]=[]
        for rr in old:
            k=(kind,rr["id"]);r=rows.pop(k,{"direct":{},"proxy":{},"basis":"No new source-specific direction admitted."})
            if not r["basis"] or set(r["direct"])&set(r["proxy"]):raise ValueError("Invalid carrier rationale")
            for f in ("direct","proxy"):
                if set(r[f])-set(keys) or any(type(x)!=int or x not in (-1,1) for x in r[f].values()):raise ValueError("Invalid direction")
            if ((kind=="gate" and int(rr["id"]) in h.EXCLUDED_GATES) or (kind=="channel" and rr["id"] in h.EXCLUDED_CHANNELS)) and (r["direct"] or r["proxy"]):raise ValueError("Excluded authority analogue")
            groups[kind].append(r)
    if rows:raise ValueError("New carrier absent from old complete catalogue")
    return reg,groups,keys,domains

def masks(keys,domains,obs):
    b.checked_obs(obs,set(keys))
    z=[]
    for d in DOMAINS:
        plus=sum(1<<i for i,k in enumerate(keys) if domains[k]==d and obs.get(k)==1)
        minus=sum(1<<i for i,k in enumerate(keys) if domains[k]==d and obs.get(k)==-1)
        n=(plus|minus).bit_count()
        z.append((np.uint64(plus),np.uint64(minus),.25/n if n else 0.))
    return z

def load_evidence(path,keys):
    x=json.loads(path.read_text())
    if x["schema"]!="private_hd_specific_observation_adjudication_v01" or x["map_sha256"]!=MAP_SHA or set(x["items"])!=set(keys):raise ValueError("Evidence/map binding drift")
    texts={}
    for k,r in x["source_digests"].items():
        p=Path(r["path"])
        if p.resolve().is_relative_to(b.ROOT) or b.digest(p)!=r["sha256"]:raise ValueError("Private evidence source drift")
        texts[k]=p.read_text().splitlines()
    for k,r in x["items"].items():
        if not r["rationale"] or any(x["profiles"][i][k]!=r[tag] for i,tag in enumerate(("broad","narrow"))):raise ValueError("Adjudication/profile drift")
        if any(r[t] is not None for t in ("broad","narrow")) and not r["located_anchors"]:raise ValueError("Missing located evidence")
        for z in r["located_anchors"]:
            if z["source"] not in texts or not 1<=z["line"]<=len(texts[z["source"]]) or z["anchor"].casefold() not in texts[z["source"]][z["line"]-1].casefold():raise ValueError("Evidence anchor drift")
    for obs in x["profiles"]:b.checked_obs(obs,set(keys))
    return x["profiles"]

def build_weights(a,WM,AM,H,flags,known,rob):
    # The full non-HD outcomes are independent of the new HD score. Exact
    # multiplicities by HD interval are sufficient; never assume independence.
    prior=rob["full_union_blends_strict_survivors"]
    selected={k:np.asarray(v,np.int64) for k,v in prior.items()}
    if any(np.any(np.diff(v)<=0) or np.any((v<0)|(v>=g.N)) for v in selected.values()):raise ValueError("Prior survivor index drift")
    w={k:np.zeros(g.HD_N,np.int64) for k in ("full","common",*["old_"+k for k in selected])}
    for k in c.COMBOS:
        for z in c.METRICS:w[k+"|"+z]=np.zeros(g.HD_N,np.int64)
    processed=0;unknown=0
    def add(k,ids):
        w[k]+=np.bincount(ids,minlength=g.HD_N)
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not(wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):raise ValueError("Grid alignment drift")
        for p,r,size in zip((a.west/"chunks"/wi["file"],a.angles/"shards"/ai["file"],a.join/"shards"/hi["file"]),(wi,ai,hi),(64,136,4),strict=True):
            if p.stat().st_size!=n*size or b.digest(p)!=r["sha256"]:raise ValueError("Grid digest drift")
        ids=np.memmap(a.join/"shards"/hi["file"],dtype="<i4",mode="r",shape=(n,))
        if np.any(ids<-1) or np.any(ids>=g.HD_N):raise ValueError("Invalid state index")
        good=ids>=0;unknown+=int((~good).sum());add("full",ids[good])
        ok=known[processed:processed+n];f=flags[processed:processed+n]
        if np.any(ok&~good):raise ValueError("HD boundary marked usable")
        add("common",ids[ok])
        for name,gs in c.COMBOS.items():
            for k in c.METRICS:add(name+"|"+k,ids[ok&c.combo(f,gs,k)])
        for name,v in selected.items():
            i=v[(v>=processed)&(v<processed+n)]-processed
            if np.any(~ok[i]):raise ValueError("Old survivor not common")
            add("old_"+name,ids[i])
        processed+=n
    if processed!=g.N or unknown!=125 or w["full"].sum()!=g.N-125 or any(w["old_"+k].sum()!=len(v) for k,v in selected.items()):raise ValueError("Weight accounting drift")
    return w

def cross_counts(w,x,y):
    ge=(x>=-g.EPS)&(y>=-g.EPS);gt=(x>g.EPS)&(y>g.EPS)
    tie=(np.abs(x)<=g.EPS)&(np.abs(y)<=g.EPS)
    def n(k,mask):return int(w[k][mask].sum())
    out={"HD_no_lower":n("common",ge),"HD_strict_both":n("common",gt),"HD_equal_both":n("common",tie)}
    for name in c.COMBOS:
        out[name]={"HD_strict_and_others_strict_any":n(name+"|strict_any",gt),
                   "HD_strict_and_others_strict_all":n(name+"|strict_all",gt),
                   "HD_no_lower_others_strict_any":n(name+"|strict_any",ge),
                   "HD_equal_others_strict_any":n(name+"|strict_any",tie),
                   "HD_no_lower_others_ge_any":n(name+"|ge_any",ge),
                   "HD_no_lower_others_ge_all":n(name+"|ge_all",ge)}
    return out

def components(base,shared,specific):
    # Specific-only versus replacement blend versus correlated block
    # extension, with old structural weighting preserved in extended_blend.
    return {"specific":specific,"specific_structural":(base+specific)/2,
            "shared_specific":(shared+specific)/2,"extended_blend":(base+(shared+specific)/2)/2}

def run(a):
    paths=[a.west,a.angles,a.hd_cache,a.join,a.mapping_library,a.inventory,a.overlap,a.cross_coding,a.context,a.adjudication,a.specific_evidence,a.hd_result,a.state_input,a.cross_result,a.flags,a.robustness,a.output,*a.hd_evidence,*a.evidence]
    if any(p.resolve().is_relative_to(b.ROOT) for p in paths) or a.output.exists():raise ValueError("External immutable private paths required")
    if len(a.hd_evidence)!=2 or len(a.evidence)!=2:raise ValueError("Both old evidence profiles required")
    W,WM,A,AM,H,proof,oldgroups,shared,ref,at,rows,obs,old_observations,prior,cross,context=h.load_inputs(a)
    reg,groups,keys,domains=load_map(oldgroups)
    specific=load_evidence(a.specific_evidence,keys);specific.append(specific[0])
    hr=json.loads(a.hd_result.read_text());cr=json.loads(a.cross_result.read_text());rob=json.loads(a.robustness.read_text())
    if hr["runner_sha256"]!=b.digest(h.__file__) or hr["state_output_sha256"]!=b.digest(a.state_input) or hr["map_sha256"]!=h.MAP_SHA:raise ValueError("Old HD result drift")
    if cr["runner_sha256"]!=b.digest(c.__file__) or cr["hd_result_sha256"]!=b.digest(a.hd_result) or cr["state_input_sha256"]!=b.digest(a.state_input) or cr["flag_output_sha256"]!=b.digest(a.flags):raise ValueError("Old cross receipt drift")
    if rob["runner_sha256"]!=b.digest(rb.__file__) or rob["cross_receipt_sha256"]!=b.digest(a.cross_result):raise ValueError("Old robustness receipt drift")
    for k,p in (("prior_overlap_sha256",a.overlap),("prior_cross_coding_sha256",a.cross_coding),("prior_context_sha256",a.context)):
        if hr[k]!=b.digest(p) or cr[k]!=b.digest(p):raise ValueError("Old baseline receipt drift")
    if hr["evidence_sha256"]!=[b.digest(p) for p in a.evidence] or hr["HD_evidence_sha256"]!=[b.digest(p) for p in a.hd_evidence]:raise ValueError("Old evidence binding drift")
    with np.load(a.state_input,allow_pickle=False) as f:
        olddelta=f["delta"];bd=f["base_delta"]
        if tuple(f["arms"].tolist())!=h.SCORES or str(f["map_sha256"])!=h.MAP_SHA:raise ValueError("Old arm registry drift")
    with np.load(a.flags,allow_pickle=False) as f:
        flags=f["flags"];known=f["known"]
        if tuple(f["groups"].tolist())!=c.GROUPS or tuple(f["metrics"].tolist())!=c.METRICS:raise ValueError("Non-HD flag registry drift")
    if olddelta.shape!=(3,len(h.SCORES),g.HD_N) or bd.shape!=(3,g.HD_N) or len(flags)!=g.N or int(known.sum())!=cr["common_rows"]:raise ValueError("Cached shape drift")
    geo,base,ri,_=h.load_states(a.hd_cache,rows,obs,ref["HD"],at)
    if not np.allclose(bd,(base-base[ri]).T,atol=g.EPS/4,rtol=0):raise ValueError("Old structural scores drift")
    w=build_weights(a,WM,AM,H,flags,known,rob)
    if w["common"].sum()!=cr["common_rows"]:raise ValueError("Common grid drift")
    for i,label in PAIRS:
        if cross_counts(w,bd[i],bd[1])!=cr["counts"][label]["baseline"]:raise ValueError("Old baseline cross counts drift")
        for j,k in enumerate(h.SCORES):
            if cross_counts(w,olddelta[i,j],olddelta[1,j])!=cr["counts"][label][k]:raise ValueError("Old cross arm drift")
    results=[{} for _ in specific];joint={label:{} for _,label in PAIRS}
    extrema={label:{k:[np.full(g.HD_N,np.inf),np.full(g.HD_N,-np.inf)] for k in KINDS} for _,label in PAIRS}
    for mode in h.MAPS:
        bits=h.model_bits(geo,groups,keys,mode)
        for family,bb in bits.items():
            tag=family+"|"+mode;dd=[]
            for i,o in enumerate(specific):
                z=s.score(bb,masks(keys,domains,o))
                v=z["score"];r=hr["profiles"][i][tag]["reference"]["archetypes"]
                old=olddelta[i,h.SCORES.index(tag+"|archetypes")]+r
                sc=components(base[:,i],old,v);ds={}
                rec={"specific_mapped_items":int(z["known_items"][ri]),"specific_conflicting_items":int(z["conflicting_items"][ri]),"specific_mapped_rows":int(w["full"][z["known_items"]>0].sum()),"reference":{},"ranks":{}}
                for kind,q in sc.items():
                    ds[kind]=q-q[ri];rec["reference"][kind]=float(q[ri])
                    rec["ranks"][kind]={"full_grid":h.ranks(q,q[ri],w["full"]),
                        "equal_specific_item_count":h.ranks(q,q[ri],w["full"],z["known_items"]==z["known_items"][ri])}
                rec["specific_bounds"]=h.bound_ranks(z["lo"],z["hi"],z["lo"][ri],z["hi"][ri],w["full"])
                results[i][tag]=rec;dd.append(ds)
            for i,label in PAIRS:
                for kind in KINDS:
                    x,y=dd[i][kind],dd[1][kind];both=np.minimum(x,y)
                    entry=cross_counts(w,x,y)
                    entry["previous_robust_rivals"]={"strict":int(w["old_"+label][both>g.EPS].sum()),"no_lower":int(w["old_"+label][both>=-g.EPS].sum())}
                    joint[label][tag+"|"+kind]=entry
                    if family.startswith("union_"):
                        lo,hi=extrema[label][kind]
                        np.minimum(lo,both,out=lo);np.maximum(hi,both,out=hi)
    # Across all six full-union variants, min of same-arm two-coding deltas.
    robust={}
    for _,label in PAIRS:
        robust[label]={}
        for k,(lo,hi) in extrema[label].items():
            robust[label][k]={}
            for quant,d in (("every",lo),("any",hi)):
                row=cross_counts(w,d,d)
                # Artificial duplicated min deltas only support strict/no-lower,
                # not actual both-score equality; drop the tie-only fields.
                row.pop("HD_equal_both")
                for name in c.COMBOS:row[name].pop("HD_equal_others_strict_any")
                row["previous_robust_rivals"]={"strict":int(w["old_"+label][d>g.EPS].sum()),"no_lower":int(w["old_"+label][d>=-g.EPS].sum())}
                robust[label][k][quant]=row
    result={"status":"EXECUTED_GENERIC_SPECIFIC_OBSERVABLE_BLOCK_NOT_VALIDATION","grid_rows":g.N,"ranked_rows":int(w["full"].sum()),"common_rows":int(w["common"].sum()),"map_sha256":MAP_SHA,
        "items":len(keys),"profiles":results,"same_row":joint,"six_union_robustness":robust,
        "old_arm_pairs_replayed":2*(len(h.SCORES)+1),"new_point_choices_per_coding":len(h.ARMS)*len(KINDS),
        "specific_evidence_sha256":b.digest(a.specific_evidence),"runner_sha256":b.digest(__file__),"prior_cross_sha256":b.digest(a.cross_result),"prior_robustness_sha256":b.digest(a.robustness)}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("Source-specific HD full-grid and frozen non-HD same-row comparison complete.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","mapping-library","inventory","overlap","cross-coding","context","adjudication","specific-evidence","hd-result","state-input","cross-result","flags","robustness","output"):
        p.add_argument("--"+k,type=Path,required=True)
    for k in ("evidence","hd-evidence"):p.add_argument("--"+k,type=Path,action="append",required=True)
    run(p.parse_args())
if __name__=="__main__":main()
