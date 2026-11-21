#!/usr/bin/env python3
"""Join the verified 15-minute Western UTC grid to existing exact HD state cache.

This creates a SOURCE-NEUTRAL per-sample integer lookup into a verified HD
structural-state universe. It does NOT rank people's personalities, compute
houses/sect, store private natal data, or claim sub-grid completeness.

Time-boundary grid samples are assigned -1 (UNRESOLVED) rather than arbitrary
near-root states. The original full HD engine independently checks seeded
sampled states against their cached feature SHA-256.
"""
from __future__ import annotations
import argparse
from datetime import UTC,datetime
from hashlib import sha256
import gzip
import json
import os
from pathlib import Path
import tempfile

import numpy as np

from hdmatch.runtime.century_cache import (
    verify_century_cache,structural_features_sha256
)
from hdmatch.runtime.chart_adapter import ExactChartAdapter
from hdmatch.schemas import StructuralChartFeatures

INDEX_SCHEMA="western-source-neutral-utc-grid-float64-pilot-v1-NONCANONICAL"
REPORT_SCHEMA="western-grid-to-HD-structural-exact-interval-index-v1"
EPOCH=datetime(1970,1,1,tzinfo=UTC)


def sha_file(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def canon(obj)->bytes:
    return (json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()

def utc(value:str)->datetime:
    dt=datetime.fromisoformat(value.replace("Z","+00:00"))
    if dt.tzinfo is None or dt.utcoffset()!=UTC.utcoffset(None):
        raise ValueError("Require explicit UTC timestamp")
    return dt.astimezone(UTC)

def ns(dt:datetime)->int:
    duration=dt-EPOCH
    return (duration.days*86400+duration.seconds)*1_000_000_000 + duration.microseconds*1000

def freeze(path:Path,b:bytes):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,"wb") as f:
        f.write(b);f.flush();os.fsync(f.fileno())

def load_verified_intervals(root:Path,adapter:ExactChartAdapter):
    # The canonical verifier fully parses the entire merged universe and checks
    # every structural row, logical-universe hash and compressed shard hash.
    manifest=verify_century_cache(root,expected_engine_fingerprint=adapter.fingerprint)
    starts=[];ends=[];features=[]
    previous=None
    for shard in manifest.shards:
        with gzip.open(root/shard.filename,"rb") as file:
            for line in file:
                if not line.strip():continue
                row=json.loads(line)
                start=utc(row["start_utc"])
                end=utc(row["end_utc"])
                if end<=start:
                    raise RuntimeError("Nonpositive HD interval")
                if previous is not None and start!=previous:
                    raise RuntimeError("Gap/overlap in HD structural cache")
                starts.append(ns(start));ends.append(ns(end))
                features.append(row["chart_features_hash"])
                previous=end
    if len(starts)!=manifest.interval_count:
        raise RuntimeError("HD interval count mismatch")
    if starts[0]!=ns(manifest.utc_start) or ends[-1]!=ns(manifest.utc_end_exclusive):
        raise RuntimeError("HD source cache horizon mismatch")
    if len(starts)>=2**31:
        raise RuntimeError("HD state count cannot fit int32 index")
    return manifest,np.array(starts,dtype=np.int64),np.array(ends,dtype=np.int64),features

def lookup(samples:np.ndarray,starts:np.ndarray,ends:np.ndarray,margin_ns:int):
    if samples.dtype!=np.dtype(np.int64):
        raise ValueError("Expected nanosecond UTC int64 timestamp array")
    i=np.searchsorted(starts,samples,side="right")-1
    if np.any(i<0) or np.any(i>=len(starts)):
        raise RuntimeError("Uncovered UTC sample")
    if np.any(samples>=ends[i]) or np.any(samples<starts[i]):
        raise RuntimeError("HD structural cache has an uncovered timestamp")
    margin=np.minimum(samples-starts[i],ends[i]-samples)
    unresolved=margin<=margin_ns
    result=i.astype("<i4")
    result[unresolved]=-1
    return result,unresolved

def from_production(chart)->StructuralChartFeatures:
    return StructuralChartFeatures(
        type=chart.type,strategy=chart.strategy,authority=chart.authority,
        profile=chart.profile,definition=chart.definition,
        defined_centers=chart.defined_centers,
        channels=chart.channels,
        activation_gates={k:v.gate for k,v in chart.activations.items()})

def run(args):
    westroot=args.western_index.resolve()
    hdroot=args.hd_cache.resolve()
    if args.output.exists():
        raise FileExistsError("Output must be new, don't overwrite a frozen join")
    if not 0<=args.boundary_margin_seconds<=15:
        raise ValueError("Boundary margin outside allowed range")
    if not 0<=args.independent_parity_samples<=20000:
        raise ValueError("Too many/few independent validation samples")
    wplan=json.loads((westroot/"plan.json").read_bytes())
    wmanifest=json.loads((westroot/"verified_manifest.json").read_bytes())
    if wplan["schema"]!=INDEX_SCHEMA or wmanifest["schema"]!=INDEX_SCHEMA:
        raise ValueError("Western grid source schema mismatch")
    if sha_file(westroot/"plan.json")!=wmanifest["plan_sha256"]:
        raise RuntimeError("Western verified plan hash mismatch")
    if wplan["record_bytes"]!=64:
        raise RuntimeError("Incorrect Western record shape")
    adapter=ExactChartAdapter(args.ephemeris)
    hmanifest,starts,ends,feature_hashes=load_verified_intervals(hdroot,adapter)
    wstart=utc(wplan["utc_start_inclusive"]);wend=utc(wplan["utc_end_exclusive"])
    if ns(wstart)!=starts[0] or ns(wend)!=ends[-1]:
        raise RuntimeError("Western grid and HD structural cache horizons differ")
    step_ns=wplan["step_minutes"]*60*1_000_000_000
    out=args.output
    out.mkdir(parents=True)
    (out/"shards").mkdir()
    margin_ns=int(round(args.boundary_margin_seconds*1e9))
    parts=[];global_idx=0;unresolved_total=0
    for shard in wmanifest["chunks"]:
        if shard["first_index"]!=global_idx:
            raise RuntimeError("Gap in Western time-grid shards")
        filename=westroot/"chunks"/shard["file"]
        if sha_file(filename)!=shard["sha256"]:
            raise RuntimeError("Western source shard hash mismatch")
        n=shard["count"]
        samples=np.int64(ns(wstart))+(
             np.int64(global_idx)+np.arange(n,dtype=np.int64))*np.int64(step_ns)
        ids,unresolved=lookup(samples,starts,ends,margin_ns)
        unresolved_total+=int(unresolved.sum())
        output=out/"shards"/("hd_ids_"+str(len(parts)).zfill(5)+".bin")
        raw=ids.tobytes(order="C")
        freeze(output,raw)
        parts.append({"file":output.name,"index_first":global_idx,
                "count":n,"sha256":sha256(raw).hexdigest(),
                "unresolved_boundary_count":int(unresolved.sum()),
                "first_hd_state_index":int(ids[0]),"last_hd_state_index":int(ids[-1])})
        global_idx+=n
    if global_idx!=wplan["total_samples"]:
        raise RuntimeError("Western sample count mismatch")
    # Recompute pseudorandom, deterministic production charts at 256+ instants.
    rng=np.random.default_rng(20261119)
    sample_index=np.sort(rng.choice(global_idx,size=min(global_idx,args.independent_parity_samples),
                                  replace=False))
    checks=0;unresolved_picks=0
    for idx in sample_index:
        idx=int(idx)
        t=ns(wstart)+idx*step_ns
        ids,unresolved=lookup(np.array([t],dtype=np.int64),starts,ends,margin_ns)
        if unresolved[0]:
            unresolved_picks+=1
            continue
        utc_dt=wstart+__import__("datetime").timedelta(minutes=idx*wplan["step_minutes"])
        expected_hash=feature_hashes[int(ids[0])]
        got=from_production(adapter.calculate(utc_dt))
        if structural_features_sha256(got)!=expected_hash:
            raise RuntimeError("Production structural mismatch at "+utc_dt.isoformat())
        checks+=1
    report={
        "schema":REPORT_SCHEMA,
        "status":"VERIFIED_WESTERN_GRID_TO_EXACT_HD_STRUCTURAL_INTERVAL_JOIN",
        "west_verified_manifest_sha256":sha_file(westroot/"verified_manifest.json"),
        "hd_verified_manifest_sha256":sha_file(hdroot/"manifest.json"),
        "hd_engine_fingerprint":adapter.fingerprint,
        "utc_start":wstart.isoformat(),"utc_end_exclusive":wend.isoformat(),
        "step_minutes":wplan["step_minutes"],
        "total_utc_grid_samples":global_idx,
        "total_hd_structural_intervals":len(starts),
        "unresolved_near_boundary_samples":unresolved_total,
        "boundary_margin_seconds":args.boundary_margin_seconds,
        "interval_index_encoding":"little_endian_signed_int32_per_utc_grid_sample; -1 means unresolved",
        "shards":parts,
        "independent_parity_samples_verified":checks,
        "independent_parity_samples_unresolved":unresolved_picks,
        "full_grid_covered":True,
        "continuous_time_coverage":"NOT_CERTIFIED",
        "all_non_sun_line_activation_coverage":"NOT_INCLUDED",
        "western_houses_sect_or_behavior_model":"NOT_INCLUDED",
        "human_predictive_validity":"NOT_TESTED",
    }
    data=canon(report)
    freeze(out/"manifest.json",data)
    print("WESTERN_HD_GRID_JOIN_VERIFIED",json.dumps({
        "samples":global_idx,"hd_intervals":len(starts),
        "join_shards":len(parts),"unresolved_boundary_samples":unresolved_total,
        "independent_parity_checks":checks,
        "manifest_sha256":sha256(data).hexdigest()},sort_keys=True))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--western-index",required=True,type=Path)
    p.add_argument("--hd-cache",required=True,type=Path)
    p.add_argument("--ephemeris",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--boundary-margin-seconds",type=float,default=0.2)
    p.add_argument("--independent-parity-samples",type=int,default=512)
    run(p.parse_args())

if __name__=="__main__":main()
