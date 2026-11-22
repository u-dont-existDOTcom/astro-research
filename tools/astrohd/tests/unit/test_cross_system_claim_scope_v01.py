"""Synthetic regression for source-neutral Gemini comparison critique.

These tests check metadata handling, never whether astrology predicts a person.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SP=importlib.util.spec_from_file_location("scope",ROOT/"scripts/audit_cross_system_claim_scope_v01.py")
scope=importlib.util.module_from_spec(SP)
SP.loader.exec_module(scope)


def base():
    return {
        "schema":"astrohd_cross_system_claim_scope_v01",
        "claim":"conditional_best_rank",
        "universe_coverage":"finite_sample_grid",
        "model_frozen_before_target_exposure":False,
        "source_rule_conditions_compiled":False,
        "actual_scoring_executed":False,
        "candidate_representations":[
            {"representation":"exact_instant","western_method":"same_instant"},
            {"representation":"hd_stable_interval","western_method":"posthoc_best_midpoint"}
        ]
    }


class ScopeAuditTests(unittest.TestCase):
    def test_selecting_best_house_midpoint_detected(self):
        result=scope.audit(base())
        self.assertIn("selective_best_Western_in_HD_interval",result["issues"])

    def test_claim_of_global_continuous_rank_from_sparse_grid_rejected(self):
        c=base()
        c["claim"]="continuous_universe_best_rank"
        self.assertIn("finite_samples_not_continuous_universe",scope.audit(c)["issues"])

    def test_old_hd_shortlist_cannot_support_full_new_comparison(self):
        c=base()
        c["universe_coverage"]="old_hd_selected_panel"
        self.assertIn("uncertified_candidate_universe",scope.audit(c)["issues"])

    def test_postexposure_rank_cannot_be_called_frozen_independent(self):
        self.assertIn("rank_is_post_exposure_development_only",scope.audit(base())["issues"])

    def test_precise_rival_sampling_allowed_for_bounded_model(self):
        c=base()
        c["model_frozen_before_target_exposure"]=True
        c["source_rule_conditions_compiled"]=True
        c["actual_scoring_executed"]=True
        c["candidate_representations"][1]["western_method"]="fixed_systematic_lattice"
        r=scope.audit(c)
        self.assertFalse(r["issues"])
        self.assertTrue(r["cannot_certify_source_or_human_accuracy"])

    def test_prenatal_difference_not_imputed_as_independent_predictive_evidence(self):
        c=base()
        c["claim"]="structural_information_gain"
        c["feature_redundancy_estimated_on_declared_time_population"]=False
        c["denominator_time_weighted_or_explicitly_qualified"]=False
        r=scope.audit(c)
        self.assertIn("no_measured_joint_feature_redundancy",r["issues"])
        self.assertIn("no_temporal_denominator",r["issues"])

    def test_no_untouched_validation_cannot_claim_human_accuracy(self):
        c=base()
        c["claim"]="empirical_predictive_advantage"
        c["prospective_untouched_human_cohort"]=False
        c["chart_free_comparator"]=False
        c["independent_verification_of_results"]=False
        r=scope.audit(c)
        self.assertIn("no_untouched_human_cohort",r["issues"])
        self.assertIn("no_chart_free_baseline",r["issues"])

    def test_malformed_scope_rejected(self):
        c=base()
        c["candidate_representations"][0]["representation"]="a narrative date bucket"
        with self.assertRaisesRegex(ValueError,"candidate"):
            scope.audit(c)

if __name__=="__main__":
    unittest.main()
