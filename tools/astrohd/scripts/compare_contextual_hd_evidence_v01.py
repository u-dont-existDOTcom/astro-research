#!/usr/bin/env python3
"""Compare a separately admitted context-qualified observation with frozen HD.

The prior full-grid non-HD comparison can be reused only when every new
both-coding HD-no-lower signature was already eligible under the old HD scores.
No target-specific new weights, forced token selection or global trait claim.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
import numpy as np
import hd_generic_answer_sensitivity_v01 as s
import compare_multitradition_cross_coding_v01 as cc
import diagnose_multitradition_survivors_v01 as diag
b=s.b;g=s.g

def compare_scores(active,ri,rows,old,new,weights):
    o,d=s.score_numerators(active,rows,old);n,e=s.score_numerators(active,rows,new)
    od=o-o[ri];nd=n-n[ri]
    return od,nd,{"old_reference_score":float(o[ri]/d),"new_reference_score":float(n[ri]/e),
                   "old_ranks":s.counts(od,weights),"new_ranks":s.counts(nd,weights)}

def filter_sets(a,H,state_sigs,eligible,sets):
    """All prior survivor identities use the original clock index."""
    out={k:[] for k in sets};processed=0;seen={k:0 for k in sets}
    arr={k:np.asarray(v,np.int64) for k,v in sets.items()}
    for k,v in arr.items():
        if np.any(np.diff(v)<=0) or np.any((v<0)|(v>=g.N)):raise ValueError("Unaligned prior set")
    for h in H["shards"]:
        n=h["count"]
        if h["index_first"]!=processed:raise ValueError("Join alignment drift")
        p=a.join/"shards"/h["file"]
        if b.digest(p)!=h["sha256"]:raise ValueError("Join integrity drift")
        ids=np.memmap(p,dtype="<i4",mode="r",shape=(n,))
        for k,idx in arr.items():
            chosen=idx[(idx>=processed)&(idx<processed+n)]
            j=ids[chosen-processed]
            if np.any((j<0)|(j>=len(state_sigs))):raise ValueError("Unknown prior survivor HD state")
            out[k].extend(chosen[eligible[state_sigs[j]]].tolist());seen[k]+=len(chosen)
        processed+=n
    if processed!=g.N or any(seen[k]!=len(v) for k,v in sets.items()):raise ValueError("Prior set coverage drift")
    return out

def run(a):
    files=[a.west,a.angles,a.hd_cache,a.join,a.mapping_library,a.inventory,a.packet,a.question_bank,a.raw,a.adjudication,a.overlap,a.cross_coding,a.diagnostic,a.output,*a.hd_evidence]
    if any(p.resolve().is_relative_to(b.ROOT) for p in files) or a.output.exists():raise ValueError("External immutable private paths required")
    if len(a.hd_evidence)!=2:raise ValueError("Both frozen codings required")
    W,WM,A,AM,H,proof=g.verify_inputs(a)
    ov=json.loads(a.overlap.read_text());cross=json.loads(a.cross_coding.read_text());di=json.loads(a.diagnostic.read_text())
    if ov["runner_sha256"]!=b.digest(cc.m.__file__) or cross["runner_sha256"]!=b.digest(cc.__file__) or cross["full_overlap_sha256"]!=b.digest(a.overlap):raise ValueError("Earlier receipt drift")
    if di["runner_sha256"]!=b.digest(diag.__file__) or di["prior_overlap_sha256"]!=b.digest(a.overlap) or di["prior_cross_coding_sha256"]!=b.digest(a.cross_coding):raise ValueError("Diagnostic receipt drift")
    inv=json.loads(a.inventory.read_text());ref=next(q["chart_midpoint"] for q in inv["comparison_units"] if q["private_id"]=="REFERENCE")
    at=g.timestamp(ref["utc"]);rows=b.load_mapping(a.mapping_library)
    ev=[json.loads(p.read_text()) for p in a.hd_evidence]
    for i,e in enumerate(ev):
        if e["inventory_sha256"]!=b.digest(a.inventory) or ov["profiles"][i]["HD_evidence_sha256"]!=b.digest(a.hd_evidence[i]):raise ValueError("Old evidence drift")
    old=[e["hd"] for e in ev]
    packet=json.loads(a.packet.read_text());bank=json.loads(a.question_bank.read_text())
    ids=s.packet_questions(packet,bank,b.digest(a.question_bank),rows,old)
    raw=json.loads(a.raw.read_text());adj=json.loads(a.adjudication.read_text())
    if raw["prior_packet_sha256"]!=b.digest(a.packet) or raw["source_question_bank_sha256"]!=b.digest(a.question_bank) or adj["raw_sha256"]!=b.digest(a.raw) or adj["original_packet_sha256"]!=b.digest(a.packet):raise ValueError("Contextual evidence binding drift")
    if [q["qualified_id"] for q in raw["responses"]]!=["question_bank_v1::"+i for i in ids] or set(q["qualified_id"] for q in adj["items"])!={q["qualified_id"] for q in raw["responses"]}:raise ValueError("Response coverage drift")
    # This separate semantic sensitivity is selected by a human evidence
    # adjudication, not by the score. Do not auto-code free text.
    tokens=adj["admission_policy"]["new_contextual_tokens"]
    if set(tokens)-set(ids):raise ValueError("Contextual token outside original question packet")
    encoded=s.coder.code(rows,tokens)
    extra={k:v["observation"] for k,v in encoded.items() if v["observation"] is not None}
    if not extra or set(extra)&{k for o in old for k,v in o.items() if v is not None}:raise ValueError("No new admitted observation or frozen overwrite")
    new=[{**old[0],**extra},old[1]]
    active,state_sigs,ri,n_struct=s.load_signatures(a.hd_cache,rows,ref["HD"],at)
    rivals=cross["strict_survivor_indices"][s.CORE]
    weights,rweights,unknown=s.grid_weights(a,W,WM,A,AM,H,state_sigs,len(active),rivals)
    ds=[compare_scores(active,ri,rows,o,n,weights) for o,n in zip(old,new,strict=True)]
    old_ok=(ds[0][0]>=0)&(ds[1][0]>=0)
    new_ok=(ds[0][1]>=0)&(ds[1][1]>=0)
    if int(weights[old_ok].sum())!=cross["HD_eligible_both_codings"]:raise ValueError("Previous eligibility replay failed")
    for i,(_,_,d) in enumerate(ds):
        prev=ov["profiles"][i]["counts"]["coverage"]
        if d["old_ranks"]!={"higher":prev["HD_strictly_higher"],"tied":prev["HD_tied"],"lower":prev["HD_lower"]}:raise ValueError("Old rank replay failed")
    # If eligibility expands, the prior survivor set is insufficient.
    # Never pretend this subset method solves that broader comparison.
    if np.any(new_ok&~old_ok&(weights>0)):raise ValueError("Eligibility expanded; full non-HD rescan required")
    sets={**cross["strict_survivor_indices"],"universal_all_included":di["weak_all_included_indices"]}
    survivors=filter_sets(a,H,state_sigs,new_ok,sets)
    if len(survivors[s.CORE])!=int(rweights[new_ok].sum()):raise ValueError("Rival identity/count mismatch")
    out={"status":"EXECUTED_CONTEXT_QUALIFIED_HD_SENSITIVITY_NOT_UNCONDITIONAL_OBSERVATION_OR_VALIDATION",
         "grid_rows":g.N,"ranked_rows":int(weights.sum()),"unknown_HD":unknown,"new_predicate_count":len(extra),
         "profiles":[z[2] for z in ds],"old_both_eligible":int(weights[old_ok].sum()),"new_both_eligible":int(weights[new_ok].sum()),
         "strictly_higher_HD_both":int(weights[(ds[0][1]>0)&(ds[1][1]>0)].sum()),
         "new_survivor_indices":survivors,"new_survivor_counts":{k:len(v) for k,v in survivors.items()},
         "old_survivor_counts":{k:len(v) for k,v in sets.items()},
         "exact_reduction":"verified new both-coding HD-no-lower set is subset of old; all non-HD score variants unchanged",
         "raw_sha256":b.digest(a.raw),"adjudication_sha256":b.digest(a.adjudication),"runner_sha256":b.digest(__file__),
         "prior_overlap_sha256":b.digest(a.overlap),"prior_cross_coding_sha256":b.digest(a.cross_coding),"prior_diagnostic_sha256":b.digest(a.diagnostic)}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("Context-qualified full-grid HD and exact prior survivor filtering complete.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","mapping-library","inventory","packet","question-bank","raw","adjudication","overlap","cross-coding","diagnostic","output"):
        p.add_argument("--"+k,type=Path,required=True)
    p.add_argument("--hd-evidence",action="append",type=Path,required=True)
    run(p.parse_args())
if __name__=="__main__":main()
