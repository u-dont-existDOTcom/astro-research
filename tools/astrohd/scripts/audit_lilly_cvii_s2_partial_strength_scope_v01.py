#!/usr/bin/env python3
"""Fail-closed original Lilly CVII S2 joined partial-strength acceptance.

Source-bound original 1647 joins after first-stage empty only. 12 original
S1-space x printed orb x candidate-scope eligibility method alternatives
each crossed with 72 partial natal fortitude methods (864 total). Root
historical manners ruler and human predictive validation remain OPEN.

Task branch preflight is strict. Acceptance requires exact original S2
counts and source-bound original century report. No private case records.
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TASK="state/tasks/20261123-lilly-CVII-S2-joined-partial-strength.json"
RESULT="tools/astrohd/reference/research/lilly_cvii_s2_joined_partial_strength_full_century_public_v01.json"
OLDER="tools/astrohd/reference/research/lilly_cvii_s2_original_joining_full_century_public_v01.json"
MODES=("ascending_sign","regiomontanus_first_house",
       "ascending_sign_or_intercepted_sign")
ORBS=("1647_table_smaller_orbs","1647_table_larger_orbs")
SCOPES=("four_externals_only","all_other_classical_planets")
NUM=3506400

def check(root:Path,preflight:bool=False):
    task=json.loads((root/TASK).read_text())
    branch=subprocess.check_output(
        ["git","branch","--show-current"],cwd=root,text=True).strip()
    if branch!=task["required_branch"]:
        raise ValueError("Wrong branch for original source S2 partial task")
    if task["required_repo"]!="u-dont-existDOTcom/astro-research" or not task["suspended_competing_task_sources"]:
        raise ValueError("Wrong active public repo or task collision")
    if task["status"] not in ("ACTIVE_BOUNDED_SUBTASK_PARENT_OPEN",
                              "BOUNDED_SUBTASK_REVIEW_READY_PARENT_OPEN"):
        raise ValueError("Root task status unexpectedly promoted")
    if preflight:
        return {"status":"PASS_ORIGINAL_S2_PARTIAL_BRANCH_PREFLIGHT",
                "root_historical_behavioral_goal":"OPEN"}
    for rel in task["required_artifacts"]:
        if not (root/rel).is_file():
            raise ValueError("Missing source acceptance output "+rel)
    j=json.loads((root/RESULT).read_text())
    old=json.loads((root/OLDER).read_text())["counts"]
    c=j["counts"]
    if j["samples"]!=NUM or j["all_eligibility_x_partial_strength_policy_count"]!=864:
        raise ValueError("Source clock or full 12x72 scenario coverage changed")
    if (c["HD_root_unknown"]!=125 or c["near_sun_horizon_sect_unknown"]!=5049
        or c["ptolemy_conditional_fourmode_common"]!=4553 or
        j["HD_structural_intervals"]!=288908):
        raise ValueError("Original same-time Ptolemy/HD source cohorts drift")
    if j["original_all_stage_Lilly_manners_ruler_computed"] is not False:
        raise ValueError("Incomplete original ruler accidentally reported as final")
    if j["individual_personality_predictive_accuracy_established"] is not False:
        raise ValueError("Source-only celestial agreement is not human validation")
    if j["private_natal_or_interview_data_loaded"] is not False:
        raise ValueError("Owner or participant private data outside authorized public path")
    for mode in MODES:
        for orb in ORBS:
            for scope in SCOPES:
                prefix="|".join((mode,orb,scope))
                for newname,oldname in (
                    ("S2_sole","S2_one_joined_planet"),
                    ("S2_multi","S2_multiple_joined_planets"),
                    ("S2_any","S2_any"),
                    ("S2_empty_go_to_later","S2_zero_proceed_to_S3"),
                    ("S2_ptolemy_any","S2_ptolemy_any")
                ):
                    if c[prefix+"|"+newname]!=old[prefix+"|"+oldname]:
                        raise ValueError("Source eligible S2 previous original astronomy changed "+prefix)
                if c[prefix+"|stable_all72_sole"]!=old[prefix+"|S2_one_joined_planet"]:
                    raise ValueError("Sole S2 candidate may not vanish from partial score uncertainty")
                if (c[prefix+"|stable_all72_sole"]+
                    c[prefix+"|stable_all72_multi_strict"]!=
                    c[prefix+"|stable_all72_any"]):
                    raise ValueError("Multi-stage source candidate consensus broken")
                if c[prefix+"|stable_all72_multi_strict"]>old[prefix+"|S2_multiple_joined_planets"]:
                    raise ValueError("Conditional S2 candidate invented")
                for terms in j["partial_strength_variants"]["terms"]:
                    for policy in j["partial_strength_variants"]["reception_peregrine"]:
                        for house in j["partial_strength_variants"]["houses"]:
                            for t in j["partial_strength_variants"]["station_numerical_not_source_authored"]:
                                tag="|".join((terms,policy,house,f"station={t:.2f}"))
                                if (c[prefix+"|"+tag+"|conditional_candidate"]+
                                    c[prefix+"|"+tag+"|multi_unknown_strength"]+
                                    c[prefix+"|S2_empty_go_to_later"] !=
                                    old[mode+"|S1_empty"]):
                                    raise ValueError("Every 864 original S2 model must account for S1-empty")
    return {"status":"PASS_1647_S2_ALL_864_ORIGINAL_SOURCE_CONDITIONAL_PARTIAL_STRENGTH",
            "sampled_UTC":NUM,"source_methods":864,
            "root_historical_behavioral_goal":"OPEN",
            "conditional_Ptolemy_rows":4553,"HD_transition_abstentions":125}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preflight",action="store_true")
    a=p.parse_args()
    print(json.dumps(check(ROOT,a.preflight),sort_keys=True))

if __name__=="__main__":main()
