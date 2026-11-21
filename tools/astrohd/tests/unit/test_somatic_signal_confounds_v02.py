"""Synthetic non-bespoke affect/cue classification tests. No private accounts."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("somatic",ROOT/"scripts/audit_somatic_signal_confounds_v02.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
RULES=m.load_rules(json.loads((ROOT/"reference/research/generic_somatic_decision_signal_disambiguation_v02.json").read_bytes()))

def case(**changes):
    obj={"episode_id":"synthetic_A",
         "context":"romantic_interaction",
         "signal_type":"sexual_or_romantic_drive",
         "signal_intensity":"powerful",
         "signal_duration":"repeated_or_sustained",
         "initial_reasoning_conflict":"red_flags_or_value_conflict",
         "action_type":"avoided_situation",
         "action_completed":True,
         "self_regulation":"anticipatory_situation_selection",
         "outcome_independently_checked":None,
         "generality":"single_case",
         "origin":"first_person_self_report"}
    obj.update(changes)
    return obj

class SomaticSignalTests(unittest.TestCase):
    def test_powerful_sexual_desire_is_not_splenic_source_match(self):
        out=m.analyze_case(case(),RULES)
        self.assertEqual(out["source_interpretation"],"VISCERAL_DRIVE_EXPLANATION_CANDIDATE")
        self.assertFalse(out["quiet_splenic_like_phenomenology_meets_minimal_signals"])
        self.assertTrue(out["self_regulation_effort_reported"])
        self.assertFalse(out["authority_reliability_established"])
        self.assertIsNone(out["natal_score_delta"])

    def test_strong_urge_and_successful_situation_selection_coexist(self):
        out=m.analyze_case(case(action_type="avoided_situation",
                                self_regulation="anticipatory_situation_selection"),RULES)
        self.assertTrue(out["self_regulation_effort_reported"])
        self.assertFalse(out["independently_verified_effectiveness"])

    def test_rapport_does_not_verify_third_party(self):
        out=m.analyze_case(case(context="nonromantic_trust",
                                signal_type="rapport_or_good_feeling",
                                signal_duration="unknown",
                                signal_intensity="unknown"),RULES)
        self.assertEqual(out["source_interpretation"],"AFFECTIVE_SOCIAL_IMPRESSION")
        self.assertFalse(out["independently_verified_effectiveness"])

    def test_quiet_source_like_cue_requires_both_observed_properties(self):
        out=m.analyze_case(case(context="neutral_decision",
                                signal_type="quiet_safety_instinct",
                                signal_intensity="quiet",
                                signal_duration="brief_once"),RULES)
        self.assertTrue(out["quiet_splenic_like_phenomenology_meets_minimal_signals"])
        self.assertFalse(out["authority_reliability_established"])
        self.assertIsNone(out["natal_score_delta"])

    def test_quiet_cue_with_unknown_duration_is_not_source_proof(self):
        out=m.analyze_case(case(context="neutral_decision",
                                signal_type="quiet_safety_instinct",
                                signal_intensity="quiet",
                                signal_duration="unknown"),RULES)
        self.assertFalse(out["quiet_splenic_like_phenomenology_meets_minimal_signals"])
        self.assertEqual(out["source_interpretation"],"INCOMPLETE_QUIET_SPLENIC_LIKE_CUE")

    def test_sudden_confidence_distinct_from_sexual_arousal(self):
        out=m.analyze_case(case(context="neutral_decision",signal_type="answer_certainty",
                                signal_intensity="unknown",signal_duration="unknown",
                                action_type="acted_toward"),RULES)
        self.assertEqual(out["source_interpretation"],"COGNITIVE_OR_INTUITIVE_CERTAINTY_UNRESOLVED")

    def test_invalid_or_unverified_outcome_rejected(self):
        with self.assertRaisesRegex(ValueError,"Cannot verify outcome"):
            m.analyze_case(case(action_completed=False,outcome_independently_checked=True),RULES)
        with self.assertRaisesRegex(ValueError,"Unexpected signal_type"):
            m.analyze_case(case(signal_type="splenic_guaranteed"),RULES)
        with self.assertRaisesRegex(ValueError,"boolean or unknown"):
            m.analyze_case(case(action_completed="yes"),RULES)

    def test_duplicate_episode_not_counted_twice(self):
        cases={"schema":m.SOURCE_SCHEMA,"cases":[case(),case()]}
        with self.assertRaisesRegex(ValueError,"Duplicate cases"):
            m.audit_all(RULES,cases)

    def test_no_all_example_to_general_profile_promotion(self):
        cases={"schema":m.SOURCE_SCHEMA,"cases":[case(),case(
            episode_id="synthetic_B",signal_type="answer_certainty",context="neutral_decision",
            signal_intensity="unknown",signal_duration="unknown",action_type="acted_toward",
            generality="self_reported_general_pattern")]}
        result=m.audit_all(RULES,cases)
        self.assertEqual(result["n_selected_cases"],2)
        self.assertTrue(result["not_representative_frequency"])
        self.assertTrue(result["no_reason_to_rerank_century"])
        self.assertTrue(result["no_source_based_hd_authority_decision_predictive_score"])

    def test_no_chart_aware_fit_method_and_no_private_labels(self):
        source=(ROOT/"scripts/audit_somatic_signal_confounds_v02.py").read_text().lower()
        proto=(ROOT/"reference/research/generic_somatic_decision_signal_disambiguation_v02.json").read_text().lower()
        for token in ("birth_time","actual_chart_id","raw_private_transcript","named_third_party_identity"):
            self.assertNotIn(token,source+"\n"+proto)

if __name__=="__main__":unittest.main()
