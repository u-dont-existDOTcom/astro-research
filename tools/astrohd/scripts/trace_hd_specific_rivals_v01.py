#!/usr/bin/env python3
"""Exact old/new full-union rival identities and signed HD item attribution.

This is a post-selection description, not new evidence or rank optimization.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
import numpy as np
import compare_hd_specific_observables_v01 as q
h=q.h;b=q.b;g=q.g;s=q.s;c=q.c

def item_weights(keys,domains,obs):
    out=np.zeros(len(keys))
    for d in q.DOMAINS:
        i=[j for j,k in enumerate(keys) if domains[k]==d and obs.get(k) is not None]
        for j in i:out[j]=.25/len(i)*obs[keys[j]]
    return out

def item_scores(bits,weights):
    p,n=bits;mask=np.left_shift(np.uint64(1),np.arange(len(weights),dtype=np.uint64))
    return (((p[:,None]&mask)!=0).astype(np.int8)-((n[:,None]&mask)!=0).astype(np.int8))*weights

def run(a):
    files=[a.west,a.angles,a.hd_cache,a.join,a.mapping_library,a.inventory,a.overlap,a.cross_coding,a.context,a.adjudication,a.specific_evidence,a.hd_result,a.state_input,a.cross_result,a.flags,a.robustness,a.comparison,a.output,*a.hd_evidence,*a.evidence]
    if any(p.resolve().is_relative_to(b.ROOT) for p in files) or a.output.exists():raise ValueError("External immutable inputs required")
    result=json.loads(a.comparison.read_text());hr=json.loads(a.hd_result.read_text());cr=json.loads(a.cross_result.read_text());rob=json.loads(a.robustness.read_text())
    for k,p in (("specific_evidence_sha256",a.specific_evidence),("prior_cross_sha256",a.cross_result),("prior_robustness_sha256",a.robustness)):
        if result[k]!=b.digest(p):raise ValueError("Specific result source drift")
    if result["runner_sha256"]!=b.digest(q.__file__) or result["map_sha256"]!=q.MAP_SHA or hr["state_output_sha256"]!=b.digest(a.state_input) or cr["hd_result_sha256"]!=b.digest(a.hd_result) or cr["flag_output_sha256"]!=b.digest(a.flags) or rob["cross_receipt_sha256"]!=b.digest(a.cross_result):raise ValueError("Prior computation binding drift")
    W,WM,A,AM,H,proof,oldgroups,shared,ref,at,rows,obs,old_observations,prior,cross,context=h.load_inputs(a)
    _,groups,keys,domains=q.load_map(oldgroups);specific=q.load_evidence(a.specific_evidence,keys);specific.append(specific[0])
    with np.load(a.state_input,allow_pickle=False) as f:
        olddelta=f["delta"];bd=f["base_delta"]
        if tuple(f["arms"].tolist())!=h.SCORES or str(f["map_sha256"])!=h.MAP_SHA:raise ValueError("Prior HD arms drift")
    with np.load(a.flags,allow_pickle=False) as f:
        flags=f["flags"];known=f["known"]
        if tuple(f["groups"].tolist())!=c.GROUPS or tuple(f["metrics"].tolist())!=c.METRICS:raise ValueError("Non-HD flag drift")
    if olddelta.shape!=(3,len(h.SCORES),g.HD_N) or bd.shape!=(3,g.HD_N) or len(flags)!=g.N or int(known.sum())!=result["common_rows"]:raise ValueError("Cache shape drift")
    geo,base,ri,_=h.load_states(a.hd_cache,rows,obs,ref["HD"],at)
    if not np.allclose(bd,(base-base[ri]).T,rtol=0,atol=g.EPS/4):raise ValueError("Old HD baseline replay drift")
    ww=q.build_weights(a,WM,AM,H,flags,known,rob)
    arms={}
    for mode in h.MAPS:
        bits=h.model_bits(geo,groups,keys,mode)
        for family in h.FAMILIES:
            if not family.startswith("union_"):continue
            tag=family+"|"+mode;bb=bits[family];ds=[];sp=[]
            for i,o in enumerate(specific):
                v=s.score(bb,q.masks(keys,domains,o))["score"];sp.append(v)
                r=hr["profiles"][i][tag]["reference"]["archetypes"]
                shared_score=olddelta[i,h.SCORES.index(tag+"|archetypes")]+r
                score=q.components(base[:,i],shared_score,v)["extended_blend"];ds.append(score-score[ri])
                if abs(score[ri]-result["profiles"][i][tag]["reference"]["extended_blend"])>g.EPS/4:raise ValueError("Reference replay drift")
            for i,label in q.PAIRS:
                if q.cross_counts(ww,ds[i],ds[1])!={k:v for k,v in result["same_row"][label][tag+"|extended_blend"].items() if k!="previous_robust_rivals"}:raise ValueError("Specific arm count replay drift")
            arms[tag]={"bits":bb,"delta":ds,"specific":sp}
    robust={label:np.minimum.reduce([np.minimum(a0["delta"][i],a0["delta"][1]) for a0 in arms.values()]) for i,label in q.PAIRS}
    sets={label:{"old":rob["full_union_blends_strict_survivors"][label],"new":[]} for _,label in q.PAIRS}
    for x in sets.values():x["states_old"]=[];x["states_new"]=[]
    processed=0
    for shard in H["shards"]:
        n=shard["count"];p=a.join/"shards"/shard["file"]
        if shard["index_first"]!=processed or b.digest(p)!=shard["sha256"]:raise ValueError("Join alignment drift")
        ids=np.memmap(p,dtype="<i4",mode="r",shape=(n,));idx=np.maximum(ids,0)
        ok=known[processed:processed+n]&c.combo(flags[processed:processed+n],c.GROUPS,"strict_any")
        for label,ss in sets.items():
            new=ok&(robust[label][idx]>g.EPS)
            ss["new"].extend((processed+np.flatnonzero(new)).tolist());ss["states_new"].extend(ids[new].tolist())
            rr=np.asarray(ss["old"],np.int64);rr=rr[(rr>=processed)&(rr<processed+n)]-processed
            if np.any(~ok[rr]):raise ValueError("Old robust survivor lost frozen non-HD membership")
            ss["states_old"].extend(ids[rr].tolist())
        processed+=n
    if processed!=g.N:raise ValueError("Incomplete grid identity replay")
    out={}
    for i,label in q.PAIRS:
        ss=sets[label];expected=result["six_union_robustness"][label]["extended_blend"]["every"]
        if len(ss["new"])!=expected["all_primary"]["HD_strict_and_others_strict_any"] or len(set(ss["new"])&set(ss["old"]))!=expected["previous_robust_rivals"]["strict"]:raise ValueError("Exact new survivor identity drift")
        entry={"old_indices":ss["old"],"new_indices":ss["new"],"intersection":len(set(ss["new"])&set(ss["old"])),"cohorts":{}}
        for which in ("old","new"):
            ids=np.asarray(ss["states_"+which],np.int64)
            reports={}
            for tag,arm in arms.items():
                report={}
                for p in (i,1):
                    j=np.concatenate(([ri],ids));v=item_scores(tuple(x[j] for x in arm["bits"]),item_weights(keys,domains,specific[p]))
                    if not np.allclose(v.sum(axis=1),arm["specific"][p][j],rtol=0,atol=g.EPS/4):raise ValueError("Specific item sum replay drift")
                    ds=v[1:]-v[:1]
                    report[str(p)]={"items":{k:{"reference_contribution":float(v[0,z]),"mean_delta":float(ds[:,z].mean()) if len(ids) else 0.,
                       "gain_rows":int((ds[:,z]>g.EPS).sum()),"loss_rows":int((ds[:,z]<-g.EPS).sum())} for z,k in enumerate(keys)},
                       "mean_extended_delta":float(arm["delta"][p][ids].mean()) if len(ids) else 0.}
                report["strict_both"]=int(((arm["delta"][i][ids]>g.EPS)&(arm["delta"][1][ids]>g.EPS)).sum())
                reports[tag]=report
            entry["cohorts"][which]=reports
        out[label]=entry
    result={"status":"EXECUTED_EXACT_SPECIFIC_RIVAL_IDENTITY_AND_ITEM_TRACE_NOT_VALIDATION","grid_rows":processed,"pairs":out,
        "comparison_sha256":b.digest(a.comparison),"runner_sha256":b.digest(__file__)}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("Specific-observable old/new rival identities and item sums reconciled.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","mapping-library","inventory","overlap","cross-coding","context","adjudication","specific-evidence","hd-result","state-input","cross-result","flags","robustness","comparison","output"):
        p.add_argument("--"+k,type=Path,required=True)
    for k in ("evidence","hd-evidence"):p.add_argument("--"+k,action="append",required=True,type=Path)
    run(p.parse_args())
if __name__=="__main__":main()
