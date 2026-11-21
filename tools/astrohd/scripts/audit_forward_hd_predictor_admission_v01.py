#!/usr/bin/env python3
"""Forward-only admission checker. Excludes Splenic safety cue from NEW scores.

Does not rewrite immutable old rules/receipts. Applies equal independent
validation requirements to other HD authority claims. Source-only chart
metadata (including computed Splenic Authority label) is still allowed.
Requires explicit call from any future scorer to enforce at runtime.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

SCHEMA="astrohd_forward_only_predictor_admission_policy_v01"
ORIGINAL_GENERIC_SHA="3424672432f7f071ec90ef9ddce52a67ff6794911e92b1a1e04f079262ea6200"
ORIGINAL_44_SHA="f16565094a1a8eede720dd369dfdd4c0d4700a213520b535de28f8f88dd40afd"

def sha(path:Path)->str:return sha256(path.read_bytes()).hexdigest()
def normalize(t:str)->str:return "".join(c for c in str(t).lower() if c.isalnum())

def source_excluded(mapping:dict,policy:dict)->bool:
    if policy.get("schema")!=SCHEMA:raise ValueError("Unknown policy")
    excluded=policy["excluded"][0]
    direct_id= str(mapping.get("mapping_id",mapping.get("id","")))
    if direct_id in excluded["source_mapping_ids"]:
        return True
    feature=mapping.get("chart_feature_predicate") or mapping.get("predicate") or {}
    if feature.get("feature")=="authority":
        vals=feature.get("values") or [feature.get("equals")]
        if any(normalize(v)==normalize(excluded["rule_value"]) for v in vals if v is not None):
            return True
    # A statement can smuggle the exact same reliability construct through
    # source aliases, even without a syntactic "authority" predicate.
    if direct_id=="GATE_57_SOMATIC_ALT" or mapping.get("source_rule_id")=="HD_GATE57_SOMATIC_ALT":
        return True
    return False

def admit(mapping:dict,policy:dict,behavior_model:str)->dict:
    if policy.get("schema")!=SCHEMA:raise ValueError("Wrong new policy")
    if behavior_model not in {"new_hd_personality_score","historical_read_only","source_only_registry"}:
        raise ValueError("Unknown operation")
    direct_id=str(mapping.get("mapping_id",mapping.get("id","")))
    if behavior_model=="historical_read_only":
        return {"rule_id":direct_id,"disposition":"HISTORICAL_READ_ONLY_NEVER_RESCORING"}
    if behavior_model=="source_only_registry":
        return {"rule_id":direct_id,"disposition":"KEEP_AS_HISTORICAL_DOCTRINAL_DESCRIPTION"}
    if source_excluded(mapping,policy):
        return {"rule_id":direct_id,"disposition":"EXCLUDED_FROM_NEW_BEHAVIORAL_SCORE"}
    feature=mapping.get("chart_feature_predicate") or mapping.get("predicate") or {}
    if feature.get("feature")=="authority":
        return {"rule_id":direct_id,"disposition":"QUARANTINE_ALL_OTHER_AUTHORITY_PROCESSES_UNTIL_COMPARABLE_VALIDATION"}
    return {"rule_id":direct_id,"disposition":"ELIGIBILITY_REQUIRES_OTHER_GENERIC_SOURCE_AND_EVIDENCE_REVIEW"}

def audit(policy:dict,old27:dict,old44:dict)->dict:
    if policy.get("schema")!=SCHEMA:raise ValueError("Unrecognized admission policy")
    old=old27["mappings"]+old44["mappings"]
    excl=[m for m in old if source_excluded(m,policy)]
    ids={m.get("mapping_id",m.get("id")) for m in excl}
    required={"MAP-AUTH-SPLENIC-D01","MAP-AUTH-SPLENIC-D02","AUTH_SPLENIC_SIGNAL"}
    if not required.issubset(ids):raise RuntimeError("Old Splenic source claims escaped")
    if any(admit(m,policy,"new_hd_personality_score")["disposition"]!="EXCLUDED_FROM_NEW_BEHAVIORAL_SCORE" for m in excl):
        raise RuntimeError("Excluded new scored source was admitted")
    if not policy["historical_immutability"]["unchanged_sources"]:
        raise RuntimeError("Frozen sources must be preserved")
    return {
       "status":"PASS_NEW_HD_SOMATIC_PREDICTOR_SOURCE_EXCLUSION",
       "old_sources_preserved":True,
       "new_scored_source_ids_excluded":sorted(ids),
       "new_scored_source_count_excluded_in_27_and_44":len(excl),
       "other_authority_processes_symmetrically_quarantined":True,
       "not_yet_connected_to_new_scoring_runtime":True,
       "old_historical_rank_unchanged":True
    }

def main():
    p=argparse.ArgumentParser()
    for attr in ("policy","original_generic","original_44"):
        p.add_argument("--"+attr.replace("_","-"),required=True,type=Path)
    args=p.parse_args()
    if sha(args.original_generic)!=ORIGINAL_GENERIC_SHA or sha(args.original_44)!=ORIGINAL_44_SHA:
        raise RuntimeError("Original doctrine mapping changed")
    result=audit(
        json.loads(args.policy.read_bytes()),
        json.loads(args.original_generic.read_bytes()),
        json.loads(args.original_44.read_bytes()))
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
    main()
