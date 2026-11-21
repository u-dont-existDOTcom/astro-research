#!/usr/bin/env python3
"""Whole-source Authority-only evidence overlay for a PRIVATE chart collection.

Reuses a fixed generic source-contract + independently calculated full HD
charts, NOT target-specific weights. Does not assume a social impression is
an important decision; does not infer opposite traits from absence of evidence.
No new natal score, ranking, or chart time leaks to source control.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

SUPPORTED={
 "Splenic":"HD_SPLENIC",
 "Self Projected":"HD_SELF_PROJECTED",
 "Emotional Solar Plexus":"HD_EMOTIONAL",
}
INVENTORY_SCHEMA="private_astrologer_complete_western_hd_14_better_hd_intervals_inventory_v01"
EVIDENCE_STATUS="POSTEXPOSURE_SOURCE_OBSERVATIONS_NO_NATAL_SCORE"

def sha(path:Path)->str:return sha256(path.read_bytes()).hexdigest()

def study(inventory:dict,evidence:dict)->dict:
    if inventory.get("schema")!=INVENTORY_SCHEMA:
        raise ValueError("Wrong private comparison source")
    if evidence.get("status")!=EVIDENCE_STATUS:
        raise ValueError("Wrong source condition audit")
    rows=inventory["comparison_units"]
    if len(rows)!=15 or sum(r["private_id"]=="REFERENCE" for r in rows)!=1:
        raise ValueError("Need original plus all 14 old shortlist intervals")
    counts=evidence.get("strict_authority_eligible_episode_counts",{})
    if set(counts)!={"HD_SPLENIC","HD_SELF_PROJECTED","HD_EMOTIONAL"}:
        raise ValueError("Missing expected complete source Authority conditions")
    if any(type(n)!=int or n<0 for n in counts.values()):
        raise ValueError("Invalid source evidence number")
    partial=evidence.get("episodes_reporting_immediate_bodily_awareness")
    if type(partial)!=int or partial<0:
        raise ValueError("Missing context-specific partial bodily impression evidence")
    byauthority=Counter()
    results=[]
    for i,r in enumerate(rows):
        chart=r["chart_midpoint"]["HD"]
        authority=chart["authority"]
        if authority not in SUPPORTED:
            raise ValueError("Unsupported Authority is unresolved, never silently mark no evidence")
        key=SUPPORTED[authority]
        byauthority[authority]+=1
        results.append({
            "case_id":r["private_id"],
            "HD_authority":authority,
            "HD_profile":chart["profile"],
            "strict_important_decision_condition_episodes":counts[key],
            "source_claim_conclusive":False,
            "no_opposite_inferred_for_other_authorities":True,
            "conditional_observation":"Bodily impressions can occur irrespective of a chart's theoretical Authority; mere impression is NOT a choice."
        })
    return {
        "schema":"private_nonbespoke_hd_authority_contrast_from_source_episodes_v01",
        "source_case_count":len(rows),
        "competing_authorities":dict(byauthority),
        "source_strict_decision_conditions":counts,
        "non_decision_immediate_bodily_impressions_reported":partial,
        "any_global_decision_authority_winner":False,
        "historical_hd_23_rule_scores_changed":False,
        "new_western_personality_score":None,
        "scope":"Previously listed 14 old-HD-score alternatives plus reference, NOT full 100-year joint search",
        "outcomes":results
    }

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--private-inventory",type=Path,required=True)
    p.add_argument("--private-evidence",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError("Immutable comparison already exists")
    z=study(json.loads(a.private_inventory.read_bytes()),json.loads(a.private_evidence.read_bytes()))
    z["source_inventory_sha256"]=sha(a.private_inventory)
    z["source_evidence_sha256"]=sha(a.private_evidence)
    a.output.write_text(json.dumps(z,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"comparison_case_count":z["source_case_count"],
                      "all_strict_source_counts":z["source_strict_decision_conditions"],
                      "no_new_natal_rank":True,
                      "output_sha256":sha(a.output)},sort_keys=True))

if __name__=="__main__":main()
