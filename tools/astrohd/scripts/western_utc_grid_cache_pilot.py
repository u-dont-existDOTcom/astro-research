#!/usr/bin/env python3
"""Generic SOURCE-NEUTRAL Western ephemeris UTC grid index, NONCANONICAL PILOT.

This stores no survey, natal identity, candidate scoring, HD states, house
placements or inferred personality. It can index any finite UTC time grid
from Swiss Ephemeris longitudes, verify input file hashes, and resume after
a context break. The canonical V4.3 full century exact-interval cache is
a DIFFERENT project artifact (src/hdmatch/runtime/century_cache.py).

Records are 8 float64 values per timestamp:
  Sun Moon Mercury Venus Mars Jupiter Saturn longitudes; Mercury speed.
Timestamp = immutable UTC_start + record_index * step_minutes.

No calls to a language model occur per chart.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import struct
import tempfile
import swisseph as swe

SCHEMA="western-source-neutral-utc-grid-float64-pilot-v1-NONCANONICAL"
ORDER=("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn")
PLANETS=(swe.SUN,swe.MOON,swe.MERCURY,swe.VENUS,swe.MARS,
         swe.JUPITER,swe.SATURN)
RECORD=struct.Struct("<8d")
SOURCE_FLAGS=swe.FLG_SWIEPH|swe.FLG_SPEED
EPHMASK=swe.FLG_JPLEPH|swe.FLG_MOSEPH|swe.FLG_SWIEPH


def sha_bytes(data:bytes)->str:
    return sha256(data).hexdigest()


def sha_file(path:Path)->str:
    return sha_bytes(path.read_bytes())


def canon(obj:dict)->bytes:
    return (json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()


def atomic(path:Path,content:bytes)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,t=tempfile.mkstemp(prefix=".grid-write-",dir=str(path.parent))
    try:
        with os.fdopen(fd,"wb") as f:
            f.write(content); f.flush(); os.fsync(f.fileno())
        os.replace(t,path)
    finally:
        if os.path.exists(t):os.unlink(t)


def utc_parse(text:str)->datetime:
    dt=datetime.fromisoformat(text.replace("Z","+00:00"))
    if dt.tzinfo is None or dt.utcoffset()!=timedelta(0):
        raise ValueError("Time must be explicit, UTC-offset-aware ISO 8601")
    return dt.astimezone(timezone.utc)


def epoch_minutes(dt:datetime)->int:
    epoch=datetime(1970,1,1,tzinfo=timezone.utc)
    diff=dt-epoch
    if diff.total_seconds()%60:
        raise ValueError("This pilot uses integral-minute UTC timestamp endpoints")
    return int(diff.total_seconds())//60


def jd_utc(dt:datetime)->float:
    return swe.julday(dt.year,dt.month,dt.day,
                      dt.hour + dt.minute/60 +dt.second/3600)


def setup(ephe:Path)->dict:
    if swe.version!="2.10.03":raise RuntimeError("Unexpected Swiss Ephemeris version "+swe.version)
    hashes={}
    for name in ("sepl_18.se1","semo_18.se1"):
        f=ephe/name
        if not f.is_file(): raise FileNotFoundError("Missing Swiss .se1 "+str(f))
        hashes[name]=sha_file(f)
    swe.set_ephe_path(str(ephe))
    for y,m,d in ((1927,1,1),(1980,1,1),(2026,1,1)):
        jd=swe.julday(y,m,d,12.)
        for p in PLANETS:
            _,ret=swe.calc_ut(jd,p,SOURCE_FLAGS)
            if (ret&EPHMASK)!=swe.FLG_SWIEPH:raise RuntimeError("SWIEPH file fallback detected")
    return hashes


def calculate_at(dt:datetime)->tuple[float,...]:
    jd=jd_utc(dt)
    values=[];speed=None
    for i,p in enumerate(PLANETS):
        v,ret=swe.calc_ut(jd,p,SOURCE_FLAGS)
        if (ret&EPHMASK)!=swe.FLG_SWIEPH:
            raise RuntimeError("SWIEPH fallback at "+dt.isoformat()+" "+ORDER[i])
        if not math.isfinite(v[0]) or not 0<=v[0]<360:
            raise RuntimeError("Invalid geocentric longitude "+ORDER[i])
        values.append(v[0])
        if i==2:
            speed=v[3]
            if not math.isfinite(speed):raise RuntimeError("Invalid Mercury speed")
    return (*values,speed)


def prepare_plan(args)->dict:
    start=utc_parse(args.start_utc)
    end=utc_parse(args.end_utc)
    if end<=start: raise ValueError("End must be after start")
    if args.step_minutes not in (1,5,15,30,60,180,360,720,1440):
        raise ValueError("Unsupported step size")
    n=(epoch_minutes(end)-epoch_minutes(start))//args.step_minutes
    if n<=0 or (epoch_minutes(end)-epoch_minutes(start))%args.step_minutes:
        raise ValueError("Start/end must cover an integer number of samples")
    if args.chunk_samples<1 or args.chunk_samples>100000:
        raise ValueError("Chunk size must be in 1..100000")
    if n>5000000:
        raise ValueError("Noncanonical pilot limited to five million sample instants per run; split by UTC year and verify shards")
    return {"schema":SCHEMA,"status":"SOURCE_NEUTRAL_GRID_ONLY_NOT_PROFILE_RANKING",
            "source_sha256":sha_file(Path(__file__)),
            "ephe_sha256":setup(args.ephe),
            "swisseph_version":swe.version,
            "requested_flags":"SWIEPH|SPEED",
            "record_order":list(ORDER)+["Mercury_lon_speed"],
            "record_binary":"little_endian_float64_x8",
            "record_bytes":RECORD.size,
            "utc_start_inclusive":start.isoformat(),
            "utc_end_exclusive":end.isoformat(),
            "step_minutes":args.step_minutes,
            "chunk_samples":args.chunk_samples,
            "total_samples":n,"chart_model_hash":None,
            "survey_data":None,
            "v4_3_compliant":False,
            "continuous_interval_coverage":False,
            "notes":"COMPLETE COVERAGE OF THE DECLARED UTC GRID ONLY; NO BETWEEN-SAMPLE GUARANTEE"}


def check_plan(out:Path,plan:dict,allow_create:bool)->dict:
    path=out/"plan.json"
    if not path.exists():
        if not allow_create:raise FileNotFoundError("Run plan first")
        if out.exists() and any(out.iterdir()):
            raise RuntimeError("Output directory must be empty for new plan")
        out.mkdir(parents=True,exist_ok=True)
        atomic(path,canon(plan))
        return plan
    existing=json.loads(path.read_bytes())
    if existing!=plan:raise RuntimeError("Frozen plan mismatch: cannot reuse this output directory")
    return existing


def chunk_info(plan:dict,i:int)->tuple[int,int]:
    offset=i*plan["chunk_samples"]
    return offset,min(plan["total_samples"]-offset,plan["chunk_samples"])


def chunk_name(i:int)->str:
    return f"grid_{i:05d}.bin"


def validate_existing_chunk(path:Path,n:int)->str:
    if path.stat().st_size!=n*RECORD.size:
        raise RuntimeError("Unverified partial chunk "+str(path))
    checkfile=path.with_suffix(path.suffix+".sha256")
    if not checkfile.is_file():
        raise RuntimeError("Missing generation-time SHA sidecar; quarantine incomplete chunk "+str(path))
    pinned=checkfile.read_text().strip()
    if len(pinned)!=64 or any(c not in "0123456789abcdef" for c in pinned):
        raise RuntimeError("Invalid generation-time SHA sidecar "+str(checkfile))
    actual=sha_file(path)
    if actual!=pinned:
        raise RuntimeError("Generation-time SHA mismatch "+str(path))
    return actual


def build(out:Path,plan:dict):
    start=utc_parse(plan["utc_start_inclusive"])
    total=plan["total_samples"]
    chunks=(total+plan["chunk_samples"]-1)//plan["chunk_samples"]
    completed=0
    for i in range(chunks):
        offset,n=chunk_info(plan,i)
        path=out/"chunks"/chunk_name(i)
        if path.is_file():
            validate_existing_chunk(path,n)
            completed+=1
            continue
        raw=bytearray(n*RECORD.size)
        for j in range(n):
            when=start+timedelta(minutes=(offset+j)*plan["step_minutes"])
            RECORD.pack_into(raw,j*RECORD.size,*calculate_at(when))
        raw_digest=sha_bytes(raw)
        atomic(path,bytes(raw))
        atomic(path.with_suffix(path.suffix+".sha256"),(raw_digest+"\n").encode())
        if validate_existing_chunk(path,n)!=raw_digest:
            raise RuntimeError("Post-write SHA mismatch")
        completed+=1
        if (i+1)%10==0 or i==chunks-1:
            print("CACHE_CHUNK",i+1,"/",chunks,"SHA",sha_bytes(raw),flush=True)
    print("CACHE_BUILD_DONE",completed,"chunks",total,"records")


def verify(out:Path,plan:dict):
    start=utc_parse(plan["utc_start_inclusive"])
    chunks=(plan["total_samples"]+plan["chunk_samples"]-1)//plan["chunk_samples"]
    manifest={"schema":SCHEMA,"plan_sha256":sha_file(out/"plan.json"),
              "total_samples":plan["total_samples"],
              "first_utc":plan["utc_start_inclusive"],
              "end_exclusive_utc":plan["utc_end_exclusive"],
              "grid_only":True,
              "between_grid_samples":"NOT_VERIFIED",
              "v4_3_compliant":False,
              "chunks":[]}
    for i in range(chunks):
        first,n=chunk_info(plan,i)
        p=out/"chunks"/chunk_name(i)
        if not p.is_file():raise FileNotFoundError(str(p))
        checksum=validate_existing_chunk(p,n)
        # Spot-check exact intended records independently, always by SWIEPH.
        with p.open("rb") as f:
            for pos in sorted({0,n//2,n-1}):
                f.seek(pos*RECORD.size)
                stored=f.read(RECORD.size)
                when=start+timedelta(minutes=(first+pos)*plan["step_minutes"])
                expected=RECORD.pack(*calculate_at(when))
                if stored!=expected:
                    raise RuntimeError("Grid record byte-exact parity mismatch "+p.name+" record "+str(pos))
        manifest["chunks"].append({"file":p.name,"sha256":checksum,
                                   "first_index":first,"count":n,
                                   "size_bytes":n*RECORD.size})
    verified=out/"verified_manifest.json"
    data=canon(manifest)
    if verified.exists() and verified.read_bytes()!=data:
        raise RuntimeError("Would overwrite prior incompatible verification")
    atomic(verified,data)
    print("GRID_PILOT_VERIFIED",json.dumps({
      "total_samples":plan["total_samples"],"chunks":len(manifest["chunks"]),
      "utc_start":plan["utc_start_inclusive"],"utc_end_exclusive":plan["utc_end_exclusive"],
      "manifest_sha256":sha_bytes(data),"all_shards_sha_checked":True,
      "grid_only":True},sort_keys=True))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["plan","build","verify"])
    parser.add_argument("--start-utc",required=True)
    parser.add_argument("--end-utc",required=True)
    parser.add_argument("--step-minutes",type=int,default=15)
    parser.add_argument("--chunk-samples",type=int,default=8192)
    parser.add_argument("--ephe",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    plan=prepare_plan(args)
    check_plan(args.out,plan,allow_create=args.action=="plan")
    if args.action=="plan":
        print("GRID_PILOT_PLAN_FROZEN",sha_file(args.out/"plan.json"),
              "records",plan["total_samples"])
    elif args.action=="build": build(args.out,plan)
    else:verify(args.out,plan)


if __name__=="__main__": main()
