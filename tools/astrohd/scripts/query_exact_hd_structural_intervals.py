#!/usr/bin/env python3
"""Search the VERIFIED exact HD structural century cache by its actual fields.

This is source-neutral ARCHITECTURE lookup, not an astrology-to-personality
likelihood score. Query Type, Authority, Profile, Center, Channel, and optional
activation (side:planet=gate); return all matching UTC intervals and their
total duration with an audit receipt. Any actual person query is passed at
runtime, never in the repository.

The interval query is exact for the canonical structural-v1 registry; non-Sun
activation line features, advanced substructure, Western houses/sect and real
behavior evidence are explicitly UNSUPPORTED rather than silently guessed.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import UTC,datetime,timedelta
from hashlib import sha256
import gzip
import json
from pathlib import Path

from hdmatch.runtime.century_cache import (
    GlobalCandidateState,verify_pinned_century_cache,
)
from hdmatch.runtime.chart_adapter import ExactChartAdapter


def parse_utc(value:str)->datetime:
    t=datetime.fromisoformat(value.replace("Z","+00:00"))
    if t.tzinfo is None or t.utcoffset()!=timedelta(0):
        raise ValueError("Require explicitly UTC timestamp")
    return t.astimezone(UTC)

def digest(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def score_condition(state:GlobalCandidateState,conditions:dict)->bool:
    f=state.chart_features
    if conditions["type"] is not None and f.type!=conditions["type"]:return False
    if conditions["authority"] is not None and f.authority!=conditions["authority"]:return False
    if conditions["profile"] is not None and f.profile!=conditions["profile"]:return False
    for center in conditions["centers"]:
        if center not in f.defined_centers:return False
    for channel in conditions["channels"]:
        if channel not in f.channels:return False
    for carrier,gate in conditions["gates"].items():
        if f.activation_gates.get(carrier)!=gate:return False
    return True

def parse_gate_filter(raw:list[str])->dict[str,int]:
    result={}
    for part in raw:
        if "=" not in part:raise ValueError("Activation predicate must be side:body=integer_gate")
        carrier,value=part.split("=",1)
        if not carrier.startswith(("personality:","design:")):
            raise ValueError("Activation requires personality: or design: prefix")
        if not value.isdecimal() or not 1<=int(value)<=64:
            raise ValueError("Invalid gate number")
        if carrier in result:raise ValueError("Duplicate activation predicate")
        result[carrier]=int(value)
    return result

def run(args):
    root=args.hd_cache.resolve()
    start,end=parse_utc(args.start_utc),parse_utc(args.end_utc)
    if end<=start:raise ValueError("Query end before start")
    if args.output.exists():raise FileExistsError("Query output already exists")
    adapter=ExactChartAdapter(args.ephemeris)
    manifest=verify_pinned_century_cache(
        root,
        expected_engine_fingerprint=adapter.fingerprint,
        expected_manifest_sha256=args.manifest_sha256,
        expected_canonical_rows_sha256=args.logical_sha256
    )
    if start<manifest.utc_start or end>manifest.utc_end_exclusive:
        raise ValueError("Requested UTC period outside pinned cache")
    cond={"type":args.type,"authority":args.authority,"profile":args.profile,
          "centers":tuple(sorted(set(args.center))),
          "channels":tuple(sorted(set(args.channel))),
          "gates":parse_gate_filter(args.activation_gate)}
    # Do not allow empty criteria, since an all-state dump is accidental
    # and can be huge. A deliberately broad query must name one field.
    if all(cond[k] in (None,(),{}) for k in cond):
        raise ValueError("Supply at least one source-neutral structural filter")
    if args.type and args.type not in {"reflector","projector","generator","manifesting_generator","manifestor"}:
        raise ValueError("Type is not canonical")
    if args.authority and args.authority not in {
        "lunar","emotional","sacral","splenic","ego_manifested","ego_projected",
        "self_projected","mental_environmental",
    }:
        # Actual enum names can differ; don't silently map an unknown label.
        raise ValueError("Unknown canonical authority label")
    counter=Counter();whole_states=0;match_states=0;seconds=0.
    rawhash=sha256()
    matched=[]
    timeline_previous=None
    for shard in manifest.shards:
        path=root/shard.filename
        raw=gzip.decompress(path.read_bytes())
        if len(raw)!=shard.uncompressed_bytes:
            raise RuntimeError("Compressed shard decompressed byte count mismatch")
        rawhash.update(raw)
        for rawline in raw.splitlines():
            if not rawline:continue
            row=json.loads(rawline)
            st=GlobalCandidateState.model_validate(row)
            whole_states+=1
            if timeline_previous is not None and st.start_utc!=timeline_previous:
                raise RuntimeError("Noncontiguous structural state partition")
            timeline_previous=st.end_utc
            counter[st.chart_features.type]+=1
            if st.end_utc<=start or st.start_utc>=end:continue
            if not score_condition(st,cond):continue
            left,right=max(start,st.start_utc),min(end,st.end_utc)
            if right<=left:continue
            match_states+=1
            span=(right-left).total_seconds()
            seconds+=span
            if matched and matched[-1]["end_utc"]==left.isoformat():
                matched[-1]["end_utc"]=right.isoformat()
                matched[-1]["duration_seconds"]+=span
                matched[-1]["source_state_count"]+=1
            else:
                matched.append({"start_utc":left.isoformat(),
                   "end_utc":right.isoformat(),"duration_seconds":span,
                   "source_state_count":1})
    if whole_states!=manifest.interval_count or rawhash.hexdigest()!=manifest.canonical_rows_sha256:
        raise RuntimeError("Exact HD cache logical universe does not match pinned manifest")
    if timeline_previous!=manifest.utc_end_exclusive:
        raise RuntimeError("Exact HD cache final coverage mismatch")
    total=(end-start).total_seconds()
    report={
       "schema":"source-neutral-exact-HD-structural-interval-query-v1",
       "status":"COMPLETE_DECLARED_STRUCTURAL_FEATURE_SET_ONLY",
       "manifest_sha256":digest(root/"manifest.json"),
       "logical_universe_sha256":manifest.canonical_rows_sha256,
       "chart_engine_fingerprint":manifest.engine_fingerprint,
       "start_utc":start.isoformat(),"end_exclusive_utc":end.isoformat(),
       "filter":cond,
       "total_cached_states_read_and_validated":whole_states,
       "total_matching_structural_states":match_states,
       "total_matching_duration_seconds":round(seconds,6),
       "matching_fraction_of_requested_UTC_window":round(seconds/total,8),
       "matching_contiguous_windows":len(matched),
       "source_hd_types_unweighted_state_counts":dict(counter),
       "matches":matched,
       "scope":"EXACT SOURCE REGISTRY OF TYPE/AUTHORITY/PROFILE/CENTERS/CHANNELS/GATES ONLY",
       "does_not_implement_non_sun_lines":True,
       "no_western_angles_or_qualitative_behavior_inference":True,
       "scientific_personality_validity":"NOT_ESTABLISHED",
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    b=(json.dumps(report,sort_keys=True,ensure_ascii=False,separators=(",",":"))+"\n").encode()
    args.output.write_bytes(b)
    print("PINNED_HD_STRUCTURAL_FILTER_DONE",json.dumps({
       "matching_states":match_states,"contiguous_windows":len(matched),
       "matching_hours":round(seconds/3600,3),
       "fraction":round(seconds/total,8),
       "output_sha256":sha256(b).hexdigest(),
       "scope":"source-neutral HD categorical structure, not personality fit"
    },sort_keys=True),flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hd-cache",required=True,type=Path)
    p.add_argument("--ephemeris",required=True,type=Path)
    p.add_argument("--manifest-sha256",required=True)
    p.add_argument("--logical-sha256",required=True)
    p.add_argument("--start-utc",required=True)
    p.add_argument("--end-utc",required=True)
    p.add_argument("--type")
    p.add_argument("--authority")
    p.add_argument("--profile")
    p.add_argument("--center",action="append",default=[])
    p.add_argument("--channel",action="append",default=[])
    p.add_argument("--activation-gate",action="append",default=[])
    p.add_argument("--output",required=True,type=Path)
    run(p.parse_args())

if __name__=="__main__":main()
