#!/usr/bin/env python3
"""Run/verify/reuse exact HD structural-cache segments using the EXISTING engine.

Production-relevant reusable component; NOT a new chart algorithm.
Existing repository programs:
  scripts/build_century_candidate_cache_fast.py (gate + Sun line events)
  scripts/merge_century_candidate_caches.py (verified contiguous merge)
  hdmatch.runtime.century_cache (manifest and structural state verification)

The orchestrator is restartable and refuses to reuse inconsistent segments,
change a frozen plan, overwrite partial staging, or merge gaps.

The cache is structural-chart-features-v1; full non-Sun line info, all Western
houses/sects and behavior predictions are NOT stored or certified here.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC,datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

from hdmatch.runtime.century_cache import verify_century_cache
from hdmatch.runtime.chart_adapter import ExactChartAdapter


def utc(s:str)->datetime:
    dt=datetime.fromisoformat(s.replace("Z","+00:00"))
    if dt.tzinfo is None or dt.utcoffset()!=UTC.utcoffset(None):
        raise ValueError("Expected explicitly UTC-aware datetime")
    return dt.astimezone(UTC)

def sha_file(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def canon(obj)->bytes:
    return (json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()

def freeze(path:Path,data:bytes):
    if path.exists():
        if path.read_bytes()!=data:
            raise RuntimeError("Frozen segment plan or report already has different contents")
        return
    flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
    fd=os.open(path,flags,0o600)
    with os.fdopen(fd,"wb") as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())

def segments(start:datetime,end:datetime):
    if end<=start:raise ValueError("Expected positive UTC range")
    decade_start=((start.year//10)+1)*10
    markers=[start]
    for y in range(decade_start,end.year+1,10):
        marker=datetime(y,1,1,tzinfo=UTC)
        if start<marker<end:markers.append(marker)
    markers.append(end)
    return tuple(zip(markers[:-1],markers[1:],strict=True))

def name(start,end):
    return "segment_"+start.strftime("%Y%m%dT%H%M%SZ")+"_to_"+end.strftime("%Y%m%dT%H%M%SZ")

def inspect_segment(path:Path,start:datetime,end:datetime,fingerprint:str):
    m=verify_century_cache(path,expected_engine_fingerprint=fingerprint)
    if m.utc_start!=start or m.utc_end_exclusive!=end:
        raise RuntimeError("Segment manifest UTC horizon mismatch: "+str(path))
    if m.interval_count<1:
        raise RuntimeError("Segment has no stable states")
    if m.feature_vector_schema_version!="structural-chart-features-v1":
        raise RuntimeError("Unrecognized structural feature schema")
    if m.boundary_policy_version!="activation-gates-plus-sun-lines-forward-design-v2":
        raise RuntimeError("Wrong exact structural boundary convention")
    if abs(m.design_root_tolerance_seconds-0.01)>1e-12:
        raise RuntimeError("Mixed Design root tolerance")
    return {"name":path.name,"start_utc":start.isoformat(),
            "end_exclusive_utc":end.isoformat(),"states":m.interval_count,
            "manifest_sha256":sha_file(path/"manifest.json"),
            "canonical_rows_sha256":m.canonical_rows_sha256}

def run_segment(start,end,config):
    dest=config["output_root"]/name(start,end)
    if dest.is_dir() and (dest/"manifest.json").is_file():
        return inspect_segment(dest,start,end,config["fingerprint"])
    if dest.exists():
        raise RuntimeError("Existing incomplete destination: "+str(dest))
    stage=config["output_root"]/("."+name(start,end)+".incomplete")
    if stage.exists():
        raise RuntimeError("Existing staging directory: quarantine before retry "+str(stage))
    cmd=[sys.executable,str(config["builder"]),"--ephemeris",str(config["ephemeris"]),
         "--output",str(stage),"--start",start.isoformat(),
         "--end-exclusive",end.isoformat(),
         "--shard-years","10","--root-tolerance-seconds","0.01",
         "--scan-step-days","0.25","--verify-every",str(config["verify_every"]),
         "--generation-commit",config["generation_commit"]]
    env=os.environ.copy()
    env["PYTHONPATH"]=str(config["repo_root"]/"src")+os.pathsep+str(config["builder"].parent)+os.pathsep+env.get("PYTHONPATH","")
    result=subprocess.run(cmd,env=env,cwd=str(config["builder"].parent),
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    log=config["output_root"]/"logs"/(name(start,end)+".txt")
    freeze(log,result.stdout.encode())
    if result.returncode:
        raise RuntimeError(f"Builder failed: {name(start,end)} code={result.returncode}; see {log}")
    inspected=inspect_segment(stage,start,end,config["fingerprint"])
    os.rename(stage,dest)
    return {**inspected,"name":dest.name}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ephemeris",type=Path,required=True)
    ap.add_argument("--output-root",type=Path,required=True)
    ap.add_argument("--start-utc",required=True)
    ap.add_argument("--end-utc",required=True)
    ap.add_argument("--repo-root",type=Path,required=True)
    ap.add_argument("--workers",type=int,default=4)
    ap.add_argument("--verify-every",type=int,default=500)
    ap.add_argument("--generation-commit",default="research-exact-HD-segments")
    ap.add_argument("--merge-output",type=Path)
    args=ap.parse_args()
    if not 1<=args.workers<=8 or not 1<=args.verify_every<=100000:
        raise ValueError("Unreasonable bounded worker count or verification interval")
    start,end=utc(args.start_utc),utc(args.end_utc)
    pairs=segments(start,end)
    if len(pairs)>100:
        raise ValueError("Too many segments: split work explicitly")
    root=args.repo_root.resolve()
    builder=(root/"scripts"/"build_century_candidate_cache_fast.py").resolve()
    generator=(root/"scripts"/"swieph_ab_rerun.py").resolve()
    merger=(root/"scripts"/"merge_century_candidate_caches.py").resolve()
    if not (builder.is_file() and generator.is_file() and merger.is_file()):
        raise FileNotFoundError("Existing optimized builder, generator or merger missing")
    ephe=args.ephemeris.resolve()
    adapter=ExactChartAdapter(ephe)
    output=args.output_root.resolve()
    if args.merge_output and output==args.merge_output.resolve():
        raise ValueError("Merged canonical cache cannot overwrite input-segment root")
    output.mkdir(parents=True,exist_ok=True)
    (output/"logs").mkdir(exist_ok=True)
    plan={
      "schema":"existing-hd-structural-builder-decade-orchestration-v1",
      "start_utc":start.isoformat(),"end_exclusive_utc":end.isoformat(),
      "boundary_segments":[(a.isoformat(),b.isoformat()) for a,b in pairs],
      "engine_fingerprint":adapter.fingerprint,
      "builder_sha256":sha_file(builder),
      "generator_sha256":sha_file(generator),
      "merger_sha256":sha_file(merger),
      "verify_every":args.verify_every,
      "generation_commit":args.generation_commit,
      "root_tolerance_seconds":0.01,
      "scan_step_days":0.25,
      "ephe_sources":[{"name":Path(f.path).name,"sha256":f.sha256} for f in adapter.provider.metadata.files],
      "nominal_cache_schema":"century-candidate-cache-v2",
      "feature_scope":"M0 structural gates, Sun lines, bodygraph; NOT full non-Sun lines or all astrology",
      "no_behavior_or_birth_key":True,
    }
    freeze(output/"plan.json",canon(plan))
    config={"output_root":output,"fingerprint":adapter.fingerprint,
            "builder":builder,"ephemeris":ephe,"repo_root":root,
            "verify_every":args.verify_every,"generation_commit":args.generation_commit}
    results=[]
    failures=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        future={pool.submit(run_segment,a,b,config):(a,b) for a,b in pairs}
        for f in as_completed(future):
            a,b=future[f]
            try:
                receipt=f.result()
                results.append(receipt)
                print("SEGMENT_VERIFIED",receipt["name"],
                      receipt["states"],receipt["manifest_sha256"],flush=True)
            except Exception as exc:
                failures.append(f"{name(a,b)}:{type(exc).__name__}:{exc}")
                print("SEGMENT_FAILED",failures[-1],flush=True)
    if failures:
        raise RuntimeError("Not all segments verified; canonical merge BLOCKED. "+
                           " | ".join(failures))
    results.sort(key=lambda r:r["start_utc"])
    if [(r["start_utc"],r["end_exclusive_utc"]) for r in results] != [
         (a.isoformat(),b.isoformat()) for a,b in pairs]:
        raise RuntimeError("Segment completeness/chronology mismatch")
    receipt={"schema":"verified-hd-structural-segment-batch-v1",
             "plan_sha256":sha_file(output/"plan.json"),
             "segment_count":len(results),
             "total_segment_states_before_cross_boundary_merge":sum(r["states"] for r in results),
             "segments":results,"complete_segment_coverage":True,
             "merge_pending":not bool(args.merge_output),
             "scope":"structural exact-state v1; not full V4.3 mapped-feature compliance"}
    if args.merge_output:
        merge_command=[sys.executable,str(merger),"--ephemeris",str(ephe),
             "--inputs-root",str(output),"--output",str(args.merge_output.resolve()),
             "--generation-commit",args.generation_commit]
        env=os.environ.copy();env["PYTHONPATH"]=str(root/"src")+os.pathsep+env.get("PYTHONPATH","")
        result=subprocess.run(merge_command,env=env,cwd=str(root),
                              stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        freeze(output/"logs"/"final_merge.txt",result.stdout.encode())
        if result.returncode:
            raise RuntimeError("Canonical merge failed; see logs/final_merge.txt")
        merged=inspect_segment(args.merge_output.resolve(),start,end,adapter.fingerprint)
        receipt["merged_cache"]=merged
        receipt["merge_pending"]=False
    freeze(output/"complete_receipt.json",canon(receipt))
    print("SEGMENT_BATCH_COMPLETE",json.dumps({
        "segments":len(results),"states":receipt["total_segment_states_before_cross_boundary_merge"],
        "receipt_sha256":sha_file(output/"complete_receipt.json"),
        "merge_pending":receipt["merge_pending"]},sort_keys=True),flush=True)

if __name__=="__main__": main()
