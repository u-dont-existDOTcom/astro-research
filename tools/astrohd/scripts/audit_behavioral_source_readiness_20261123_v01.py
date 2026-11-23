#!/usr/bin/env python3
"""Reuse the existing AstroHD chart-feature coverage checker, not a new score.

This source-neutral audit compares three *development-only* requirement
profiles against the exact SHA-frozen public Nov19 Western+HD feature
registry: a minimal astronomical mechanics reference, a historically
governed + human outcome source admission example, and a non-binding
22-feature whole-registry pressure test.

An intentionally failed gate is a CORRECT measured source-readiness result,
not a broken audit or proof astrology is false. The audit itself reports
PASS only if it correctly identifies expected blocking gaps and refuses
to claim human predictive validation, a finished score or natal rank.

Does NOT import or inspect private birth, interview or person-specific
profile evidence. Reuses audit_full_chart_feature_coverage.coverage().
"""
from __future__ import annotations
import argparse
import json
from hashlib import sha256
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_full_chart_feature_coverage_v02 import coverage

TASK="state/tasks/20261123-astrohd-behavioral-readiness.json"
PROFILE="tools/astrohd/reference/research/astrohd_behavioral_source_readiness_profiles_20261123_v01.json"
RECEIPT="tools/astrohd/reference/research/astrohd_behavioral_source_readiness_receipt_20261123_v01.json"

def source_sha(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def verify_task(root:Path)->dict:
    j=json.loads((root/TASK).read_text())
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=root,text=True).strip()
    if branch!=j["branch"] or j["repository"]!="u-dont-existDOTcom/astro-research":
        raise ValueError("Wrong active source-neutral evaluation task/branch")
    if not j["exclusive"] or j["complete_owner_goal"] or not j["suspended_competing_sources"]:
        raise ValueError("Exclusive task, owner OPEN, or branch isolation broken")
    if j["status"] not in ("ACTIVE_BOUNDED_TASK_PARENT_OPEN",
                         "BOUNDED_TASK_HOSTED_REVIEW_READY_PARENT_OPEN"):
        raise ValueError("Unexpected owner task status")
    return j

def build(root:Path)->dict:
    profile=json.loads((root/PROFILE).read_text())
    if profile["schema"]!="astrohd_reused_mechanical_and_human_source_readiness_profiles_20261123_v01":
        raise ValueError("Unknown prereadiness source experiment")
    source=root/profile["source_registry_path"]
    if source_sha(source)!=profile["source_registry_sha256"]:
        raise ValueError("Original source-registry SHA drift; must explicitly rebaseline feature readiness")
    if profile["human_prediction_validated"] or profile["full_chart_rank_computed"] or profile["source_personal_birth_or_interview_records_used"]:
        raise ValueError("Nonempirical requirements misrepresented as human score")
    if len(profile["profiles"])!=3:
        raise ValueError("Three independent readiness profiles, not a score, required")
    r=json.loads(source.read_text())
    results=[]
    for entry in profile["profiles"]:
        candidate={k:entry[k] for k in ("model_version","precision_claim","required_features")}
        out=coverage(r,candidate)
        if out["status"]!=entry["expected_coverage_status"] or out["required_feature_failures"]!=entry["expected_uncertified"]:
            raise ValueError("Unregistered feature requirement/certification changed: "+entry["id"])
        if out["certified_predictive_human_personality"] or out["v4_3_complete_model_certified"]:
            raise ValueError("Mechanical presence incorrectly declared predictive")
        results.append({
            "profile_id":entry["id"],
            "status":out["status"],
            "feature_count":out["features_checked"],
            "uncertified_feature_ids":out["required_feature_failures"],
            "mechanics_coverage_only":out["certified_for_required_mechanics_only"],
            "historically_complete_source_governors":False,
            "independent_human_behavior_prediction_certified":False
        })
    if results[0]["status"]!="PASS_MECHANICAL_COVERAGE" or results[1]["mechanics_coverage_only"] or results[2]["mechanics_coverage_only"]:
        raise ValueError("Source gate not correctly separating bounded finite mechanical pass from human failure")
    return {
       "schema":"astrohd_existing_coverage_gate_reused_frozen_source_readiness_receipt_20261123_v01",
       "status":"PASS_READINESS_AUDIT_CORRECTLY_IDENTIFIES_INCOMPLETE_HUMAN_MODEL",
       "date_utc":"2026-11-23",
       "source_registry_path":profile["source_registry_path"],
       "source_registry_sha256":profile["source_registry_sha256"],
       "source_profile_sha256":source_sha(root/PROFILE),
       "source_coverage_gate":"tools/astrohd/scripts/audit_full_chart_feature_coverage_v02.py",
       "source_profiles":results,
       "root_project_status":"OPEN",
       "original_complete_Lilly_CVII_and_Ptolemy_III13_governors":False,
       "preregistered_full_cross_system_human_behavioral_model_frozen":False,
       "independent_private_blinded_human_validation_executed":False,
       "no_private_natal_birth_interview_case_data_read":True,
       "not_every_worldwide_birthplace_or_continuous_instant_covered":True,
       "no_new_human_personality_score_generated":True
    }

def audit(root:Path,preflight=False,out:Path|None=None)->dict:
    verify_task(root)
    if preflight:
        return {"status":"PASS_PUBLIC_READINESS_BRANCH_PREFLIGHT",
                "owner_goal":"OPEN","no_personal_research_data_used":True}
    for required in json.loads((root/TASK).read_text())["required_artifacts"]:
        if not (root/required).is_file():
            raise ValueError("Required public source-neutral task artifact missing: "+required)
    actual=build(root)
    if out is not None:
        if out.exists():raise FileExistsError("Do not overwrite immutable source readiness receipt")
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(actual,sort_keys=True,indent=2)+"\n")
    receipt=root/RECEIPT
    if not receipt.exists():
        raise ValueError("Expected real reproducible source/readiness evidence receipt missing")
    known=json.loads(receipt.read_text())
    if known!=actual:
        raise ValueError("Source-readiness artifact no longer reproducible from frozen coverage registry")
    return {"status":actual["status"],"readiness_profiles":len(actual["source_profiles"]),
            "source_registry_sha256":actual["source_registry_sha256"],
            "parent_human_behavioral_goal":actual["root_project_status"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preflight",action="store_true")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    print(json.dumps(audit(ROOT,a.preflight,a.out),sort_keys=True))

if __name__=="__main__":main()
