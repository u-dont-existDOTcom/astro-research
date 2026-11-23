#!/usr/bin/env python3
"""Fail closed original Lilly 1647 p535 dignity-participation acceptance.

The active task is source-specified S1 secondary inclusion, not a source-
complete manners governor and not empirical human trait prediction. Verify
original complete source population, each of 3 historic terms x3 competing
S1 place interpretations, independent frozen S1 primary cohort checks,
uncertain sect brackets and original shared Ptolemy/HD source denominators.

Only invented-data tests and source-neutral aggregate can enter public Git.
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TASK="state/tasks/20261123-lilly-CVII-p535-secondary.json"
RESULT="tools/astrohd/reference/research/lilly_cvii_p535_secondary_participants_full_century_public_v01.json"
OLD="tools/astrohd/reference/research/lilly_cvii_s1_eligible_partial_strength_full_century_public_v01.json"
MODES=("ascending_sign","regiomontanus_first_house","ascending_sign_or_intercepted_sign")
TERMS=("Lilly_1647_original_first_print_p104","ptolemy_printed_1940","egyptian_printed_1940")
SAMPLES=3506400

def audit(root:Path,preflight=False):
    t=json.loads((root/TASK).read_text())
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=root,text=True).strip()
    if branch!=t["required_branch"] or t["required_repository"]!="u-dont-existDOTcom/astro-research":
        raise ValueError("Original S1 source task branch/repository mismatch")
    if not t["exclusive"] or t["parent_complete"] or not t["suspended_competing_sources"]:
        raise ValueError("Original owner parent OPEN or exclusive task isolation violated")
    if t["status"] not in ("ACTIVE_BOUNDED_SUBTASK_PARENT_OPEN","BOUNDED_SUBTASK_HOSTED_REVIEW_READY_PARENT_OPEN"):
        raise ValueError("Unexpected source task status")
    if preflight:
        return {"status":"PASS_ORIGINAL_P535_SECONDARY_BRANCH_PREFLIGHT",
                "root_human_behavioral_validation":"OPEN"}
    for path in t["required_artifacts"]:
        if not (root/path).is_file():raise ValueError("Required source-authored artifact missing: "+path)
    j=json.loads((root/RESULT).read_text())
    c=j["counts"]
    prior=json.loads((root/OLD).read_text())["counts"]
    if j["sample_UTC_count"]!=SAMPLES or j["source_method_count"]!=9:
        raise ValueError("Original full source UTC clock or 9 historic methods incomplete")
    if (c["original_HD_margin_unknown"]!=125 or c["original_sector_uncertain"]!=5049
        or c["original_Ptolemy_fourmode_common_conditional"]!=4553 or
        c["original_Ptolemy_conditional_HD_unknown"]!=0 or
        j["original_HD_structural_intervals"]!=288908):
        raise ValueError("Previous original source HD/sect/Ptolemy cohort changed")
    if not j["prior_S1_source_cohorts_reproduced"]:
        raise ValueError("Unlicensed original S1 modifications")
    if (j["historically_complete_Lilly_manners_ruler_computed"] or
        j["complete_Ptolemy_III13_soul_governor_computed"] or
        j["independent_human_behavior_validation"] or
        j["private_natal_or_interview_evidence_used"]):
        raise ValueError("A source participant count was promoted to full ruler/human accuracy or private data")
    for mode in MODES:
        oldkeys=("empty_go_to_later_stages","sole_primary_occupant","multiple_principal_occupants")
        newkeys=("no_primary","sole_primary","multiple_primary")
        for old,new in zip(oldkeys,newkeys,strict=True):
            if c[mode+"|source_S1_"+new]!=prior[mode+"|"+old]:
                raise ValueError("Actual original S1 primary planet source counts not preserved")
        count_present=SAMPLES-c[mode+"|source_S1_no_primary"]
        if c[mode+"|all_three_printed_terms_exact_full_participant_set"]>count_present:
            raise ValueError("Three-term participant agreement outside original primary presence")
        for term in TERMS:
            key=mode+"|"+term+"|"
            g=c[key+"extra_secondary_certain_any"]
            possible=c[key+"extra_secondary_possible_any"]
            if not(0<=g<=possible<=count_present):
                raise ValueError("Dignity-secondary source presence/sect bounds invalid")
            if c[key+"primary_sole_with_certain_secondary"]+c[key+"primary_multi_with_certain_secondary"]!=g:
                raise ValueError("Source primary participant class/dignity participant intersection incorrect")
            if c[key+"total_secondary_planet_occurrences"]>7*count_present:
                raise ValueError("More than seven original classical source participants counted")
            for name in ("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"):
                if c[key+"certain_secondary_"+name]>c[key+"possible_secondary_"+name]:
                    raise ValueError("Certain secondary source planet must also be possible")
    if c["all_nine_same_original_primary_ROLE_and_secondary_participants"]>c["all_nine_geometries_terms_same_exact_total_participant_set"]:
        raise ValueError("Role-stable original source set cannot exceed identity-only stability")
    if c["all_nine_same_roles_and_extra_secondary"]>c["all_nine_same_original_primary_ROLE_and_secondary_participants"]:
        raise ValueError("Count of new secondary participants exceeds same-role corpus")
    return {"status":"PASS_ORIGINAL_1647_P535_SECONDARY_SOURCE_FULL_CENTURY_NINE_METHODS",
            "original_UTC_samples":SAMPLES,"history_methods":9,
            "original_HD_root_abstentions":125,"parent_manners_and_personality_goal":"OPEN"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--preflight",action="store_true")
    x=ap.parse_args()
    print(json.dumps(audit(ROOT,x.preflight),sort_keys=True))

if __name__=="__main__":main()
