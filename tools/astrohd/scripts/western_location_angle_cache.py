#!/usr/bin/env python3
"""Reusable location-scoped Swiss Asc/MC, sect and Placidus-cusp UTC grid cache.

Based on the previously verified SOURCE-NEUTRAL 15-minute Western longitude
index. This supplement requires a LOCATION (lat/lon/elevation), not an owner
name, birth date, behavioral questionnaire, or private chart. It stores, for
each existing UTC sampled timestamp, 17 little-endian float64 values:

ASC, MC, ARMC, true obliquity, TRUE solar altitude, Placidus cusps 1..12.

Whole-sign houses derive from floor(ASC/30), classical planetary signs from
the existing source-neutral longitude cache. Placidus continuous house
positions may be calculated from ARMC, obliquity and stored longitude/latitude
at scoring time. Solar altitude determines diurnal versus nocturnal sect; a
boundary band near zero altitude is explicitly *uncertain*.

This is a finite UTC sample-grid complement, not a continuous event engine,
not V4.3 model validation, and not evidence that a chart predicts personality.
"""
from __future__ import annotations
import argparse
from datetime import UTC,datetime,timedelta
from hashlib import sha256
import json,math,os
from pathlib import Path
import struct,tempfile

import swisseph as swe

SCHEMA="location-conditioned-western-angles-utc-grid-v1-NONCANONICAL"
SOURCE_SCHEMA="western-source-neutral-utc-grid-float64-pilot-v1-NONCANONICAL"
DATA_FORMAT=struct.Struct("<17d")
SOURCE=struct.Struct("<8d")
FLAGS=swe.FLG_SWIEPH|swe.FLG_SPEED
EPH_MASK=swe.FLG_SWIEPH|swe.FLG_JPLEPH|swe.FLG_MOSEPH


