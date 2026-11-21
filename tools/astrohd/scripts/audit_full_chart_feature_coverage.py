#!/usr/bin/env python3
"""Compile-time feature coverage gate for future natal chart-to-survey scorers.

No participant data or ephemeris calculations here. The registry records which
mechanical fields the new source-neutral caches can actually compute and at
what time resolution. A model demanding absent features must FAIL rather than
treat their absence as non-matches or score zero. This says nothing about
whether classical interpretations causally predict real personality.

Example:
  audit_full_chart_feature_coverage.py --registry dev.json --model requirements.json
      --out receipt.json

Model schema:
  {"model_version":"v40-dev", "precision_claim":"FINITE_GRID_15M",
   "required_features":["TROPICAL_7_LONGITUDES","WHOLE_SIGN_12_HOUSES"]}

For continuous precise coverage of *all model features*, only features with
EXACT_STRUCTURAL_INTERVALS are accepted, and any model using sampled geometry
is reported NOT CERTIFIED.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

VALID_MODEL_PRECISION={"FINITE_GRID_15M","CONTINUOUS_STRUCTURAL"}
SUPPORTED_STATUSES={"ready","derivable"}
VALID_STATUS=set(SUPPORTED_STATUSES)|{
    "pilot","missing","not_precomputed","needs_primary_source_compiler",
    "not_in_structural_v1","source_unvalidated","not_frozen",
    "not_proven",
}

def sha_file(path:Path)->str:return sha256(path.read_bytes()).hexdigest()
def coverage(registry:dict,model:dict)->dict:
    if registry.get("schema")!="astrohd_complete_chart_feature_coverage_register/0.1.0":
        raise ValueError("Unrecognized feature register version")
    if not isinstance(model.get("model_version"),str) or not model["model_version"].strip():
        raise ValueError("Model version is required")
    precision=model.get("precision_claim")
    if precision not in VALID_MODEL_PRECISION:
        raise ValueError("Must explicitly declare finite 15m grid vs continuous structural")
    requested=model.get("required_features")
    if not isinstance(requested,list) or not requested or any(not isinstance(x,str) for x in requested):
        raise ValueError("Nonempty list of explicitly required fields is mandatory")
    if len(set(requested))!=len(requested):
        raise ValueError("Duplicate feature requirement")
    entries=registry["features"]
    ids=[r["id"] for r in entries]
    if len(ids)!=len(set(ids)):
        raise ValueError("Feature registry duplicate")
    byid={r["id"]:r for r in entries}
    sources=registry["source_register"]
    output=[]
    for feature_id in requested:
        if feature_id not in byid:
            raise ValueError("Unknown required feature: "+feature_id)
        row=byid[feature_id]
        if row["status"] not in VALID_STATUS:
            raise ValueError("Unknown registry feature status: "+row["status"])
        ready=row["status"] in SUPPORTED_STATUSES
        if row["src"] is not None:
            source=sources.get(row["src"])
            if source is None or not source.get("manifest_sha256"):
                ready=False
        if precision=="CONTINUOUS_STRUCTURAL" and row["scope"]!="EXACT_STRUCTURAL_INTERVALS":
            ready=False
        output.append({"feature":feature_id,"source":row["src"],
            "declared_scope":row["scope"],"status":row["status"],
            "complete_for_model_precision":ready})
    missing=[x["feature"] for x in output if not x["complete_for_model_precision"]]
    return {
        "status":"PASS_MECHANICAL_COVERAGE" if not missing else "FAIL_MISSING_OR_UNCERTIFIED_REQUIRED_FEATURES",
        "model_version":model["model_version"],
        "precision_claim":precision,
        "features_checked":len(output),
        "coverage":output,
        "required_feature_failures":missing,
        "certified_for_required_mechanics_only":not missing,
        "certified_predictive_human_personality":False,
        "v4_3_complete_model_certified":False,
        "note":"Source feature availability does not establish meaningful behavior-direction mapping."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--registry",type=Path,required=True)
    p.add_argument("--model",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():raise FileExistsError("Do not overwrite previous coverage receipt")
    src=json.loads(args.registry.read_bytes())
    model=json.loads(args.model.read_bytes())
    report=coverage(src,model)
    report["registry_sha256"]=sha_file(args.registry)
    report["model_sha256"]=sha_file(args.model)
    b=(json.dumps(report,sort_keys=True,indent=2)+"\n").encode()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_bytes(b)
    print("FEATURE_COVERAGE_GATE",json.dumps({
        "status":report["status"],"features_checked":report["features_checked"],
        "missing":report["required_feature_failures"],
        "output_sha256":sha256(b).hexdigest()},sort_keys=True))
    if not report["certified_for_required_mechanics_only"]:
        raise SystemExit(2)

if __name__=="__main__":main()
