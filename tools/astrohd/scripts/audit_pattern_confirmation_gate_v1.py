#!/usr/bin/env python3
"""Reusable evidence gate, not a personality questionnaire or a scoring runtime.

An anecdote is an observation about a PARTICULAR event, never an established
across-context personality pattern merely because it is vivid. An interpreter
must propose a scoped, falsifiable generalization; the respondent confirms,
limits, rejects or corrects it. Even confirmation only authorizes independent
source/score review of a DEVELOPMENT self-report, not automatic natal points
or an empirical prediction. Portable across participants and model systems.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

SCHEMA="generic_behavior_pattern_confirmation_protocol_v1"
ALLOWED={
    "proposed_unconfirmed","generally_correct_with_scope",
    "correct_only_in_some_contexts","partly_correct_needs_revision",
    "mostly_incorrect","cannot_assess",
}
CONFIRMED={"generally_correct_with_scope","correct_only_in_some_contexts"}

def sha(path:Path)->str:return sha256(path.read_bytes()).hexdigest()

def validate_protocol(protocol:dict)->dict:
    if protocol.get("schema")!=SCHEMA:
        raise ValueError("Unexpected protocol")
    steps=[x["id"] for x in protocol["workflows"]]
    expected=["STEP0_FREEZE_RESEARCH_CONSTRUCTS","STEP1_BIDIRECTIONAL_EXAMPLES",
              "STEP2_INFER_GENERAL_PATTERN","STEP3_REQUIRE_OWNER_CONFIRMATION",
              "STEP4_FREEZE_PROFILE_FOR_MODEL","STEP5_TEST_UNTOUCHED_PEOPLE"]
    if steps!=expected:
        raise RuntimeError("Pattern-confirmation sequence changed")
    if not protocol["evidence_protocol"].get("automatic_score_change_prohibited"):
        raise RuntimeError("Scoring anecdotes automatically violates owner requirement")
    if not protocol["evidence_protocol"].get("confirmation_not_same_as_accuracy"):
        raise RuntimeError("Participant confirmation is not independent validation")
    return {"protocol_id":SCHEMA,"stages":len(steps),"no_unconfirmed_pattern_scoring":True}

def triage_pattern(record:dict[str,Any])->dict:
    """Triage proposed respondent-general descriptions; NEVER return a score."""
    if not isinstance(record,dict):raise TypeError("Pattern record must be dict")
    required={"hypothesis","scope_conditions","counterexample_status",
              "source_episode_ids","confirmation_status"}
    if not required.issubset(record):
        raise ValueError("Missing required staged-evidence fields")
    if not str(record["hypothesis"]).strip():
        raise ValueError("Empty generalized hypothesis")
    if not str(record["scope_conditions"]).strip():
        raise ValueError("Missing actual scope of the proposed personality pattern")
    status=record["confirmation_status"]
    if status not in ALLOWED:raise ValueError("Invalid participant confirmation state")
    episodes=record["source_episode_ids"]
    if not isinstance(episodes,list) or any(not isinstance(s,str) or not s for s in episodes):
        raise ValueError("Invalid episode source IDs")
    if not record["counterexample_status"]:
        raise ValueError("Unspecified disconfirmation search")
    # Only a real response source outside Git can confirm; a checkbox text
    # without source provenance must not be accepted as a participant action.
    received=bool(str(record.get("participant_response_private_source_id") or "").strip())
    eligible=status in CONFIRMED and received
    return {
        "pattern_status":("SELF_REPORT_PATTERN_CONFIRMED_FOR_SOURCE_REVIEW"
                          if eligible else "NOT_CONFIRMED_ABSTAIN"),
        "eligible_for_source_review":eligible,
        "eligible_for_automatic_natal_scoring":False,
        "profile_inference_certainty":"self_report_confirmation_not_predictive_validation"
    }

def main()->None:
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--protocol",type=Path,required=True)
    p=parser.parse_args()
    print(json.dumps(validate_protocol(json.loads(p.protocol.read_bytes())),sort_keys=True))

if __name__=="__main__":main()
