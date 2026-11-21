#!/usr/bin/env python3
"""Retrieve one complete *MECHANICAL* 15m natal-grid record from three caches.

Requires a UTC timestamp EXACTLY on the declared Western source lattice.
No astronomical planetary/HD recomputation, participant identity, chart-to-
personality prediction, or scoring happens. Returns:
  - seven tropical geocentric classical planet longitudes, Mercury speed
  - ASC/MC, sect, obliquity, all Placidus cusps, Whole Sign planet houses
  - all 21 traditional planet-pair angular separations (using 5 major aspects)
  - exact HD StructuralChartFeatures (Type/Authority/Profile/Channels/Gates)
  - pinned source provenance and unresolved-transition flags

Not a continuous-time lookup; any timestamp within the HD 0.2s unresolved
transition margin stays unresolved. Non-Sun HD lines not emitted by structural v1.
"""
from __future__ import annotations
import argparse
from datetime import UTC,datetime,timedelta
from hashlib import sha256
import gzip,json,math,struct
from pathlib import Path
from zoneinfo import ZoneInfo

from hdmatch.schemas import StructuralChartFeatures
from hdmatch.runtime.century_cache import GlobalCandidateState

PLANETS=("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn")
SGNS=("Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra",
      "Scorpio","Sagittarius","Capricorn","Aquarius","Pisces")
RULERS=("Mars","Venus","Mercury","Moon","Sun","Mercury",
        "Venus","Mars","Jupiter","Saturn","Saturn","Jupiter")
EXALT={"Sun":0,"Moon":1,"Mercury":5,"Venus":11,
       "Mars":9,"Jupiter":3,"Saturn":6}
ANGLES=((0,"conjunction"),(60,"sextile"),(90,"square"),
        (120,"trine"),(180,"opposition"))
SOURCE_ROW=struct.Struct("<8d")
LOCATION_ROW=struct.Struct("<17d")
HD_ROW=struct.Struct("<i")
W_SCHEMA="western-source-neutral-utc-grid-float64-pilot-v1-NONCANONICAL"
A_SCHEMA="location-conditioned-western-angles-utc-grid-v1-NONCANONICAL"
J_SCHEMA="western-grid-to-HD-structural-exact-interval-index-v1"


def sha_file(path:Path)->str:return sha256(path.read_bytes()).hexdigest()
def utc(value:str)->datetime:
    t=datetime.fromisoformat(value.replace("Z","+00:00"))
    if t.tzinfo is None or t.utcoffset()!=timedelta(0):
        raise ValueError("Explicit UTC timestamp required")
    return t.astimezone(UTC)

