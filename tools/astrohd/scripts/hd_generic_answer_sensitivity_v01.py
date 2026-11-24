#!/usr/bin/env python3
"""Exhaustive hypothetical completion of a version-bound generic HD question set.

Answer effects are NOT personal observations or probabilities. Only the existing
frozen non-authority token map and score are used. Inputs/results stay private.
"""
from __future__ import annotations
import argparse,gzip,json,math,os
from collections import Counter,defaultdict
from hashlib import sha256
from itertools import product
from pathlib import Path
import numpy as np
import compare_bounded_behavior_v01 as b
import compare_full_grid_behavior_v01 as g
import code_frozen_hd_observations_v01 as coder
import compare_multitradition_cross_coding_v01 as cc

CORE="ptolemy_blend + lilly + vedic_union + chinese_union|strict_any"

def packet_questions(packet,bank,bank_sha,rows,baselines):
    if packet["source_question_bank_sha256"]!=bank_sha:
        raise ValueError("Question-bank version digest changed")
    byid={q["id"]:q for q in bank["questions"]}
    if len(byid)!=len(bank["questions"]):raise ValueError("Question bank duplicate IDs")
    ids=[]
    for q in packet["questions"]:
        i=q["id"]
        if q["qualified_id"]!="question_bank_v1::"+i or i in ids or i not in byid:
            raise ValueError("Unresolved original question identity")
        for k in ("domain","prompt","response_format","followups","minimum_evidence"):
            if q[k]!=byid[i][k]:raise ValueError("Original question content changed: "+i)
        if q["answer"] is not None:raise ValueError("Sensitivity must not admit a personal answer")
        rs=[r for r in rows if i in r["question_ids"]]
        if not rs or any(len(r["question_ids"])!=1 for r in rs):
            raise ValueError("Missing single-question token map")
        if any(o.get(r["mapping_id"]) is not None for o in baselines for r in rs):
            raise ValueError("Hypothetical completion would overwrite existing observation")
        ids.append(i)
    return ids

def options(rows,ids):
    out=[]
    for i in ids:
        tokens=set()
        for r in rows:
            if r["question_ids"]==[i]:
                tokens.update(r["predicted_response"]["support_answer_tokens"])
                tokens.update((r.get("contradiction_rule") or {}).get("answer_tokens",[]))
        # All tokens with the same effect are one class. Unknown, neutral or
        # unmapped responses all have the same null scoring consequence.
        opt=[];seen=set()
        for t in [None,*sorted(tokens)]:
            z=coder.code(rows,{i:t})
            effect=tuple(z[r["mapping_id"]]["observation"] for r in rows)
            if effect not in seen:
                seen.add(effect);opt.append((t,effect))
        out.append(opt)
    return out

