#!/usr/bin/env python3
"""Independently audit fast gate+Sun-line HD cache against conservative ALL-lines engine.

This script REUSES the repository's preexisting exact chart-state engine and
optimized fast century builder. It compares the complete reduced HD structures,
every transition boundary and the covered UTC duration on a bounded test window.
It also checks actual production charts at both sides of each accepted boundary.

The audit certifies only THE REQUESTED TEST WINDOW AND FEATURE REGISTRY.
It does not validate an entire century, other chart features, astrology-to-
personality maps, or all real birth minutes. Never use a successful spot check
as evidence of a universally complete production cache.
"""
from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from hashlib import sha256
import json
from pathlib import Path
import sys

from hdmatch.chart.boundaries import (
    audit_interval_partition, build_chart_state_intervals,
)
from hdmatch.runtime.chart_adapter import ExactChartAdapter
from hdmatch.runtime.century_cache import load_century_candidate_states
from hdmatch.schemas import StructuralChartFeatures

def normalize(value: str) -> datetime:
    when=datetime.fromisoformat(value.replace("Z","+00:00"))
    if when.tzinfo is None or when.utcoffset()!=timedelta(0):
        raise ValueError("Expected explicit UTC timestamp")
    return when.astimezone(UTC)

def sha_file(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def to_structural(stable) -> StructuralChartFeatures:
    bg=stable.bodygraph
    return StructuralChartFeatures(
        type=bg.type.value,
        strategy=bg.strategy.value,
        authority=bg.authority.value,
        profile=bg.profile,
        definition=bg.definition.value,
        defined_centers=tuple(x.value for x in bg.defined_centers),
        channels=bg.channels,
        activation_gates={
            f"{activation.side}:{activation.body.value}":activation.gate
            for activation in stable.activations
        },
    )

def reduce_all_line_intervals(intervals):
    result=[]
    for interval in intervals:
        features=to_structural(interval.features)
        if result and result[-1][2]==features:
            left,_,old=result[-1]
            result[-1]=(left,interval.end_utc,old)
        else:
            result.append((interval.start_utc,interval.end_utc,features))
    return tuple(result)

def audit_pairs(exact,fast,window_start,window_end,*,tolerance_seconds:float):
    if tolerance_seconds<=0:
        raise ValueError("Boundary matching tolerance must be positive")
    if not exact or not fast:
        raise ValueError("Cannot compare empty state partitions")
    if exact[0][0]!=window_start or exact[-1][1]!=window_end:
        raise ValueError("Conservative engine does not span entire requested window")
    if fast[0].start_utc!=window_start or fast[-1].end_utc!=window_end:
        raise ValueError("Fast cache does not span entire requested window")
    if len(exact)!=len(fast):
        raise ValueError(f"Number of structural intervals differs: exact={len(exact)} fast={len(fast)}")
    max_time_delta=0.0
    for index,((a,b,features),candidate) in enumerate(zip(exact,fast,strict=True)):
        if features != candidate.chart_features:
            raise ValueError(f"Structural feature mismatch at interval {index}")
        for point,reference in (
            (candidate.start_utc,a),(candidate.end_utc,b)
        ):
            drift=abs((point-reference).total_seconds())
            max_time_delta=max(max_time_delta,drift)
            if drift>tolerance_seconds:
                raise ValueError(f"Transition drift at interval {index}: {drift:.6f}s")
    return max_time_delta

def run(args):
    start=normalize(args.start_utc)
    end=normalize(args.end_utc)
    if end<=start or (end-start).days>7:
        raise ValueError("This intensive parity audit supports >0 and <=7 days per invocation")
    adapter=ExactChartAdapter(args.ephemeris)
    fast=load_century_candidate_states(
        args.cache,timezone_name="UTC",expected_engine_fingerprint=adapter.fingerprint
    )
    if fast[0].start_utc!=start or fast[-1].end_utc!=end:
        raise ValueError("Fast shard and test window do not agree")
    for a,b in zip(fast,fast[1:]):
        if a.end_utc!=b.start_utc:
            raise ValueError("Fast states have a gap/overlap")
    all_lines=build_chart_state_intervals(
        adapter.provider,start,end,root_tolerance_seconds=args.root_tolerance_seconds
    )
    audit_interval_partition(all_lines,start,end)
    exact=reduce_all_line_intervals(all_lines)
    drift=audit_pairs(exact,fast,start,end,tolerance_seconds=args.boundary_tolerance_seconds)
    # Important: one set of independent spot checks per FAST interval,
    # near both boundaries and in its interior, to detect wrong increments.
    n_checks=0
    for state in fast:
        span=(state.end_utc-state.start_utc).total_seconds()
        for fraction in (0.01,0.25,0.5,0.75,0.99):
            instant=state.start_utc+timedelta(seconds=fraction*span)
            if instant<=state.start_utc or instant>=state.end_utc:
                continue
            observed=adapter.calculate(instant)
            bg=observed
            struct=StructuralChartFeatures(
                type=bg.type,strategy=bg.strategy,authority=bg.authority,
                profile=bg.profile,definition=bg.definition,
                defined_centers=bg.defined_centers,
                channels=bg.channels,
                activation_gates={k:v.gate for k,v in bg.activations.items()},
            )
            if struct!=state.chart_features:
                raise ValueError("Fast cache disagrees with directly calculated natal chart at "+instant.isoformat())
            n_checks+=1
    result={
        "status":"PASS_BOUNDED_SOURCE_NEUTRAL_FAST_VS_CONSERVATIVE_PARITY",
        "start_utc":start.isoformat(),
        "end_exclusive_utc":end.isoformat(),
        "fast_interval_count":len(fast),
        "conservative_all_line_interval_count":len(all_lines),
        "conservative_reduced_structural_intervals":len(exact),
        "maximum_boundary_difference_seconds":round(drift,6),
        "allowed_maximum_drift_seconds":args.boundary_tolerance_seconds,
        "independent_production_chart_spot_checks":n_checks,
        "fast_cache_manifest_sha256":sha_file(Path(args.cache)/"manifest.json"),
        "source_validation_scope":"ONE DECLARED TEST WINDOW ONLY",
        "source_model_validity":"NOT_EVALUATED",
        "whole_century_complete":False,
        "human_prediction_accuracy":"NOT_EVALUATED",
    }
    output=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out.exists():
        raise FileExistsError("Refuse to overwrite already frozen audit")
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(output,encoding="utf-8")
    print(json.dumps(result,sort_keys=True))
    print("AUDIT_SHA256",sha256(output.encode()).hexdigest())


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ephemeris",required=True,type=Path)
    p.add_argument("--cache",required=True,type=Path)
    p.add_argument("--start-utc",required=True)
    p.add_argument("--end-utc",required=True)
    p.add_argument("--root-tolerance-seconds",type=float,default=0.01)
    p.add_argument("--boundary-tolerance-seconds",type=float,default=0.15)
    p.add_argument("--out",required=True,type=Path)
    run(p.parse_args())


if __name__=="__main__":
    main()
