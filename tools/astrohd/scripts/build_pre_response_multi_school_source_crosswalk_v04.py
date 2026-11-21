#!/usr/bin/env python3
"""Pre-response, source-witness crosswalk: 1 recorded + 14 old HD shortlist charts.

Chart geometry is verifiable, but astrology-to-personality conjectures are NOT
calibrated probabilities or scores. The 14 previous cases are an HD-only
filtered panel, never a certified winner set for the NEW combined model.
No true birth timestamp, names, place or interview quotations are returned.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

INVENTORY_SHA = "063442574493887e526c124a5f32f7bcba67c477f417c6a5859d279aae8e087b"
QUESTION_SHA = "0158106c51530142c2ec2620bbfb0bf0dc3258aa18ef9150cf86b61cc0470e1d"
SCHOOLS = ("HD_SOURCE", "PTOLEMY_III13_PARTIAL", "LILLY_MANNERS_PARTIAL",
           "MODERN_WESTERN_PARTIAL")
SIGNS = ("Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces")
TRAD_RULERS = ("Mars","Venus","Mercury","Moon","Sun","Mercury",
               "Venus","Mars","Jupiter","Saturn","Saturn","Jupiter")
MODE = {
 "Aries":"equinoctial","Libra":"equinoctial",
 "Cancer":"solstitial","Capricorn":"solstitial",
 "Taurus":"fixed","Leo":"fixed","Scorpio":"fixed","Aquarius":"fixed",
 "Gemini":"bicorporeal","Virgo":"bicorporeal",
 "Sagittarius":"bicorporeal","Pisces":"bicorporeal",
}
EXPECTED_IDS={"REFERENCE"} | {f"C{i:02}" for i in range(1,15)}
REF_EXPECTED_QUESTIONS={f"C{i:02}" for i in range(1,11)}

def sha(path:Path)->str: return sha256(path.read_bytes()).hexdigest()

def audit_question_bank(bank:dict)->None:
    if bank.get("schema")!="astrohd_multi_school_contrast_question_bank_v04":
        raise ValueError("Wrong frozen question bank")
    qs=bank["questions"]
    ids=[q["id"] for q in qs]
    if set(ids)!=REF_EXPECTED_QUESTIONS or len(ids)!=len(set(ids)):
        raise ValueError("Question scope drift")
    for q in qs:
        if q.get("automatic_natal_score")!="NO" or q.get("research_status")!="SELECTED_PRE_OWNER_RESPONSE":
            raise RuntimeError("Blind source contract was silently rewritten")
        if not q["text"] or not q["response_shape"] or not q["source_context"]:
            raise ValueError("Empty source-facing question")
    if len(bank.get("school_coverage",[]))!=4:
        raise ValueError("Missing Western/HD schools")

def case_witness(u:dict)->dict:
    h=u["chart_midpoint"]["HD"]
    w=u["chart_midpoint"]["Western"]["source_witness"]
    if h["type"]!="Projector":raise RuntimeError("Unexpected comparison Type")
    p=w["traditional_planets"]
    asc=w["ascendant_sign"]
    if asc not in SIGNS:raise ValueError("Invalid rising sign")
    moon=p["Moon"]["sign"]
    mercury=p["Mercury"]["sign"]
    if moon not in MODE or mercury not in MODE:
        raise ValueError("Unexpected Moon/Mercury sign")
    ruler=TRAD_RULERS[SIGNS.index(asc)]
    if ruler not in p:raise RuntimeError("Missing Ascendant ruler")
    chan=set(h["complete_channels"])
    cross=h["cross_sun_earth_activations"]
    cross_gates=[cross[x]["gate"] for x in ("personality:sun","personality:earth",
                                          "design:sun","design:earth")]
    aspects=w["all_seven_planet_tight_aspects_within_3deg"]
    sun_mars_square=any(x["aspect"]=="square" and
                 set(x["planets"])=={"Sun","Mars"} for x in aspects)
    # These are observed chart-carrier contrasts, not positive/negative
    # claims about the person. No missing trait is inferred from 0 carrier.
    return {
      "case_id":u["private_id"],
      "HD":{
        "profile":h["profile"],"authority":h["authority"],
        "channels":sorted(chan),"cross_gates_personality_sun_earth_design_sun_earth":cross_gates,
      },
      "PTOLEMY_III13_PARTIAL":{
        "Mercury_sign":mercury,"Mercury_sign_class":MODE[mercury],
        "Moon_sign":moon,"Moon_sign_class":MODE[moon],
        "governor_and_contrary_conditions":"NOT_COMPUTED",
      },
      "LILLY_MANNERS_PARTIAL":{
        "ASC_sign":asc,"ASC_ruler":ruler,
        "ruler_sign":p[ruler]["sign"],
        "ruler_basic_dignity":p[ruler]["essential_dignity"],
        "manner_significator_not_necessarily_ASC_ruler":True,
        "exact_house_boundary_coverage":"ONE_ILLUSTRATIVE_MIDPOINT",
      },
      "MODERN_WESTERN_PARTIAL":{
        "Sun_sign":p["Sun"]["sign"],
        "close_Sun_Mars_square_3deg":sun_mars_square,
        "outer_planet_source":"SEPARATE_PINNED_OPTIONAL_V01_NOT_REEVALUATED_BY_THIS_CROSSWALK",
      },
      "source_feature_tags":{
        "HD_RULERSHIP_CONSCIOUS_GATE45":cross_gates[0]==45,
        "HD_CONSENSUS_LEADERSHIP_CH7_31":"7-31" in chan,
        "HD_EXPERIENCE_PRIVACY_CH13_33":"13-33" in chan,
        "HD_RECIPROCITY_VALUES_CH19_49":"19-49" in chan,
        "HD_EXPERIENCE_CYCLE_CH30_41":"30-41" in chan,
        "HD_CORRECTION_CH18_58":"18-58" in chan,
        "HD_DETAILS_CH17_62":"17-62" in chan,
        "HD_5th_line_profile":"5" in h["profile"].split("/"),
        "HD_3rd_line_profile":"3" in h["profile"].split("/"),
        "WEST_MERCURY_VIRGO":mercury=="Virgo",
        "WEST_MOON_TAURUS":moon=="Taurus",
        "WEST_SUN_LEO":p["Sun"]["sign"]=="Leo",
        "WEST_CLOSE_SUN_MARS_SQUARE":sun_mars_square,
      },
      "chart_to_behavior_fit":"UNSCORED",
      "negative_survey_evidence":None,
    }

def run(bank:dict,inventory:dict)->dict:
    audit_question_bank(bank)
    if inventory.get("schema")!="private_astrologer_complete_western_hd_14_better_hd_intervals_inventory_v01":
        raise ValueError("Wrong source inventory")
    units=inventory["comparison_units"]
    ids=[x["private_id"] for x in units]
    if len(units)!=15 or set(ids)!=EXPECTED_IDS:
        raise ValueError("Missing old-chart candidate: no partial shortlist permitted")
    rows=[case_witness(x) for x in units]
    counts={}
    for key in rows[0]["source_feature_tags"]:
        counts[key]=sum(int(r["source_feature_tags"][key]) for r in rows)
    return {
      "schema":"private_pre_response_multi_school_source_chart_crosswalk_v04",
      "status":"FROZEN_SOURCE_WITNESS_NOT_RANKED_OR_CALIBRATED",
      "source_years_or_exact_private_birth_metadata_included":False,
      "comparison_universe":"OLD_HD_FILTERED_14_PLUS_REFERENCE_NOT_CERTIFIED_ALL_CENTURY_NEW_MODEL",
      "question_bank_expected_sha256":QUESTION_SHA,
      "case_count":len(rows),
      "source_school_names":SCHOOLS,
      "source_feature_counts_panel":counts,
      "rows":rows,
      "no_behavioral_prediction_probability":True,
      "no_natal_chart_priority_from_essential_dignity":True,
      "no_chart_absence_is_behavioral_negation":True,
      "no_scored_new_model":True,
      "full_continuous_Western_interval_coverage":False,
    }

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--question-bank",required=True,type=Path)
    p.add_argument("--private-inventory",required=True,type=Path)
    p.add_argument("--out-private",required=True,type=Path)
    a=p.parse_args()
    if a.out_private.exists():raise FileExistsError("Cannot overwrite sealed pre-response witness")
    if sha(a.question_bank)!=QUESTION_SHA or sha(a.private_inventory)!=INVENTORY_SHA:
        raise RuntimeError("Source pinned SHA no longer matches")
    obj=run(json.loads(a.question_bank.read_bytes()),json.loads(a.private_inventory.read_bytes()))
    obj["private_inventory_sha256"]=INVENTORY_SHA
    obj["question_bank_sha256"]=QUESTION_SHA
    data=json.dumps(obj,indent=2,sort_keys=True)+"\n"
    a.out_private.parent.mkdir(parents=True,exist_ok=True)
    a.out_private.write_text(data)
    print(json.dumps({
      "status":obj["status"],
      "cases":len(obj["rows"]),
      "source_classes":list(SCHOOLS),
      "panel_carrier_counts":obj["source_feature_counts_panel"],
      "private_sha256":sha(a.out_private),
    },sort_keys=True))
if __name__=="__main__":main()
