#!/usr/bin/env python3
"""Check that every prior accepted/unresolved Human Design mapping is preserved.

This does NOT certify a chart-to-behavior prediction, promote unresolved claims,
or modify any frozen ranking. It enforces evidence and source continuity before
a new Western+HD combined source-scoring version is authored.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def digest(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def audit(repo_root:Path,ledger:dict)->dict:
    if ledger.get("schema")!="astrohd-prior-HD-mapping-reuse-ledger-v1":
        raise ValueError("Unexpected mapping-source reuse ledger")
    srcdata={}
    for input in ledger["source_reference"]:
        p=repo_root/input["path"]
        if not p.is_file() or digest(p.read_bytes())!=input["digest"]:
            raise RuntimeError("Source HD mapping changed or missing: "+input["path"])
        srcdata[input["id"]]=json.loads(p.read_bytes())
    if set(srcdata)!={"v1","v43_aug","v2_candidates"}:raise RuntimeError("Required earlier source model missing")
    actual={
       "v1":{x["mapping_id"]:x for x in srcdata["v1"]["mappings"]},
       "v43_aug":{x["id"]:x for x in srcdata["v43_aug"]["mappings"]},
       "v2_candidates":{x["candidate_id"]:x for x in srcdata["v2_candidates"]["candidates"]}
    }
    keys={f"{source}:{item_id}" for source,items in actual.items() for item_id in items}
    seen=set()
    counts={}
    for item in ledger["entries"]:
        key=item["key"]
        if key in seen:raise RuntimeError("Duplicate prior mapping key "+key)
        seen.add(key)
        src,ident=key.split(":",1)
        if src not in actual or ident not in actual[src]:
            raise RuntimeError("Ledger contains unrecognized or deleted historical mapping "+key)
        reference=actual[src][ident]
        expected_status=reference.get("status") if src=="v1" else reference.get("confirmatory_status","candidate_only") if src=="v2_candidates" else "historical_frozen_target_specific"
        if item["source_status"]!=expected_status:
            raise RuntimeError("Historical source status was changed for "+key)
        if item.get("accepted_into_new_model") is not False:
            raise RuntimeError("Source-only inventory improperly promoted a historical mapping "+key)
        if item.get("review_required") is not True:
            raise RuntimeError("Unreviewed historical mapping "+key)
        counts[src]=counts.get(src,0)+1
    if keys!=seen:
        raise RuntimeError(f"Historical HD mapping coverage incomplete; missing={len(keys-seen)}, extraneous={len(seen-keys)}")
    if len(srcdata["v43_aug"]["contradictions"])!=ledger["counts"]["v43_aug_contradictions"]:
        raise RuntimeError("Historical contradiction inventory changed")
    if len(keys)!=ledger["counts"]["total"]:raise RuntimeError("Mapping tally changed")
    return {"status":"PASS_PRIOR_HD_MAPPING_PRESERVATION","all_entries_accounted_for":len(seen),
      "source_counts":counts,"no_automatic_source_promotion":True,
      "existing_ranks_unchanged":True,
      "new_complete_behavioral_model":"NOT_YET_BUILT",
      "can_use_new_rules_to_claim_blind_owner_validation":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--ledger",type=Path,required=True)
    args=p.parse_args()
    result=audit(args.repo_root,json.loads(args.ledger.read_bytes()))
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":main()
