#!/usr/bin/env python3
"""Audit *asserted evidence scope* in cross-system natal comparison reports.

The audit is source-neutral and metadata-only. It never certifies that scores,
charts, sources, prospective outcomes, or independence calculations actually
exist. It flags a conclusion that exceeds its declared reproducible inputs.
This is an optional reporting aid, NOT a production chart scorer or new gate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

LABELS = {
    "symbolic_fit",
    "conditional_best_rank",
    "continuous_universe_best_rank",
    "structural_information_gain",
    "empirical_predictive_advantage",
}
REPR = {"exact_instant", "hd_stable_interval", "sampled_instant"}
WESTERN_METHODS = {
    "same_instant",
    "fixed_systematic_lattice",
    "posthoc_best_midpoint",
    "none",
}
COVERAGE = {"complete_continuous", "finite_sample_grid", "old_hd_selected_panel", "unknown"}


def audit(report: dict) -> dict:
    if report.get("schema") != "astrohd_cross_system_claim_scope_v01":
        raise ValueError("Unknown comparison report schema")
    goal = report.get("claim")
    if goal not in LABELS:
        raise ValueError("Unrecognized claim type")
    coverage = report.get("universe_coverage")
    if coverage not in COVERAGE:
        raise ValueError("Must declare universe coverage")
    candidates = report.get("candidate_representations")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Need explicit candidate representation list")
    if not isinstance(report.get("model_frozen_before_target_exposure"), bool):
        raise ValueError("Target exposure must be stated")
    issues = []
    for c in candidates:
        if c.get("representation") not in REPR:
            raise ValueError("Unknown candidate representation")
        if c.get("western_method") not in WESTERN_METHODS:
            raise ValueError("Unknown Western computation method")
        if c["representation"] == "hd_stable_interval":
            if c["western_method"] == "posthoc_best_midpoint":
                issues.append("selective_best_Western_in_HD_interval")
            elif c["western_method"] == "none" and goal in (
                "conditional_best_rank", "continuous_universe_best_rank"
            ):
                issues.append("HD_interval_no_Western_coverage")
        if c["representation"] == "exact_instant" and c["western_method"] == "none" and goal in (
            "conditional_best_rank", "continuous_universe_best_rank"
        ):
            issues.append("exact_instant_no_Western_evaluation")
    if goal in {"conditional_best_rank", "continuous_universe_best_rank"}:
        if not report.get("source_rule_conditions_compiled"):
            issues.append("missing_source_governor_or_full_conditions")
        if coverage in {"old_hd_selected_panel", "unknown"}:
            issues.append("uncertified_candidate_universe")
        if coverage == "finite_sample_grid" and goal == "continuous_universe_best_rank":
            issues.append("finite_samples_not_continuous_universe")
        if not report.get("actual_scoring_executed"):
            issues.append("no_actual_rank_reproduction")
    if goal == "structural_information_gain":
        if not report.get("feature_redundancy_estimated_on_declared_time_population"):
            issues.append("no_measured_joint_feature_redundancy")
        if not report.get("denominator_time_weighted_or_explicitly_qualified"):
            issues.append("no_temporal_denominator")
    if goal == "empirical_predictive_advantage":
        if not report.get("prospective_untouched_human_cohort"):
            issues.append("no_untouched_human_cohort")
        if not report.get("chart_free_comparator"):
            issues.append("no_chart_free_baseline")
        if not report.get("independent_verification_of_results"):
            issues.append("no_independent_evaluation")
        if not report["model_frozen_before_target_exposure"]:
            issues.append("development_target_exposed_before_freeze")
    # An after-exposure version can be useful, but it is never an independent
    # human validation just by being retrospectively frozen.
    if goal in {"conditional_best_rank", "continuous_universe_best_rank"}:
        if not report["model_frozen_before_target_exposure"]:
            issues.append("rank_is_post_exposure_development_only")
    return {
        "status": "METADATA_SCOPE_AUDIT_NOT_A_REPRODUCTION",
        "claim": goal,
        "issues": sorted(set(issues)),
        "metadata_contains_no_self_reported_scope_contradictions": not issues,
        "cannot_certify_source_or_human_accuracy": True,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(audit(json.loads(args.input.read_text())), sort_keys=True))


if __name__ == "__main__":
    main()
