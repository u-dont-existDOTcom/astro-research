#!/usr/bin/env python3
"""DEVELOPMENT-ONLY, AFTER-THE-ANSWER-KNOWN sensitivity to an ATOMIC CH26–44 claim.

This does NOT modify or promote the old compound HD Channel 26–44
entrepreneurship/persuasion/deception mapping. It reuses the old chart predicate
and conditional-prevalence *mechanics*, while hypothetically interpreting
only the persuasive-transmission clause. The behavioral source validity of
that separation is UNPROVEN.

The added hypothesis competes with Gate26 in the SAME original dependency
cluster; it does not count as a second independent persuasive finding.

Output: number of century structural states scoring substantively above the
reference under several illustrative confidence values. Private subject
timestamp, raw self-report and answers only come from private files; never
include this source in a canonical confirmatory scorer.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json,math,sys
from pathlib import Path
from time import perf_counter


BASELINE_SHA="b930e87a366a7d06d0efe40c9ec83044be62116935ec1a986b06c3868fcf9bce"
OLD_PREVALENCE_SHA="24fcf067ace194366426ed26e5c10ac59b0afa1734991e7844efd1bbe69074fc"
ORIGINAL_ID="CH_26_44_ENTERPRISE"
ATOMIC_ID="CH_26_44_PERSUASIVE_TRANSMISSION_HYPOTHESIS"
LOWER_TIER_ID="GATE_26_PERSUASION_ALT"
CONFIDENCES=(0.,0.25,0.5,0.75,0.9)


def file_sha(path:Path)->str:return sha256(path.read_bytes()).hexdigest()

def optional_atom(original, confidence):
    if not 0.<=confidence<=1.:raise ValueError("Invalid sensitivity confidence")
    if original["id"]!=ORIGINAL_ID or original["cluster"]!="ENTERPRISE_PERSUASION_PATTERN":
        raise ValueError("Original full Channel26–44 pathway changed")
    mapping=deepcopy(original)
    mapping["id"]=ATOMIC_ID
    mapping["behavior"]="Hypothetical atomic persuasive transmission when intentionally engaged; no innate deception recognition, bargaining or universal commercial motivation"
    mapping["confidence"]=confidence
    mapping["source"]=original["source"]+"; new clause-only source interpretation requires independent qualification"
    mapping["post_selection"]=True
    return mapping

def validate(source,adjudication,existing):
    if file_sha(source)!=adjudication.get("raw_clarification_sha256"):
        raise RuntimeError("Private persuasion testimony source does not match its adjudication")
    if adjudication.get("target_version")!="V3.7+interview-dev-20261120-002":
        raise RuntimeError("Unexpected target version")
    if adjudication.get("previous_HD_rank_sha256")!=BASELINE_SHA:
        raise RuntimeError("Previous target rank hash mismatch")
    if existing["status"]!="EXPLORATORY_V37_CORRECTED_OBSERVABLES_REUSE_OF_V36_HD_PATHWAYS":
        raise RuntimeError("Existing source rank status differs")
    if existing["full_century_provisional_HD_only_ranking"]["status"]!="COMPLETED_POST_EXPOSURE_V37_23_DIRECT_OBSERVABLE_HD_ONLY":
        raise RuntimeError("Previous full century source rank not the expected saved version")

def analyze(args):
    if args.output.exists():raise FileExistsError("Cannot overwrite sensitivity result")
    prior=json.loads(args.prior.read_bytes())
    previous=json.loads(args.previous_ranking.read_bytes())
    adjudication=json.loads(args.adjudication.read_bytes())
    validate(args.raw,adjudication,previous)
    if file_sha(args.prior)!=OLD_PREVALENCE_SHA or file_sha(args.previous_ranking)!=BASELINE_SHA:
        raise RuntimeError("Pinned scorer prevalence/previous ranking changed")
    repo=args.repo_root.resolve()
    sys.path.insert(0,str(repo/"scripts"))
    import replay_historical_v36_hd_on_verified_cache as history
    import replay_v37_development_direct_hd_observables as v37
    import v43_profile_netinfo_rerun as scorer
    old_model=history.current_model(repo)
    codings=json.loads(args.prior_coding.read_bytes())
    direct=v37.eligibility_audit(old_model,codings)
    direct_ids={m["id"] for m in direct}
    if LOWER_TIER_ID not in direct_ids or ORIGINAL_ID in direct_ids:
        raise RuntimeError("Prior direct eligible gate26/compound26–44 source statuses changed")
    original=next(m for m in old_model["mappings"] if m["id"]==ORIGINAL_ID)
    existing=deepcopy(old_model);existing["mappings"]=direct;existing["contradictions"]=[]
    states,manifest=history.source_states(args.hd_cache)
    reference_t=history.utc(prior["reference_comparisons"][0]["input_utc"])
    ref_index=history.find_state(states,reference_t)
    p=prior["prevalence_by_mapping"]
    prevalence=dict(p)
    if ORIGINAL_ID not in prevalence:raise RuntimeError("Missing original full channel prevalence")
    # Same astronomical chart predicate and parents -> the previous
    # predicate prevalence can be reused in the what-if. This does not make
    # an atomic behavioral prediction source-validated.
    prevalence[ATOMIC_ID]=prevalence[ORIGINAL_ID]
    start=perf_counter()
    atomic=optional_atom(original,original["confidence"])
    matching_indices=[]
    base_score=[]
    for idx,state in enumerate(states):
        baseline=scorer.score_one(state,existing,p,False)
        base_score.append(float(baseline["net"]))
        if scorer.match_predicate(state,atomic["predicate"]) and all(
            scorer.match_predicate(state,parent) for parent in atomic["parents"]
        ):
            matching_indices.append(idx)
    reference_base=base_score[ref_index]
    base_before=sum(s>reference_base+1e-9 for s in base_score)
    baseline_saved=previous["comparison_charts"][0]["development_net_rubric_bits"]
    if abs(reference_base-baseline_saved)>2e-5:
        raise RuntimeError("Old model baseline numerical score does not reproduce its receipt")
    variant_results=[]
    for confidence in CONFIDENCES:
        new_model=deepcopy(existing)
        atomic=optional_atom(original,confidence)
        atomic.pop("post_selection") # only while running this explicitly named WHAT-IF
        new_model["mappings"]=direct+[atomic]
        updated=list(base_score)
        for idx in matching_indices:
            score=scorer.score_one(states[idx],new_model,prevalence,False)
            if score["net"]<base_score[idx]-1e-9:
                raise RuntimeError("Adding a same-cluster alternative unexpectedly reduced the score")
            updated[idx]=float(score["net"])
        ref_score=updated[ref_index]
        better=sum(s>ref_score+1e-9 for s in updated)
        equal=sum(abs(s-ref_score)<=1e-9 for s in updated)
        max_other=max(s for i,s in enumerate(updated) if i!=ref_index)
        variant_results.append({
           "hypothetical_channel_confidence":confidence,
           "reference_rubric_bits":round(ref_score,7),
           "reference_increment_from_original":round(ref_score-reference_base,7),
           "strictly_higher_substantive_HDstates":better,
           "equal_score_structural_states_including_reference":equal,
           "reference_unique_top_by_NET_SCORE":better==0 and equal==1,
           "max_competitor_net":round(max_other,7),
           "interpretation":"UNVALIDATED_POSTEXPOSURE_HYPOTHETICAL_ATOMIZATION_NOT_A_NEW_HUMAN_PREDICTOR",
        })
    return {
       "schema":"atomic_26_44_persuasion_counterfactual_sensitivity_v1",
       "status":"RESEARCH_ONLY_POSTEXPOSURE_NOT_AN_ACCEPTED_SCORE",
       "source_priorHD_44_baseline_model_digest":previous["historic_mapping_source"],
       "prior_new_HD_score_sha256":BASELINE_SHA,
       "prior_44_pathway_prevalence_sha256":OLD_PREVALENCE_SHA,
       "owner_raw_clarification_digest":file_sha(args.raw),
       "private_adjudication_digest":file_sha(args.adjudication),
       "astronomical_source_universe_manifest_SHA256":prior["HD_cache_manifest_sha256"],
       "previous_recorded_chart_net_score":round(reference_base,7),
       "previous_number_strictly_better":base_before,
       "source_complete_channel_rule_held_out":ORIGINAL_ID,
       "previous_supported_partial_gate_rule":LOWER_TIER_ID,
       "same_evidence_dependency_cluster":"ENTERPRISE_PERSUASION_PATTERN",
       "what_if_channel_type":"narrow persuasive transmission clause, deliberately excludes unverified innate deception recognition, enterprise leverage and commercial motivation",
       "source_significance":"No new source or independent human validation supports the candidate atom; it was chosen after seeing the known answer.",
       "all_structural_states_scored":len(states),
       "states_matching_complete_26_44_channel_and_prerequisites":len(matching_indices),
       "results":variant_results,
       "calculation_seconds":round(perf_counter()-start,3),
       "validity_notice":"The apparent first-place position, if any, is a post-selection demonstration of score sensitivity, not birth-date inference or Western+HD comparison. Other model mappings, full historical frozen scores and profile input remain unchanged."
    }

def main():
    ap=argparse.ArgumentParser()
    for name in ("repo_root","hd_cache","prior","previous_ranking","prior_coding","raw","adjudication","output"):
        ap.add_argument("--"+name.replace("_","-"),required=True,type=Path)
    args=ap.parse_args()
    result=analyze(args)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    b=(json.dumps(result,sort_keys=True,indent=2)+"\n").encode()
    with args.output.open("xb") as out:out.write(b)
    print("SOURCE_ATOMIZATION_SENSITIVITY",json.dumps({
      "baseline":result["previous_recorded_chart_net_score"],
      "preexisting_higher":result["previous_number_strictly_better"],
      "states_with_complete_channel":result["states_matching_complete_26_44_channel_and_prerequisites"],
      "confidence_cases":[(x["hypothetical_channel_confidence"],x["reference_rubric_bits"],x["strictly_higher_substantive_HDstates"]) for x in result["results"]],
      "output_sha256":sha256(b).hexdigest(),
      "scientifically_validated":False},sort_keys=True))

if __name__=="__main__":main()
