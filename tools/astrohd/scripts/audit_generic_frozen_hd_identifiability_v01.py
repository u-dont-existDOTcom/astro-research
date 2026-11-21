#!/usr/bin/env python3
"""Non-bespoke HD identifiability census using all 27 PREEXISTING frozen generic mappings.

This does NOT claim behavioral prediction. It asks the sharper structural
question: could *any* scoring function whose inputs consist SOLELY of the 27
generic V1 frozen chart-feature predicates distinguish the recorded chart
from ALL others in a certified century HD structural-state universe?

If a second source state has the same 27-bit truth vector, no rule limited
to those predicates can yield a unique chart-to-observables #1 for the
recorded chart. Calendar duration or arbitrary tie breaking is NOT
behavioral identification. A future richer generic model may distinguish.
All true-owner data and census outputs stay in PRIVATE input/output files.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from replay_historical_v36_hd_on_verified_cache import (
    source_states,find_state,utc,CENTURY_MANIFEST_SHA
)
MAP_SHA="3424672432f7f071ec90ef9ddce52a67ff6794911e92b1a1e04f079262ea6200"
RANK_SHA="b930e87a366a7d06d0efe40c9ec83044be62116935ec1a986b06c3868fcf9bce"
ALLOWED_FEATURES={"type","authority","profile","defined_centers"}
ALLOWED_OPERATORS={"equals_any","contains_any","not_contains_any","profile_has_line"}
EXPECTED_FROZEN=27
EXPECTED_HD_STATES=288908
EXPECTED_PRIVATE_RANK="EXPLORATORY_V37_CORRECTED_OBSERVABLES_REUSE_OF_V36_HD_PATHWAYS"

def sha(path:Path)->str:return sha256(path.read_bytes()).hexdigest()

def frozen_predicates(mapping_path:Path)->list[tuple[str,dict]]:
    if sha(mapping_path)!=MAP_SHA:
        raise RuntimeError("Generic source mapping changed; no longer non-bespoke baseline")
    obj=json.loads(mapping_path.read_bytes())
    if obj.get("model_version")!="V4/V3.2-symbolic-v1":
        raise RuntimeError("Wrong generic mapping version")
    arr=[]
    for x in obj["mappings"]:
        if x["status"]!="frozen":continue
        rule=x["chart_feature_predicate"]
        if rule["feature"] not in ALLOWED_FEATURES or rule["operator"] not in ALLOWED_OPERATORS:
            raise RuntimeError("Unexpected generic frozen feature or operator")
        if not rule.get("values"):
            raise RuntimeError("Empty frozen generic rule values")
        arr.append((x["mapping_id"],rule))
    if len(arr)!=EXPECTED_FROZEN or len({x[0] for x in arr})!=len(arr):
        raise RuntimeError("Frozen generic mappings count or uniqueness changed")
    return arr

def normalize(x:str)->str:
    return "".join(c for c in x.lower() if c.isalnum())

def truth(state:dict, rule:dict)->bool:
    feature=rule["feature"];operator=rule["operator"]
    if feature not in ALLOWED_FEATURES or operator not in ALLOWED_OPERATORS:
        raise ValueError("Unsupported generic map predicate")
    values={normalize(str(v)) for v in rule["values"]}
    if operator=="profile_has_line":
        if feature!="profile":raise ValueError("Line operator only on profile")
        return bool({str(state["pl"]),str(state["dl"])}&set(map(str,rule["values"])))
    if operator=="equals_any":
        if feature=="type":value=normalize(state["type"])
        elif feature=="authority":value=normalize(state["auth"])
        else:raise ValueError("Equals only for type/authority")
        aliases={"emotionalsolarplexus":"emotional","solarplexus":"emotional",
                 "heart":"ego","heartego":"ego"}
        return aliases.get(value,value) in {aliases.get(v,v) for v in values}
    if feature!="defined_centers":raise ValueError("Contains only for centers")
    canonical={
       "ego":"heart","heartego":"heart","will":"heart","identity":"g",
       "solarplexus":"solarplexus",
    }
    present={canonical.get(normalize(v),normalize(v)) for v in state["centers"]}
    want={canonical.get(v,v) for v in values}
    contains=bool(present&want)
    return contains if operator=="contains_any" else not contains

def signature(state:dict,predicates:list[tuple[str,dict]])->int:
    result=0
    for i,(_,p) in enumerate(predicates):
        if truth(state,p):result |= (1<<i)
    return result

def census(states:list[dict],reference_index:int,predicates:list[tuple[str,dict]])->dict:
    if not 0<=reference_index<len(states):
        raise ValueError("Source reference index out of bounds")
    ref_sig=signature(states[reference_index],predicates)
    matching_count=0
    match_duration_days=0.
    all_sig={}
    for s in states:
        sig=signature(s,predicates)
        all_sig[sig]=all_sig.get(sig,0)+1
        if sig==ref_sig:
            matching_count+=1
            match_duration_days+=s["dur"]
    if matching_count!=all_sig[ref_sig]:raise AssertionError("Inconsistent group count")
    if matching_count<1:raise AssertionError("Reference absent from its own class")
    if matching_count==1:unique=True
    else:unique=False
    return {
        "total_hd_source_intervals":len(states),
        "frozen_generic_predicate_count":len(predicates),
        "distinct_27bit_chart_feature_signatures":len(all_sig),
        "number_of_intervals_with_same_generic_signature_as_reference":matching_count,
        "total_days_same_signature_as_reference":round(match_duration_days,6),
        "reference_signature_is_unique_within_this_feature_model":unique,
        "unique_rank_one_identifiability_for_any_score_based_only_on_27_frozen_predicates":unique,
        "principled_conclusion":(
           "Unique #1 is not ruled out by signature ties, but has NOT been demonstrated."
           if unique else
           "Cannot be uniquely #1 under any source-scoring function using ONLY the same 27 generic frozen chart-feature predicates; equivalent states share all observable predictions."
        ),
        "no_human_match_proven":True,
        "no_scoring_weights_or_questionnaire_answers_used":True,
    }

def run(args:argparse.Namespace)->dict:
    if args.output.exists():raise FileExistsError("Private immutable output exists")
    frozen=frozen_predicates(args.generic_map)
    if sha(args.private_rank)!=RANK_SHA:raise RuntimeError("Recorded source reference changed")
    private=json.loads(args.private_rank.read_bytes())
    if private["status"]!=EXPECTED_PRIVATE_RANK:raise RuntimeError("Wrong owner baseline")
    ref_utc=utc(private["comparison_charts"][0]["exact_utc"])
    states,m=source_states(args.hd_cache)
    if len(states)!=EXPECTED_HD_STATES or sha(args.hd_cache/"manifest.json")!=CENTURY_MANIFEST_SHA:
        raise RuntimeError("Wrong certified structural-state universe")
    idx=find_state(states,ref_utc)
    score=census(states,idx,frozen)
    record={
        "schema":"generic_frozen_hd_27_mapping_identifiability_census_v01",
        "status":"NON_BESPOKE_GENERIC_SOURCE_ONLY_NOT_BEHAVIORAL_VALIDATION",
        "preexisting_map_sha256":sha(args.generic_map),
        "reference_private_birth_source_sha256":sha(args.private_rank),
        "hd_cache_manifest_sha256":sha(args.hd_cache/"manifest.json"),
        "exact_recorded_utc_kept_private":True,
        "preexisting_27_frozen_rule_ids":[x[0] for x in frozen],
        "reference_signature_bitstring":format(signature(states[idx],frozen),f"0{len(frozen)}b"),
        "result":score,
        "boundary":"Does not evaluate any other non-bespoke model using different features (e.g. channels, gates, Western); source mapping uses no calibrated P(answer|chart).",
    }
    data=json.dumps(record,sort_keys=True,indent=2)+"\n"
    args.output.write_text(data)
    return {"status":record["status"],"private_output_sha256":sha(args.output),**score}

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--generic-map",type=Path,required=True)
    p.add_argument("--private-rank",type=Path,required=True)
    p.add_argument("--hd-cache",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    print(json.dumps(run(p.parse_args()),sort_keys=True))
if __name__=="__main__":main()
