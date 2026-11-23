#!/usr/bin/env python3
"""Fail-closed original Lilly 1647 full ordered CVII stages source coverage.

Require a real original 3.5m sampled UTC source scan with exact published
historic S3/S4/S5 partition checks. Source-conditional single-primary
candidate is not historical final manners ruler or empirical human trait.
Task identity is branch bound; underlying owner project remains OPEN.
"""
from __future__ import annotations
import argparse
import subprocess
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
TASK="state/tasks/20261123-lilly-CVII-ordered-stage-coverage.json"
OUTPUT="tools/astrohd/reference/research/lilly_cvii_ordered_stage_coverage_full_century_public_v01.json"
OLD_S3="tools/astrohd/reference/research/lilly_cvii_s3_original_dispositor_self_other_aspect_full_century_public_v01.json"
OLD_S4="tools/astrohd/reference/research/lilly_cvii_s4_s5_genuine_later_full_century_public_v01.json"
MODES=("ascending_sign","regiomontanus_first_house","ascending_sign_or_intercepted_sign")
ORB=("1647_table_smaller_orbs","1647_table_larger_orbs")
JOIN=("four_externals_only","all_other_classical_planets")
BEHOLD=("dispositor_sign_ray","dispositor_orb_near_ray")
OTHER=("rays_only","rays_or_bodily")
PARTILE=("partile_Moon_or_Mercury","partile_same_planet_Moon_and_Mercury")
N=3506400
LABELS=(
"S1_one_primary","S1_multiple_primaries","S2_one_joined",
"S2_multiple_joined","S3_asc_lord","SY_self_dispositor_source_unknown",
"SX_other_aspector_no_dispositor_source_unknown",
"S4_partile_possible_one_force_unknown",
"S4_partile_possible_multiple_force_unknown",
"S5_positive_place_same_unique_six_models","S5_positive_place_tied_or_unknown")

def audit(root:Path,preflight=False):
    t=json.loads((root/TASK).read_text())
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=root,text=True).strip()
    if branch!=t["required_branch"] or t["required_repo"]!="u-dont-existDOTcom/astro-research":
        raise ValueError("Active source task branch/repository mismatch")
    if not t["exclusive"] or not t["suspended_sources"] or t["not_source_complete_historical_manners_ruler"] is not True:
        raise ValueError("Old competing task or missing source/owner outcome boundary")
    if t["status"] not in ("ACTIVE_BOUNDED_TASK_PARENT_OPEN","BOUNDED_TASK_READY_FOR_HOSTED_REVIEW_PARENT_OPEN"):
        raise ValueError("Unrecognized historical source task state")
    if preflight:return {"status":"PASS_ORIGINAL_ORDERED_LILLY_SOURCE_TASK_PREFLIGHT","parent":"OPEN"}
    for name in t["required_artifacts"]:
        if not (root/name).is_file():raise ValueError("Source task missing required artifact "+name)
    j=json.loads((root/OUTPUT).read_text());c=j["counts"]
    s3=json.loads((root/OLD_S3).read_text())["counts"]
    s4=json.loads((root/OLD_S4).read_text())["counts"]
    if j["samples"]!=N or j["original_96_stage_path_scenarios"]!=96:
        raise ValueError("Original full sampled century/96 source variants missing")
    if j["HD_structural_intervals"]!=288908 or c["HD_root_margin_unassigned"]!=125 or c["Ptolemy_conditional_fourmode_common"]!=4553:
        raise ValueError("Frozen source HD/Ptolemy denominator changed")
    if (j["historically_selected_single_final_manners_ruler"] is not False or
        j["independent_human_personality_accuracy"] is not False or
        j["private_natal_interview_ratings_used"] is not False or
        j["forcible_partile_1647_original_still_unadjudicated"] is not True):
        raise ValueError("Unlicensed historical source or private-human claim")
    for mode in MODES:
        for orb in ORB:
            for join in JOIN:
                for seeing in BEHOLD:
                    for other in OTHER:
                        base="|".join((mode,orb,join,seeing,"all="+other))
                        for part in PARTILE:
                            k=base+"|"+part
                            if sum(c[k+"|"+name] for name in LABELS)!=N:
                                raise ValueError("Source stage missing or duplicated clock row")
                            if c[k+"|S1_one_primary"]+c[k+"|S1_multiple_primaries"]!=s3[base+"|S1"]:
                                raise ValueError("Historical S1 source cohort drift")
                            if c[k+"|S2_one_joined"]+c[k+"|S2_multiple_joined"]!=s3[base+"|S2"]:
                                raise ValueError("Historical S2 source cohort drift")
                            for fresh,old in (("S3_asc_lord","S3"),
                                ("SY_self_dispositor_source_unknown","SY"),
                                ("SX_other_aspector_no_dispositor_source_unknown","SX")):
                                if c[k+"|"+fresh]!=s3[base+"|"+old]:
                                    raise ValueError("Historical source S3/SX/SY underdetermination altered")
                            if (c[k+"|S4_partile_possible_one_force_unknown"]+
                                c[k+"|S4_partile_possible_multiple_force_unknown"]!=
                                s4[k+"|S4_GEOMETRIC_possible_forcible_unverified"]):
                                raise ValueError("Original S4 possible cohort changed")
                            if (c[k+"|S5_positive_place_same_unique_six_models"]!=
                                s4[k+"|S5_six_source_same_unique_five_positive_lord"] or
                                c[k+"|S5_positive_place_tied_or_unknown"]!=
                                s4[k+"|S5_six_source_tied_or_sect_unknown"]):
                                raise ValueError("Printed S5 six-rule candidate/tie source cohort changed")
                            if c[k+"|source_primary_conditional_candidate"]+c[k+"|historical_strength_or_rule_not_unique"]!=N:
                                raise ValueError("Unresolved historical source statuses not conserved")
    if (c["cross96_same_provisional_primary_candidate"]+
        c["cross96_stages_disagree"]+
        c["cross96_stage_agrees_but_no_single_provisional_body"]!=N):
        raise ValueError("Source-variant consensus/uncertainty cannot cover full UTC clock")
    return {"status":"PASS_ORIGINAL_LILLY_1647_ALL96_ORDERED_STAGES_SOURCE_CONDITIONAL",
            "original_sampled_UTC":N,"source_stage_variants":96,
            "root_historical_and_empirical_predictive_outcome":"OPEN"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preflight",action="store_true")
    a=p.parse_args()
    print(json.dumps(audit(ROOT,a.preflight),sort_keys=True))
if __name__=="__main__":main()