def score_numerators(active,rows,obs):
    """Exact integer representation of the old cluster-mean rubric."""
    keys=[r["mapping_id"] for r in rows]
    b.checked_obs(obs,keys)
    if active.ndim!=2 or active.shape[1]!=len(rows):raise ValueError("Unaligned predicate array")
    clusters=defaultdict(list)
    for i,r in enumerate(rows):
        if obs.get(keys[i]) is not None:clusters[r["dependency_cluster"]].append(i)
    if not clusters:return np.zeros(len(active),np.int64),1
    den=math.lcm(*[len(x) for x in clusters.values()])
    num=np.zeros(len(active),np.int64)
    for inds in clusters.values():
        sign=np.array([obs[keys[i]] for i in inds],np.int64)
        num+=(active[:,inds]@sign)*(den//len(inds))
    return num,den*len(clusters)

def counts(delta,weights):
    return {"higher":int(weights[delta>0].sum()),"tied":int(weights[delta==0].sum()),"lower":int(weights[delta<0].sum())}

def load_signatures(root,rows,ref,at):
    mp=root/"manifest.json";manifest=json.loads(mp.read_text())
    if b.digest(mp)!=g.HD_MANIFEST or manifest["canonical_rows_sha256"]!=g.HD_ROWS:raise ValueError("HD source manifest changed")
    seen={};keys={};patterns=[];state_ids=[];prev=None;refhits=0;refsig=None;digest=sha256()
    for shard in manifest["shards"]:
        raw=(root/shard["filename"]).read_bytes()
        if sha256(raw).hexdigest()!=shard["sha256"]:raise ValueError("HD shard changed")
        raw=gzip.decompress(raw)
        if len(raw)!=shard["uncompressed_bytes"]:raise ValueError("HD shard bytes changed")
        digest.update(raw);n=0
        for line in raw.splitlines():
            x=json.loads(line);a,c=map(g.timestamp,(x["start_utc"],x["end_utc"]))
            if (prev is not None and a!=prev) or c<=a:raise ValueError("HD state continuity drift")
            prev=c;n+=1
            ch=g.source_hd_chart(x["chart_features"])
            key=(ch["type"],ch["profile"],tuple(sorted(ch["defined_centers"])))
            if key not in keys:
                sig=tuple(b.hd_active(ch,r["chart_feature_predicate"]) for r in rows)
                if any(v is None for v in sig):raise ValueError("Unexpected unknown structural predicate")
                if sig not in seen:
                    seen[sig]=len(patterns);patterns.append(sig)
                keys[key]=seen[sig]
            j=keys[key];state_ids.append(j)
            if a<=at<c:
                refhits+=1;refsig=j
                if patterns[j]!=tuple(b.hd_active(ref,r["chart_feature_predicate"]) for r in rows):raise ValueError("Exact reference predicate drift")
        if n!=shard["state_count"]:raise ValueError("HD shard count drift")
    if len(state_ids)!=g.HD_N or digest.hexdigest()!=g.HD_ROWS or refhits!=1:raise ValueError("HD logical digest/count/reference drift")
    return np.asarray(patterns,np.int64),np.asarray(state_ids,np.int32),refsig,len(keys)

def grid_weights(a,W,WM,A,AM,H,state_sigs,n_sigs,rivals):
    total=np.zeros(n_sigs,np.int64);rweights=total.copy();processed=0;unknown=0;seen=0
    if len(set(rivals))!=len(rivals) or rivals!=sorted(rivals):raise ValueError("Invalid previous rival indices")
    rr=np.asarray(rivals,np.int64)
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not(wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):raise ValueError("Grid alignment drift")
        paths=(a.west/"chunks"/wi["file"],a.angles/"shards"/ai["file"],a.join/"shards"/hi["file"])
        for p,meta,size in zip(paths,(wi,ai,hi),(64,136,4),strict=True):
            if p.stat().st_size!=n*size or b.digest(p)!=meta["sha256"]:raise ValueError("Grid source shard drift")
        ids=np.memmap(paths[2],dtype="<i4",mode="r",shape=(n,))
        if np.any(ids<-1) or np.any(ids>=len(state_sigs)):raise ValueError("Invalid HD index")
        good=ids>=0;unknown+=int((~good).sum())
        total+=np.bincount(state_sigs[ids[good]],minlength=n_sigs)
        j=rr[(rr>=processed)&(rr<processed+n)]-processed
        if np.any(ids[j]<0):raise ValueError("Previous rival on unknown HD row")
        rweights+=np.bincount(state_sigs[ids[j]],minlength=n_sigs);seen+=len(j)
        processed+=n
    if processed!=g.N or unknown!=125 or seen!=len(rivals) or total.sum()!=g.N-125:
        raise ValueError("Finite grid denominator changed")
    return total,rweights,unknown

def evaluate(active,ref_index,rows,baselines,ids,opts,total,rival_weights):
    keys=[r["mapping_id"] for r in rows]
    results=[]
    for selection in product(*opts):
        answers={q:t for q,(t,_) in zip(ids,selection,strict=True)}
        encoded=coder.code(rows,answers)
        extra={k:v["observation"] for k,v in encoded.items() if v["observation"] is not None}
        records=[];delta=[]
        for old in baselines:
            if set(extra)&{k for k,v in old.items() if v is not None}:raise ValueError("Frozen baseline overwritten")
            o={**old,**extra}
            numerator,den=score_numerators(active,rows,o)
            diff=numerator-numerator[ref_index];delta.append(diff)
            records.append({"observed":sum(o.get(k) is not None for k in keys),"score":float(numerator[ref_index]/den),
                            "full_grid":counts(diff,total),"prior_rivals":counts(diff,rival_weights)})
        x,y=delta
        results.append({"hypothetical_tokens":answers,"new_observed_predicates":len(extra),
            "profiles":records,
            "both_codings":{"full_grid_strictly_higher":int(total[(x>0)&(y>0)].sum()),
                "full_grid_no_lower":int(total[(x>=0)&(y>=0)].sum()),
                "prior_rivals_strictly_higher":int(rival_weights[(x>0)&(y>0)].sum()),
                "prior_rivals_no_lower":int(rival_weights[(x>=0)&(y>=0)].sum()),
                "prior_rivals_equal":int(rival_weights[(x==0)&(y==0)].sum())}})
    if len(results)!=math.prod(map(len,opts)):raise ValueError("Incomplete token-product")
    return results

def run(a):
    files=[a.west,a.angles,a.hd_cache,a.join,a.mapping_library,a.inventory,a.packet,a.question_bank,a.overlap,a.cross_coding,a.output,*a.hd_evidence]
    if any(p.resolve().is_relative_to(b.ROOT) for p in files) or a.output.exists():raise ValueError("External private immutable paths required")
    if len(a.hd_evidence)!=2:raise ValueError("Two frozen HD evidence profiles required")
    W,WM,A,AM,H,proof=g.verify_inputs(a)
    cross=json.loads(a.cross_coding.read_text());overlap=json.loads(a.overlap.read_text())
    if cross["runner_sha256"]!=b.digest(cc.__file__) or cross["full_overlap_sha256"]!=b.digest(a.overlap) or overlap["runner_sha256"]!=b.digest(cc.m.__file__):raise ValueError("Previous receipt drift")
    inv=json.loads(a.inventory.read_text());ref=next(q["chart_midpoint"] for q in inv["comparison_units"] if q["private_id"]=="REFERENCE")
    at=g.timestamp(ref["utc"]);rows=b.load_mapping(a.mapping_library)
    ev=[json.loads(p.read_text()) for p in a.hd_evidence]
    for i,e in enumerate(ev):
        if e["inventory_sha256"]!=b.digest(a.inventory) or overlap["profiles"][i]["HD_evidence_sha256"]!=b.digest(a.hd_evidence[i]):raise ValueError("Frozen evidence drift")
    baselines=[e["hd"] for e in ev]
    packet=json.loads(a.packet.read_text());bank=json.loads(a.question_bank.read_text())
    ids=packet_questions(packet,bank,b.digest(a.question_bank),rows,baselines);opts=options(rows,ids)
    active,state_sigs,ri,n_struct=load_signatures(a.hd_cache,rows,ref["HD"],at)
    rivals=cross["strict_survivor_indices"][CORE]
    total,rweights,unknown=grid_weights(a,W,WM,A,AM,H,state_sigs,len(active),rivals)
    results=evaluate(active,ri,rows,baselines,ids,opts,total,rweights)
    # All-null row is the exact old frozen score on the complete grid.
    base=results[0]
    if any(v is not None for v in base["hypothetical_tokens"].values()):raise ValueError("Expected null baseline")
    for i,q in enumerate(base["profiles"]):
        old=overlap["profiles"][i]["counts"]["coverage"]
        if q["full_grid"]!={"higher":old["HD_strictly_higher"],"tied":old["HD_tied"],"lower":old["HD_lower"]}:raise ValueError("Old full-grid HD rank replay failed")
        if abs(q["score"]-b.hd_score(ref["HD"],rows,baselines[i])["score"])>g.EPS:raise ValueError("Old reference score replay failed")
    if base["both_codings"]["prior_rivals_equal"]!=len(rivals):raise ValueError("Prior rival HD score replay failed")
    result={"status":"HYPOTHETICAL_ALL_MAPPED_ANSWER_CLASSES_NOT_OBSERVATIONS_OR_VALIDATION","grid_rows":g.N,"ranked_rows":int(total.sum()),
        "unknown_HD":unknown,"predicate_signatures":len(active),"structural_signatures":n_struct,"question_count":len(ids),
        "question_options":{q:len(o) for q,o in zip(ids,opts,strict=True)},"scenario_count":len(results),
        "previous_rival_count":len(rivals),"scenarios":results,"grid_proof":proof,"runner_sha256":b.digest(__file__),
        "packet_sha256":b.digest(a.packet),"overlap_sha256":b.digest(a.overlap),"cross_coding_sha256":b.digest(a.cross_coding)}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("Complete hypothetical generic HD answer-class comparison; no personal answers or score update admitted.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","mapping-library","inventory","packet","question-bank","overlap","cross-coding","output"):
        p.add_argument("--"+k,type=Path,required=True)
    p.add_argument("--hd-evidence",action="append",type=Path,required=True)
    run(p.parse_args())
if __name__=="__main__":main()
