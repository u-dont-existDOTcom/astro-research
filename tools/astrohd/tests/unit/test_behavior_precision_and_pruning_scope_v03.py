"""Synthetic-only regression for richer semantic questions and pruning scope.

Never use the known owner's actual birth time or survey case as a fixture.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"scripts/audit_dual_system_pruning_scope_v1.py"
sp=importlib.util.spec_from_file_location("prune_contract_v1",SCRIPT)
m=importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)
BANK=json.loads((ROOT/"reference/research/behavioral_interview_precision_v03.json").read_bytes())

def synthetic_old():
    return {"status":m.ORIGINAL_MODEL_STATUS,
            "count_V37_directly_reported_whole_observables":23,
            "comparison_charts":[{"development_net_rubric_bits":9.4704565}],
            "full_century_provisional_HD_only_ranking":{
                "structural_interval_count":288908,
                "no_western_ranking":True,
                "no_independent_human_validation":True,
                "reference_and_alternative_interval_ranks":[{
                    "unmerged_structural_order":16,
                    "strictly_better_substantive_score_states":14,
                }],
            }}

class PrecisionAndPruningTests(unittest.TestCase):
    def test_old_exact_hd_exhaustion_is_verified_separately(self):
        result=m.verify_old_source(synthetic_old(),m.ORIGINAL_HD_SHA)
        self.assertTrue(result["old_hd_only_model_complete_on_its_stated_exact_structural_states"])
        self.assertEqual(result["old_hd_23_pathway_strictly_higher_states"],14)

    def test_no_false_claim_historical_source_hash(self):
        with self.assertRaisesRegex(RuntimeError,"byte-identical"):
            m.verify_old_source(synthetic_old(),"1"*64)

    def test_no_false_claim_if_western_rank_injected_into_old_report(self):
        case=synthetic_old()
        case["full_century_provisional_HD_only_ranking"]["no_western_ranking"]=False
        with self.assertRaisesRegex(RuntimeError,"limitation"):
            m.verify_old_source(case,m.ORIGINAL_HD_SHA)

    def test_old_filter_complete_only_for_identical_fixed_old_hd_metric(self):
        old=m.verify_old_source(synthetic_old(),m.ORIGINAL_HD_SHA)
        result=m.determine_scope(old,candidate_rule="OLD_HD_SCORE_STRICT_GT",
                                 final_hd_frozen=False,final_western_frozen=False,
                                 final_score_upper_bounds_certified=False,
                                 continuous_western_coverage_proven=False,
                                 historical_model_same_as_final=True)
        self.assertTrue(result["old_hd_score_filter_complete_for_its_own_frozen_rule"])
        self.assertTrue(result["old_hd_14_state_shortlist_valid_for_the_same_strict_old_hd_rule"])
        self.assertFalse(result["safe_to_stop_full_century_chart_search"])

    def test_old_hd_shortlist_cannot_prune_new_chart_to_behavior_model(self):
        old=m.verify_old_source(synthetic_old(),m.ORIGINAL_HD_SHA)
        result=m.determine_scope(old,candidate_rule="FULL_NEW_HD_AND_WESTERN",
                                 final_hd_frozen=False,final_western_frozen=False,
                                 final_score_upper_bounds_certified=False,
                                 continuous_western_coverage_proven=False,
                                 historical_model_same_as_final=False)
        self.assertFalse(result["old_hd_14_state_shortlist_valid_for_the_same_strict_old_hd_rule"])
        self.assertFalse(result["certified_full_western_hd_no_missed_higher_score"])
        self.assertEqual(result["current_outcome"],"NOT_DECIDED_FOR_COMPLETE_WESTERN_HD")
        self.assertFalse(result["western_samples_guarantee_between_timestamps"])

    def test_missing_any_final_model_proof_prevents_pruning(self):
        old=m.verify_old_source(synthetic_old(),m.ORIGINAL_HD_SHA)
        vals={
            "final_hd_frozen":True,"final_western_frozen":True,
            "final_score_upper_bounds_certified":True,
            "continuous_western_coverage_proven":True,
            "historical_model_same_as_final":True,
        }
        for field in vals:
            changed={**vals,field:False}
            out=m.determine_scope(old,candidate_rule="FULL_NEW_HD_AND_WESTERN",**changed)
            self.assertFalse(out["safe_to_stop_full_century_chart_search"],field)

    def test_even_all_unverified_proof_flags_cannot_claim_safe_pruning(self):
        old=m.verify_old_source(synthetic_old(),m.ORIGINAL_HD_SHA)
        result=m.determine_scope(
            old,candidate_rule="FULL_NEW_HD_AND_WESTERN",
            final_hd_frozen=True,final_western_frozen=True,
            final_score_upper_bounds_certified=True,
            continuous_western_coverage_proven=True,
            historical_model_same_as_final=True)
        self.assertTrue(result["claimed_prerequisites_are_not_proof"])
        self.assertFalse(result["certified_full_western_hd_no_missed_higher_score"])
        self.assertEqual(result["admissible_final_upper_bound_verifier"],"NOT_IMPLEMENTED")

    def test_counterexample_old_low_but_new_better_both(self):
        # Invented, purely arithmetic example that disproves pruning by an old
        # score when the currently admissible *model version* changes.
        old_actual,old_alt=9.47,9.45
        new_hd_actual,new_hd_alt=7.0,9.0
        new_west_actual,new_west_alt=4.0,7.0
        self.assertLess(old_alt,old_actual)
        self.assertGreater(new_hd_alt,new_hd_actual)
        self.assertGreater(new_west_alt,new_west_actual)

    def test_precision_bank_version_no_implicit_score(self):
        self.assertEqual(BANK["status"],"SOURCE_AWARE_POST_EXPOSURE_DEVELOPMENT_ONLY_NO_SCORED_RESPONSES")
        self.assertTrue(BANK["replaces_no_previous_answers"])
        self.assertTrue(all(q["scoring_policy"]=="NO_AUTO_SCORE" for q in BANK["questions"]))
        self.assertEqual(len(BANK["questions"]),7)

    def test_separate_detecting_patterns_and_inferring_lying(self):
        d={x["id"]:x for x in BANK["dimensions"]}
        self.assertIn("PATTERN_NOTICE",d)
        self.assertIn("GOOD_FAITH_PRIOR",d)
        self.assertIn("DELIBERATE_DISHONESTY_INFERENCE",d)
        self.assertIn("SELF_DECEPTION_INFERENCE",d)
        self.assertIn("PATTERN_CALIBRATION",d)
        self.assertNotEqual(d["GOOD_FAITH_PRIOR"]["meaning"],d["PATTERN_NOTICE"]["meaning"])

    def test_distinguish_principledness_from_practical_adaptation(self):
        ids={x["id"] for x in BANK["dimensions"]}
        self.assertTrue({"CONVICTION_STRENGTH","EVIDENCE_RESPONSIVENESS",
                         "PRACTICAL_FLEXIBILITY","PEER_PERCEPTION"}<=ids)
        self.assertTrue({"WORLD_FACING_SCOPE","SPIRITUAL_SCOPE","STATUS_AND_REWARD_MOTIVE",
                         "EFFORT_AND_TRADEOFFS","SELF_EVALUATION_REFERENCE"}<=ids)

    def test_questions_allow_counterexamples_mixed_and_unknown(self):
        all_controls=" ".join(c for q in BANK["questions"] for c in q["controls"]).lower()
        text=" ".join(q["respondent_prompt"] for q in BANK["questions"]).lower()
        self.assertIn("innocently",text)
        self.assertIn("later information",text)
        self.assertIn("actually do",text)
        self.assertIn("no example",all_controls)
        self.assertIn("do not assume",all_controls)

    def test_no_private_third_party_identity_or_specific_event_committed(self):
        source=(ROOT/"reference/research/behavioral_interview_precision_v03.json").read_text().lower()
        for unapproved_field in ('"verbatim_user_excerpts"', '"full_name"', '"birth_time_exact"', '"third_party_identity"'):
            self.assertNotIn(unapproved_field,source)
        self.assertNotIn("facebook.com/",source)

if __name__=="__main__":
    unittest.main()
