#!/usr/bin/env python3
"""Independent fail-closed audit of Western 15m -> HD structural-state join.

Validates source manifests and ALL source/join shard SHA-256 checksums and
numeric ID coverage. This audits a finite sampled grid, not the continuous
birth-time universe or behavioral validity. Do not mistake an ID for a
human personality result.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

def digest(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def audit_join(west:Path,hd:Path,joined:Path)->dict:
    out=json.loads((joined/"manifest.json").read_bytes())
    w=json.loads((west/"verified_manifest.json").read_bytes())
    h=json.loads((hd/"manifest.json").read_bytes())
    if out["schema"]!="western-grid-to-HD-structural-exact-interval-index-v1":
        raise ValueError("Invalid join schema")
    if out["west_verified_manifest_sha256"]!=digest(west/"verified_manifest.json"):
        raise ValueError("Western manifest fingerprint mismatch")
    if out["hd_verified_manifest_sha256"]!=digest(hd/"manifest.json"):
        raise ValueError("HD manifest fingerprint mismatch")
    if out["total_utc_grid_samples"]!=w["total_samples"]:
        raise ValueError("Total indexed samples inconsistent with Western source")
    if out["total_hd_structural_intervals"]!=h["interval_count"]:
        raise ValueError("HD interval count mismatch")
    if out["utc_start"]!=w["first_utc"] or out["utc_end_exclusive"]!=w["end_exclusive_utc"]:
        raise ValueError("Western time window not covered")
    if out["utc_start"].replace("+00:00","Z")!=h["utc_start"] or out["utc_end_exclusive"].replace("+00:00","Z")!=h["utc_end_exclusive"]:
        raise ValueError("HD timeline not aligned with Western index")
    if len(out["shards"])!=len(w["chunks"]):
        raise ValueError("Expected one HD index shard per Western source shard")
    count=0;unresolved=0
    for position,(hdsh,wsh) in enumerate(zip(out["shards"],w["chunks"],strict=True)):
        if hdsh["index_first"]!=count or wsh["first_index"]!=count:
            raise ValueError("Missing or overlapping sample window")
        if hdsh["count"]!=wsh["count"]:
            raise ValueError("Wrong per-shard sample count")
        fp=joined/"shards"/hdsh["file"]
        if fp.stat().st_size!=4*hdsh["count"]:
            raise ValueError("Invalid HD index bytes")
        if digest(fp)!=hdsh["sha256"]:
            raise ValueError("HD join shard has changed")
        # Verify the original Western astronomy shard has not changed.
        western_path=west/"chunks"/wsh["file"]
        if digest(western_path)!=wsh["sha256"]:
            raise ValueError("Western astronomy source shard has changed")
        ids=np.memmap(fp,dtype="<i4",mode="r",shape=(hdsh["count"],))
        if np.any(ids < -1) or np.any(ids>=h["interval_count"]):
            raise ValueError("Out-of-range HD state index")
        missing=int((ids==-1).sum())
        if hdsh["unresolved_boundary_count"]!=missing:
            raise ValueError("Wrong per-shard boundary uncertainty count")
        if int(ids[0])!=hdsh["first_hd_state_index"] or int(ids[-1])!=hdsh["last_hd_state_index"]:
            raise ValueError("HD state boundary records changed")
        unresolved+=missing
        count+=hdsh["count"]
    for item in h["shards"]:
        if digest(hd/item["filename"])!=item["sha256"]:
            raise ValueError("HD structural source shard has changed")
    if count!=out["total_utc_grid_samples"]:
        raise ValueError("Missing expected sample rows")
    if unresolved!=out["unresolved_near_boundary_samples"]:
        raise ValueError("Aggregated boundary uncertainty count mismatch")
    return {
        "status":"PASS_JOINED_SOURCE_NEUTRAL_GRID_SHARD_AUDIT",
        "sample_count":count,
        "HD_structural_intervals":h["interval_count"],
        "HD_index_shards":len(out["shards"]),
        "unresolved_HD_transition_near_samples":unresolved,
        "combined_join_manifest_sha256":digest(joined/"manifest.json"),
        "western_cache_manifest_sha256":out["west_verified_manifest_sha256"],
        "HD_cache_manifest_sha256":out["hd_verified_manifest_sha256"],
        "scope":"VERIFIED DECLARED FINITE UTC GRID ONLY",
        "continuous_instants_covered":False,
        "validated_personality_match":False,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--western-index",type=Path,required=True)
    ap.add_argument("--hd-cache",type=Path,required=True)
    ap.add_argument("--join",type=Path,required=True)
    args=ap.parse_args()
    print(json.dumps(audit_join(args.western_index,args.hd_cache,args.join),sort_keys=True))

if __name__=="__main__":main()
