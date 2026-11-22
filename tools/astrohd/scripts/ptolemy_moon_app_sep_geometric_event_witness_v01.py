#!/usr/bin/env python3
"""Ptolemy I.24 / III.13: EXACT Moon-to-planet aspect chronology witness.

This is a precision astronomical event finder, NOT Ptolemy's fifth complete
"phase or aspect" rulership mode, Moon-applying/separating judgment at an
unspecified historical orb, governor assignment, personality scoring or
prospective prediction.

Book I.24 allows conjunctions and traditional aspects, says proximity must
be "not great" without prescribing an exact numeric threshold, and treats
ecliptic latitude specially for bodily conjunctions. To avoid inventing an
historical orb, we report exact past/future event roots over a separately
identified, ARBITRARY ENGINEERING 3-day search horizon, with no assertion
that any pair qualifies under Ptolemy's proximity rule.

Swiss Ephemeris source is independently hash-pinned to public downloaded
binary ephemerides. It differs in file hash from the historical 1926-2026
century planet grid, though a separate source-neutral seven-time diagnostic
found planetary-longitude differences <=0.000002 degrees. Not silently
identified with the century-cache source.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
import math
from pathlib import Path

import swisseph as swe

DATA_HASHES={
 "sepl_18.se1":"9f057b316b1890a7f9340d0bf92db96edbab4939dbcc54762b62f6a70a059eb0",
 "semo_18.se1":"1ca07bd67c24374d77226180c20a4f9996cba013697894810518e7eb582ca4f7",
}
SWISSEPH_VER="2.10.03"
SOURCE_FLAGS=swe.FLG_SWIEPH|swe.FLG_SPEED
MASK=swe.FLG_SWIEPH|swe.FLG_MOSEPH|swe.FLG_JPLEPH
BODIES={"Sun":swe.SUN,"Mercury":swe.MERCURY,"Venus":swe.VENUS,
        "Mars":swe.MARS,"Jupiter":swe.JUPITER,"Saturn":swe.SATURN}
ASPECTS=((0,"conjunction"),(60,"sextile"),(90,"square"),
         (120,"trine"),(180,"opposition"),
         (240,"trine"),(270,"square"),(300,"sextile"))
SOURCE_HORIZON_DAYS=3
SOURCE_SAMPLE_HOURS=6

def sha(path:Path)->str:
 h=sha256()
 with path.open("rb") as inp:
  for block in iter(lambda:inp.read(1024*1024),b""):
   h.update(block)
 return h.hexdigest()

def configure(ephe:Path)->None:
 if swe.version!=SWISSEPH_VER:
  raise RuntimeError("Different Swiss Ephemeris library release")
 for file,expected in DATA_HASHES.items():
  path=ephe/file
  if sha(path)!=expected:
   raise RuntimeError("Ephemeris source differs: "+file)
 swe.set_ephe_path(str(ephe))

def utc(s:str)->datetime:
 dt=datetime.fromisoformat(s.replace("Z","+00:00"))
 if dt.tzinfo is None or dt.utcoffset()!=timedelta(0):
  raise ValueError("An explicit UTC timestamp is required")
 return dt.astimezone(timezone.utc)

def jd(dt:datetime)->float:
 if dt.tzinfo is None or dt.utcoffset()!=timedelta(0):
  raise ValueError("UTC required")
 return swe.julday(dt.year,dt.month,dt.day,
  dt.hour+dt.minute/60.+dt.second/3600.+dt.microsecond/3600000000.)

def body(julian:float,number:int)->tuple[float,float,float]:
 v,flags=swe.calc_ut(julian,number,SOURCE_FLAGS)
 if flags&MASK!=swe.FLG_SWIEPH:
  raise RuntimeError("Moshier/JPL fallback not admitted")
 return (float(v[0]),float(v[1]),float(v[3]))

def wrapped_residual(lunar:float,planet:float,target_degrees:float)->float:
 # Exact conjunction/trine etc are roots at residual zero. Values across
 # ±180 wrap DISCONTINUOUSLY, so root brackets must reject wrap jumps.
 return (lunar-planet-target_degrees+180.)%360.-180.

def bisect_event(fn,a:float,b:float,fa:float,fb:float,tol_deg:float=1e-7)->tuple[float,float]:
 if not a<=b:raise ValueError("Reversed root search")
 if fa==0:return a,fa
 if fb==0:return b,fb
 if fa*fb>0:raise ValueError("Root not bracketed")
 if max(abs(fa),abs(fb))>=90:
  raise ValueError("Discontinuity falsely bracketed as an aspect")
 for _ in range(55):
  mid=(a+b)/2.
  fm=fn(mid)
  if abs(fm)<tol_deg or (b-a)*86400<0.0001:
   return mid,fm
  if fa*fm<=0:
   b=mid;fb=fm
  else:
   a=mid;fa=fm
 return mid,fm

def conjunction_latitude_scope(moon_lat:float,planet_lat:float)->str:
 if abs(moon_lat)<1e-5 or abs(planet_lat)<1e-5:
  return "NEAR_ECLIPTIC_UNRESOLVED"
 if moon_lat*planet_lat>0:
  return "SAME_ECLIPTIC_SIDE"
 return "OPPOSITE_ECLIPTIC_SIDE"

def find_events(at:datetime)->dict:
 j0=jd(at)
 # Fixed engineering look-around, no historical "orb" inferred.
 window=SOURCE_HORIZON_DAYS
 step=SOURCE_SAMPLE_HOURS/24.
 times=[j0-window+i*step for i in range(2*window*24//SOURCE_SAMPLE_HOURS+1)]
 lunar_grid=[body(t,swe.MOON)[0] for t in times]
 all_events=[]
 for name,pnum in BODIES.items():
  planetary_grid=[body(t,pnum)[0] for t in times]
  for target,label in ASPECTS:
   for i in range(len(times)-1):
    a,b=times[i],times[i+1]
    fa=wrapped_residual(lunar_grid[i],planetary_grid[i],target)
    fb=wrapped_residual(lunar_grid[i+1],planetary_grid[i+1],target)
    if fa*fb>0 or max(abs(fa),abs(fb))>=90:
     continue
    def residual(t:float)->float:
     return wrapped_residual(body(t,swe.MOON)[0],body(t,pnum)[0],target)
    root,err=bisect_event(residual,a,b,fa,fb)
    if abs(err)>1e-5:
     raise RuntimeError("Contact root not adequately solved")
    # If exact root coincides with sampled interval boundary, deduplicate.
    if any(e["planet"]==name and e["target_angle_degrees"]==target
       and abs(e["julian_day"]-root)*86400<1.0 for e in all_events):
     continue
    ml,mlat,mspeed=body(root,swe.MOON)
    pl,plat,pspeed=body(root,pnum)
    gap=(root-j0)*86400
    record={
      "planet":name,
      "aspect_name":label,
      "target_angle_degrees":target,
      "julian_day":root,
      "offset_seconds_from_reference":round(gap,4),
      "chronology":"BEFORE_REFERENCE_EXACT_CONTACT" if gap<-0.001 else
          "AFTER_REFERENCE_EXACT_CONTACT" if gap>0.001 else "AT_REFERENCE",
      "residual_degrees":round(wrapped_residual(ml,pl,target),10),
      "moon_longitude_speed_deg_per_day":round(mspeed,8),
      "planet_longitude_speed_deg_per_day":round(pspeed,8),
      "ecliptic_latitude_condition_for_bodily_contact":
         conjunction_latitude_scope(mlat,plat) if target==0 else
         "NOT_APPLICABLE_FOR_GEOMETRIC_ASPECT",
    }
    all_events.append(record)
 all_events.sort(key=lambda e:(e["offset_seconds_from_reference"],e["planet"],e["target_angle_degrees"]))
 for record in all_events:
  record.pop("julian_day")
 return {
  "schema":"ptolemy_i24_lunar_exact_aspect_chronology_geometric_witness_v01",
  "status":"EXACT_GEOMETRIC_EVENT_ROOTS_ONLY_HISTORIC_ORB_AND_SOURCE_GOVERNANCE_UNRESOLVED",
  "time_utc":at.isoformat(),
  "source_edition":"Tetrabiblos I.24, III.13, Robbins 1940 English/Greek edition",
  "research_search_horizon_days_each_side":SOURCE_HORIZON_DAYS,
  "research_sampling_hours":SOURCE_SAMPLE_HOURS,
  "search_horizon_is_not_ptolemaic_orb":True,
  "ephemeris_source_hashes":DATA_HASHES,
  "root_count":len(all_events),
  "roots":all_events,
  "missing_original_rules":[
   "Ptolemy's 'interval not great' has no numeric cutoff here",
   "Moon separating/applying semantic and handling of all exact rays",
   "latitude/ecliptic side qualification for bodily contacts",
   "planetary governor choice and contradictory testimony",
   "historical phase/aspect as fifth source domination mode",
  ],
  "does_not_complete_fifth_domination_mode":True,
  "does_not_assign_personality_or_human_prediction":True,
 }

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--ephe",required=True,type=Path)
 p.add_argument("--utc",required=True)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args()
 if a.out.exists():
  raise FileExistsError("Existing source-bound output may not be replaced")
 configure(a.ephe)
 report=find_events(utc(a.utc))
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":report["status"],"events":report["root_count"],
                   "human_prediction":False},sort_keys=True))

if __name__=="__main__":
 main()
