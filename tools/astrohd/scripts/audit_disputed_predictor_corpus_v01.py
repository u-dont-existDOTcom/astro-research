#!/usr/bin/env python3
"""Fail-closed stratified community disagreement screening. Never infer prevalence.

This audit does NOT claim astrology works, which predictor is objectively most
often wrong, or that a source contradiction overrides source qualifications.
It checks evidence scope and keeps technical calculation bugs separate from
psychological personality and future event predictions. Original source
excerpts must remain attributable, not auto-validated as facts.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from datetime import date
import json
from pathlib import Path
from urllib.parse import urlparse

SCHEMA="astrohd_disputed_predictor_forum_seed_v01"
PROTO="astrohd_disputed_predictor_forum_audit_protocol_v01"
TYPES={
"first_person_mismatch","first_person_support","first_person_mixed",
"first_person_or_secondhand_mixed","first_person_or_secondhand_support",
"practitioner_mismatch","practitioner_interpretation_mismatch",
"practitioner_mixed","practitioner_reinterpretation",
"implementation_report","official_calculation_note","official_nonpredictive_statement",
"provider_scope_statement"
}
READ={"full_original_page","original_forum_search_excerpt","original_official_search_excerpt","secondary_summary","unopened_link"}
DISPOSITIONS={
"REMOVE_FROM_NEW_SCORE_OWNER_DIRECTIVE","QUARANTINE_SOURCE_ONLY",
"CONDITIONAL_SOURCE_ADJUDICATION","EMPIRICAL_VALIDATION_NEEDED",
"CALCULATION_PARITY_ONLY","NOT_A_PREDICTION",
"INSUFFICIENT_FORUM_COVERAGE","ELIGIBLE_IF_INDEPENDENTLY_VALIDATED"
}
BROAD_FAMILIES={
"human_design","western_modern","western_hellenistic_renaissance",
"vedic_jyotish","chinese_bazi","chinese_ziwei","gene_keys",
"other_astro_traditions_uncovered"
}

def audit(protocol:dict,seed:dict)->dict:
    if protocol.get("schema")!=PROTO or seed.get("schema")!=SCHEMA:
        raise ValueError("Wrong audit source schema")
    if not protocol.get("no_statistical_popularity_claim"):
        raise RuntimeError("Unjustified ranking by complaint volume")
    strata={x["id"] for x in protocol["frozen_strata"]}
    if strata!=BROAD_FAMILIES:raise RuntimeError("Broad system class coverage reduced")
    if seed.get("status")!="SCREENING_PILOT_NONEXHAUSTIVE_NO_FORUM_PREVALENCE":
        raise RuntimeError("Incorrect evidentiary status")
    ids=set();byid={}
    for cl in seed["claims"]:
        id=cl["id"]
        if id in ids:raise ValueError("Duplicate predictor ID")
        if not isinstance(id,str) or not id:raise ValueError("Bad predictor ID")
        ids.add(id);byid[id]=cl
        if cl["stratum"] not in strata or cl["disposition"] not in DISPOSITIONS:
            raise ValueError("Unknown system class or source disposition")
        if cl.get("forum_population_denominator") is not None or cl.get("empirically_calibrated") is not False:
            raise RuntimeError("Cannot invent forum denominator or model calibration")
        if not cl.get("required_verification"):
            raise ValueError("Every claim needs a counterfactual protocol")
    seen=set()
    evidence_counts=Counter();poles=defaultdict(Counter)
    limited_views=0;prospective=0
    for x in seed["evidence"]:
        key=x["id"]
        if key in seen:raise ValueError("Repeated evidence ID")
        seen.add(key)
        if x["claim_id"] not in ids or x["evidence_type"] not in TYPES:
            raise ValueError("Unrecognized claim or evidence class")
        if x["read_mode"] not in READ:raise ValueError("Missing read provenance")
        source=urlparse(x["url"])
        if source.scheme!="https" or not source.netloc or not x.get("summary"):
            raise ValueError("Unverified evidence attribution")
        if x.get("date") is not None:
            try:date.fromisoformat(x["date"])
            except (TypeError,ValueError):raise ValueError("Invalid source date")
        if x.get("prospective_prediction_record_verified") is not False:
            raise RuntimeError("Prospective evidence was not verified")
        if x.get("scorable_accuracy_result") is not False:
            raise RuntimeError("Forum anecdote not a calibrated prediction")
        if x["read_mode"]!="full_original_page":limited_views+=1
        if x["prospective_prediction_record_verified"]:prospective+=1
        evidence_counts[x["claim_id"]]+=1
        poles[x["claim_id"]][x["evidence_type"]]+=1
    no_evidence=sorted(ids-set(evidence_counts))
    by_stratum={}
    for name in sorted(strata):
        claims=[x for x in seed["claims"] if x["stratum"]==name]
        count=sum(evidence_counts[x["id"]] for x in claims)
        by_stratum[name]={"claims_registered":len(claims),"seed_evidence_units":count,
                          "claims_with_no_seed_evidence":sum(evidence_counts[c["id"]]==0 for c in claims),
                          "no_population_denominator":True}
    firstperson_mismatch=sum("first_person_mismatch" in x["evidence_type"] for x in seed["evidence"])
    screen_flags=[{
        "claim_id":c["id"],"stratum":c["stratum"],"disposition":c["disposition"],
        "community_reports_in_purposive_seed":evidence_counts[c["id"]],
        "recorded_objection_or_issue_types":dict(poles[c["id"]]),
        "genuine_rate_or_population_rank":None,
        "needs_independent_validation":True
    } for c in seed["claims"]]
    return {
        "status":"SCREENING_ONLY_COVERAGE_AND_PROVENANCE_PASS",
        "stratum_coverage":by_stratum,
        "source_claims_registered":len(ids),
        "sampled_evidence_units":len(seen),
        "claims_without_direct_seed_evidence":no_evidence,
        "direct_firstperson_mismatch_source_units":firstperson_mismatch,
        "excerpts_not_direct_page_reads":limited_views,
        "prospective_verified_prediction_records":prospective,
        "any_per_system_top_frequency_rank_supported":False,
        "no_original_clauses_overwritten":True,
        "disposition_screen_not_statistical_winner":screen_flags,
    }

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--protocol",required=True,type=Path)
    p.add_argument("--seed",required=True,type=Path)
    a=p.parse_args()
    z=audit(json.loads(a.protocol.read_bytes()),json.loads(a.seed.read_bytes()))
    print(json.dumps(z,sort_keys=True))
if __name__=="__main__":
    main()
