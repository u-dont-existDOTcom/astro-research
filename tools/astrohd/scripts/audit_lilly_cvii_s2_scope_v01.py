#!/usr/bin/env python3
"""Original 1647 Lilly CVII second-stage source-bound report acceptance.

Requires actual full century data and original previous S2 frozen counts;
never promotes source conditional joining to a unique historical manners ruler
or an independent human-behavior claim.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TASK="state/tasks/20261123-lilly-CVII-S2-joining.json"
AGG="tools/astrohd/reference/research/lilly_cvii_s2_original_joining_full_century_public_v01.json"
OLD="tools/astrohd/reference/research/lilly_cvii_ptolemy_same_instant_ordered_fallback_public_v02.json"
MODES=("ascending_sign","regiomontanus_first_house","ascending_sign_or_intercepted_sign")
SCOPES=("four_externals_only","all_other_classical_planets")
ORBS=("1647_table_smaller_orbs","1647_table_larger_orbs")

def audit(root:Path):
    t=json.loads((root/TASK).read_text())
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=root,text=True).strip()
    if branch!=t["required_branch"] or t["required_repo"]!="u-dont-existDOTcom/astro-research":
        raise ValueError("Wrong canonical branch/repository for task")
    if not t["parent_not_satisfied_by_task"] or not t["suspended_competing_task_sources"]:
        raise ValueError("Parent owner outcome incorrectly completed or concurrent task not isolated")
    for rel in t["required_artifacts"]:
        if not (root/rel).is_file():raise ValueError("Missing original full source task deliverable: "+rel)
    j=json.loads((root/AGG).read_text());c=j["counts"]
    earlier=json.loads((root/OLD).read_text())["counts"]
    if j["samples"]!=3506400 or j["source_sensitive_S2_eligibility_method_count"]!=12:
        raise ValueError("Original full UTC and 12 method population missing")
    if c["HD_root_uncertain"]!=125 or c["ptolemy_conditional_four_mode_common"]!=4553:
        raise ValueError("Original HD/Ptolemy conditional cohort drift")
    if j["HD_structural_interval_total"]!=288908:
        raise ValueError("Original HD structural source changed")
    for mode in MODES:
        if c[mode+"|S1_present"]+c[mode+"|S1_empty"]!=3506400:
            raise ValueError("Source S1 earlier/later window invalid")
        for orb in ORBS:
            for scope in SCOPES:
                key="|".join((mode,orb,scope))
                old="|".join((mode,orb,scope,"dispositor_sign_ray","partile_Moon_or_Mercury"))
                if c[key+"|S2_any"]!=earlier[old+"|S2"]:
                    raise ValueError("Old five-stage source S2 count not reproduced")
                if c[key+"|S2_ptolemy_any"]!=earlier["same_instant_Ptolemy_"+old+"|S2"]:
                    raise ValueError("Old Ptolemy S2 same-time conditional count not reproduced")
                if (c[key+"|S2_zero_proceed_to_S3"]+c[key+"|S2_one_joined_planet"]+
                    c[key+"|S2_multiple_joined_planets"]!=c[mode+"|S1_empty"]):
                    raise ValueError("Source joining zero/one/multi source partition invalid")
                if c[key+"|S2_joined_to_both_Moon_and_Mercury"]>c[key+"|S2_any"]:
                    raise ValueError("Two-joining-contacts cannot exceed any-joining")
    for label in ("actual_Lilly_CVII_manners_ruler_computed",
                  "actual_Ptolemy_III13_soul_governor_computed",
                  "independent_human_behavioral_validation",
                  "private_user_thirdparty_natal_source_records_loaded"):
        if j[label] is not False:raise ValueError("Unsupported original human or full-ruler claim: "+label)
    return {"status":"PASS_LILLY_1647_S2_FULL_12_SOURCE_VARIANTS_FROZEN_SAME_UTC",
            "UTC_samples":3506400,"conditional_ptolemy":4553,
            "root_owner_historical_and_behavioral_outcome":"OPEN"}

if __name__=="__main__":
    print(json.dumps(audit(ROOT),sort_keys=True))
