#!/usr/bin/env python3
"""Audit one VERIFIED HD structural cache segment on a complete finite UTC grid.

All features are recomputed through the normal production chart engine at
every tested UTC timestamp, then compared against the supposedly stable fast
interval. Transition-near samples are flagged unresolved rather than guessed.

Completeness covers the DECLARED SAMPLED UTC GRID ONLY, not the continuous
time between samples or the entire century unless that whole range was tested.
"""
from __future__ import annotations

import argparse
from datetime import UTC,datetime,timedelta
from hashlib import sha256
import json
from pathlib import Path

from hdmatch.runtime.chart_adapter import ExactChartAdapter
from hdmatch.runtime.century_cache import load_century_candidate_states
from hdmatch.schemas import StructuralChartFeatures

def utc(value:str)->datetime:
    t=datetime.fromisoformat(value.replace("Z","+00:00"))
    if t.tzinfo is None or t.utcoffset()!=timedelta(0):
        raise ValueError("Explicit UTC-only timestamps")
    return t.astimezone(UTC)

def sha_file(p:Path)->str:
    return sha256(p.read_bytes()).hexdigest()

def from_production(chart)->StructuralChartFeatures:
    return StructuralChartFeatures(
        type=chart.type,
        strategy=chart.strategy,
        authority=chart.authority,
        profile=chart.profile,
        definition=chart.definition,
        defined_centers=chart.defined_centers,
        channels=chart.channels,
        activation_gates={k:v.gate for k,v in chart.activations.items()}
    )

def state_index_at(states,when,at_index=0):
    current=at_index
    while current<len(states) and states[current].end_utc<=when:
        current+=1
    if current>=len(states):
        raise RuntimeError("Uncovered UTC grid timestamp")
    state=states[current]
    if when<state.start_utc or when>=state.end_utc:
        raise RuntimeError("Gap or overlap in structural cache")
    return current

def is_near_transition(state,at,epsilon:float)->bool:
    return min((at-state.start_utc).total_seconds(),
               (state.end_utc-at).total_seconds())<=epsilon

def run(args):
    start=utc(args.start_utc);end=utc(args.end_utc)
    if end<=start or (end-start).days>366:
        raise ValueError("Test one bounded year or smaller")
    if args.step_minutes not in (1,5,15,30,60):
        raise ValueError("Specify a supported finite UTC grid step")
    total_minutes=(end-start).total_seconds()/60
    if total_minutes!=int(total_minutes) or total_minutes%args.step_minutes:
        raise ValueError("Window not divisible by chosen minute grid")
    if args.boundary_margin_seconds<0:
        raise ValueError("Invalid boundary exclusion margin")
    if args.out.exists():
        raise FileExistsError("Audit artifact already exists")
    adapter=ExactChartAdapter(args.ephemeris)
    states=load_century_candidate_states(
        args.cache,timezone_name="UTC",
        expected_engine_fingerprint=adapter.fingerprint)
    if states[0].start_utc!=start or states[-1].end_utc!=end:
        raise RuntimeError("Cache horizon does not equal requested test window")
    for prev,following in zip(states,states[1:]):
        if prev.end_utc!=following.start_utc:
            raise RuntimeError("Fast cache has gap or overlap")
    checked=0;near_boundary=0;index=0
    boundary_example=[]
    hashes=sha256()
    expected_count=int(total_minutes//args.step_minutes)
    for i in range(expected_count):
        t=start+timedelta(minutes=i*args.step_minutes)
        index=state_index_at(states,t,index)
        s=states[index]
        if is_near_transition(s,t,args.boundary_margin_seconds):
            near_boundary+=1
            if len(boundary_example)<10:boundary_example.append(t.isoformat())
            continue
        observed=from_production(adapter.calculate(t))
        if observed!=s.chart_features:
            raise RuntimeError("FALSE STABILITY at UTC "+t.isoformat()+
                f": state={s.state_id} sample_index={i}")
        checked+=1
        hashes.update(i.to_bytes(8,"little"))
        hashes.update(s.chart_features_hash.encode())
    report={
        "status":"PASS_VERIFIED_FAST_HD_CACHE_ON_FINITE_UTC_GRID",
        "engine_fingerprint":adapter.fingerprint,
        "cache_manifest_sha256":sha_file(Path(args.cache)/"manifest.json"),
        "utc_start":start.isoformat(),"utc_end_exclusive":end.isoformat(),
        "step_minutes":args.step_minutes,"samples_expected":expected_count,
        "samples_checked":checked,"boundary_margin_seconds":args.boundary_margin_seconds,
        "unresolved_near_boundary_samples":near_boundary,
        "unresolved_examples":boundary_example,
        "cached_structural_interval_count":len(states),
        "checked_state_sequence_sha256":hashes.hexdigest(),
        "scope":"ENTIRE DECLARED FINITE GRID EXCEPT UNRESOLVED BOUNDARY-NEAR SAMPLES",
        "continuous_time_coverage":"NOT_CERTIFIED",
        "whole_century_certified":False,
        "personality_predictive_validity":"NOT_TESTED",
        "hd_line_information_scope":"gate transitions plus Sun lines, not all non-Sun lines"
    }
    a=json.dumps(report,sort_keys=True,indent=2)+"\n"
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(a)
    print("FAST_HD_GRID_PARITY",json.dumps(report,sort_keys=True))
    print("REPORT_SHA256",sha256(a.encode()).hexdigest())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ephemeris",required=True,type=Path)
    p.add_argument("--cache",required=True,type=Path)
    p.add_argument("--start-utc",required=True)
    p.add_argument("--end-utc",required=True)
    p.add_argument("--step-minutes",type=int,default=15)
    p.add_argument("--boundary-margin-seconds",type=float,default=0.2)
    p.add_argument("--out",required=True,type=Path)
    run(p.parse_args())

if __name__=="__main__":main()
