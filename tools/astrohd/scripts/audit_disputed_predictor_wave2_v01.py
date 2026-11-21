#!/usr/bin/env python3
"""Validate second forum source search and merge WITHOUT silently rewriting pilot.

Forums are purposive source exemplars, not population samples, predictors or
birth-chart validation. Separate thread/speaker/source read modes explicitly.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("pilot",HERE/"audit_disputed_predictor_corpus_v01.py")
pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilot)
SCHEMA="astrohd_disputed_predictor_forum_wave2_v01"
VALID_READ={"full_original_page","original_forum_search_excerpt"}
VALID_STATUS="SECOND_TARGETED_PUBLIC_SOURCE_PASS_NOT_POPULATION_SAMPLE"

def discussion_key(url:str)->str:
    u=urlparse(url)
    path=[p for p in u.path.split("/") if p]
    if "comments" in path:
        idx=path.index("comments")
        if len(path)>idx+1:return "reddit:"+path[idx+1].lower()
    return u.netloc.lower()+":"+"/".join(path)

def merge(p:dict,baseline:dict,wave:dict)->dict:
    if wave.get("schema")!=SCHEMA or wave.get("status")!=VALID_STATUS:
        raise ValueError("Wrong wave2 source schema/status")
    if not (wave.get("statistical_denominators_available") is False and wave.get("verified_prospective_natal_prediction_receipts")==0):
        raise RuntimeError("No proven denominator or prospective accuracy")
    if len(wave.get("new_claims",[]))!=2:raise ValueError("Unexpected wave2 new claim scope")
    if len(wave.get("new_evidence",[]))!=20:raise ValueError("Unfinished or expanded wave2 sample")
    old_claim_ids={c["id"] for c in baseline["claims"]}
    for c in wave["new_claims"]:
        if c["id"] in old_claim_ids:raise ValueError("Overwrite of old claim")
        old_claim_ids.add(c["id"])
    old_ids={e["id"] for e in baseline["evidence"]}
    new_ids=set();actor_thread_seen=set();full=0
    for e in wave["new_evidence"]:
        if e["id"] in old_ids or e["id"] in new_ids:raise ValueError("Repeated evidence ID")
        new_ids.add(e["id"])
        if e["claim_id"] not in old_claim_ids:raise ValueError("Unknown claim")
        if e["read_mode"] not in VALID_READ:raise ValueError("Read mode not independently grounded")
        if e["read_mode"]=="full_original_page":full+=1
        if e.get("independent_birth_record_verified") is not False or e.get("objective_outcome_verified") is not False or e.get("prospective_prediction_record_verified") is not False:
            raise RuntimeError("Self-reports cannot be promoted to verified outcomes")
        if not e.get("source_actor_id"):raise ValueError("Missing observed actor relation")
        u=urlparse(e["url"])
        if u.scheme!="https" or not u.netloc or not e.get("summary"):
            raise ValueError("Missing real original reference")
        source_parts=[x for x in u.path.split("/") if x]
        if len(source_parts)>=3 and source_parts[1]=="comments":
            real_thread=source_parts[2]
            if e["discussion_id"]!=real_thread:raise ValueError("Discussion identity discrepancy")
        if e["source_actor_id"]!="OP_PLUS_COMMENT":
            pair=(e["discussion_id"],e["source_actor_id"])
            if pair in actor_thread_seen:raise ValueError("Duplicate actor in same discussion")
            actor_thread_seen.add(pair)
    if full!=wave["full_page_read_count"] or full+wave["excerpts_count"]!=len(new_ids):
        raise ValueError("Incorrect source read-mode count")
    old_urls={e["url"] for e in baseline["evidence"]}
    overlap_urls=sorted(old_urls & {e["url"] for e in wave["new_evidence"]})
    old_threads={discussion_key(e["url"]) for e in baseline["evidence"]}
    wave_threads={discussion_key(e["url"]) for e in wave["new_evidence"]}
    overlap_threads=sorted(old_threads & wave_threads)
    merged=json.loads(json.dumps(baseline))
    merged["claims"].extend(wave["new_claims"])
    merged["evidence"].extend([dict(
         id=e["id"],claim_id=e["claim_id"],url=e["url"],
         date=e["reported_source_date"],evidence_type=e["evidence_type"],
         summary=e["summary"],read_mode=e["read_mode"],
         independent_birth_record_verified=e["independent_birth_record_verified"],
         prospective_prediction_record_verified=e["prospective_prediction_record_verified"],
         scorable_accuracy_result=False,
    ) for e in wave["new_evidence"]])
    result=pilot.audit(p,merged)
    result["waves_completed"]=2
    result["additional_wave_evidence_units"]=len(new_ids)
    result["new_claim_ids"]=[c["id"] for c in wave["new_claims"]]
    result["wave2_full_page_read_units"]=full
    result["wave2_excerpt_read_units"]=len(new_ids)-full
    result["overlapping_old_and_wave2_discussion_urls"]=overlap_urls
    result["overlapping_old_and_wave2_normalized_threads"]=overlap_threads
    result["combined_distinct_discussion_sources"] = len(old_threads|wave_threads)
    result["overlapping_thread_does_not_equal_independent_participant"]=True
    return result

def main()->None:
    a=argparse.ArgumentParser()
    for n in ("protocol","baseline","wave2"):
        a.add_argument("--"+n,required=True,type=Path)
    z=a.parse_args()
    res=merge(json.loads(z.protocol.read_bytes()),json.loads(z.baseline.read_bytes()),json.loads(z.wave2.read_bytes()))
    print(json.dumps({"status":res["status"],"claims":res["source_claims_registered"],
                      "evidence_units":res["sampled_evidence_units"],
                      "wave2_full":res["wave2_full_page_read_units"],
                      "wave2_excerpt":res["wave2_excerpt_read_units"],
                      "overlap_prior_threads":len(res["overlapping_old_and_wave2_normalized_threads"]),
                      "prospective_natal_records":res["prospective_verified_prediction_records"],
                      "valid_population_rate":res["any_per_system_top_frequency_rank_supported"],
                      "source_sweep_count":res["waves_completed"]},sort_keys=True))
if __name__=="__main__": main()
