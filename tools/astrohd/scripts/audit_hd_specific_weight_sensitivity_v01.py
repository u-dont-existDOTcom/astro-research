#!/usr/bin/env python3
"""Post-result weight sensitivity, not an optimized replacement score.

Compare equal-item weighting with the same total available weight and all
single-domain omissions. No choice based on a reference-favorable rank.
"""
import argparse,json,os
from pathlib import Path
import numpy as np
import compare_hd_specific_observables_v01 as q
import trace_hd_specific_rivals_v01 as trace
h=q.h;b=q.b;g=q.g;s=q.s;c=q.c
POLICIES=("equal_domains","equal_items_same_mass",*("omit_"+d for d in q.DOMAINS))

def weighted_masks(keys,domains,obs,policy):
    z=q.masks(keys,domains,obs)
    if policy=="equal_domains":return z
    if policy=="equal_items_same_mass":
        n=sum((int(p)|int(m)).bit_count() for p,m,_ in z)
        mass=.25*sum((int(p)|int(m))!=0 for p,m,_ in z)
        return [(p,m,mass/n if n else 0.) for p,m,_ in z]
    if policy.startswith("omit_") and policy[5:] in q.DOMAINS:
        return [(p,m,0. if d==policy[5:] else w) for d,(p,m,w) in zip(q.DOMAINS,z,strict=True)]
    raise ValueError("Unknown weighting policy")

def run(a):
    inputs=[a.west,a.angles,a.hd_cache,a.join,a.mapping_library,a.inventory,a.overlap,a.cross_coding,a.context,a.adjudication,a.specific_evidence,a.hd_result,a.state_input,a.cross_result,a.flags,a.robustness,a.comparison,a.trace,a.output,*a.hd_evidence,*a.evidence]
    if any(p.resolve().is_relative_to(b.ROOT) for p in inputs) or a.output.exists():raise ValueError("Private immutable paths required")
    r=json.loads(a.comparison.read_text());tr=json.loads(a.trace.read_text());hr=json.loads(a.hd_result.read_text());cr=json.loads(a.cross_result.read_text())
    if r["runner_sha256"]!=b.digest(q.__file__) or r["map_sha256"]!=q.MAP_SHA or r["specific_evidence_sha256"]!=b.digest(a.specific_evidence) or r["prior_cross_sha256"]!=b.digest(a.cross_result) or r["prior_robustness_sha256"]!=b.digest(a.robustness):raise ValueError("Specific result binding drift")
    if tr["runner_sha256"]!=b.digest(trace.__file__) or tr["comparison_sha256"]!=b.digest(a.comparison):raise ValueError("Trace receipt drift")
    if cr["hd_result_sha256"]!=b.digest(a.hd_result) or cr["state_input_sha256"]!=b.digest(a.state_input) or cr["flag_output_sha256"]!=b.digest(a.flags):raise ValueError("Cached source drift")
    W,WM,A,AM,H,proof,oldgroups,shared,ref,at,rows,obs,_,prior,cross,context=h.load_inputs(a)
    _,groups,keys,domains=q.load_map(oldgroups)
    specific=q.load_evidence(a.specific_evidence,keys);specific.append(specific[0])
    with np.load(a.state_input,allow_pickle=False) as f:
        delta=f["delta"];bd=f["base_delta"]
        if tuple(f["arms"].tolist())!=h.SCORES or str(f["map_sha256"])!=h.MAP_SHA:raise ValueError("Arm registry drift")
    with np.load(a.flags,allow_pickle=False) as f:
        flags=f["flags"];known=f["known"]
        if tuple(f["groups"].tolist())!=c.GROUPS or tuple(f["metrics"].tolist())!=c.METRICS:raise ValueError("Flag registry drift")
    if delta.shape!=(3,len(h.SCORES),g.HD_N) or bd.shape!=(3,g.HD_N) or len(flags)!=g.N or int(known.sum())!=r["common_rows"]:raise ValueError("Array coverage drift")
    geo,base,ri,_=h.load_states(a.hd_cache,rows,obs,ref["HD"],at)
    if not np.allclose(bd,(base-base[ri]).T,rtol=0,atol=g.EPS/4):raise ValueError("Old structural score drift")
    # Evaluate survival of the newly certified context/original cohorts, not
    # just earlier HD maximal timestamps.
    w=q.build_weights(a,WM,AM,H,flags,known,{"full_union_blends_strict_survivors":{k:v["new_indices"] for k,v in tr["pairs"].items()}})
    if w["common"].sum()!=r["common_rows"]:raise ValueError("Common coverage drift")
    extrema={p:{label:[np.full(g.HD_N,np.inf),np.full(g.HD_N,-np.inf)] for _,label in q.PAIRS} for p in POLICIES}
    for mode in h.MAPS:
        bits=h.model_bits(geo,groups,keys,mode)
        for family in h.FAMILIES:
            if not family.startswith("union_"):continue
            tag=family+"|"+mode
            for policy in POLICIES:
                ds=[]
                for i,o in enumerate(specific):
                    val=s.score(bits[family],weighted_masks(keys,domains,o,policy))["score"]
                    shared_score=delta[i,h.SCORES.index(tag+"|archetypes")]+hr["profiles"][i][tag]["reference"]["archetypes"]
                    sc=q.components(base[:,i],shared_score,val)["extended_blend"];ds.append(sc-sc[ri])
                for i,label in q.PAIRS:
                    d=np.minimum(ds[i],ds[1]);lo,hi=extrema[policy][label]
                    np.minimum(lo,d,out=lo);np.maximum(hi,d,out=hi)
    results={}
    for policy,v in extrema.items():
        results[policy]={}
        for label,(lo,hi) in v.items():
            results[policy][label]={}
            for quant,d in (("every",lo),("any",hi)):
                a0=q.cross_counts(w,d,d);a0.pop("HD_equal_both")
                for name in c.COMBOS:a0[name].pop("HD_equal_others_strict_any")
                a0["previously_certified_strict_survivors"]={"strict":int(w["old_"+label][d>g.EPS].sum()),"no_lower":int(w["old_"+label][d>=-g.EPS].sum())}
                results[policy][label][quant]=a0
                if policy=="equal_domains":
                    old={k:z for k,z in r["six_union_robustness"][label]["extended_blend"][quant].items() if k!="previous_robust_rivals"}
                    if {k:z for k,z in a0.items() if k!="previously_certified_strict_survivors"}!=old:raise ValueError("Baseline weighting replay drift")
    out={"status":"EXECUTED_POST_RESULT_WEIGHT_SENSITIVITY_NOT_VALIDATION","grid_rows":g.N,"policies":POLICIES,"results":results,"runner_sha256":b.digest(__file__),"comparison_sha256":b.digest(a.comparison),"trace_sha256":b.digest(a.trace)}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("All weight sensitivities and previous baseline reproduced.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","mapping-library","inventory","overlap","cross-coding","context","adjudication","specific-evidence","hd-result","state-input","cross-result","flags","robustness","comparison","trace","output"):
        p.add_argument("--"+k,type=Path,required=True)
    for k in ("evidence","hd-evidence"):p.add_argument("--"+k,action="append",type=Path,required=True)
    run(p.parse_args())
if __name__=="__main__":main()
