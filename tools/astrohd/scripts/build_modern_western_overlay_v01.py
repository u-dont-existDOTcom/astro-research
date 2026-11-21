#!/usr/bin/env python3
"""Optional MODERN Western-astrologer packet extension (Uranus/Neptune/Pluto).

Does not turn modern interpretations into historical Ptolemaic/Lilly testimony.
Reads previous private sealed letter mapping so all chart labels remain stable;
does not print or reveal its true-reference letter. No DOB/UTC in output.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import swisseph as swe

OUTER={"Uranus":swe.URANUS,"Neptune":swe.NEPTUNE,"Pluto":swe.PLUTO}
SEVEN={"Sun":swe.SUN,"Moon":swe.MOON,"Mercury":swe.MERCURY,
       "Venus":swe.VENUS,"Mars":swe.MARS,"Jupiter":swe.JUPITER,"Saturn":swe.SATURN}
SIGNS=("Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
       "Sagittarius","Capricorn","Aquarius","Pisces")
ASPECTS=((0,"conjunction"),(60,"sextile"),(90,"square"),
         (120,"trine"),(180,"opposition"))
SWISS=swe.FLG_SWIEPH|swe.FLG_SPEED
SOURCE_MASK=swe.FLG_SWIEPH|swe.FLG_MOSEPH|swe.FLG_JPLEPH

def sha(p:Path)->str:return sha256(p.read_bytes()).hexdigest()
def separation(a:float,b:float)->float:return abs((a-b+180)%360-180)
def aspect(a:float,b:float,orb:float=3.0)->dict|None:
    sep=separation(a,b)
    deg,name=min(ASPECTS,key=lambda x:abs(x[0]-sep))
    delta=abs(deg-sep)
    return {"name":name,"orb":round(delta,3)} if delta<=orb else None

def outer_for_chart(when:datetime,site:dict)->dict:
    jd=swe.julday(when.year,when.month,when.day,
                   when.hour+when.minute/60+when.second/3600+when.microsecond/3.6e9)
    _,angles=swe.houses_ex(jd,site["latitude"],site["longitude"],b"R",swe.FLG_SWIEPH)
    eps=swe.calc_ut(jd,swe.ECL_NUT,swe.FLG_SWIEPH)[0][0]
    lons={}
    pos={}
    asc_sign=int(float(angles[0])//30)
    for name,code in {**SEVEN,**OUTER}.items():
        vals,ret=swe.calc_ut(jd,code,SWISS)
        if (ret&SOURCE_MASK)!=swe.FLG_SWIEPH:
            raise RuntimeError("Swiss fallback for "+name)
        lons[name]=float(vals[0])
        if name in OUTER:
            h=swe.house_pos(float(angles[2]),site["latitude"],eps,
                            (float(vals[0]),float(vals[1])),b"R")
            pos[name]={
                "sign":SIGNS[int(vals[0]//30)],
                "sign_degree":round(float(vals[0])%30,3),
                "whole_house":(int(vals[0]//30)-asc_sign)%12+1,
                "regio_house":int(h),
                "retrograde":float(vals[3])<0,
            }
    contacts=[]
    for a in OUTER:
        for b in SEVEN:
            witness=aspect(lons[a],lons[b])
            if witness:
                contacts.append({"pair":[a,b],**witness})
        for b,longitude in (("Ascendant",float(angles[0])),
                            ("Midheaven",float(angles[1]))):
            witness=aspect(lons[a],longitude)
            if witness:contacts.append({"pair":[a,b],**witness})
    return {"outer_positions":pos,"contacts_with_seven_and_angles_3deg":contacts,
            "unqualified_modern_personality_score":None,
            "scope":"selected tropical modern major-aspect witnesses only; not all astrologer doctrine"}

def make(inventory:dict,key:dict)->str:
    rows={r["private_id"]:r for r in inventory["comparison_units"]}
    if len(rows)!=15 or len(key["entry_mapping"])!=15 or key["entry_count"]!=15:
        raise ValueError("Incorrect complete-case set")
    if {r["private_id"] for r in key["entry_mapping"]}!=set(rows):
        raise ValueError("Sealed chart roster differs from source")
    site=inventory["private_chart_location"]
    lines=["# Optional modern Western outer-planet supplement",
           "Use together with the SAME anonymous A–O labels in the Western-only",
           "practitioner packet. The corresponding true-chart key remains sealed.",
           "This is a seven-planet historical reading plus **optional modern**",
           "Uranus/Neptune/Pluto placements and selected major aspects; neither",
           "tradition has demonstrated calibrated natal personality likelihoods.",
           "No birth dates, time, participant identity or previously computed HD ranks",
           "are disclosed. Each case is one midpoint, not a full HD interval.",
           ""]
    for r in key["entry_mapping"]:
        row=rows[r["private_id"]]
        t=datetime.fromisoformat(row["chart_midpoint"]["utc"])
        x=outer_for_chart(t,site)
        lines.extend([f"## Chart {r['label']}",""])
        for name,z in x["outer_positions"].items():
            lines.append(f"- {name}: {z['sign']} {z['sign_degree']:.2f}°, "+
                         f"Whole Sign house {z['whole_house']}, Regiomontanus "+
                         f"house {z['regio_house']}, retrograde {z['retrograde']}.")
        if x["contacts_with_seven_and_angles_3deg"]:
            lines.append("- Modern outer-to-inner/angle major aspects at <=3°:")
            for v in x["contacts_with_seven_and_angles_3deg"]:
                lines.append(f"  - {v['pair'][0]}–{v['pair'][1]} "+
                             f"{v['name']} orb {v['orb']:.2f}°")
        else:lines.append("- No outer-to-classical/angle major contacts within this cutoff.")
        lines.append("")
    return "\n".join(lines)+"\n"

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--inventory",type=Path,required=True)
    p.add_argument("--sealed-key",type=Path,required=True)
    p.add_argument("--ephemeris",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError("Private outputs are immutable")
    data=json.loads(args.inventory.read_bytes())
    key=json.loads(args.sealed_key.read_bytes())
    if sha(args.inventory)!=key["source_inventory_sha256"]:
        raise RuntimeError("Sealed key used another original inventory")
    if swe.version!="2.10.03":raise RuntimeError("Changed Swiss version")
    swe.set_ephe_path(str(args.ephemeris))
    result=make(data,key)
    args.output.write_text(result)
    print(json.dumps({"status":"OPTIONAL_MODERN_SOURCE_WITNESSES_ONLY",
                      "private_output_sha256":sha(args.output),
                      "sealed_key_unchanged":True,"external_practitioner_review":False},
                     sort_keys=True))
if __name__=="__main__":main()
