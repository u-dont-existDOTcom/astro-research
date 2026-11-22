#!/usr/bin/env python3
"""Measure how many distinct Western rising signs occur in each *HD* state.

Source-neutral astronomy. Read exact structural HD IDs mapped to a finite,
fixed-location Western 15-minute sample grid and ASC values from a previously
verified location-cusp grid, checking SHA256 file identities per shard. This is
NOT a personality score, probability of human chart correctness, or continuous
ecliptic-ASC count within an HD interval.

A state can traverse a zodiac sign boundary entirely between samples: the
number of *observed* rising signs is only a lower bound on continuous coverage.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

HD_SCHEMA="western-grid-to-HD-structural-exact-interval-index-v1"
ANGLE_SCHEMA="location-conditioned-western-angles-utc-grid-v1-NONCANONICAL"


def sha(path:Path)->str:
    h=sha256()
    with path.open("rb") as stream:
        for part in iter(lambda:stream.read(1<<20),b""):
            h.update(part)
    return h.hexdigest()


def validate(join:dict,angle:dict)->tuple[int,int]:
    if join.get("schema")!=HD_SCHEMA or angle.get("schema")!=ANGLE_SCHEMA:
        raise ValueError("Source schemas not recognized")
    n=join.get("total_utc_grid_samples")
    states=join.get("total_hd_structural_intervals")
    if not isinstance(n,int) or n<=0 or n!=angle.get("total_samples"):
        raise ValueError("Misaligned time population")
    if not isinstance(states,int) or states<=0:
        raise ValueError("Missing HD structural state population")
    if join.get("step_minutes")!=15:
        raise ValueError("Expected fixed 15-minute sample lattice")
    js=join.get("shards",[])
    ag=angle.get("shards",[])
    if not js or len(js)!=len(ag):
        raise ValueError("Missing or conflicting shard inventory")
    start=0
    for a,b in zip(js,ag):
        if a.get("index_first")!=start or b.get("first_index")!=start:
            raise ValueError("Noncontiguous shard index")
        if a.get("count")!=b.get("count"):
            raise ValueError("Shard sample counts differ")
        start+=a["count"]
    if start!=n:raise ValueError("Incomplete declared grid")
    return n,states


def classify_ids_and_rising(ids:np.ndarray, asc_degrees:np.ndarray, state_count:int):
    ids=np.asarray(ids)
    asc=np.asarray(asc_degrees)
    if ids.ndim!=1 or asc.ndim!=1 or len(ids)!=len(asc):
        raise ValueError("Shape mismatch")
    if np.any((ids < -1)|(ids>=state_count)):
        raise ValueError("HD state index outside declared cache")
    if np.any(~np.isfinite(asc)) or np.any((asc<0)|(asc>=360)):
        raise ValueError("Invalid ASC")
    valid=ids>=0
    return ids[valid].astype(np.int32),np.floor(asc[valid]/30).astype(np.int8),int((~valid).sum())


def survey(join_root:Path,angles_root:Path,verify_shards=True)->dict:
    joinpath=join_root/"manifest.json"
    anglespath=angles_root/"verified_manifest.json"
    join=json.loads(joinpath.read_bytes())
    angles=json.loads(anglespath.read_bytes())
    n,state_count=validate(join,angles)
    masks=np.zeros(state_count,dtype=np.uint16)
    sample_weight=np.zeros(state_count,dtype=np.int32)
    unresolved=0
    for jd,ad in zip(join["shards"],angles["shards"]):
        ids_path=join_root/"shards"/jd["file"]
        asc_path=angles_root/"shards"/ad["file"]
        count=jd["count"]
        if ids_path.stat().st_size!=4*count or asc_path.stat().st_size!=17*8*count:
            raise RuntimeError("Source shard bytes/row size mismatch")
        if verify_shards and (sha(ids_path)!=jd["sha256"] or sha(asc_path)!=ad["sha256"]):
            raise RuntimeError("HD+Western source SHA-256 mismatch")
        ids=np.memmap(ids_path,mode="r",dtype="<i4",shape=(count,))
        asc=np.memmap(asc_path,mode="r",dtype="<f8",shape=(count,17))[:,0]
        h,s,unknown=classify_ids_and_rising(ids,asc,state_count)
        unresolved+=unknown
        np.bitwise_or.at(masks,h,(np.uint16(1)<<s.astype(np.uint16)))
        sample_weight+=np.bincount(h,minlength=state_count).astype(np.int32)
    if unresolved!=join.get("unresolved_near_boundary_samples"):
        raise RuntimeError("Unresolved HD source boundary count drift")
    if int(sample_weight.sum())+unresolved!=n:
        raise RuntimeError("Not all samples accounted")
    distinct=np.fromiter((int(x).bit_count() for x in masks),dtype=np.int8,count=state_count)
    bins=Counter(int(x) for x in distinct)
    # This is an HD-state count, not a time-weighted prevalence or a human prior.
    state_multi=int((distinct>1).sum())
    sample_multi=int(sample_weight[distinct>1].sum())
    present=int((distinct>0).sum())
    return {
        "schema":"hd_state_vs_western_asc_sign_source_neutral_census_v01",
        "status":"COMPLETE_FINITE_GRID_STRUCTURAL_NONREDUNDANCY_NOT_PREDICTIVE",
        "horizon_utc":[join["utc_start"],join["utc_end_exclusive"]],
        "grid_interval_minutes":15,
        "source_location_policy":"one_declared_fixed_location; no participant identifier",
        "source_manifest_sha256":{"hd_join":sha(joinpath),"western_angles":sha(anglespath)},
        "each_binary_shard_sha256_reverified":verify_shards,
        "grid_samples_declared":n,
        "near_HD_transition_unknown_samples":unresolved,
        "total_exact_HD_structural_states":state_count,
        "states_with_at_least_one_grid_sample":present,
        "states_with_no_grid_sample":bins.get(0,0),
        "HD_state_observed_distinct_rising_sign_histogram":dict(sorted(bins.items())),
        "states_with_at_least_two_observed_western_rising_signs":state_multi,
        "fraction_of_all_states_with_multi_sign_observed":state_multi/state_count,
        "non_boundary_grid_samples_in_states_with_multi_sign_observed":sample_multi,
        "fraction_of_resolved_time_grid_samples_with_multi_sign_state":sample_multi/(n-unresolved),
        "no_personality_behavior_scores":True,
        "no_independent_human_validation":True,
        "not_a_continuous_time_ASC_boundary_census":True,
        "note":"Observed rising signs form a finite-lattice lower bound; absence of two sampled signs does not prove an HD state contains just one continuous rising sign. Time-weighted and HD-state-counted proportions are different denominators."
    }


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--join",required=True,type=Path)
    a.add_argument("--angles",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    a.add_argument("--skip-shard-hashes",action="store_true")
    opt=a.parse_args()
    if opt.out.exists():raise FileExistsError("Never overwrite the private source-bound census receipt")
    result=survey(opt.join,opt.angles,verify_shards=not opt.skip_shard_hashes)
    opt.out.parent.mkdir(parents=True,exist_ok=True)
    opt.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("HD_ASC_CROSS_SYSTEM_CENSUS",json.dumps({k:result[k] for k in ("grid_samples_declared","total_exact_HD_structural_states","near_HD_transition_unknown_samples","states_with_at_least_two_observed_western_rising_signs","fraction_of_resolved_time_grid_samples_with_multi_sign_state","HD_state_observed_distinct_rising_sign_histogram")},sort_keys=True))
if __name__=="__main__":main()
