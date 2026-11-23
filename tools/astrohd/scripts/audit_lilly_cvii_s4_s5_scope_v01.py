#!/usr/bin/env python3
"""Lilly original 1647 CVII S4/S5 source-bound acceptance / branch gate.

Before publication, verify the actual complete finite UTC century receipt,
all earlier 48 new S3 true-LATER counts and historical earlier 96 original
S4/S5 partitions, including conditional Ptolemy records. Different
partile requirements and term sources remain independently visible.
No privately identifiable natal sources or human accuracy in public.
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
TASK="state/tasks/20261123-lilly-CVII-S4-S5-partile-dignity.json"
PUBLIC="tools/astrohd/reference/research/lilly_cvii_s4_s5_genuine_later_full_century_public_v01.json"
OLDER="tools/astrohd/reference/research/lilly_cvii_all_other_planets_full_century_public_v01.json"
NEW_S3="tools/astrohd/reference/research/lilly_cvii_s3_original_dispositor_self_other_aspect_full_century_public_v01.json"
MODES=("ascending_sign","regiomontanus_first_house","ascending_sign_or_intercepted_sign")
ORB=("1647_table_smaller_orbs","1647_table_larger_orbs")
JOIN=("four_externals_only","all_other_classical_planets")
BEHOLD=("dispositor_sign_ray","dispositor_orb_near_ray")
OTHER=("rays_only","rays_or_bodily")
PARTILE=("partile_Moon_or_Mercury","partile_same_planet_Moon_and_Mercury")
NUM=3506400

def check(root:Path,preflight:bool=False):
    task=json.loads((root/TASK).read_text())
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=root,text=True).strip()
    if branch!=task["required_branch"] or task["required_repo"]!="u-dont-existDOTcom/astro-research":
        raise ValueError("Wrong original S4/S5 active source branch/repo")
    if not task["suspended_competing_sources"] or task["root_completed"] is not False:
        raise ValueError("Owner root completion laundered or task active isolation lost")
    if task["status"] not in ("ACTIVE_BOUNDED_TASK_PARENT_OPEN","BOUNDED_TASK_READY_FOR_HOSTED_REVIEW_PARENT_OPEN"):
        raise ValueError("Unexpected original-source task identity status")
    if preflight:return {"status":"PASS_ORIGINAL_S4_S5_BRANCH_PREFLIGHT","owner_root_status":"OPEN"}
    for path in task["required_artifacts"]:
        if not (root/path).is_file():raise ValueError("Missing genuine source-based original artifact "+path)
    j=json.loads((root/PUBLIC).read_text());c=j["counts"]
    old=json.loads((root/OLDER).read_text())["counts"]
    prior=json.loads((root/NEW_S3).read_text())["counts"]
    if j["samples"]!=NUM or j["original_source_partile_S4_S5_eligibility_methods"]!=96 or j["S4_S5_eligibility_x_S5_source_candidate_scoring_methods"]!=576:
        raise ValueError("Original full sample clock / stage model coverage incomplete")
    if (c["HD_root_margin_unknown"]!=125 or c["conditional_Ptolemy_4mode_possible_common_lord"]!=4553
        or j["HD_structural_interval_total"]!=288908):
        raise ValueError("Original HD and conditional Ptolemy source population drift")
    if not j["old_96_source_S4_S5_and_new_48_S3_LATER_exactly_reconciled"]:
        raise ValueError("Previous original S3 and S4/S5 stage counts no longer proven")
    if (j["S4_forcible_aspect_historical_rule_adjudicated"] or j["original_1647_CVII_S5_full_manners_ruler_selected"]):
        raise ValueError("Geometric partile or positive-only dignity candidate called full source ruler")
    if not j["S3_SX_SY_historical_source_gaps_retained"]:
        raise ValueError("Old SX and self-dispositor SY unlicensed passage to S4/S5")
    if not j["no_real_human_personality_prediction"] or not j["no_private_natal_birth_interview_or_person_source_evidence_used"]:
        raise ValueError("Human personalized/private results in source-neutral scan")
    for m in MODES:
        for orb in ORB:
            for join in JOIN:
                for behold in BEHOLD:
                    for other in OTHER:
                        prefix="|".join((m,orb,join,behold,"all="+other))
                        if c[prefix+"|genuine_LATER"]!=prior[prefix+"|LATER"]:
                            raise ValueError("Genuine 48-source LATER evidence changed")
                        if c[prefix+"|SY_self_with_no_other"]!=prior[prefix+"|SY_without_other_aspecting"]:
                            raise ValueError("Own-dispositor source-unknown was deleted")
                        for kind in PARTILE:
                            key=prefix+"|"+kind
                            oldkey="|".join((m,orb,join,behold,kind,"all="+other))
                            S4=c[key+"|S4_GEOMETRIC_possible_forcible_unverified"]
                            S5=c[key+"|S5_NO_geometric_partile"]
                            sy4=c[key+"|SY_with_geometric_partile_legacy"]
                            sy5=c[key+"|SY_without_geometric_partile_legacy"]
                            if S4+S5!=prior[prefix+"|LATER"]:
                                raise ValueError("S4/S5 did not partition genuinely eligible LATER")
                            if sy4+sy5!=prior[prefix+"|SY_without_other_aspecting"]:
                                raise ValueError("Unresolved source self-dispositor partile cases disappeared")
                            if S4+sy4!=old[oldkey+"|S4"] or S5+sy5!=old[oldkey+"|S5"]:
                                raise ValueError("Old original 96-stage S4/S5 counts no longer reconstruct exactly")
                            if (S4!=c[key+"|S4_exactly_one_body"]+c[key+"|S4_multiple_bodies"] or
                                S5!=c[key+"|S5_six_source_same_unique_five_positive_lord"]+
                                    c[key+"|S5_six_source_tied_or_sect_unknown"]):
                                raise ValueError("Unknown/tie participants silently dropped")
                            for term in j["p536_S5_original_print_term_sources"]:
                                for agg in j["p536_S5_place_point_aggregation_options"]:
                                    q=term+"|"+agg
                                    if (c[key+"|S5_"+q+"|unique_positive"]+
                                        c[key+"|S5_"+q+"|tie_or_unknown"]!=S5):
                                        raise ValueError("Missing six source-conditional final dignity score results")
                            if (c[key+"|Ptolemy_S4_possible"]+
                                c[key+"|Ptolemy_SY_with_geometric_partile_legacy"]!=
                                old["Ptolemy_"+oldkey+"|S4"] or
                                c[key+"|Ptolemy_S5_no_partile"]+
                                c[key+"|Ptolemy_SY_without_geometric_partile_legacy"]!=
                                old["Ptolemy_"+oldkey+"|S5"]):
                                raise ValueError("Conditional Ptolemy original prior source evidence changed")
    return {"status":"PASS_ORIGINAL_LILLY_S4_S5_TRUE_LATER_576_SOURCE_CONDITIONAL_MODELS",
            "sampled_UTC":NUM,"S4_S5_source_policy_combinations":576,
            "prior_stage_reconstruction":True,"root_owner_human_validation":"OPEN"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preflight",action="store_true")
    a=p.parse_args()
    print(json.dumps(check(ROOT,a.preflight),sort_keys=True))
if __name__=="__main__":main()
