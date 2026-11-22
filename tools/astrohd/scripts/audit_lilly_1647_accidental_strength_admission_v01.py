#!/usr/bin/env python3
"""Lilly original first-print p115–116 source-coverage gate for complete strength.

This is NOT a full numeric strength model: it prevents prior partial
positive 5/4/3/2/1 essential dignity candidate outputs from being promoted to
actual 1647 essential+accidental manners rulers while receptions, negative
dignities, planetary speeds, original orientation and star epoch are missing.
Only public source-neutral metadata/aggregate; never birth or interview files.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/"reference/research"
LEDGER="lilly_1647_accidental_fortitudes_debilities_source_coverage_v01.json"
PRIOR="lilly_cvii_original_essential_dignity_final_fallback_public_v01.json"
SOURCE_P115="fe75468d8eaf129a1f643d6d652455e81eb95b0aedd3016091e3ce7c204e4aab"
PRIOR_DIGEST="e095a691b0c2d9f92c657bcf8a73a13144ff5b8d62f513dd5454852275d78467"
REQUIRED_MISSING={
 "domicile_or_mutual_reception_by_house",
 "exaltation_or_mutual_reception_by_exaltation",
 "detriment","fall","peregrine",
 "retrograde","swift_motion","slow_motion",
 "regulus_cor_leonis_conjunction","spica_conjunction","algol_conjunction",
 "mercury_venus_oriental","saturn_jupiter_mars_occidental",
 "midheaven_or_ascendant_house","under_sun_beams",
}

def audit(source_bytes,previous_bytes):
    data=json.loads(source_bytes)
    prior=json.loads(previous_bytes)
    proof=hashlib.sha256(previous_bytes).hexdigest()
    if proof!=PRIOR_DIGEST or data["prior_source_bound_output"]["previous_numeric_aggregate_sha256"]!=proof:
        raise ValueError("Old frozen source-neutral 5-component evidence overwritten")
    if data.get("schema")!="lilly_1647_original_fortitudes_debilities_source_coverage_v01":
        raise ValueError("Invalid original source coverage contract")
    if data["source"]["original_page_render_sha256"].get("115")!=SOURCE_P115:
        raise ValueError("Direct 1647 original p115 identity not frozen")
    if data["source"]["source_scanned_pdf_sha256"]!="2cb53e20e122ffc6e47917ba10241f6c49687cd7a4696f3b5db655a2a1aab28b":
        raise ValueError("Wrong authorized original-source PDF")
    rules=data["original_first_print_scored_components"]
    ids=[x["id"] for x in rules]
    if len(ids)!=len(set(ids)) or len(ids)<34:
        raise ValueError("Missing or duplicate original source fortitudes or debilities")
    missing=REQUIRED_MISSING-set(ids)
    if missing:raise ValueError("Full-strength gate missing source rules: "+",".join(sorted(missing)))
    family={x["family"] for x in rules}
    if family!={"essential_positive","essential_negative",
               "accidental_positive","accidental_negative"}:
        raise ValueError("Four original table categories must remain separate")
    for x in rules:
        if x["source_read"]!="DIRECT" and x["implementation_status"]=="IMPLEMENTED":
            raise ValueError("Unclear source glyph cannot certify a numerical score")
        if x["points"] is not None and (not isinstance(x["points"],int) or abs(x["points"])>8):
            raise ValueError("Original tabular score not normalized")
        if x["family"].endswith("negative") and x["points"] is not None and x["points"]>0:
            raise ValueError("Debility polarity reversed")
        if x["family"].endswith("positive") and x["points"] is not None and x["points"]<0:
            raise ValueError("Fortitude polarity reversed")
    old=data["prior_source_bound_output"]
    if (old["actual_1647_complete_essential_dignity_with_receptions_and_penalties"] is not False
        or old["actual_1647_complete_accidental_strength_and_debilities"] is not False
        or old["source_unique_Lilly_manners_ruler"] is not False
        or old["human_natal_predictive_validity_established"] is not False):
        raise ValueError("Partial preexisting positive score promoted without source qualification")
    if (data["decision"]["full_source_strength_admissible_now"] is not False
        or data["decision"]["complete_personality_rank_admissible_now"] is not False
        or data["decision"]["no_private_evidence_in_public_register"] is not True):
        raise ValueError("Cannot admit source-incomplete full ruler/personality ranking")
    available=data["certified_software_inputs"]
    if available["complete_all_fortitude_rules_from_existing_cached_columns"] is not False:
        raise ValueError("Missing historical planet motion/nodes/star inputs hidden")
    if not all(a in available["original_planets"] for a in
               ("Sun_lon","Moon_lon","Mercury_lon","Mercury_lon_speed")):
        raise ValueError("Original finite source-grid provenance missing")
    if prior["samples"]!=3506400 or prior["HD_structural_interval_total"]!=288908:
        raise ValueError("Prior source-neutral century denominator changed")
    return {"status":"PASS_ORIGINAL_1647_ACCIDENTAL_FULL_STRENGTH_BLOCKED",
            "original_source_rules":len(rules),
            "blocked_required_components":len([x for x in rules if
               x["implementation_status"] not in
               ("IMPLEMENTED_CONDITIONALLY_WITH_NEAR_HORIZON_ABSTENTION",
                "IMPLEMENTED_IN_THREE_ORIGINAL_PRINT_VARIANTS",
                "IMPLEMENTED_FOR_THREE_PRINT_SCHEMES")]),
            "preserved_prior_source_sha256":proof,
            "historical_final_manners_ruler_scored":False,
            "human_predictive_validation":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=BASE)
    a=ap.parse_args()
    print(json.dumps(audit((a.root/LEDGER).read_bytes(),(a.root/PRIOR).read_bytes()),sort_keys=True))
if __name__=="__main__":main()
