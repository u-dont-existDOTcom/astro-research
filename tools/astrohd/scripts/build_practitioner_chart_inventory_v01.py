#!/usr/bin/env python3
"""Full-chart practitioner comparison inventory, NOT human astrology validation.

Reuse source-verified PRIVATE exact HD intervals and one fixed natal location.
Chart facts are never checked into Git. Enumerate every strictly higher-ranked
structural interval from the original provisional V3.7 HD-only century search,
plus the recorded reference. Do not assume Western geometry is constant inside
an exact *HD* interval; perform a scoped ascending-sign sweep as an explicit
approximation. 'Better score' is never 'better human personality'.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any

import swisseph as swe
from hdmatch.runtime.chart_adapter import ExactChartAdapter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from replay_v37_development_direct_hd_observables import from_engine, utc
from ptolemy_iii13_source_condition_witness import (
    PLANETS, RULERS, SIGNS, chart_facts,
)

ORIGINAL_RANK_SHA = "b930e87a366a7d06d0efe40c9ec83044be62116935ec1a986b06c3868fcf9bce"
RANK_STATUS = "EXPLORATORY_V37_CORRECTED_OBSERVABLES_REUSE_OF_V36_HD_PATHWAYS"
WITNESS_STATUS = "SOURCE_CONDITION_WITNESS_ONLY_NO_WESTERN_PERSONALITY_SCORING"
EXPECTED_EPHE = {
    "sepl_18.se1": "ca1393ceab3a44fbc895887cf789c68819ae6a1cbc9b22225872dbe4ccd99a66",
    "semo_18.se1": "1ca07bd67c24374d77226180c20a4f9996cba013697894810518e7eb582ca4f7",
}
ANGLES = {"regiomontanus": b"R"}
PART_OF_CENTURY = "PRIVATE_FULL_14_STRICTLY_HIGHER_HD_STRUCTURAL_INTERVALS"

def sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

def jd_for(when: datetime) -> float:
    when = when.astimezone(timezone.utc)
    return swe.julday(when.year, when.month, when.day,
                      when.hour + when.minute/60 + when.second/3600
                      + when.microsecond/3.6e9)

def ascendant_deg(when: datetime, site: dict) -> float:
    return float(swe.houses_ex(jd_for(when), site["latitude"],
                    site["longitude"], b"R", swe.FLG_SWIEPH)[1][0])

def rising_sweep(start: datetime, end: datetime, site: dict,
                 cadence_minutes: int = 5) -> dict:
    """5-minute *survey* of possible rising signs, NOT a certified cusp solver."""
    if end <= start or cadence_minutes < 1:
        raise ValueError("Invalid sweep window")
    times: list[datetime] = [start]
    step = timedelta(minutes=cadence_minutes)
    t = start + step
    while t < end:
        times.append(t)
        t += step
    times.append(end-timedelta(microseconds=1))
    names = []
    for t in times:
        sign = SIGNS[int(ascendant_deg(t,site)/30)]
        if not names or names[-1] != sign:
            names.append(sign)
    return {
        "method": f"five-minute chart-sweep plus endpoints; NOT guaranteed exact continuous sign coverage",
        "rising_signs_seen_in_time_order": names,
        "samples": len(times),
        "not_full_western_interval_certification": True,
    }

def house_rulers_and_angles(when: datetime, site: dict) -> dict:
    jd = jd_for(when)
    cusps, angles = swe.houses_ex(jd, site["latitude"], site["longitude"], b"R", swe.FLG_SWIEPH)
    eps = swe.calc_ut(jd, swe.ECL_NUT, swe.FLG_SWIEPH)[0][0]
    asc_lon = float(angles[0]);asc_sign = int(asc_lon//30)
    planets = {}
    for planet, code in PLANETS.items():
        pos,ret = swe.calc_ut(jd, code, swe.FLG_SWIEPH | swe.FLG_SPEED)
        if (ret & (swe.FLG_SWIEPH | swe.FLG_MOSEPH | swe.FLG_JPLEPH)) != swe.FLG_SWIEPH:
            raise RuntimeError("Expected Swiss ephemeris, got fallback")
        lon,lat = float(pos[0]),float(pos[1])
        ph = swe.house_pos(float(angles[2]),site["latitude"],eps,(lon,lat),b"R")
        if not 1 <= ph < 13:
            raise RuntimeError("Invalid Regiomontanus house")
        planets[planet] = {
            "longitude_degrees": round(lon,7),
            "latitude_degrees": round(lat,7),
            "retrograde": bool(pos[3]<0),
            "whole_sign_house": (int(lon//30)-asc_sign)%12 + 1,
            "regiomontanus_house": int(ph),
            "regiomontanus_house_decimal": round(ph,4),
        }
    # A planet exactly on a house boundary can switch house under small changes.
    return {
        "regiomontanus_ascendant_longitude_degrees": round(asc_lon,7),
        "traditional_ascendant_lord": RULERS[asc_sign],
        "angle_scheme": "Regiomontanus for later Lilly-based comparison; whole-sign separately",
        "planet_houses":planets,
        "planetary_sect_honorability": "UNCOMPILED_NOT_AUTOMATIC_CHARACTER_POINTS",
    }

def chart_for(when: datetime, site: dict, adapter: ExactChartAdapter) -> dict:
    chart = adapter.calculate(when)
    state = from_engine(chart)
    active = {
        side: {"gate":int(a.gate),"line":int(a.line)}
        for side,a in chart.activations.items()
    }
    cross = {}
    for field in ("personality:sun","personality:earth","design:sun","design:earth"):
        if field not in active:
            raise RuntimeError("Missing defining Sun/Earth HD activation")
        cross[field] = active[field]
    return {
        "utc": when.isoformat(),
        "HD":{
            "type":state["type"],"authority":state["auth"],"profile":state["profile"],
            "definition":state["definition"],
            "defined_centers":sorted(state["centers"]),
            "complete_channels":["-".join(map(str,p)) for p in sorted(state["channels"])],
            "cross_sun_earth_activations":cross,
            "all_planet_carrier_gate_lines":active,
        },
        "Western":{
            "source_witness":chart_facts(when, site),
            "regiomontanus_houses":house_rulers_and_angles(when,site),
        },
    }

def run(args:argparse.Namespace) -> dict:
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():
        raise FileExistsError("Private output exists; never overwrite")
    if swe.version != "2.10.03":
        raise RuntimeError("Swiss version changed")
    if sha(args.rank) != ORIGINAL_RANK_SHA:
        raise RuntimeError("Historic V3.7 HD century rankings differ")
    for name,digest in EXPECTED_EPHE.items():
        if sha(args.ephemeris/name) != digest:
            raise RuntimeError("Swiss source ephemeris checksum differs "+name)
    swe.set_ephe_path(str(args.ephemeris))
    rank=json.loads(args.rank.read_bytes())
    witness=json.loads(args.witness.read_bytes())
    if rank.get("status") != RANK_STATUS or witness.get("status") != WITNESS_STATUS:
        raise RuntimeError("Wrong private source study epoch")
    if witness.get("private_candidate_rank_sha256") != sha(args.rank):
        raise RuntimeError("Western witness and HD rank were not from one run")
    top=rank["full_century_provisional_HD_only_ranking"]
    if top["structural_interval_count"] != 288908:
        raise RuntimeError("Wrong historic century cache")
    intervals=top["top20"]
    refs=top["reference_and_alternative_interval_ranks"]
    if refs[0]["unmerged_structural_order"] != 16 or (
            refs[0]["strictly_better_substantive_score_states"] != 14):
        raise RuntimeError("The source rank and strict superiority count changed")
    if len(intervals)<15:
        raise RuntimeError("Cannot prove all 14 substantive higher states present")
    actual_score=rank["comparison_charts"][0]["development_net_rubric_bits"]
    if abs(actual_score-9.4704565)>0.0000001:
        raise RuntimeError("Historic reference score changed")
    # All 14 listed intervals have higher score, whereas item 15 ties.
    strictly_better = intervals[:14]
    if not all(r["net_rubric_bits"]>actual_score for r in strictly_better):
        raise RuntimeError("Some candidate is not strictly higher-scoring")
    if intervals[14]["net_rubric_bits"] != actual_score:
        raise RuntimeError("Equal scoring control changed")
    site=witness["reference"]["site"]
    ref=utc(witness["reference"]["UTC"])
    adapter=ExactChartAdapter(args.ephemeris)
    if abs((utc(strictly_better[0]["start_utc"])+(
        utc(strictly_better[0]["end_exclusive_utc"])-utc(strictly_better[0]["start_utc"]))/2-
         utc(witness["alternative"]["UTC"])).total_seconds())>1e-5:
        raise RuntimeError("Top candidate mismatch from prior Western witness")
    rows=[{
        "private_id":"REFERENCE","chronological_interval_rank":16,
        "historical_score":actual_score,"chart_midpoint":chart_for(ref,site,adapter),
        "rising_sweep":None,
    }]
    for i,r in enumerate(strictly_better,1):
        start,end=utc(r["start_utc"]),utc(r["end_exclusive_utc"])
        point=start+(end-start)/2
        row={
            "private_id":f"C{i:02d}","chronological_interval_rank":i,
            "start_utc":start.isoformat(),"end_utc_exclusive":end.isoformat(),
            "historical_score":r["net_rubric_bits"],
            "interval_duration_hours":round((end-start).total_seconds()/3600,7),
            "chart_midpoint":chart_for(point,site,adapter),
            "rising_sweep":rising_sweep(start,end,site,5),
        }
        if row["chart_midpoint"]["HD"]["profile"]!=r["profile"]:
            raise RuntimeError("Profile drift on computed midpoint")
        if sorted(row["chart_midpoint"]["HD"]["complete_channels"])!=sorted(r["channels"]):
            raise RuntimeError("Full channels drift on computed midpoint")
        rows.append(row)
    data={
        "schema":"private_astrologer_complete_western_hd_14_better_hd_intervals_inventory_v01",
        "scope":PART_OF_CENTURY,
        "provisional_hd_only_not_joint_behavior_ranking":True,
        "complete_strict_higher_HD_state_coverage":14,
        "all_midpoints_contain_exactly_one_HD_structural_state":True,
        "Western_interval_ascendant_continuity":"NOT_PROVEN; sweep only",
        "predictive_accuracy":"NOT_ESTABLISHED",
        "human_professional_review":"NOT_YET_PERFORMED",
        "reference_v37_rank_unchanged":16,
        "same_private_place_for_every_comparison":True,
        "private_chart_location":site,
        "source_sha256":{"historic_hd_rank":sha(args.rank),"western_witness":sha(args.witness)},
        "comparison_units":rows,
    }
    b=(json.dumps(data,sort_keys=True,indent=2)+"\n").encode()
    args.output.write_bytes(b)
    summary={
        "status":PART_OF_CENTURY,
        "complete_strictly_higher_source_intervals":len(strictly_better),
        "source_date_families":len({r["start_utc"][:10] for r in strictly_better}),
        "inventory_sha256":sha256(b).hexdigest(),
        "original_source_unchanged":True,
    }
    return summary

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--rank",type=Path,required=True)
    p.add_argument("--witness",type=Path,required=True)
    p.add_argument("--ephemeris",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    print(json.dumps(run(p.parse_args()),sort_keys=True))

if __name__=="__main__":
    main()
