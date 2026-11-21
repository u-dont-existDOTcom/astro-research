#!/usr/bin/env python3
"""Bounded owner-research completion gates; no empirical claims from code tests.

Terminal report may conclude with a qualified null/no-rank result. Separate
untouched prospective validation is optional and does not get silently
promoted to a new mandatory blocker.
"""
from __future__ import annotations
import json
from pathlib import Path
import argparse

SCHEMA="astrohd_owner_chart_research_bounded_completion_roadmap_v01"
TRACKS=("F","P","S","R","G","V")
CORE=("F","P","S","R","G")
KNOWN_TERMINAL={
"F":{"AUDIT_REPORT_COMPLETE_WITH_QUALIFIED_DISPOSITIONS","AUDIT_REPORT_COMPLETE_WITH_RECORDED_EVIDENCE_GAPS"},
"P":{"PROFILE_DEVELOPMENT_FROZEN_SELF_REPORT_WITH_CONTEXT","PROFILE_PARTIAL_UNCONFIRMED_ATOMIC_SUBDIMENSIONS"},
"S":{"SOURCE_RULEBOOKS_VERSIONED_FROZEN_AND_QUALIFIED","MATERIAL_RULES_UNSCORABLE_WITH_REASONS"},
"R":{"RANKED_FINITE_SCOPE_WITH_QUALIFICATIONS","NO_DEFENSIBLE_RANK_POSSIBLE_SOURCE_GAPS","COMPLETE_BOUNDED_REPORT_WITH_UNRESOLVED_UNCOVERED_STATES"},
"G":{"GEMINI_RESPONSE_CAPTURED_AND_RECONCILED","NOT_SENT_NO_AUTHORIZED_ROUTE_READY_TO_SEND"},
"V":{"HUMAN_PREDICTIVE_VALIDATION_REPORTED","UNVALIDATED_SYMBOLIC_REPORT_COMPLETED_NO_HUMAN_COHORT"},
}

def validate_plan(plan:dict)->dict:
    if plan.get("schema")!=SCHEMA:raise ValueError("Unexpected plan")
    items={t["id"]:t for t in plan["tracks"]}
    if set(items)!=set(TRACKS):raise ValueError("Missing research lane")
    for key,required in KNOWN_TERMINAL.items():
        if set(items[key]["terminal_outputs"])!=required:
            raise ValueError("Completion status definitions drifted for "+key)
        if not items[key].get("acceptance"):raise ValueError("No exit conditions for "+key)
    if not items["V"].get("optional"):
        raise RuntimeError("Prospective human validation silently made mandatory")
    if plan["end_definition"]["empirical_validation_not_mandatory_to_close_descriptive_work"] is not True:
        raise RuntimeError("Unrequested empirical validation is blocking a bounded report")
    if plan["end_definition"]["no_indefinite_source_search"] is not True:
        raise RuntimeError("Unbounded forum research")
    if plan["end_definition"]["no_promoting_unreproduced_better_rank_as_finished"] is not True:
        raise RuntimeError("No finished rank without reproducibility")
    if plan["model_status_now"]["source_qualified_non_bespoke_combined_scorer_ready"]:
        raise RuntimeError("False current source completeness")
    if plan["model_status_now"]["splenic_accuracy_claim"]!="EXCLUDED_FROM_NEW_NUMERIC_PERSONALITY_SCORE":
        raise RuntimeError("Splenic accuracy improperly reintroduced")
    return items

def assess(plan:dict,status_overrides:dict|None=None)->dict:
    items=validate_plan(plan)
    current={k:items[k]["current"] for k in items}
    if status_overrides:
        unknown=set(status_overrides)-set(TRACKS)
        if unknown:raise ValueError("Unexpected status target")
        current.update(status_overrides)
    for key,state in current.items():
        if (state not in KNOWN_TERMINAL[key]) and (state not in {"OPEN","OPEN_SOURCE_ADJUDICATION","OPEN_FULL_CENTURY",
            "OPEN_EXTERNAL_ROUTE_UNAVAILABLE","UNAVAILABLE_DIRECT_ROUTE","HIGH_LEVEL_CONFIRMED_FACETS_UNSCORED",
            "NOT_YET_REQUESTED_AS_COMPLETION_GATE","UNVALIDATED_SYMBOLIC_REPORT_COMPLETED_NO_HUMAN_COHORT"}):
            raise ValueError("Unexpected stage state "+key+":"+state)
    finished={k:current[k] in KNOWN_TERMINAL[k] for k in TRACKS}
    # Inability to send to Google is an explicitly noted terminal delivery,
    # never represented as a received response.
    return {
      "report_complete":all(finished[k] for k in CORE),
      "unfinished_core_tracks":[k for k in CORE if not finished[k]],
      "optional_empirical_validation_complete":current["V"]=="HUMAN_PREDICTIVE_VALIDATION_REPORTED",
      "gemini_reply_received_via_user_paste":current["G"]=="GEMINI_RESPONSE_CAPTURED_AND_RECONCILED" and "Owner pasted" in items["G"].get("captured_route",""),
      "gemini_direct_reply_received":current["G"]=="GEMINI_RESPONSE_CAPTURED_AND_RECONCILED" and items["G"].get("captured_route")=="DIRECT_AUTHENTICATED_GEMINI_RESPONSE_VERIFIED",
      "gemini_external_reply_unavailable":current["G"]=="NOT_SENT_NO_AUTHORIZED_ROUTE_READY_TO_SEND",
      "finished_tracks":finished
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plan",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(assess(json.loads(args.plan.read_bytes())),sort_keys=True))
if __name__=="__main__":main()
