#!/usr/bin/env python3
"""Ptolemy III.13 source-conditioned WESTERN CHART FACTS, no personality score.

Uses Swiss Ephemeris and exact private UTC selector receipts at runtime.
Computes Mercury and Moon sign/modalities, first-level sign dispositors,
Moon solar-phase witness, sect, house and planet condition and *tight aspects*.

IMPORTANT: Sign rulers alone are NOT Ptolemy's complete five-way domination
algorithm. 'Tight aspects' here use an explicitly modern engineering window
of <=3 degrees; this is NOT equivalent to the historical ruler or
'configuration' claim. No character diagnosis or probability is inferred.

The personal chart timestamps and exact output NEVER enter Git. The generic
source-precondition algorithm and synthetic tests do.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import json,math
from pathlib import Path

import swisseph as swe

SOURCE_REGISTER_SCHEMA="western_ptolemy_III13_claim_provenance_register_v1"
SOURCE_REGISTER_PATH="reference/research/ptolemy_iii13_natal_character_claims_v1.json"
PLANETS={
    "Sun":swe.SUN,"Moon":swe.MOON,"Mercury":swe.MERCURY,
    "Venus":swe.VENUS,"Mars":swe.MARS,"Jupiter":swe.JUPITER,"Saturn":swe.SATURN
}
SIGNS=("Aries","Taurus","Gemini","Cancer","Leo","Virgo",
       "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces")
RULERS=("Mars","Venus","Mercury","Moon","Sun","Mercury",
        "Venus","Mars","Jupiter","Saturn","Saturn","Jupiter")
EXALT={"Sun":0,"Moon":1,"Mercury":5,"Venus":11,
       "Mars":9,"Jupiter":3,"Saturn":6}
ASPECTS=((0,"conjunction"),(60,"sextile"),(90,"square"),
         (120,"trine"),(180,"opposition"))
FLAGS=swe.FLG_SWIEPH|swe.FLG_SPEED
SOURCE_MASK=swe.FLG_SWIEPH|swe.FLG_MOSEPH|swe.FLG_JPLEPH
EPHE_HASHES={
    "sepl_18.se1":"ca1393ceab3a44fbc895887cf789c68819ae6a1cbc9b22225872dbe4ccd99a66",
    "semo_18.se1":"1ca07bd67c24374d77226180c20a4f9996cba013697894810518e7eb582ca4f7"
}

def sha_file(p:Path)->str:return sha256(p.read_bytes()).hexdigest()
def utc(value:str)->datetime:
    dt=datetime.fromisoformat(value.replace("Z","+00:00"))
    if dt.tzinfo is None or dt.utcoffset()!=timezone.utc.utcoffset(dt):
        raise ValueError("Explicit UTC timezone required")
    return dt.astimezone(timezone.utc)

def modality(index:int)->str:
    return ("cardinal","fixed","mutable")[index%3]

def planet_dignity(planet:str,sign_index:int)->dict:
    if planet not in EXALT or not (0<=sign_index<12):
        raise ValueError("Invalid traditional planet/sign")
    return {
        "domicile":RULERS[sign_index]==planet,
        "exaltation":EXALT[planet]==sign_index,
        "detriment":RULERS[(sign_index+6)%12]==planet,
        "fall":((EXALT[planet]+6)%12)==sign_index
    }

def pair_aspects(longitudes:dict[str,float],max_orb:float=3.0)->list[dict]:
    if not 0<max_orb<=5:raise ValueError("Engineering orb outside supported window")
    names=list(longitudes)
    result=[]
    for i,a in enumerate(names):
        for b in names[i+1:]:
            sep=abs((longitudes[a]-longitudes[b]+180.)%360.-180.)
            target,name=min(ASPECTS,key=lambda x:abs(x[0]-sep))
            orb=abs(target-sep)
            if orb<=max_orb:
                result.append({"planets":[a,b],"aspect":name,"orb_degrees":round(orb,6)})
    return sorted(result,key=lambda x:(x["orb_degrees"],x["planets"]))

def chart_facts(at:datetime,site:dict)->dict:
    jd=swe.julday(at.year,at.month,at.day,
                  at.hour+at.minute/60.+at.second/3600.+at.microsecond/3.6e9)
    vals={}
    for name,code in PLANETS.items():
        v,ret=swe.calc_ut(jd,code,FLAGS)
        if (ret&SOURCE_MASK)!=swe.FLG_SWIEPH:
            raise RuntimeError("Ephemeris fallback forbidden: "+name)
        index=int(v[0]//30)
        vals[name]={"longitude":float(v[0]),"latitude":float(v[1]),
                    "speed":float(v[3]),"sign":SIGNS[index],
                    "sign_index":index,"mode":modality(index),
                    "sign_domicile_dispositor":RULERS[index],
                    "essential_dignity":planet_dignity(name,index)}
    try:
        cusps,angles=swe.houses_ex(jd,site["latitude"],site["longitude"],
                                  b'P',swe.FLG_SWIEPH)
    except swe.Error as e:
        raise ValueError("Placidus not available at this latitude") from e
    asc=float(angles[0])
    sun=vals["Sun"];moon=vals["Moon"];mercury=vals["Mercury"]
    alt=swe.azalt(jd,swe.ECL2HOR,
          (site["longitude"],site["latitude"],site.get("elevation_m",0.)),
          0,0,(sun["longitude"],sun["latitude"],0))[1]
    phase=(moon["longitude"]-sun["longitude"])%360.
    phase_flag=("waxing_approx_geocentric" if 0<phase<180 else
                "waning_approx_geocentric" if 180<phase<360 else
                "PHASE_BOUNDARY_UNRESOLVED")
    sect="UNRESOLVED_NEAR_HORIZON" if abs(alt)<=0.1 else "day" if alt>0 else "night"
    asc_sign=int(asc//30)
    all_lons={name:rec["longitude"] for name,rec in vals.items()}
    conjunctions=pair_aspects(all_lons,3.)
    selected=[]
    for planet in ("Mercury","Moon"):
        current=vals[planet]
        selected.append({
            "source_character_focus":planet,
            "sign":current["sign"],"mode":current["mode"],
            "whole_sign_house":1+(current["sign_index"]-asc_sign)%12,
            "sign_domicile_dispositor_ONLY":current["sign_domicile_dispositor"],
            "essential_dignity":current["essential_dignity"],
            "tight_aspect_witnesses_not_complete_domination":[a for a in conjunctions
                            if planet in a["planets"]]
        })
    return {
        "UTC":at.isoformat(),"site":site,
        "ascendant_sign":SIGNS[asc_sign],
        "ascendant_longitude":round(asc,7),
        "mc_sign":SIGNS[int(float(angles[1])//30)],
        "sect":sect,"sun_true_altitude_degrees":round(float(alt),6),
        "moon_sun_geocentric_phase_degrees":round(float(phase),5),
        "moon_phase_witness":phase_flag,
        "traditional_planets":{name:{
            "sign":rec["sign"],"sign_modality":rec["mode"],
            "longitude_degrees":round(rec["longitude"],7),
            "essential_dignity":rec["essential_dignity"]}
            for name,rec in vals.items()},
        "character_focus_source_witnesses":selected,
        "all_seven_planet_tight_aspects_within_3deg":conjunctions,
        "source_preconditions_missing":["Ptolemy's full multi-rulership soul dominator algorithm",
             "full applications/separations of Moon and Mercury with rulership",
             "familiarity to sect and exact degrees/terms/faces",
             "combined conditional honorable vs adverse governance",
             "historical multiple simultaneous testimony arbitration"],
        "character_behavior_score":None,
        "empirical_personality_prediction":False,
        "interpretation_scope":"SOURCE-BOUNDED GEOMETRIC WITNESSES; NO AUTOMATIC CHARACTER CONCLUSIONS",
    }

def run(args):
    if args.output.exists():raise FileExistsError("Do not overwrite source-specified chart facts")
    source_file=args.repo_root/SOURCE_REGISTER_PATH
    source=json.loads(source_file.read_bytes())
    if source.get("schema")!=SOURCE_REGISTER_SCHEMA or source.get("source",{}).get("independent_predictions")!=0:
        raise ValueError("Unexpected source-status register")
    if len(source["rules"])!=13 or any(a.get("automatically_scored") for a in source["rules"]):
        raise RuntimeError("Unapproved automatic source personality scoring")
    source_ephe=args.ephemeris
    if swe.version!="2.10.03":
        raise RuntimeError("Changed Swiss Ephemeris runtime")
    for file,expected in EPHE_HASHES.items():
        if sha_file(source_ephe/file)!=expected:
            raise RuntimeError("Changed Swiss source ephemeris file")
    swe.set_ephe_path(str(source_ephe))
    private=json.loads(args.selector.read_bytes())
    if private.get("status")!="NEW_POST_EXPOSURE_REPLAY_OF_OLD_V3_6_TARGET_MODEL_NOT_V43_PRODUCTION":
        raise RuntimeError("Wrong private reference selection archive")
    arr=private.get("reference_comparisons",[])
    if len(arr)<3:raise RuntimeError("Expected private comparator archive")
    reference_time=utc(arr[0]["input_utc"])
    # Use exact midpoint of the strongest HD ranking interval, not a time
    # copied from memory. Both instants are kept private.
    rank=json.loads(args.candidate_rank.read_bytes())
    if rank.get("status")!="EXPLORATORY_V37_CORRECTED_OBSERVABLES_REUSE_OF_V36_HD_PATHWAYS":
        raise RuntimeError("Wrong candidate provenance")
    top=rank["full_century_provisional_HD_only_ranking"]["top20"][0]
    left=utc(top["start_utc"]);right=utc(top["end_exclusive_utc"])
    candidate=left+(right-left)/2
    chart_ref=chart_facts(reference_time,args.site)
    chart_cand=chart_facts(candidate,args.site)
    row={
        "schema":"ptolemy_iii13_character_chart_geometry_witness_pair_v1",
        "status":"SOURCE_CONDITION_WITNESS_ONLY_NO_WESTERN_PERSONALITY_SCORING",
        "owner_private_record_contains_comparator_birth_times":True,
        "reference":chart_ref,"alternative":chart_cand,
        "registered_source_sha256":sha_file(source_file),
        "private_selector_sha256":sha_file(args.selector),
        "private_candidate_rank_sha256":sha_file(args.candidate_rank),
        "swieph_source_sha256":EPHE_HASHES,
        "scope":"Two example instants, not a full century Western source ranking",
        "source_note":"Robbins's English Tetrabiblos III.13 (LacusCurtius lines 21–64); 13 conditional source registrations; no sole-dominator inference.",
        "psychological_accuracy":"NOT_ESTABLISHED",
    }
    data=(json.dumps(row,indent=2,sort_keys=True)+"\n").encode()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(data)
    print("PTOLEMY_CONDITIONAL_WITNESS",json.dumps({
        "status":row["status"],
        "reference_focus":[(x["source_character_focus"],x["sign"],x["mode"]) for x in chart_ref["character_focus_source_witnesses"]],
        "alternative_focus":[(x["source_character_focus"],x["sign"],x["mode"]) for x in chart_cand["character_focus_source_witnesses"]],
        "reference_tight_aspects":len(chart_ref["all_seven_planet_tight_aspects_within_3deg"]),
        "alternative_tight_aspects":len(chart_cand["all_seven_planet_tight_aspects_within_3deg"]),
        "source_preconditions_missing":len(chart_ref["source_preconditions_missing"]),
        "sha256":sha256(data).hexdigest()},sort_keys=True))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--selector",type=Path,required=True)
    p.add_argument("--candidate-rank",type=Path,required=True)
    p.add_argument("--ephemeris",type=Path,required=True)
    p.add_argument("--site-latitude",type=float,required=True)
    p.add_argument("--site-longitude",type=float,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    args.site={"latitude":args.site_latitude,"longitude":args.site_longitude,"elevation_m":0.}
    run(args)

if __name__=="__main__":
    main()
