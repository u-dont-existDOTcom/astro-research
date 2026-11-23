#!/usr/bin/env python3
"""Branch-bound proof that original Lilly 1647 CVII S1 was actually applied.

The task is BOUNDED: candidate eligibility among occupying planets under
three source-conditioned geometries, with partial 72-policy strength
sensitivity. Never report a completed full historical manners ruler or a
validated human behavior prediction. Branch preflight before execution;
artifact acceptance only after actual source-bound full-century run.
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
TASK="state/tasks/20261123-lilly-cvii-first-stage-eligibility.json"
AGG="tools/astrohd/reference/research/lilly_cvii_s1_eligible_partial_strength_full_century_public_v01.json"
MODES=("ascending_sign","regiomontanus_first_house",
       "ascending_sign_or_intercepted_sign")
EXPECTED={"ascending_sign":1428060,"regiomontanus_first_house":1409411,
          "ascending_sign_or_intercepted_sign":1516373}
PTOL_EXPECTED={"ascending_sign":1746,"regiomontanus_first_house":1920,
               "ascending_sign_or_intercepted_sign":1865}

def audit(root:Path,preflight=False):
    obj=json.loads((root/TASK).read_text())
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=root,text=True).strip()
    if branch!=obj["required_branch"] or obj["required_repo"]!="u-dont-existDOTcom/astro-research":
        raise ValueError("Active task branch/repository source preflight mismatch")
    if obj["task_status"] not in ("ACTIVE_BOUNDED_SUBTASK_PARENT_OPEN","BOUNDED_SUBTASK_MERGE_READY_PARENT_OPEN"):
        raise ValueError("Task source status not active/ready")
    if not obj["suspended_competing_task_sources"] or not obj["privacy"]:
        raise ValueError("Competing tasks or privacy not explicitly covered")
    if preflight:
        return {"status":"PASS_ACTIVE_S1_TASK_PREFLIGHT","branch":branch,
                "root_historical_and_human_outcome":"OPEN"}
    p=root/AGG
    if not p.exists():raise ValueError("Original full-century source artifact absent")
    j=json.loads(p.read_text());c=j["counts"]
    if j["source_UTC_samples"]!=3506400 or j["source_sensitive_S1_x_partial_strength_policy_count"]!=216:
        raise ValueError("Not all original finite clock samples or 216 source scenarios computed")
    if (c["HD_root_margin_unassigned"]!=125 or c["conditional_ptolemy_4mode_sample"]!=4553 or
        c["sect_horizon_uncertain"]!=5049):
        raise ValueError("Old original independent source cohorts changed")
    for mode in MODES:
        zero=c[mode+"|empty_go_to_later_stages"]
        one=c[mode+"|sole_primary_occupant"]
        multi=c[mode+"|multiple_principal_occupants"]
        if zero+one+multi!=3506400 or one+multi!=EXPECTED[mode]:
            raise ValueError("Lilly first-stage source-eligibility partition drift")
        if c[mode+"|conditional_ptolemy_first_present"]!=PTOL_EXPECTED[mode]:
            raise ValueError("Same UTC Ptolemy/Lilly source first-stage overlap drift")
        if c[mode+"|stable_all72_sole_occupant"]!=one:
            raise ValueError("Sole original source occupancies must not disappear")
        if c[mode+"|stable_all72_multi_partial_candidate"]>multi:
            raise ValueError("Partial strength winner inflated beyond eligible multiple bodies")
        for name in ("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"):
            if c[mode+"|sole_"+name]>c[mode+"|occupant_"+name]:
                raise ValueError("Noneligible classical planet or nonsource sole count")
    if (j["historically_final_Lilly_manners_significator_computed"] or
        j["independent_human_behavior_criterion_used"] or
        j["owner_or_third_party_private_birth_records_loaded"]):
        raise ValueError("Source-only first-stage counted as personal behavioral research or historical ruler")
    if not j["ptolemy_actual_soul_governor_not_computed"]:
        raise ValueError("Ptolemy incomplete source testimony disguised as final governor")
    for rel in obj["required_artifacts"]:
        if not (root/rel).is_file():raise ValueError("Required durable source artifact absent "+rel)
    return {"status":"PASS_SOURCE_BOUND_ORIGINAL_1647_S1_COMPLETE_BOUNDED_ONLY",
            "UTC_clock_samples":3506400,"scenarios":216,
            "root_historical_and_human_outcome":"OPEN",
            "HD_unknown_samples":125,"ptolemy_conditional_samples":4553}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--preflight",action="store_true")
    args=parser.parse_args()
    print(json.dumps(audit(ROOT,args.preflight),sort_keys=True))

if __name__=="__main__":main()
