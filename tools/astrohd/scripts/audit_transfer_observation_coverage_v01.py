#!/usr/bin/env python3
"""Compare evidence coverage, not natal charts or model scores.

Preserve nulls, compare identical version-bound keys, expose source and
admission differences, and produce candidate-neutral clarification targets.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import compare_bounded_behavior_v01 as b
import compare_hd_archetype_century_v01 as h
import compare_hd_specific_observables_v01 as q
import code_frozen_hd_observations_v01 as coder

FAMILIES=("hd","western","shared","specific")

def compare_items(first,second,keys):
    keys=set(keys)
    b.checked_obs(first,keys)
    b.checked_obs(second,keys)
    a={k for k,v in first.items() if v is not None}
    c={k for k,v in second.items() if v is not None}
    common=a&c
    return {"items":len(keys),"development_observed":len(a),
            "transfer_observed":len(c),"common_observed":len(common),
            "development_only":sorted(a-c),"transfer_only":sorted(c-a),
            "both_unobserved":sorted(keys-(a|c)),
            "common_items":sorted(common),
            "opposite_sign_common_items":sorted(k for k in common if first[k]!=second[k])}

def audit(first,second,registry):
    if set(first)!=set(FAMILIES) or set(second)!=set(FAMILIES) or set(registry)!=set(FAMILIES):
        raise ValueError("Incomplete observation family registry")
    return {k:compare_items(first[k],second[k],registry[k]) for k in FAMILIES}

def run(a):
    paths=[a.mapping_library,a.context_adjudication,a.specific_evidence,
           a.transfer_evidence,a.output,*a.owner_hd,*a.owner_shared]
    if any(x.resolve().is_relative_to(b.ROOT) for x in paths) or a.output.exists():
        raise ValueError("External immutable private evidence paths required")
    if len(a.owner_hd)!=2 or len(a.owner_shared)!=2:
        raise ValueError("Both original evidence codings required")
    rows=b.load_mapping(a.mapping_library)
    _,groups,shared=h.load_map()
    _,_,keys,domains=q.load_map(groups)
    registry={"hd":{r["mapping_id"] for r in rows},"western":b.WEST_KEYS,
              "shared":set().union(*(set(v) for v in shared["domains"].values())),
              "specific":set(keys)}
    T=json.loads(a.transfer_evidence.read_text())
    if T["schema"]!="private_fixed_transfer_evidence_v01" or T["source_maps"]!={"generic":b.digest(a.mapping_library),"shared":h.pc.MAP_SHA,"specific":q.MAP_SHA}:
        raise ValueError("Transfer evidence/map identity drift")
    source=Path(T["source_file"])
    if source.resolve().is_relative_to(b.ROOT) or b.digest(source)!=T["source_sha256"]:
        raise ValueError("Transfer interview identity drift")
    if len(T["profiles"])!=2:
        raise ValueError("Transfer evidence profile count")
    specific=q.load_evidence(a.specific_evidence,keys)
    adj=json.loads(a.context_adjudication.read_text())
    extra={k:v["observation"] for k,v in coder.code(rows,adj["admission_policy"]["new_contextual_tokens"]).items() if v["observation"] is not None}
    out={}
    for i,label in enumerate(("broad","narrow")):
        old=json.loads(a.owner_hd[i].read_text())
        sh=json.loads(a.owner_shared[i].read_text())
        if sh["hd_evidence_sha256"]!=b.digest(a.owner_hd[i]) or sh["map_sha256"]!=h.pc.MAP_SHA:
            raise ValueError("Development evidence binding drift")
        hd=dict(old["hd"])
        if i==0:
            if set(extra)&{k for k,v in hd.items() if v is not None}:
                raise ValueError("Prior admission overwrite")
            hd.update(extra)
        owner={"hd":hd,"western":old["western"],"shared":sh["observations"],"specific":specific[i]}
        p=T["profiles"][i]
        if p["label"]!=label or any(set(p[f])!=registry[f] for f in FAMILIES):
            raise ValueError("Transfer coding identity drift")
        for f in FAMILIES:
            for k,v in p[f].items():
                e=T["adjudication"][f].get(k)
                if v is not None and (not e or e[label]!=v or not e["rationale"] or not e["questions"] or any(type(n)!=int or not 1<=n<=T["source_count"] for n in e["questions"])):
                    raise ValueError("Transfer admission lacks a source anchor")
        out[label]=audit(owner,{f:p[f] for f in FAMILIES},registry)
    result={"status":"OBSERVATION_COVERAGE_ONLY_NO_NEW_MODEL_SELECTION",
            "coverage":out,"source_sha256":b.digest(source),
            "transfer_evidence_sha256":b.digest(a.transfer_evidence),
            "owner_hd_sha256":[b.digest(x) for x in a.owner_hd],
            "owner_shared_sha256":[b.digest(x) for x in a.owner_shared],
            "owner_specific_sha256":b.digest(a.specific_evidence),
            "context_adjudication_sha256":b.digest(a.context_adjudication),
            "runner_sha256":b.digest(__file__),
            "interpretation":"Counts of coded slots, not independent psychological traits or a numerical completeness threshold. Unknown is not negative. Do not use any chart or rank to select follow-up questions."}
    os.umask(0o077)
    with a.output.open("x") as f:
        json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("Observation coverage audit complete; no natal or model inputs loaded.")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("mapping-library","context-adjudication","specific-evidence","transfer-evidence","output"):
        p.add_argument("--"+k,type=Path,required=True)
    for k in ("owner-hd","owner-shared"):
        p.add_argument("--"+k,type=Path,action="append",required=True)
    run(p.parse_args())

if __name__=="__main__":main()
