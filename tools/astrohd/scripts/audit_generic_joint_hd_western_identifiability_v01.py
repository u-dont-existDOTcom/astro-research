#!/usr/bin/env python3
"""Non-bespoke combined identifiability: pre-existing frozen 27 HD predicates
PLUS Ptolemy's two primary Mercury/Moon sign labels.

A uniqueness ceiling is not a personality score. This census is exhaustive
ONLY on the verified 3.5M quarter-hour grid (HD boundary-near -1 rows stay
unresolved) and only for these 29 coarse predefined chart predicates.
It uses no participant answer, no chart-directed weighting, no full Western
governor/sect/house methods and no updated HD Gate/Channel interpretations.
All personal birth/chart details and results remain in owner-private files.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_generic_frozen_hd_identifiability_v01 import (
    frozen_predicates,signature,RANK_SHA,EXPECTED_HD_STATES
)
from audit_ptolemy_sign_pair_grid_identifiability_v01 import (
    source_pair,count_pairs,WITNESS_SHA,MANIFEST_SHA as WEST_MANIFEST_SHA
)
from replay_historical_v36_hd_on_verified_cache import (
    source_states,find_state,utc,CENTURY_MANIFEST_SHA
)
from verify_western_hd_join_index import audit_join

JOIN_SHA="b4426125ea94165ad198f6864f8a690b415f77de68560ea6b8a2435bd417ff85"
GENERIC_CENSUS_SHA="3f084f52eda5fe5c09478664ebe7e3c2797e2a62d3ef497807d92f4724a13ec0"

def sha(path:Path)->str:return sha256(path.read_bytes()).hexdigest()

def compare_west_hd(hdids:np.ndarray,western:np.ndarray,
                    matched_state_mask:np.ndarray,reference_pair:int)->tuple[int,int,set[int]]:
    if len(hdids)!=len(western):raise ValueError("Need corresponding joined records")
    if western.shape[1]!=8:raise ValueError("Unexpected Western source width")
    good=hdids>=0
    if np.any(hdids[good]>=len(matched_state_mask)):
        raise ValueError("HD index out of range")
    pair_matches=((np.floor(western[:,1]/30).astype(np.int16)*12 +
                  np.floor(western[:,2]/30).astype(np.int16))==reference_pair)
    candidate=good & pair_matches
    joint=candidate & matched_state_mask[np.maximum(hdids,0)]
    return int(joint.sum()),int((~good).sum()),{int(x) for x in hdids[joint]}

def run(args:argparse.Namespace)->dict:
    if args.output.exists():raise FileExistsError("Private census immutable")
    for p,expected,label in [
        (args.private_rank,RANK_SHA,"owner reference"),(args.witness,WITNESS_SHA,"Western witness"),
        (args.hd_cache/"manifest.json",CENTURY_MANIFEST_SHA,"HD source cache"),
        (args.western_grid/"verified_manifest.json",WEST_MANIFEST_SHA,"Western source grid"),
        (args.join/"manifest.json",JOIN_SHA,"verified join"),
        (args.old_generic_census,GENERIC_CENSUS_SHA,"old generic census")]:
        if sha(p)!=expected:raise RuntimeError(label+" SHA mismatch")
    independent=audit_join(args.western_grid,args.hd_cache,args.join)
    if independent["sample_count"]!=3506400 or independent["HD_structural_intervals"]!=EXPECTED_HD_STATES:
        raise RuntimeError("Unexpected declared coverage")
    predicates=frozen_predicates(args.generic_map)
    states,_=source_states(args.hd_cache)
    ref=json.loads(args.private_rank.read_bytes())
    refidx=find_state(states,utc(ref["comparison_charts"][0]["exact_utc"]))
    same_sig=signature(states[refidx],predicates)
    mask=np.fromiter((signature(s,predicates)==same_sig for s in states),
                     dtype=np.bool_,count=len(states))
    old=json.loads(args.old_generic_census.read_bytes())
    if int(mask.sum())!=old["result"]["number_of_intervals_with_same_generic_signature_as_reference"]:
        raise RuntimeError("Old 27-rule equivalence census not reproduced")
    ref_pair=source_pair(json.loads(args.witness.read_bytes()))
    west=json.loads((args.western_grid/"verified_manifest.json").read_bytes())
    join=json.loads((args.join/"manifest.json").read_bytes())
    if len(west["chunks"])!=len(join["shards"]):
        raise RuntimeError("Unmatched source shard count")
    matching=unresolved=0
    distinct_states=set()
    for w,j in zip(west["chunks"],join["shards"],strict=True):
        if j["index_first"]!=w["first_index"] or j["count"]!=w["count"]:
            raise RuntimeError("Join shard has incorrect date/index alignment")
        h=np.memmap(args.join/"shards"/j["file"],dtype="<i4",
                    mode="r",shape=(j["count"],))
        a=np.memmap(args.western_grid/"chunks"/w["file"],dtype="<f8",
                    mode="r",shape=(w["count"],8))
        add,n_unresolved,ids=compare_west_hd(h,a,mask,ref_pair)
        matching+=add;unresolved+=n_unresolved;distinct_states.update(ids)
    if unresolved!=join["unresolved_near_boundary_samples"]:
        raise RuntimeError("Join near-boundary count drift")
    result={
        "schema":"source_neutral_generic_27hd_plus_ptolemy_2western_15min_grid_census_v01",
        "status":"COARSE_NON_BESPOKE_IDENTIFIABILITY_NOT_PERSONALITY_RANKING",
        "chart_fingerprint":"27 frozen generic HD source mapping predicates + Mercury sign + Moon sign",
        "same_private_recorded_chart_fingerprint_joint_sample_count":matching,
        "unique_hd_intervals_represented_in_joint_matches":len(distinct_states),
        "exact_old_27_hd_mapping_only_match_interval_count":int(mask.sum()),
        "total_grid_samples":independent["sample_count"],
        "unresolved_near_hd_boundaries":unresolved,
        "can_identify_unique_chart_with_only_this_fingerprint":matching==1,
        "no_bespoke_chart_weights_or_behavior_labels_used":True,
        "no_full_hd_v43_behavior_scoring":True,
        "no_complete_ptolemy_lilly_soul_rulership":True,
        "no_personality_probability_or_proved_first_place":True,
        "continuous_time_coverage":False,
        "source_sha256":{
           "HD_source_manifest":sha(args.hd_cache/"manifest.json"),
           "Western_source_manifest":sha(args.western_grid/"verified_manifest.json"),
           "joined_source_manifest":sha(args.join/"manifest.json"),
           "generic_mapping":sha(args.generic_map),
           "private_reference":sha(args.private_rank),
        }
    }
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return {k:v for k,v in result.items() if k!="source_sha256"}

def main():
    p=argparse.ArgumentParser()
    for name in ("private_rank","witness","hd_cache","western_grid","join",
                 "generic_map","old_generic_census","output"):
        p.add_argument("--"+name.replace("_","-"),required=True,type=Path)
    print(json.dumps(run(p.parse_args()),sort_keys=True))
if __name__=="__main__":main()