def digest(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()
def canon(obj)->bytes:
    return (json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()
def atomic(path:Path,b:bytes):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=str(path.parent),prefix=".angles-write-")
    try:
        with os.fdopen(fd,"wb") as stream:
            stream.write(b);stream.flush();os.fsync(stream.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def utc(value:str)->datetime:
    dt=datetime.fromisoformat(value.replace("Z","+00:00"))
    if dt.tzinfo is None or dt.utcoffset()!=timedelta(0):
        raise ValueError("UTC-aware timestamp required")
    return dt.astimezone(UTC)
def time_at(start:datetime,step_minutes:int,index:int)->datetime:
    return start+timedelta(minutes=step_minutes*index)

def source_plan(root:Path,ephe:Path):
    plan=json.loads((root/"plan.json").read_bytes())
    manifest=json.loads((root/"verified_manifest.json").read_bytes())
    if plan["schema"]!=SOURCE_SCHEMA or manifest["schema"]!=SOURCE_SCHEMA:
        raise RuntimeError("Source index schema invalid")
    if digest(root/"plan.json")!=manifest["plan_sha256"]:
        raise RuntimeError("Source plan digest inconsistent")
    if len(manifest["chunks"])<1 or sum(x["count"] for x in manifest["chunks"])!=plan["total_samples"]:
        raise RuntimeError("Missing source time-grid shards")
    for name,file_hash in plan["ephe_sha256"].items():
        if digest(ephe/name)!=file_hash:
            raise RuntimeError("Swiss source file mismatch "+name)
    if swe.version!=plan["swisseph_version"]:
        raise RuntimeError("Swiss runtime version mismatch")
    swe.set_ephe_path(str(ephe))
    return plan,manifest

def point(at:datetime,lat:float,lon:float,elev:float,cached_sun_longitude:float):
    julian=swe.julday(at.year,at.month,at.day,
                      at.hour+at.minute/60.+at.second/3600.)
    v,ret=swe.calc_ut(julian,swe.SUN,FLAGS)
    if (ret&EPH_MASK)!=swe.FLG_SWIEPH:
        raise RuntimeError("Swiss source fallback")
    if abs(v[0]-cached_sun_longitude)>1e-10:
        raise RuntimeError("Source-neutral longitude disagrees with independent SWIEPH Sun calculation")
    try:
        cusps,angles=swe.houses_ex(julian,lat,lon,b'P',swe.FLG_SWIEPH)
    except swe.Error as exc:
        raise ValueError("Placidus houses unavailable at supplied location") from exc
    if len(cusps)!=12 or len(angles)<3:
        raise RuntimeError("Malformed Swiss house calculation")
    obliq,rf=swe.calc_ut(julian,swe.ECL_NUT,swe.FLG_SWIEPH)
    # ECL_NUT is not ephemeris-file-backed in the same way as a planet; keep
    # its flag/source convention separately in the frozen manifest.
    altitude=swe.azalt(julian,swe.ECL2HOR,(lon,lat,elev),0,0,
                       (v[0],v[1],v[2]))[1]
    row=(angles[0],angles[1],angles[2],obliq[0],altitude,*cusps)
    if len(row)!=17 or any(not math.isfinite(x) for x in row):
        raise RuntimeError("Nonfinite Swiss location-specific house/sect values")
    return row

def prepare(args):
    west=args.western_index.resolve()
    ephe=args.ephe.resolve()
    if not -66<args.latitude<66:
        raise ValueError("Placidus pilot requires latitude within (-66,66) degrees")
    if not -180<=args.longitude<=180:
        raise ValueError("Invalid longitude")
    if not -500<=args.elevation<=9000:
        raise ValueError("Invalid elevation")
    west_plan,west_manifest=source_plan(west,ephe)
    return {
      "schema":SCHEMA,
      "status":"LOCATION_SCOPED_ANGLE_AND_SECT_GRID_ONLY",
      "code_sha256":digest(Path(__file__)),
      "west_plan_sha256":digest(west/"plan.json"),
      "west_manifest_sha256":digest(west/"verified_manifest.json"),
      "west_original_schema":SOURCE_SCHEMA,
      "latitude":args.latitude,"longitude":args.longitude,
      "elevation_m":args.elevation,
      "utc_start":west_plan["utc_start_inclusive"],
      "utc_end_exclusive":west_plan["utc_end_exclusive"],
      "step_minutes":west_plan["step_minutes"],
      "sample_count":west_plan["total_samples"],
      "swisseph_version":swe.version,
      "ephe_sha256":west_plan["ephe_sha256"],
      "cols":["asc","mc","armc","true_obliquity","true_sun_altitude"]+
             [f"placidus_cusp_{i}" for i in range(1,13)],
      "record_bytes":DATA_FORMAT.size,
      "binary_endian":"little_endian_float64_x17",
      "source_cusp_convention":"Placidus, tropical geocentric ecliptic, no house system fallback",
      "sect_boundary_0_1_deg":"UNRESOLVED_NEAR_HORIZON",
      "v4_3_compliant":False,"continuous_coverage":False,
      "human_prediction_accuracy":"NOT_TESTED",
      "shards":len(west_manifest["chunks"]),
    }

def load_or_freeze_plan(out:Path,plan:dict,create=False):
    f=out/"plan.json"
    if f.exists():
        if json.loads(f.read_bytes())!=plan:
            raise RuntimeError("Frozen angle cache plan mismatch")
    elif create:
        if out.exists() and any(out.iterdir()):
            raise RuntimeError("Existing nonempty output directory")
        out.mkdir(parents=True,exist_ok=True)
        atomic(f,canon(plan))
    else:raise FileNotFoundError("Plan first")
    return f

def verify_shard_hash(path:Path,expected_records:int):
    if not path.is_file() or path.stat().st_size!=expected_records*DATA_FORMAT.size:
        raise RuntimeError("Missing or partial angle shard "+str(path))
    sidecar=path.with_suffix(path.suffix+".sha256")
    if not sidecar.is_file():raise RuntimeError("Missing immutable angle shard SHA sidecar")
    actual=digest(path)
    if actual!=sidecar.read_text().strip():
        raise RuntimeError("Tampered location angle cache shard")
    return actual

def chunk_filename(index:int)->str:
    return f"angles_{index:05d}.bin"

def build(args,plan):
    west=args.western_index.resolve()
    manifest=json.loads((west/"verified_manifest.json").read_bytes())
    start=utc(plan["utc_start"])
    index=0
    for number,shard in enumerate(manifest["chunks"]):
        if shard["first_index"]!=index:
            raise RuntimeError("Non-contiguous source index")
        src=west/"chunks"/shard["file"]
        if digest(src)!=shard["sha256"]:
            raise RuntimeError("Changed source ephemeris shard")
        count=shard["count"]
        target=args.output/"shards"/chunk_filename(number)
        if target.exists():
            verify_shard_hash(target,count)
            index+=count
            continue
        raw=bytearray(count*DATA_FORMAT.size)
        with src.open("rb") as file:
            for k in range(count):
                source=SOURCE.unpack(file.read(SOURCE.size))
                t=time_at(start,plan["step_minutes"],index+k)
                values=point(t,args.latitude,args.longitude,args.elevation,source[0])
                DATA_FORMAT.pack_into(raw,k*DATA_FORMAT.size,*values)
        data=bytes(raw);digest_raw=sha256(data).hexdigest()
        atomic(target,data)
        atomic(target.with_suffix(target.suffix+".sha256"),(digest_raw+"\n").encode())
        if verify_shard_hash(target,count)!=digest_raw:
            raise RuntimeError("Postgeneration shard verification failed")
        index+=count
        if (number+1)%10==0 or number+1==len(manifest["chunks"]):
            print("LOCATION_ANGLES_SHARD",number+1,"/",len(manifest["chunks"]),
                  "total_records",index,flush=True)
    if index!=plan["sample_count"]:
        raise RuntimeError("Location-scoped index did not cover all source samples")
    print("ANGLE_CACHE_BUILD_COMPLETE",index)

def verify(args,plan):
    west=args.western_index.resolve()
    m=json.loads((west/"verified_manifest.json").read_bytes())
    start=utc(plan["utc_start"])
    n=0;files=[]
    for i,s in enumerate(m["chunks"]):
        source=west/"chunks"/s["file"]
        if digest(source)!=s["sha256"]:
            raise RuntimeError("Source Western shard changed")
        target=args.output/"shards"/chunk_filename(i)
        d=verify_shard_hash(target,s["count"])
        with target.open("rb") as got,source.open("rb") as original:
            for row_index in sorted({0,s["count"]//2,s["count"]-1}):
                got.seek(row_index*DATA_FORMAT.size)
                stored=got.read(DATA_FORMAT.size)
                original.seek(row_index*SOURCE.size)
                sun=SOURCE.unpack(original.read(SOURCE.size))[0]
                t=time_at(start,plan["step_minutes"],n+row_index)
                expected=DATA_FORMAT.pack(*point(t,args.latitude,args.longitude,args.elevation,sun))
                if stored!=expected:
                    raise RuntimeError("Source-bound geocentric/house parity mismatch")
        files.append({"file":target.name,"first_index":n,
                      "count":s["count"],"sha256":d})
        n+=s["count"]
    if n!=plan["sample_count"]:
        raise RuntimeError("Incomplete location house timestamp grid")
    report={"schema":SCHEMA,"status":"VERIFIED_COMPLETE_DECLARED_LOCATION_UTC_GRID",
        "plan_sha256":digest(args.output/"plan.json"),
        "source_west_manifest_sha256":digest(west/"verified_manifest.json"),
        "total_samples":n,"record_bytes":DATA_FORMAT.size,
        "shards":files,"scope":"FINITE UTC GRID ONLY",
        "time_between_samples":"NOT_CERTIFIED","house_angles_depend_on_supplied_location":True,
        "whole_chart_behavior_model":"NOT_IMPLEMENTED"}
    raw=canon(report);output=args.output/"verified_manifest.json"
    if output.exists() and output.read_bytes()!=raw:
        raise RuntimeError("Cannot overwrite prior verification")
    atomic(output,raw)
    print("LOCATION_ANGLES_CACHE_VERIFIED",json.dumps({
       "samples":n,"shards":len(files),"source_manifest_sha256":report["source_west_manifest_sha256"],
       "manifest_sha256":sha256(raw).hexdigest()},sort_keys=True))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=("plan","build","verify"))
    parser.add_argument("--western-index",type=Path,required=True)
    parser.add_argument("--ephe",type=Path,required=True)
    parser.add_argument("--latitude",type=float,required=True)
    parser.add_argument("--longitude",type=float,required=True)
    parser.add_argument("--elevation",type=float,default=0.)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    plan=prepare(args)
    load_or_freeze_plan(args.output,plan,create=args.action=="plan")
    if args.action=="plan":
        print("LOCATION_ANGLES_PLAN_FROZEN",digest(args.output/"plan.json"))
    elif args.action=="build":build(args,plan)
    else:verify(args,plan)

if __name__=="__main__":main()
