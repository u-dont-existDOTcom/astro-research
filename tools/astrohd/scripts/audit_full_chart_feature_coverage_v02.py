#!/usr/bin/env python3
"""Source-provenance fail-closed v02 of immutable AstroHD feature coverage.

Do NOT edit the original migrated v01 module; its original source hash is
anchored to the public migration inventory. v02 wraps its exact original
coverage semantics but refuses to mechanically certify any nominally
"ready" or "derivable" feature whose source provenance ID is blank, missing,
unregistered or lacks a manifest digest.

The output is source mechanics ONLY, never historical interpretation
completion, human predictive accuracy or permission to rank a natal chart.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import audit_full_chart_feature_coverage as legacy

ORIGINAL_MODULE=Path(__file__).with_name("audit_full_chart_feature_coverage.py")
ORIGINAL_SHA256="0534823d1550877b67994a7c348a7283fdf9affe3280cdfdb26371cf50566f91"

def sha_file(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def coverage(registry:dict,model:dict)->dict:
    if sha_file(ORIGINAL_MODULE)!=ORIGINAL_SHA256:
        raise RuntimeError("Historical v01 coverage checker drift; preserve migration inventory")
    if not isinstance(registry,dict) or not isinstance(registry.get("features"),list):
        raise ValueError("Original frozen feature registry required")
    if not isinstance(registry.get("source_register"),dict):
        raise ValueError("Registered source-provenance dictionary required")

    # Legacy expects "src" to exist even for missing unsupported features.
    # Normalize missing to None in a COPY so malformed source input cannot
    # crash or modify the caller's original registration.
    original=deepcopy(registry)
    for row in original["features"]:
        if not isinstance(row,dict):
            raise ValueError("Source feature declaration must be an object")
        row.setdefault("src",None)
    report=legacy.coverage(original,model)

    indexed={row["id"]:row for row in original["features"]}
    sources=original["source_register"]
    for item in report["coverage"]:
        row=indexed[item["feature"]]
        if row["status"] in legacy.SUPPORTED_STATUSES:
            source_id=row.get("src")
            original_record=sources.get(source_id) if isinstance(source_id,str) and source_id else None
            source_verified=(isinstance(original_record,dict)
                             and isinstance(original_record.get("manifest_sha256"),str)
                             and bool(original_record["manifest_sha256"].strip()))
            if not source_verified:
                item["complete_for_model_precision"]=False

    missing=[x["feature"] for x in report["coverage"] if not x["complete_for_model_precision"]]
    report["required_feature_failures"]=missing
    report["certified_for_required_mechanics_only"]=not missing
    report["status"]=("PASS_MECHANICAL_COVERAGE" if not missing else
                      "FAIL_MISSING_OR_UNCERTIFIED_REQUIRED_FEATURES")
    report["certified_predictive_human_personality"]=False
    report["v4_3_complete_model_certified"]=False
    report["coverage_checker_version"]="SOURCE_PROVENANCE_FAIL_CLOSED_V02"
    report["historical_v01_source_sha256"]=ORIGINAL_SHA256
    report["source_missing_for_ready_is_not_certified"]=True
    report["note"]="Only sampled feature mechanics checked, with registered source manifest for every supported feature; no human behavior validation."
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--registry",type=Path,required=True)
    parser.add_argument("--model",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Do not overwrite source-bound mechanical coverage audit evidence")
    registry=json.loads(args.registry.read_bytes())
    model=json.loads(args.model.read_bytes())
    report=coverage(registry,model)
    report["registry_sha256"]=sha_file(args.registry)
    report["model_sha256"]=sha_file(args.model)
    result=json.dumps(report,sort_keys=True,indent=2)+"\n"
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(result)
    print("ASTROHD_SOURCE_PROVENANCE_V02_GATE",json.dumps({
        "status":report["status"],
        "source_mechanics_checked":report["features_checked"],
        "uncertified_source_features":report["required_feature_failures"],
        "output_sha256":sha256(result.encode()).hexdigest()
    },sort_keys=True))
    if not report["certified_for_required_mechanics_only"]:
        raise SystemExit(2)

if __name__=="__main__":main()
