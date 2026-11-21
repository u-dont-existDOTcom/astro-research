#!/usr/bin/env python3
"""Three-wave source audit closeout with explicit missing evidence and no rates.

Source baseline preserved; incrementally merge qualified public search results.
Do not interpret counts as populations or user-level chart predictions.
"""
from __future__ import annotations
import argparse,importlib.util,json
from pathlib import Path
from urllib.parse import urlparse
from collections import Counter
HERE=Path(__file__).resolve().parent
def loadmod(name:str):
    sp=importlib.util.spec_from_file_location(name,HERE/(name+".py"))
    obj=importlib.util.module_from_spec(sp);sp.loader.exec_module(obj);return obj
pilot=loadmod("audit_disputed_predictor_corpus_v01")
w2mod=loadmod("audit_disputed_predictor_wave2_v01")
SCHEMA="astrohd_disputed_predictor_forum_wave3_v01"
READ={"full_original_page","original_forum_search_excerpt","original_official_search_excerpt"}
SCOPE="THIRD_SOURCE_QUALIFICATION_GAP_CHECK_NOT_A_POPULATION_SAMPLE"

def normalize_report(e:dict)->dict:
    return {"id":e["id"],"claim_id":e["claim_id"],"url":e["url"],
            "date":e["reported_source_date"],"evidence_type":e["evidence_type"],
            "summary":e["summary"],"read_mode":e["read_mode"],
            "independent_birth_record_verified":False,
            "prospective_prediction_record_verified":False,
            "scorable_accuracy_result":False}

def audit(protocol:dict,base:dict,wave2:dict,wave3:dict)->dict:
    a=w2mod.merge(protocol,base,wave2)
    if wave3.get("schema")!=SCHEMA or wave3.get("status")!=SCOPE:
        raise ValueError("Wrong third wave")
    if wave3.get("bounded_search_waves_completed")!=3 or not wave3.get("gaps"):
        raise ValueError("Third pass is not source-qualified/closed")
    if wave3.get("forum_failure_rates_claimed") is not False or wave3.get("independent_validated_predictions")!=0:
        raise RuntimeError("No prospective truth or failure rates")
    if len(wave3.get("new_claims",[]))!=4 or len(wave3.get("new_evidence",[]))!=11:
        raise ValueError("W3 scope drift")
    all_old_claims={x["id"] for x in base["claims"]+wave2["new_claims"]}
    all_old_evidence={x["id"] for x in base["evidence"]+wave2["new_evidence"]}
    known_threads={w2mod.discussion_key(x["url"]) for x in base["evidence"]+wave2["new_evidence"]}
    new_claims=set();new_ids=set();full=official=forum=0
    for c in wave3["new_claims"]:
        if c["id"] in all_old_claims or c["id"] in new_claims:
            raise ValueError("Unexpected duplicate claim")
        new_claims.add(c["id"])
    for e in wave3["new_evidence"]:
        if e["id"] in all_old_evidence or e["id"] in new_ids:
            raise ValueError("Unexpected duplicate evidence ID")
        new_ids.add(e["id"])
        if e["claim_id"] not in new_claims|all_old_claims:
            raise ValueError("Unknown claim ID")
        if e["read_mode"] not in READ:raise ValueError("Bad read mode")
        if e["evidence_type"] not in pilot.TYPES:raise ValueError("Unknown evidence type")
        if e.get("independent_birth_record_verified") is not False or e.get("objective_outcome_verified") is not False or e.get("prospective_prediction_record_verified") is not False:
            raise RuntimeError("Do not invent corroboration")
        u=urlparse(e["url"])
        if u.scheme!="https" or not u.netloc or not e.get("summary"):
            raise ValueError("Bad source URL")
        if not e.get("source_actor_id"):raise ValueError("Missing actor relation")
        if e["reported_source_date"]:
            from datetime import date
            date.fromisoformat(e["reported_source_date"])
        if e["read_mode"]=="full_original_page":full+=1
        elif e["read_mode"]=="original_official_search_excerpt":official+=1
        else:forum+=1
    if (full,official,forum)!=(wave3["full_page_read_count"],wave3["original_official_excerpt_count"],wave3["original_forum_excerpt_count"]):
        raise ValueError("Miscounted web read scope")
    merged=json.loads(json.dumps(base))
    merged["claims"].extend(wave2["new_claims"]+wave3["new_claims"])
    merged["evidence"].extend(normalize_report(x) for x in wave2["new_evidence"]+wave3["new_evidence"])
    result=pilot.audit(protocol,merged)
    current_threads={w2mod.discussion_key(x["url"]) for x in wave3["new_evidence"]}
    return {
        "status":"BOUNDED_THREE_WAVE_FORUM_SCREEN_COMPLETE_WITH_EVIDENCE_GAPS",
        "claim_count":result["source_claims_registered"],
        "observation_units":result["sampled_evidence_units"],
        "unique_source_discussions_across_three_waves":len(known_threads|current_threads),
        "overlapping_prior_discussions_in_third":len(known_threads&current_threads),
        "third_full_page_read_units":full,
        "third_official_excerpt_read_units":official,
        "third_forum_excerpt_read_units":forum,
        "source_specific_missing_gaps":wave3["gaps"],
        "not_a_population_sample":True,
        "no_verified_chart_prospective_prediction":result["prospective_verified_prediction_records"]==0,
        "no_calibrated_falsification_rates":not result["any_per_system_top_frequency_rank_supported"],
        "source_school_counts":{k:{"claims":v["claims_registered"],"purposive_units":v["seed_evidence_units"]} for k,v in result["stratum_coverage"].items()},
        "component_wave2_sha_requires_separate_validation":False
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("protocol","baseline","wave2","wave3"):p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(audit(*[json.loads(getattr(a,k).read_bytes()) for k in ("protocol","baseline","wave2","wave3")]),sort_keys=True))
if __name__=="__main__":main()
