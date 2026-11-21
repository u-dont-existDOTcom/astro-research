#!/usr/bin/env python3
"""Source-qualified inspection of the PREEXISTING Ptolemy Mars–Venus passage.

The conditional Ptolemy III.13 register pre-dates the owner's new personal
reports. But selecting this feature to inspect AFTER hearing a matching
story is NOT a blind confirmation. The old HD shortlist midpoints do not
represent a century-wide Western search. No user identity or chart times
are emitted to Git or terminal; output is owner-private and no scores.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

SOURCE_RULE_ID="PTOLEMY-III13-MARS-VENUS"
INVENTORY_SCHEMA="private_astrologer_complete_western_hd_14_better_hd_intervals_inventory_v01"

def sha(path:Path)->str:return sha256(path.read_bytes()).hexdigest()

def source_eligibility(registry:dict)->dict:
    source=[x for x in registry["rules"] if x["id"]==SOURCE_RULE_ID]
    if len(source)!=1:raise ValueError("Missing or duplicate Ptolemy condition")
    r=source[0]
    if r["eligibility"]!="UNRESOLVED_CONDITIONAL_GOVERNANCE":
        raise RuntimeError("Do not retroactively promote historical passage")
    if r["automatically_scored"] is not False:
        raise RuntimeError("Mars–Venus could not enter natal scoring")
    if "actual planetary alliance/governance" not in r["required_conditions"]:
        raise RuntimeError("Ptolemy governor conditionality is required")
    return r

def audit(registry:dict,inventory:dict)->dict:
    source_eligibility(registry)
    if inventory.get("schema")!=INVENTORY_SCHEMA:
        raise ValueError("Unexpected chart inventory")
    units=inventory["comparison_units"]
    if len(units)!=15 or sum(x["private_id"]=="REFERENCE" for x in units)!=1:
        raise ValueError("Must include actual plus all 14 past candidate midpoints")
    matches=[]
    for u in units:
        witness=u["chart_midpoint"]["Western"]["source_witness"]
        aspects=witness["all_seven_planet_tight_aspects_within_3deg"]
        vm=[x for x in aspects if x["aspect"]=="conjunction" and
            set(x["planets"])=={"Venus","Mars"}]
        if len(vm)>1:raise ValueError("Duplicate Mars–Venus aspect")
        if vm:
            orb=vm[0]["orb_degrees"]
            if not isinstance(orb,(int,float)) or not 0<=orb<=3:
                raise ValueError("Invalid aspect orb")
            matches.append({"private_id":u["private_id"],"orb_degrees":orb})
    ref=next((x for x in matches if x["private_id"]=="REFERENCE"),None)
    return {
        "schema":"ptolemy_preexisting_mars_venus_conditional_shortlist_midpoints_v01",
        "predeclared_historical_source_rule":SOURCE_RULE_ID,
        "source_status":"UNRESOLVED_CONDITIONAL_GOVERNANCE_NOT_AUTOMATICALLY_SCORED",
        "feature_examination_selected_after_owner_personal_report":True,
        "comparison_scope":"REFERENCE_AND_14_PREVIOUS_HD_SELECTED_MIDPOINTS_ONLY",
        "candidate_midpoints_scanned":len(units)-1,
        "actual_reference_close_conjunction":ref is not None,
        "reference_orb_degrees":ref["orb_degrees"] if ref else None,
        "old_hd_selected_candidate_midpoints_close_conjunction":sum(x["private_id"]!="REFERENCE" for x in matches),
        "no_proof_of_continuous_candidate_interval_coverage":True,
        "no_proof_of_western_or_joint_rank_one":True,
        "no_natal_score_change":True,
        "private_aspect_matching_units":matches,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--private-inventory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError("Immutable result must not overwrite")
    s=json.loads(a.source.read_bytes())
    inv=json.loads(a.private_inventory.read_bytes())
    out=audit(s,inv)
    out["source_sha256"]=sha(a.source)
    out["private_inventory_sha256"]=sha(a.private_inventory)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:out[k] for k in (
        "source_status","actual_reference_close_conjunction",
        "reference_orb_degrees",
        "old_hd_selected_candidate_midpoints_close_conjunction",
        "no_proof_of_western_or_joint_rank_one"
    )},sort_keys=True))
    print("OUTPUT_SHA256",sha(a.output))
if __name__=="__main__":main()
