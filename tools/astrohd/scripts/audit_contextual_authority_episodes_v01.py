#!/usr/bin/env python3
"""Generic episode-level observation auditor for multiple decision processes.

Distinguishes instant social impression, important CHOICE, self-heard direction,
emotional wave, deliberate analysis and sudden cognitive answer. Model
source conditions come from a source-qualified schema, not from known DOB.
This is descriptive respondent interview engineering, NOT astrology validation
or a new score. Every absent field stays UNKNOWN, not a negative result.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

SCHEMA="astrohd_contextual_behavior_and_authority_observation_contract_v01"
BOOL_FIELDS=(
 "decision_completed", "instant_body_signal", "brief_nonrepeating_signal",
 "signal_decided_choice","own_spoken_words_heard","trusted_listener_present",
 "own_speech_decided_choice","emotional_wave_over_time","wave_settled_choice",
 "prolonged_reasoning","information_missing","result_independently_observable",
)
EXPECTED_FIELDS={"episode_id","context","decision_or_impression",
                 "evidence_type","generality_assessment","context_qualifier"}
HD_CATEGORIES=("HD_SPLENIC","HD_SELF_PROJECTED","HD_EMOTIONAL")

def sha(path:Path)->str:return sha256(path.read_bytes()).hexdigest()

def load_contract(raw:dict)->dict:
    if raw.get("schema")!=SCHEMA:raise ValueError("Wrong source contract")
    entries={r["key"]:r for r in raw["generic_observation_fields"]}
    if len(entries)!=len(raw["generic_observation_fields"]):raise ValueError("Duplicate keys")
    if set(BOOL_FIELDS)-set(entries):raise ValueError("Missing three-state decision fields")
    if not raw["global_rules"]["do_not_count_missing_fields_as_false"]:
        raise RuntimeError("Unknown evidence cannot be treated as false")
    if not raw["global_rules"]["no_natal_score_from_source_familiarity"]:
        raise RuntimeError("Inappropriate natal scoring")
    if not raw["global_rules"]["across_context_generalization_requires_explicit_participant_confirmation"]:
        raise RuntimeError("No generalized pattern from examples alone")
    if not raw["source_pattern_conditions"]["someone_elses_voice_is_not_own_spoken_voice"]:
        raise RuntimeError("Important self-projected source boundary lost")
    return entries

def check_episode(event:dict[str,Any],contract:dict[str,dict])->None:
    if not EXPECTED_FIELDS.issubset(event):raise ValueError("Episode lacks provenance or context")
    for k in EXPECTED_FIELDS:
        if k not in contract:raise RuntimeError("Contract lacks base field "+k)
    for k in BOOL_FIELDS:
        if k in event and event[k] is not None and type(event[k]) is not bool:
            raise ValueError("Episode field "+k+" must be true, false or null")
    for k in ("context","decision_or_impression","evidence_type","generality_assessment"):
        options=contract[k].get("values")
        if not options or event[k] not in options:raise ValueError("Unknown "+k)
    if not isinstance(event["episode_id"],str) or not event["episode_id"]:
        raise ValueError("Opaque episode ID required")
    if not isinstance(event["context_qualifier"],str):
        raise ValueError("Context qualifier must be text")
    if event.get("signal_decided_choice") is True and event.get("decision_completed") is not True:
        raise ValueError("Cannot say signal decided choice if no choice completed")
    if event.get("own_speech_decided_choice") is True and event.get("decision_completed") is not True:
        raise ValueError("Cannot say own voice settled a choice if choice not complete")
    if event.get("wave_settled_choice") is True and event.get("decision_completed") is not True:
        raise ValueError("Cannot say emotional wave decided choice if not complete")
    if event.get("result_independently_observable") is True and event.get("decision_completed") is not True:
        raise ValueError("Cannot independently assess outcome of an unmade choice")
    # No claim that a missed contrast is "false": missing and unverified remain unknown.

def triage(event:dict[str,Any],contract:dict[str,dict])->dict:
    check_episode(event,contract)
    is_decision=event["decision_or_impression"]=="important_decision" and event.get("decision_completed") is True
    body=event.get("instant_body_signal") is True
    brief=event.get("brief_nonrepeating_signal") is True
    self_voice=event.get("own_spoken_words_heard") is True
    listener=event.get("trusted_listener_present") is True
    speech_decision=event.get("own_speech_decided_choice") is True
    emotional=event.get("emotional_wave_over_time") is True
    wave_choice=event.get("wave_settled_choice") is True
    snippets=[]
    if body:
        snippets.append("INSTANTANEOUS_BODILY_AWARENESS_REPORTED")
        if not brief:snippets.append("BREVITY_AND_NONREPETITION_UNRESOLVED")
    if event.get("prolonged_reasoning") is True:
        snippets.append("PROLONGED_ANALYSIS_REPORTED")
    if event.get("information_missing") is True:
        snippets.append("INFORMATION_LIMITATION_REPORTED")
    if event["decision_or_impression"]=="insight_or_answer":
        snippets.append("SUDDEN_INSIGHT_NOT_SPECIFIC_TO_ANY_HD_AUTHORITY")
    if event["decision_or_impression"]=="person_impression":
        snippets.append("SOCIAL_PERSON_IMPRESSION_NOT_DIRECT_EVIDENCE_OF_DECISION_AUTHORITY")
    # Strict source conditions, not a psychometric measure or an outcome.
    support={
        "HD_SPLENIC":bool(is_decision and body and brief and event.get("signal_decided_choice") is True),
        "HD_SELF_PROJECTED":bool(is_decision and self_voice and listener and speech_decision),
        "HD_EMOTIONAL":bool(is_decision and emotional and wave_choice),
    }
    return {
        "episode_id":event["episode_id"],
        "context":event["context"],
        "event_type":event["decision_or_impression"],
        "source_compatibility_conditions_met":support,
        "partial_or_competing_explanations":snippets,
        "source_specific_authority_not_established_by_one_episode":True,
        "outcome_validated":bool(event.get("result_independently_observable") is True and is_decision),
        "natal_score_delta":None,
    }

def audit_episodes(record:dict,contract:dict[str,dict])->dict:
    if record.get("schema")!="private_or_synthetic_contextual_authority_episodes_v01":
        raise ValueError("Wrong episode source schema")
    src=record.get("episodes")
    if not isinstance(src,list) or not src:raise ValueError("No episodes to review")
    ids=[x.get("episode_id") for x in src]
    if len(set(ids))!=len(ids):raise ValueError("Repeated episode ID may double count")
    results=[triage(x,contract) for x in src]
    totals={name:sum(row["source_compatibility_conditions_met"][name] for row in results)
            for name in HD_CATEGORIES}
    # Shared source features and examples do NOT establish general decisions.
    return {
        "status":"POSTEXPOSURE_SOURCE_OBSERVATIONS_NO_NATAL_SCORE",
        "total_episodes":len(results),
        "strict_authority_eligible_episode_counts":totals,
        "episodes_reporting_immediate_bodily_awareness":sum("INSTANTANEOUS_BODILY_AWARENESS_REPORTED" in x["partial_or_competing_explanations"] for x in results),
        "episodes_reporting_prolonged_analysis":sum("PROLONGED_ANALYSIS_REPORTED" in x["partial_or_competing_explanations"] for x in results),
        "episodes_with_any_strict_authority_process":sum(any(x["source_compatibility_conditions_met"].values()) for x in results),
        "any_reliable_long_run_authority_claim_proven":False,
        "sample_representative":False,
        "source_domain":"Human Design doctrine interpreted against individual self-report; not empirical astrology validity",
        "episode_details":results,
    }

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--contract",type=Path,required=True)
    p.add_argument("--episodes",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError("Private source output must be immutable")
    contract=load_contract(json.loads(args.contract.read_bytes()))
    raw=json.loads(args.episodes.read_bytes())
    summary=audit_episodes(raw,contract)
    summary["source_episodes_sha256"]=sha(args.episodes)
    summary["source_contract_sha256"]=sha(args.contract)
    args.output.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":summary["status"],"total_episodes":summary["total_episodes"],
      "strict_authority_eligible_episode_counts":summary["strict_authority_eligible_episode_counts"],
      "no_authority_proven":True,"output_sha256":sha(args.output)},sort_keys=True))
if __name__=="__main__":main()
