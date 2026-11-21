#!/usr/bin/env python3
"""Scope audit: exact OLD HD ranking is not safe pruning for a NEW Western+HD model.

Inputs: a private, SHA-pinned owner HD ranking and a source-specified search
contract. No personal DOB, autobiographical text or chart dates enter repo.
A 'safe' outcome is always RELATIVE TO THE FROZEN SCORE AND SEARCH UNIVERSE,
not empirical proof that a chart predicts a human.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

ORIGINAL_HD_SHA = "b930e87a366a7d06d0efe40c9ec83044be62116935ec1a986b06c3868fcf9bce"
ORIGINAL_MODEL_STATUS = "EXPLORATORY_V37_CORRECTED_OBSERVABLES_REUSE_OF_V36_HD_PATHWAYS"
ORIGINAL_HD_STATE_COUNT = 288908
OLD_HD_FACET_COUNT = 23
OLD_REF_SCORE = 9.4704565
OLD_STRICTLY_GREATER = 14
KNOWN_WESTERN_GRID_SAMPLE_COUNT = 3506400
EXPLICIT_NEW_EPOCH = "V3.7+interview-dev-20261120-003"

def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

def verify_old_source(rank: dict[str, Any], source_hash: str) -> dict[str, Any]:
    if source_hash != ORIGINAL_HD_SHA:
        raise RuntimeError("Original HD ranking no longer byte-identical")
    if rank.get("status") != ORIGINAL_MODEL_STATUS:
        raise RuntimeError("Unexpected score epoch")
    if rank.get("count_V37_directly_reported_whole_observables") != OLD_HD_FACET_COUNT:
        raise RuntimeError("Wrong historical 23-pathway instrument")
    full = rank["full_century_provisional_HD_only_ranking"]
    if full["structural_interval_count"] != ORIGINAL_HD_STATE_COUNT:
        raise RuntimeError("Historical HD exact-state coverage changed")
    if not full.get("no_western_ranking") or not full.get("no_independent_human_validation"):
        raise RuntimeError("Missing important old limitation")
    reference = full["reference_and_alternative_interval_ranks"][0]
    if (reference["unmerged_structural_order"] != 16 or
            reference["strictly_better_substantive_score_states"] != OLD_STRICTLY_GREATER):
        raise RuntimeError("Original reference rank drift")
    if abs(rank["comparison_charts"][0]["development_net_rubric_bits"] - OLD_REF_SCORE) > 1e-7:
        raise RuntimeError("Original reference score drift")
    return {
        "old_hd_structural_states_scored_all": ORIGINAL_HD_STATE_COUNT,
        "old_hd_23_pathway_strictly_higher_states": OLD_STRICTLY_GREATER,
        "old_hd_only_model_complete_on_its_stated_exact_structural_states": True,
        "historical_binary_source_verified": True,
    }

def determine_scope(old: dict[str, Any], *, candidate_rule: str,
                    final_hd_frozen: bool, final_western_frozen: bool,
                    final_score_upper_bounds_certified: bool,
                    continuous_western_coverage_proven: bool,
                    historical_model_same_as_final: bool) -> dict[str, Any]:
    if not old.get("historical_binary_source_verified"):
        raise ValueError("Cannot claim old HD coverage without verified receipt")
    if candidate_rule not in ("OLD_HD_SCORE_STRICT_GT", "FULL_NEW_HD_AND_WESTERN"):
        raise ValueError("Unknown selection rule")
    # For a conjunction that explicitly requires the OLD exact HD score
    # strictly greater than the actual's OLD score, ONLY the historical 14
    # pass. This is a tautological property of that frozen score, not a
    # human-profile fact or a guarantee about another score version.
    fixed_old_hd_filter_complete = candidate_rule == "OLD_HD_SCORE_STRICT_GT"
    # Caller booleans can only report prerequisites, NEVER attest a proof.
    # To establish global safe pruning in a later version, a separate
    # verified per-interval upper-bound certificate reader must check source
    # model hash, coverage, every omitted interval and mathematical validity.
    # This v1 audit contains NO such proof verifier and thus fails CLOSED.
    claimed_all_preconditions = (
        final_hd_frozen and final_western_frozen and
        final_score_upper_bounds_certified and continuous_western_coverage_proven and
        historical_model_same_as_final
    )
    globally_safe_pruning_claim = False
    return {
        "question":"Could any chart fit the survey better in BOTH current Western and HD interpretations?",
        "old_hd_score_filter_complete_for_its_own_frozen_rule":fixed_old_hd_filter_complete,
        "old_hd_14_state_shortlist_valid_for_the_same_strict_old_hd_rule":
            bool(historical_model_same_as_final and fixed_old_hd_filter_complete),
        "old_hd_14_state_shortlist_proven_complete_for_new_holistic_model":False,
        "certified_full_western_hd_no_missed_higher_score":globally_safe_pruning_claim,
        "safe_to_stop_full_century_chart_search":globally_safe_pruning_claim,
        "claimed_prerequisites_are_not_proof":claimed_all_preconditions,
        "admissible_final_upper_bound_verifier":"NOT_IMPLEMENTED",
        "current_outcome":"NOT_DECIDED_FOR_COMPLETE_WESTERN_HD",
        "western_15min_sample_count":KNOWN_WESTERN_GRID_SAMPLE_COUNT,
        "western_samples_guarantee_between_timestamps":False,
        "no_independent_human_personality_validation":True,
        "development_semantic_epoch":EXPLICIT_NEW_EPOCH,
        "scope_limitations":[
            "The HD scorer exhaustively ranked its 288908 exact structural states; it did not prune these.",
            "One old HD-only score cannot bound a new model with different source-eligible behaviors.",
            "The 3506400 Western grid timestamps are not complete continuous time.",
            "No final joint behavioral scorer or admissible upper-bound certificates existed.",
            "No astrology/HD personality accuracy is demonstrated by mathematical search completeness.",
        ],
    }

def run(rank_path: Path) -> dict[str, Any]:
    old = verify_old_source(json.loads(rank_path.read_bytes()), digest(rank_path))
    return {"verified_old_result":old, "current_scope":determine_scope(
        old, candidate_rule="FULL_NEW_HD_AND_WESTERN",
        final_hd_frozen=False, final_western_frozen=False,
        final_score_upper_bounds_certified=False,
        continuous_western_coverage_proven=False,
        historical_model_same_as_final=False,
    )}

def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--rank",type=Path,required=True)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result=run(args.rank)
    data=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.output:
        if args.output.exists():raise FileExistsError("Do not overwrite receipts")
        args.output.write_text(data)
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
