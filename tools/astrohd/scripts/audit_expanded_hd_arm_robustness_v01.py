#!/usr/bin/env python3
"""Exact across-HD-arm intersections using the verified full-grid flags."""
import argparse,json,os
from pathlib import Path
from collections import defaultdict
import numpy as np
import compare_expanded_hd_multitradition_v01 as cross
hd=cross.hd;m=cross.m

def arm_groups():
    tags=hd.SCORES
    return {"all_point_arms":tuple(range(len(tags))),
            "all_blends":tuple(i for i,k in enumerate(tags) if k.endswith("|blend")),
            "all_archetype_only":tuple(i for i,k in enumerate(tags) if k.endswith("|archetypes")),
            "full_union_blends":tuple(i for i,k in enumerate(tags) if k.startswith("union_") and k.endswith("|blend")),
            "full_union_archetypes":tuple(i for i,k in enumerate(tags) if k.startswith("union_") and k.endswith("|archetypes"))}

def summarize(packed,known,x,y):
    if x.shape!=y.shape or x.shape[1]!=len(known):raise ValueError("Unaligned HD arms")
    # Shared HD tag in both codings first, then quantify across tags.
    d=np.minimum(x,y)
    out={}
    for quant,delta in (("any_HD_arm",d.max(axis=0)),("every_HD_arm",d.min(axis=0))):
        ge=known&(delta>=-m.EPS);gt=known&(delta>m.EPS)
        z={"HD_no_lower":int(ge.sum()),"HD_strict":int(gt.sum())}
        for name,groups in cross.COMBOS.items():
            hi=cross.combo(packed,groups,"strict_any");all_ge=cross.combo(packed,groups,"ge_all")
            z[name]={"HD_strict_others_strict_any":int((gt&hi).sum()),
                     "HD_no_lower_others_strict_any":int((ge&hi).sum()),
                     "HD_no_lower_others_ge_all":int((ge&all_ge).sum())}
        out[quant]=z
    return out

def run(a):
    paths=(a.join,a.cross_receipt,a.state_input,a.flags,a.output)
    if any(p.resolve().is_relative_to(m.b.ROOT) for p in paths) or a.output.exists():raise ValueError("External private paths required")
    r=json.loads(a.cross_receipt.read_text())
    if r["runner_sha256"]!=m.b.digest(cross.__file__) or r["state_input_sha256"]!=m.b.digest(a.state_input) or r["flag_output_sha256"]!=m.b.digest(a.flags):raise ValueError("Frozen receipts changed")
    with np.load(a.state_input,allow_pickle=False) as z:
        delta=z["delta"]
        if tuple(z["arms"].tolist())!=hd.SCORES or str(z["map_sha256"])!=hd.MAP_SHA:raise ValueError("HD arms changed")
    with np.load(a.flags,allow_pickle=False) as z:
        flags=z["flags"];known=z["known"]
        if tuple(z["groups"].tolist())!=cross.GROUPS or tuple(z["metrics"].tolist())!=cross.METRICS:raise ValueError("Non-HD flag registry changed")
    if delta.shape!=(3,len(hd.SCORES),m.g.HD_N) or len(flags)!=m.g.N or int(known.sum())!=r["common_rows"]:raise ValueError("Data shape drift")
    manifest=json.loads((a.join/"manifest.json").read_text())
    source=json.loads((m.b.ROOT/"tools/astrohd/reference/research/ptolemy_iii13_five_mode_aspect_century_public_v01.json").read_text())
    if m.b.digest(a.join/"manifest.json")!=source["source_sha_manifests"]["HD"]:raise ValueError("Original HD join manifest drift")
    groups=arm_groups();counts={p:{k:{} for k in groups} for p in ("original_pair","context_pair")};survivors={p:[] for p in counts};processed=0
    for shard in manifest["shards"]:
        n=shard["count"];path=a.join/"shards"/shard["file"]
        if shard["index_first"]!=processed or path.stat().st_size!=n*4 or m.b.digest(path)!=shard["sha256"]:raise ValueError("Join alignment/hash drift")
        ids=np.memmap(path,dtype="<i4",mode="r",shape=(n,))
        if np.any(ids<-1) or np.any(ids>=m.g.HD_N):raise ValueError("Invalid HD state")
        idx=np.maximum(ids,0);f=flags[processed:processed+n];ok=known[processed:processed+n]
        if np.any(ok&(ids<0)):raise ValueError("Unknown HD row marked common")
        for i,p in ((0,"original_pair"),(2,"context_pair")):
            for name,arm in groups.items():
                x=delta[i][np.ix_(arm,idx)];y=delta[1][np.ix_(arm,idx)]
                z=summarize(f,ok,x,y);cross.add_counts(counts[p][name],z)
                if name=="full_union_blends":
                    keep=ok&(np.minimum(x,y).min(axis=0)>m.EPS)&cross.combo(f,cross.GROUPS,"strict_any")
                    survivors[p].extend((processed+np.flatnonzero(keep)).tolist())
        processed+=n
    if processed!=m.g.N:raise ValueError("Incomplete grid")
    for p in counts:
        n=counts[p]["full_union_blends"]["every_HD_arm"]["all_primary"]["HD_strict_others_strict_any"]
        if n!=len(survivors[p]):raise ValueError("Survivor identity accounting drift")
    os.umask(0o077)
    out={"status":"EXECUTED_EXACT_HD_ARM_ROBUSTNESS_NOT_VALIDATION","grid_rows":processed,
         "groups":{k:[hd.SCORES[i] for i in ix] for k,ix in groups.items()},"counts":counts,
         "full_union_blends_strict_survivors":survivors,"cross_receipt_sha256":m.b.digest(a.cross_receipt),"runner_sha256":m.b.digest(__file__)}
    with a.output.open("x") as f:json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("Across-HD-arm exact intersections complete.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("join","cross-receipt","state-input","flags","output"):p.add_argument("--"+k,type=Path,required=True)
    run(p.parse_args())
if __name__=="__main__":main()
