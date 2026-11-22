#!/usr/bin/env python3
"""Check that completion claims never exceed observed astrology artifacts.

This deliberately does not assert that the historical text is correct or that
the astrophysical source has predictive human validity. It checks the public
milestones and root status, keeping full-root outcome OPEN until genuinely
source-complete, unbiased human behavioral evaluation is available.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
MATRIX=ROOT/"state/RESEARCH-COMPLETION-SCOPE.json"
HOUSE=ROOT/"tools/astrohd/reference/research/lilly_1647_house_accidental_fortitude_full_century_public_v01.json"
PTOLEMY=ROOT/"tools/astrohd/reference/research/ptolemy_lilly_hd_same_instant_public_census_v01.json"

LANE_STATUSES={
 "source_documentary_intake":"PARTIAL_OVERALL",
 "western_planetary_grid":"COMPLETE_DECLARED_FINITE_GRID_ONLY",
 "hd_structural_join":"COMPLETE_DECLARED_FINITE_GRID_WITH_ABSTENTIONS",
 "ptolemy_iii13_full_governor":"PARTIAL_SOURCE_CONDITIONAL_ONLY",
 "lilly_cvii_full_manners_significator":"PARTIAL_SOURCE_CONDITIONAL_ONLY",
 "whole_century_behavioral_scorer":"NOT_RUN",
 "independent_human_accuracy":"NOT_ESTABLISHED",
 "global_first_rank_chart":"NOT_DETERMINED",
}
REQUIRED_SUFFIX=("method","population","scope","validation")

def audit(matrix:dict,house:dict,ptolemy:dict,root:Path)->dict:
    if matrix.get("schema")!="astro_research_completion_claims_scope_v01":
        raise ValueError("Unrecognized current claim-scope contract")
    if matrix.get("root_status")!="OPEN" or matrix.get("root_completion_certified") is not False:
        raise ValueError("Root owner outcome incorrectly completed")
    if len(matrix.get("coverage_layers",[]))!=len(LANE_STATUSES):
        raise ValueError("All material root project layers must be represented")
    lanes={r["id"]:r for r in matrix["coverage_layers"]}
    if set(lanes)!=set(LANE_STATUSES):
        raise ValueError("Incomplete or duplicate deliverable coverage")
    for key,status in LANE_STATUSES.items():
        lane=lanes[key]
        if lane.get("status")!=status:
            raise ValueError("Unverified completion/method promotion: "+key)
        if not all(lane.get(q) for q in ("subscope","missing","evidence_path")):
            raise ValueError("Completion boundary or unknowns missing: "+key)
        p=root/lane["evidence_path"]
        if not p.is_file():
            raise ValueError("Completion claim has no verifiable artifact: "+str(p))
    if house.get("samples")!=3506400 or house.get("HD_structural_intervals")!=288908:
        raise ValueError("Frozen declared original samples/HD states changed")
    hc=house["mechanical_counts"]
    if hc["HD_boundary_unassigned"]!=125 or hc["conditional_Ptolemy_fourmode_common"]!=4553:
        raise ValueError("Frozen original boundary abstentions or Ptolemy count changed")
    if house["no_complete_accidental_strength_or_manners_ruler"] is not True:
        raise ValueError("Partial house-strength result called complete historical ruler")
    if house["no_human_prediction_or_validated_rank"] is not True:
        raise ValueError("Astronomical census promoted to human prediction")
    if ptolemy["data_samples"]!=3506400 or ptolemy["human_predictive_validation"] is not False:
        raise ValueError("Ptolemy structural census incorrectly reported as human validation")
    if ptolemy["sample_counts"]["ptolemy_all_four_variants_same_robust_common_lord"]!=4553:
        raise ValueError("Conditional four-mode candidate baseline changed")
    if not all(matrix["rules"].values()):
        raise ValueError("Scope/unknown/private and predictive abstention rules must remain true")
    if len(matrix["prior_misleading_phrasing"])<4:
        raise ValueError("Previous completion-language correction missing")
    if "fixed-location" not in lanes["western_planetary_grid"]["subscope"].lower().replace("fixed source-neutral research location","fixed-location"):
        raise ValueError("One fixed research place must not be called universal worldwide century")
    if "next_safe_action" not in matrix or len(matrix["next_safe_action"])<40:
        raise ValueError("Open root work lacks explicit executable next action")
    return {
        "status":"PASS_SOURCE_SCOPED_COMPLETION_LABELS_ROOT_STILL_OPEN",
        "root_status":"OPEN",
        "source_documentary_not_execution":True,
        "finite_grid_not_all_locations_or_continuous_births":True,
        "root_human_predictive_validity_established":False,
        "root_unique_natal_rank_established":False,
        "material_lanes_checked":len(lanes),
        "sampled_UTC_clock":house["samples"],
        "independent_HD_states":house["HD_structural_intervals"]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    z=p.parse_args()
    print(json.dumps(audit(json.loads((z.root/"state/RESEARCH-COMPLETION-SCOPE.json").read_text()),
                           json.loads((z.root/"tools/astrohd/reference/research/lilly_1647_house_accidental_fortitude_full_century_public_v01.json").read_text()),
                           json.loads((z.root/"tools/astrohd/reference/research/ptolemy_lilly_hd_same_instant_public_census_v01.json").read_text()),
                           z.root),sort_keys=True))

if __name__=="__main__":main()
