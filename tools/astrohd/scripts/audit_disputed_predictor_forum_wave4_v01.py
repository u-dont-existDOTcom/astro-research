#!/usr/bin/env python3
"""Validate the owner-authorized fourth research wave, not community prevalence.

Preserves all prior three waves unchanged. Sampled utterance count is not
unique humans or statistically representative chart-failure rates. A self-
reported 20-case series is an anecdote without verified external case records.
"""
from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
from urllib.parse import urlparse

HERE=Path(__file__).resolve().parent

def load_module(name:str):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+".py"))
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

pilot=load_module("audit_disputed_predictor_corpus_v01")
w2=load_module("audit_disputed_predictor_wave2_v01")
w3=load_module("audit_disputed_predictor_three_wave_closeout_v01")
SCHEMA="astrohd_disputed_predictor_forum_wave4_owner_authorized_v01"
STATUS="NEW_OWNER_AUTHORIZED_SOURCE_FOLLOWUP_AFTER_BOUNDED_THREE_WAVE_CLOSEOUT"
VALID_READ={"full_original_page","original_forum_search_excerpt","original_official_search_excerpt"}


def merge(protocol:dict,base:dict,wave2:dict,wave3:dict,wave4:dict)->dict:
    prev=w3.audit(protocol,base,wave2,wave3)
    if prev["status"]!="BOUNDED_THREE_WAVE_FORUM_SCREEN_COMPLETE_WITH_EVIDENCE_GAPS":
        raise ValueError("Previous three waves not closed")
    if wave4.get("schema")!=SCHEMA or wave4.get("scope")!=STATUS or wave4.get("prior_waves_count")!=3:
        raise ValueError("Incorrect owner-authorized scope or three-wave origin")
    if wave4.get("representative_population_denominator") is not False or wave4.get("rank_supported") is not False:
        raise RuntimeError("Cannot infer population failure rates from selected posts")
    if wave4.get("claim_level_verified_prospective_outcomes")!=0 or wave4.get("no_independent_predicted_human_behavior_test") is not True:
        raise RuntimeError("No verified human predictions available")
    if len(wave4.get("source_claims_added",[]))!=4 or len(wave4.get("public_source_observation_units",[]))!=22:
        raise ValueError("Fourth-wave evidence scope changed without updated method")
    claims=base["claims"]+wave2["new_claims"]+wave3["new_claims"]
    old_claim_ids={c["id"] for c in claims}
    new_claim_ids=set()
    for c in wave4["source_claims_added"]:
        if c["id"] in old_claim_ids or c["id"] in new_claim_ids:
            raise ValueError("New claim collides with old")
        if c["stratum"] not in pilot.BROAD_FAMILIES or c["disposition"] not in pilot.DISPOSITIONS:
            raise ValueError("Unknown school or disposition")
        if c.get("forum_population_denominator") is not None or c.get("empirically_calibrated") is not False:
            raise RuntimeError("The source doesn't provide representative denominators")
        new_claim_ids.add(c["id"])
    claims+=wave4["source_claims_added"]
    existing=base["evidence"]+[x for x in wave2["new_evidence"]]+[x for x in wave3["new_evidence"]]
    old_evidence_ids={e["id"] for e in existing}
    known_threads={w2.discussion_key(e["url"]) for e in existing}
    actors=set()
    source_refs=[]
    coverage=Counter()
    wave4_threads=set()
    observations=[]
    for e in wave4["public_source_observation_units"]:
        if e["id"] in old_evidence_ids:raise ValueError("Reused old evidence ID")
        if e["id"] in {x["id"] for x in observations}:raise ValueError("Repeated wave4 evidence ID")
        if e["claim_id"] not in old_claim_ids|new_claim_ids:
            raise ValueError("Missing claim")
        if e["evidence_type"] not in pilot.TYPES:
            raise ValueError("Unknown evidence polarity/interpretation type")
        if e["read_mode"] not in VALID_READ:
            raise ValueError("Missing original source read scope")
        if e.get("prospective_prediction_record_verified") is not False or e.get("objective_outcome_verified") is not False or e.get("scorable_accuracy_result") is not False:
            raise RuntimeError("Unverified anecdote incorrectly promoted to human result")
        if e.get("profile_or_birth_details_recorded") is not False:
            raise ValueError("No personally identifiable source facts in public ledger")
        url=urlparse(e["url"])
        if url.scheme!="https" or not url.netloc or not e.get("summary") or not e.get("source_actor_id"):
            raise ValueError("Invalid source/actor relation")
        tid=w2.discussion_key(e["url"])
        wave4_threads.add(tid)
        actors.add((tid,e["source_actor_id"]))
        coverage[e["claim_id"]]+=1
        source_refs.append(e["id"])
        observations.append(e)
    if len(observations)!=22:
        raise ValueError("Missing fourth-wave examples")
    rm=Counter(e["read_mode"] for e in observations)
    if {k:rm.get(k,0) for k in VALID_READ}!=wave4.get("read_mode_counts"):
        raise ValueError("Incorrect original read modes")
    new_claim_school=Counter(c["stratum"] for c in wave4["source_claims_added"])
    poles=Counter(e["evidence_type"] for e in observations)
    return {
        "schema":"astrohd_disputed_predictor_forum_wave4_audit_receipt_v01",
        "status":"FOURTH_SOURCE_PASS_COMPLETE_WITH_UNVERIFIED_ANECODOTES",
        "waves_completed":4,
        "claims_registered_prior":prev["claim_count"],
        "claims_registered_now":len(claims),
        "source_observation_units_prior":prev["observation_units"],
        "source_observation_units_now":prev["observation_units"]+len(observations),
        "new_wave_sampled_units":len(observations),
        "new_distinct_source_discussions":len(wave4_threads-known_threads),
        "new_source_discussions_overlap_prior":len(wave4_threads&known_threads),
        "distinct_source_discussions_now":len(known_threads|wave4_threads),
        "read_mode_counts":dict(rm),
        "new_claim_school_counts":dict(new_claim_school),
        "new_observation_polarity_counts":dict(poles),
        "sampled_reporter_roles_not_unique_persons":len(actors),
        "independent_person_population_denominator":None,
        "verified_prospective_prediction_records":0,
        "selected_serious_adoption_harm_is_causal_attribution":False,
        "no_numeric_failure_rate_or_birth_rank_supported":True,
        "source_refs":source_refs,
        "source_gap_notes":wave4["non_independence_notes"],
    }


def main():
    p=argparse.ArgumentParser()
    for n in ("protocol","baseline","wave2","wave3","wave4"):
        p.add_argument("--"+n,required=True,type=Path)
    a=p.parse_args()
    docs=[json.loads(getattr(a,k).read_bytes()) for k in ("protocol","baseline","wave2","wave3","wave4")]
    print(json.dumps(merge(*docs),sort_keys=True))
if __name__=="__main__":main()