def position_for_grid(t:datetime,plan:dict)->int:
    start,end=utc(plan["utc_start_inclusive"]),utc(plan["utc_end_exclusive"])
    if not start<=t<end:raise ValueError("UTC time outside cache horizon")
    interval=(t-start).total_seconds()
    sample_seconds=plan["step_minutes"]*60
    if interval%sample_seconds:
        raise ValueError("Requested UTC timestamp not EXACTLY on 15m source grid")
    i=int(interval//sample_seconds)
    if not 0<=i<plan["total_samples"]:raise ValueError("Out of range")
    return i

def get_shard(shards:list[dict],index:int,first_key:str,count_key:str)->tuple[dict,int]:
    for part in shards:
        a=part[first_key]
        b=a+part[count_key]
        if a<=index<b:return part,index-a
    raise RuntimeError("Index falls inside a gap in a required data source")

def row_at(path:Path,row:int,record:struct.Struct)->tuple:
    with path.open("rb") as fp:
        fp.seek(record.size*row)
        raw=fp.read(record.size)
    if len(raw)!=record.size:raise RuntimeError("Short record in claimed verified binary source")
    return record.unpack(raw)

def sign(longitude:float)->int:return int(longitude//30)%12
def dignity(name:str,longitude:float)->dict:
    s=sign(longitude)
    return {"domicile":RULERS[s]==name,"exaltation":EXALT[name]==s,
            "detriment":RULERS[(s+6)%12]==name,
            "fall":((EXALT[name]+6)%12)==s}

def major_aspects(planets:dict)->list[dict]:
    names=list(planets)
    result=[]
    for aidx,a in enumerate(names):
        for b in names[aidx+1:]:
            longitude_a=planets[a]["longitude"]
            longitude_b=planets[b]["longitude"]
            separation=abs((longitude_a-longitude_b+180.)%360.-180.)
            target,label=min(ANGLES,key=lambda x:abs(separation-x[0]))
            result.append({"a":a,"b":b,"nearest_major_aspect":label,
                "angular_separation":round(separation,5),
                "orb_from_major_aspect":round(abs(separation-target),5)})
    return sorted(result,key=lambda x:x["orb_from_major_aspect"])

def hd_struct_by_index(root:Path,manifest:dict,index:int)->tuple[GlobalCandidateState,int]:
    offset=0
    for shard in manifest["shards"]:
        n=shard["state_count"]
        if offset<=index<offset+n:
            path=root/shard["filename"]
            if sha_file(path)!=shard["sha256"]:
                raise RuntimeError("HD source compressed shard SHA changed")
            with gzip.open(path,"rt",encoding="utf-8") as handle:
                for k,line in enumerate(handle):
                    if k==index-offset:
                        state=GlobalCandidateState.model_validate(json.loads(line))
                        return state,index-offset
            raise RuntimeError("HD source shard index missing")
        offset+=n
    raise RuntimeError("HD interval ID out of declared source range")

def inspect(args):
    west=args.western_index.resolve()
    loc=args.location_cache.resolve()
    joined=args.hd_join.resolve()
    hd=args.hd_cache.resolve()
    wm=json.loads((west/"verified_manifest.json").read_bytes())
    wp=json.loads((west/"plan.json").read_bytes())
    lm=json.loads((loc/"verified_manifest.json").read_bytes())
    lp=json.loads((loc/"plan.json").read_bytes())
    jm=json.loads((joined/"manifest.json").read_bytes())
    hm=json.loads((hd/"manifest.json").read_bytes())
    for (path,expected) in [
       (west/"verified_manifest.json",args.western_manifest_sha256),
       (loc/"verified_manifest.json",args.location_manifest_sha256),
       (joined/"manifest.json",args.join_manifest_sha256),
       (hd/"manifest.json",args.hd_manifest_sha256)]:
        if sha_file(path)!=expected:
            raise RuntimeError("Pinned input manifest mismatch "+str(path))
    if wp["schema"]!=W_SCHEMA or lp["schema"]!=A_SCHEMA or jm["schema"]!=J_SCHEMA:
        raise ValueError("Incompatible source schema")
    if lm["plan_sha256"]!=sha_file(loc/"plan.json"):
        raise RuntimeError("Location plan is not verified")
    if jm["west_verified_manifest_sha256"]!=args.western_manifest_sha256 or jm["hd_verified_manifest_sha256"]!=args.hd_manifest_sha256:
        raise RuntimeError("Joined input source SHA mismatch")
    if lp["west_manifest_sha256"]!=args.western_manifest_sha256:
        raise RuntimeError("Location source and Western source do not match")
    if wp["total_samples"]!=lm["total_samples"] or wp["total_samples"]!=jm["total_utc_grid_samples"]:
        raise RuntimeError("Inconsistent UTC sample count")
    now=utc(args.utc)
    source_index=position_for_grid(now,wp)
    # Verify every selected source shard independently rather than recomputing.
    ws,w_offset=get_shard(wm["chunks"],source_index,"first_index","count")
    ls,l_offset=get_shard(lm["shards"],source_index,"first_index","count")
    js,j_offset=get_shard(jm["shards"],source_index,"index_first","count")
    wp_file=west/"chunks"/ws["file"]
    lp_file=loc/"shards"/ls["file"]
    jp_file=joined/"shards"/js["file"]
    for path,info in [(wp_file,ws),(lp_file,ls),(jp_file,js)]:
        if sha_file(path)!=info["sha256"]:
            raise RuntimeError("A selected source shard changed after verification")
    original=row_at(wp_file,w_offset,SOURCE_ROW)
    location=row_at(lp_file,l_offset,LOCATION_ROW)
    hd_index=row_at(jp_file,j_offset,HD_ROW)[0]
    asc,mc,armc,obliq,alt=location[:5]
    anglemargin=min((asc%30),30-(asc%30))
    result={"utc":now.isoformat(),
      "local":now.astimezone(ZoneInfo(args.local_timezone)).isoformat(),
      "status":"SOURCE_NEUTRAL_COMPUTED_CHART_FEATURES_NOT_PSYCHOLOGICAL_PREDICTIONS",
      "site_latitude":lp["latitude"],"site_longitude":lp["longitude"],
      "site_elevation_m":lp["elevation_m"],
      "grid_index":source_index,"step_minutes":wp["step_minutes"],
      "ASC":round(asc,8),"MC":round(mc,8),"ARMC":round(armc,8),
      "true_obliquity":round(obliq,8),"solar_true_altitude":round(alt,8),
      "sect":"UNRESOLVED_NEAR_HORIZON" if abs(alt)<=0.1 else "day" if alt>0 else "night",
      "ASC_sign":"UNRESOLVED_NEAR_BOUNDARY" if anglemargin<=0.1 else SGNS[sign(asc)],
      "placidus_cusps":[round(x,8) for x in location[5:]],
      "sources":{"western":args.western_manifest_sha256,"location":args.location_manifest_sha256,
                 "HD":args.hd_manifest_sha256,"join":args.join_manifest_sha256},
      "hd_state_global_index":hd_index,
      "hd_structural":None,
      "hd_status":"UNRESOLVED_NEAR_TRANSITION" if hd_index<0 else "EXACT_STRUCTURAL_V1",
      "source_inference_scope":"15MIN UTC GRID WITH EXACT HD STRUCTURAL INTERVAL ID, NOT FULL CONTINUOUS OR BEHAVIORAL_MODEL"}
    planets={}
    for i,name in enumerate(PLANETS):
        longitude=original[i]
        planets[name]={"longitude":round(longitude,8),
                       "sign":SGNS[sign(longitude)],
                       "within_sign_degrees":round(longitude%30,8),
                       "whole_sign_house":None if anglemargin<=0.1 else 1+(sign(longitude)-sign(asc))%12,
                       "dignity":dignity(name,longitude)}
    planets["Mercury"]["longitude_speed_degrees_per_day"]=round(original[7],8)
    result["planets"]=planets
    result["major_aspects_all_21"]=major_aspects(planets)
    if hd_index>=0:
        state,_=hd_struct_by_index(hd,hm,hd_index)
        if not state.start_utc<=now<state.end_utc:
            raise RuntimeError("Joined HD ID does not contain requested UTC timestamp")
        result["hd_structural"]=state.chart_features.model_dump(mode="json")
        result["hd_interval_start_utc"]=state.start_utc.isoformat()
        result["hd_interval_end_exclusive_utc"]=state.end_utc.isoformat()
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--utc",required=True)
    p.add_argument("--western-index",type=Path,required=True)
    p.add_argument("--location-cache",type=Path,required=True)
    p.add_argument("--hd-cache",type=Path,required=True)
    p.add_argument("--hd-join",type=Path,required=True)
    p.add_argument("--western-manifest-sha256",required=True)
    p.add_argument("--location-manifest-sha256",required=True)
    p.add_argument("--hd-manifest-sha256",required=True)
    p.add_argument("--join-manifest-sha256",required=True)
    p.add_argument("--local-timezone",required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():
        raise FileExistsError("Refuse to change frozen sample output")
    result=inspect(args)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(result,sort_keys=True,indent=2)+"\n").encode()
    args.output.write_bytes(data)
    print("CACHED_NATAL_MECHANICAL_LOOKUP",json.dumps({
      "utc":result["utc"],"HD_status":result["hd_status"],
      "western_planets":len(result["planets"]),
      "aspects_count":len(result["major_aspects_all_21"]),
      "output_sha256":sha256(data).hexdigest()},sort_keys=True))

if __name__=="__main__":main()
