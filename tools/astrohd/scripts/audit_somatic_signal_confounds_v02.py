#!/usr/bin/env python3
"""Generic source-only confound audit: visceral drive != immediate HD Authority.

No chart features or user source inside the algorithm. Every case is a
selected self-report rather than a sample; results never produce person-trait
frequency, an astrology likelihood or a natal rank. The sources pre-exist the
current chart-comparison application and support behavioral research controls.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

SCHEMA="generic_somatic_decision_signal_disambiguation_v02"
SOURCE_SCHEMA="private_or_synthetic_somatic_decision_cases_v02"
REQUIRED=("episode_id","context","signal_type","signal_intensity",
          "signal_duration","initial_reasoning_conflict","action_type",
          "action_completed","self_regulation","outcome_independently_checked",
          "generality","origin")
SIGNALS={
    "sexual_or_romantic_drive":"VISCERAL_DRIVE_EXPLANATION_CANDIDATE",
    "rapport_or_good_feeling":"AFFECTIVE_SOCIAL_IMPRESSION",
    "quiet_safety_instinct":"POTENTIALLY_SPLENIC_LIKE_PHENOMENOLOGY_NOT_AUTHORITY_PROOF",
    "answer_certainty":"COGNITIVE_OR_INTUITIVE_CERTAINTY_UNRESOLVED",
    "none_reported":"NO_BODILY_SIGNAL_REPORTED",
    "unknown":"UNRESOLVED_SIGNAL_CLASS",
}

def sha(path:Path)->str:return sha256(path.read_bytes()).hexdigest()

def load_rules(obj:dict)->dict:
    if obj.get("schema")!=SCHEMA:raise ValueError("Wrong source taxonomy")
    flags=obj["rules"]
    for key in ("no_score_or_chart_rank_output","no_inference_from_known_chart_type",
                "sustained_strong_drive_not_independent_splenic_support",
                "avoidance_and_strong_drive_can_coexist",
                "no_projecting_long_term_pattern_from_one_illustration"):
        if flags.get(key) is not True:raise RuntimeError("Removed critical control "+key)
    if len(obj.get("method_basis",[]))<3:raise RuntimeError("Missing prior non-bespoke sources")
    fields=obj["record_fields"]
    if set(REQUIRED)-set(fields):raise RuntimeError("Some case fields missing")
    if set(SIGNALS)!=set(fields["signal_type"]):raise RuntimeError("Signal classes not complete")
    return obj

def analyze_case(case:dict,source:dict)->dict:
    if any(k not in case for k in REQUIRED):
        raise ValueError("Missing case field")
    for key in REQUIRED:
        options=source["record_fields"][key]
        if isinstance(options,list) and case[key] not in options:
            raise ValueError("Unexpected "+key+" option")
    if not isinstance(case["episode_id"],str) or not case["episode_id"]:
        raise ValueError("Episode id must be nonblank text")
    for key in ("action_completed","outcome_independently_checked"):
        if type(case[key]) not in (bool,type(None)):
            raise ValueError("Outcome and action must be boolean or unknown")
    if case["outcome_independently_checked"] is True and case["action_completed"] is not True:
        raise ValueError("Cannot verify outcome of an action not established as completed")
    name=case["signal_type"]
    initial=SIGNALS[name]
    full_quiet=(name=="quiet_safety_instinct" and
                case["signal_intensity"]=="quiet" and
                case["signal_duration"]=="brief_once")
    if name=="quiet_safety_instinct" and not full_quiet:
        category="INCOMPLETE_QUIET_SPLENIC_LIKE_CUE"
    else: category=initial
    effort=case["self_regulation"] in (
        "anticipatory_situation_selection","in_the_moment_boundary","mixed",
        "override_attempt_unsuccessful")
    result={
        "episode_id":case["episode_id"],
        "main_nonspecific_signal_class":name,
        "source_interpretation":category,
        "quiet_splenic_like_phenomenology_meets_minimal_signals":full_quiet,
        "authority_reliability_established":False,
        "competing_motivational_explanation_available":name in ("sexual_or_romantic_drive","rapport_or_good_feeling"),
        "self_regulation_effort_reported":effort,
        "source_case_genuinely_general":case["generality"]=="self_reported_general_pattern",
        "independently_verified_effectiveness":case["outcome_independently_checked"] is True,
        "natal_score_delta":None,
    }
    return result

def audit_all(source:dict,cases:dict)->dict:
    load_rules(source)
    if cases.get("schema")!=SOURCE_SCHEMA:
        raise ValueError("Wrong private/synthetic input schema")
    records=cases.get("cases")
    if not isinstance(records,list) or not records:raise ValueError("No cases")
    ids=[e.get("episode_id") for e in records]
    if len(set(ids))!=len(ids):raise ValueError("Duplicate cases")
    results=[analyze_case(x,source) for x in records]
    return {
        "schema":"source_only_somatic_phenomenology_vs_decision_confounds_v02",
        "status":"NOT_A_PERSONALITY_DIAGNOSIS_NOT_A_NATAL_SCORE",
        "n_selected_cases":len(results),
        "case_classes":dict(Counter(r["main_nonspecific_signal_class"] for r in results)),
        "case_classes_source_only":dict(Counter(r["source_interpretation"] for r in results)),
        "cases_with_source_limited_quiet_cues":sum(r["quiet_splenic_like_phenomenology_meets_minimal_signals"] for r in results),
        "cases_with_reported_self_regulation_effort":sum(r["self_regulation_effort_reported"] for r in results),
        "no_source_based_hd_authority_decision_predictive_score":True,
        "no_reason_to_rerank_century":True,
        "not_representative_frequency":True,
        "case_detail":results,
    }

def main()->None:
    p=argparse.ArgumentParser()
    for flag in ("source","cases","output"):
        p.add_argument("--"+flag,required=True,type=Path)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError("Output immutable")
    s=json.loads(args.source.read_bytes())
    c=json.loads(args.cases.read_bytes())
    out=audit_all(s,c)
    out["source_sha256"]=sha(args.source)
    out["private_cases_sha256"]=sha(args.cases)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:out[k] for k in ("status","n_selected_cases","case_classes","cases_with_source_limited_quiet_cues","cases_with_reported_self_regulation_effort","no_reason_to_rerank_century")},sort_keys=True))
    print("OUTPUT_SHA256",sha(args.output))

if __name__=="__main__":main()
