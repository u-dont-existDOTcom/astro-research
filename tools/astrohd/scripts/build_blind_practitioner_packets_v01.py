#!/usr/bin/env python3
"""Make separate, privately stored anonymized specialist comparison packets.

The INPUT is the private, source-checked inventory containing the actual chart
and 14 strictly higher V3.7 HD-only structural intervals. The evaluator sees
NEITHER scores nor the actual date/time/name/label. This is preparation for a
future external practitioner, NOT such an assessment. Sealed key stays private.
No verbatim personal answers enter the repository or any shared surface.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
import secrets
import string

INVENTORY_SCHEMA = "private_astrologer_complete_western_hd_14_better_hd_intervals_inventory_v01"

def sha(path: Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def random_labels(identifiers:list[str], seed:str)->list[tuple[str,str]]:
    if not identifiers or len(set(identifiers))!=len(identifiers):
        raise ValueError("Unique case identifiers required")
    if len(identifiers)>26:
        raise ValueError("Letter label limit")
    if not seed or len(seed)<16:
        raise ValueError("Seed must be private and high-entropy")
    order=identifiers[:]
    random.Random(seed).shuffle(order)
    return [(letter,id) for letter,id in zip(string.ascii_uppercase,order)]

def assessable_Western(case:dict)->str:
    w=case["chart_midpoint"]["Western"]
    witness=w["source_witness"]
    houses=w["regiomontanus_houses"]
    out=["**Western natal chart:**"]
    out.append(f"- Ascendant {witness['ascendant_sign']}; MC {witness['mc_sign']}; "+\
              f"sect {witness['sect']}; traditional Ascendant ruler {houses['traditional_ascendant_lord']}.")
    parts=[]
    for name,v in witness["traditional_planets"].items():
        house=houses["planet_houses"][name]
        dign=[k for k,b in v["essential_dignity"].items() if b]
        parts.append(f"{name}: {v['sign']} (whole-sign house {house['whole_sign_house']}; "+
                     f"Regiomontanus house {house['regiomontanus_house']}; "+
                     f"{', '.join(dign) if dign else 'no major sign dignity'})")
    out.extend(f"- {part}." for part in parts)
    out.append(f"- Moon elongation from Sun: {witness['moon_sun_geocentric_phase_degrees']}°; "+
               witness["moon_phase_witness"].replace("_"," ")+".")
    asp=witness["all_seven_planet_tight_aspects_within_3deg"]
    out.append("- Selected longitude contacts with **modern engineering orb <=3°** "+
               "(not the complete historical tradition's aspect doctrine): "+
               ("; ".join(f"{'-'.join(x['planets'])} {x['aspect']} ({x['orb_degrees']:.2f}°)" for x in asp)
                 if asp else "none within this particular cutoff")+".")
    out.append("- Interpret independently using a declared Western technique "+
               "(whole-sign or quadrant, traditional or modern); explicitly weigh "+
               "contradictory testimony and other aspects beyond this excerpt.")
    return "\n".join(out)

def assessable_HD(case:dict)->str:
    h=case["chart_midpoint"]["HD"]
    out=["**Human Design source structure:**"]
    out.append(f"- Type {h['type']}; Authority {h['authority']}; "+
               f"Profile {h['profile']}; definition {h['definition']}.")
    out.append("- Defined Centers: "+", ".join(h["defined_centers"])+".")
    out.append("- Complete Channels: "+", ".join(h["complete_channels"])+".")
    cross=h["cross_sun_earth_activations"]
    out.append("- Cross-forming Sun/Earth activations (personality Sun/Earth "+
               "| design Sun/Earth): "+
               f"{cross['personality:sun']['gate']}.{cross['personality:sun']['line']}/"+
               f"{cross['personality:earth']['gate']}.{cross['personality:earth']['line']} | "+
               f"{cross['design:sun']['gate']}.{cross['design:sun']['line']}/"+
               f"{cross['design:earth']['gate']}.{cross['design:earth']['line']}.")
    out.append("- Other gate-line activations: "+
               ", ".join(f"{k} {v['gate']}.{v['line']}"
                         for k,v in sorted(h["all_planet_carrier_gate_lines"].items()))+".")
    out.append("- Interpret using type, authority, profile, defined/open Centers, "+
               "channels and Incarnation Cross as a WHOLE, noting uncertainties and "+
               "truly distinctive observable claims; do not treat 44/26 and "+
               "hanging Gate 26 as independent evidence.")
    return "\n".join(out)

def make_packets(inventory:dict, seed:str)->tuple[dict,dict[str,str]]:
    if inventory.get("schema") != INVENTORY_SCHEMA:
        raise ValueError("Unexpected source inventory schema")
    rows=inventory["comparison_units"]
    ids=[r["private_id"] for r in rows]
    if len(ids)!=15 or len(set(ids))!=15 or "REFERENCE" not in ids:
        raise RuntimeError("Need all 14 alternatives plus exactly one reference")
    if not inventory.get("provisional_hd_only_not_joint_behavior_ranking"):
        raise RuntimeError("Cannot imply the alternatives are already better human matches")
    order=random_labels(ids,seed)
    byid={r["private_id"]:r for r in rows}
    seed_hash=sha256(seed.encode()).hexdigest()
    key={"schema":"private_practitioner_blind_key_v01",
         "source_inventory_sha256":None,"private_random_seed_sha256":seed_hash,
         "actual_chart_anonymous_letter":next(letter for letter,id in order if id=="REFERENCE"),
         "entry_mapping":[{"label":label,"private_id":id,"origin_utc":
                          byid[id]["chart_midpoint"]["utc"]}
                          for label,id in order],
         "instruction":"Do not reveal until practitioners freeze independent ratings"}
    opening=("# Anonymous natal-chart ranking packet\n\n"+
             "Research preparation; **no human astrologer or HD practitioner has yet reviewed these**. "+
             "The 15 cases consist of one reference and fourteen interval-midpoint comparators. "+
             "No participant name, DOB, birthplace, historic ranks or claimed correct answer "+
             "is supplied. All use the SAME private comparison location and a verified ephemeris. "+
             "No statistical independence or personality accuracy has been established.\n\n"+
             "## Independent review instructions\n\n"+
             "First state your interpretation method, what evidence could contradict "+
             "it, and whether you can read the chart without birth metadata. "+
             "Read EACH chart using the whole system rather than deciding by "+
             "the apparent rarity of one gate/aspect. "+
             "After receiving the separately frozen behavioral target, choose "+
             "which THREE charts fit best and THREE fit least; give at least "+
             "three falsifiable behaviors favoring and three opposing each "+
             "top chart. For ties, say TIE. No chart is presumed superior. "+
             "Freeze the observations and ranks before seeing the key. "+
             "These cases are post-exposure model DEVELOPMENT, not independent "+
             "astrological validation.\n\n")
    hd_txt=opening+"**Packet type:** HUMAN DESIGN. No Western placements provided.\n\n"
    western_txt=opening+"**Packet type:** WESTERN ASTROLOGY. No HD metadata provided.\n\n"
    for letter,id in order:
        row=byid[id]
        hd_txt+=f"## Chart {letter}\n\n"+assessable_HD(row)+"\n\n"
        western_txt+=f"## Chart {letter}\n\n"+assessable_Western(row)+"\n\n"
    key["entry_count"]=len(order)
    key["external_feedback_status"]="NOT_REQUESTED_NOT_OBTAINED"
    return key, {"HD":hd_txt,"Western":western_txt}

def run(args:argparse.Namespace)->dict:
    inventory=json.loads(args.inventory.read_bytes())
    seed=secrets.token_hex(32)  # private; no public stochastic source or chart bias
    key,packets=make_packets(inventory,seed)
    key["source_inventory_sha256"]=sha(args.inventory)
    target={
        "key":args.outdir/"private_practitioner_sealed_key_v01.json",
        "HD":args.outdir/"private_practitioner_hd_blind_packet_v01.md",
        "Western":args.outdir/"private_practitioner_western_blind_packet_v01.md",
    }
    if any(f.exists() for f in target.values()):
        raise FileExistsError("Refuse overwrite of blind package/key")
    args.outdir.mkdir(parents=True,exist_ok=True)
    data={k:(json.dumps(key,indent=2,sort_keys=True)+"\n" if k=="key" else packets[k])
          for k in target}
    for k,p in target.items():p.write_text(data[k])
    return {"status":"PRIVATE_PREPARATION_ONLY_NO_PRACTITIONER_YET",
            "blind_entries":len(key["entry_mapping"]),
            "key_sha256":sha(target["key"]),
            "hd_packet_sha256":sha(target["HD"]),
            "western_packet_sha256":sha(target["Western"]),
            "separate_domains":True,
            "human_review_completed":False}

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--inventory",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    print(json.dumps(run(p.parse_args()),sort_keys=True))
if __name__=="__main__":main()
