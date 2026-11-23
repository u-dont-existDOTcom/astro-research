#!/usr/bin/env python3
"""Lilly original 1647 CVII p536 S3/SX/SY source stage acceptance audit.

Before publishing, check actual original full sampled-century data and
prove that splitting the historic self-dispositor ambiguous case never
silently rewrites the earlier frozen 96 source stage partitions. An S3
source geometric planet candidate or SX other-aspector is not a full
manners significator or empirical personality prediction.
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TASK="state/tasks/20261123-lilly-CVII-S3-dispositor-self-gap.json"
RESULT="tools/astrohd/reference/research/lilly_cvii_s3_original_dispositor_self_other_aspect_full_century_public_v01.json"
OLD="tools/astrohd/reference/research/lilly_cvii_all_other_planets_full_century_public_v01.json"
MODES=("ascending_sign","regiomontanus_first_house","ascending_sign_or_intercepted_sign")
ORBS=("1647_table_smaller_orbs","1647_table_larger_orbs")
JOINS=("four_externals_only","all_other_classical_planets")
BEHOLDS=("dispositor_sign_ray","dispositor_orb_near_ray")
CONTACTS=("rays_only","rays_or_bodily")
PARTILES=("partile_Moon_or_Mercury","partile_same_planet_Moon_and_Mercury")

def check(root:Path,preflight=False):
    info=json.loads((root/TASK).read_text())
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=root,text=True).strip()
    if branch!=info["branch"] or info["repository"]!="u-dont-existDOTcom/astro-research":
        raise ValueError("Original S3 source task wrong branch/repository")
    if not info["root_not_satisfied_by_bounded_task"] or not info["suspended_competing_sources"]:
        raise ValueError("Parent historic+human owner outcome must remain OPEN")
    if info["status"] not in ("ACTIVE_BOUNDED_SUBTASK_PARENT_OPEN",
                              "BOUNDED_SUBTASK_REVIEW_READY_PARENT_OPEN"):
        raise ValueError("Unexpected source task status")
    if preflight:return {"status":"PASS_LILLY_S3_SOURCE_BRANCH_PREFLIGHT","parent":"OPEN"}
    for path in info["required_artifacts"]:
        if not (root/path).is_file():raise ValueError("No completed original source artifact "+path)
    j=json.loads((root/RESULT).read_text());c=j["counts"]
    old=json.loads((root/OLD).read_text())["counts"]
    if j["samples"]!=3506400 or j["number_source_S3_SX_self_interpretations"]!=48:
        raise ValueError("Incorrect original full source UTC/sample or method count")
    if (c["HD_root_margin_unknown"]!=125 or c["conditional_Ptolemy_fourmode_common"]!=4553
        or j["HD_structural_intervals"]!=288908):
        raise ValueError("Original HD/Ptolemy conditional source universe changed")
    for m in MODES:
        for orb in ORBS:
            for join in JOINS:
                for behold in BEHOLDS:
                    for contact in CONTACTS:
                        k="|".join((m,orb,join,behold,"all="+contact))
                        if sum(c[k+"|"+z] for z in ("S1","S2","S3","SY","SX","LATER"))!=3506400:
                            raise ValueError("One source stamp lost or double-counted in new S3")
                        if c[k+"|SY_with_other_aspecting"]+c[k+"|SY_without_other_aspecting"]!=c[k+"|SY"]:
                            raise ValueError("Missing self-dispositor any-other aspect disposition")
                        if c["Ptolemy_"+k+"|SY_with_other_aspecting"]+c["Ptolemy_"+k+"|SY_without_other_aspecting"]!=c["Ptolemy_"+k+"|SY"]:
                            raise ValueError("Ptolemy conditional self-dispositor categories omitted")
                        if c[k+"|SX_exactly_one_other_aspector"]+c[k+"|SX_multiple_other_aspectors"]!=c[k+"|SX"]:
                            raise ValueError("Other aspecting planet identities not enumerated")
                        for part in PARTILES:
                            ok="|".join((m,orb,join,behold,part,"all="+contact))
                            for stage in ("S1","S2","S3"):
                                if c[k+"|"+stage]!=old[ok+"|"+stage]:
                                    raise ValueError("Original prior stage lost evidence "+stage)
                                if c["Ptolemy_"+k+"|"+stage]!=old["Ptolemy_"+ok+"|"+stage]:
                                    raise ValueError("Prior Ptolemy same-time stage lost evidence "+stage)
                            if c[k+"|SX"]+c[k+"|SY_with_other_aspecting"]!=old[ok+"|SX"]:
                                raise ValueError("Old original SX source scope not preserved")
                            if c[k+"|LATER"]+c[k+"|SY_without_other_aspecting"]!=old[ok+"|S4"]+old[ok+"|S5"]:
                                raise ValueError("Old later fallback data not preserved")
    for key in ("historically_actual_complete_Lilly_manners_ruler",
                "historically_actual_complete_Ptolemy_soul_governor",
                "independently_validated_human_personality_accuracy",
                "private_owner_or_thirdparty_natal_case_source_used"):
        if j[key] is not False:
            raise ValueError("Original partial S3 source evidence promoted to person/historic truth")
    return {"status":"PASS_ORIGINAL_LILLY_S3_SX_SELF_ALL48_RECONCILED",
            "UTC_original_samples":3506400,"source_variants":48,
            "prior_six_stage_source_variants":96,"owner_goal":"OPEN"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--preflight",action="store_true")
    args=parser.parse_args()
    print(json.dumps(check(ROOT,args.preflight),sort_keys=True))

if __name__=="__main__":main()
