"""Generic personality hypothesis confirmation tests; no user biography."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("pconfirm",ROOT/"scripts/audit_pattern_confirmation_gate_v1.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
PROTO=json.loads((ROOT/"reference/research/behavioral_pattern_confirmation_protocol_v01.json").read_bytes())

def pattern(**edits):
    base={"hypothesis":"Usually notices a mismatch between words and behavior, then seeks corroboration before raising it.",
          "scope_conditions":"Across varied ordinary conversations, not just one extreme anecdote",
          "counterexample_status":"Observed missed cases and uncertainty documented",
          "source_episode_ids":["episode_A","episode_B"],
          "confirmation_status":"proposed_unconfirmed",
          "participant_response_private_source_id":None}
    return {**base,**edits}

class PatternGateTests(unittest.TestCase):
    def test_protocol_stages_and_scoring_block(self):
        r=m.validate_protocol(PROTO)
        self.assertEqual(r["stages"],6)
        self.assertTrue(r["no_unconfirmed_pattern_scoring"])

    def test_proposed_from_examples_never_counts_as_confirmed(self):
        r=m.triage_pattern(pattern())
        self.assertFalse(r["eligible_for_source_review"])
        self.assertFalse(r["eligible_for_automatic_natal_scoring"])

    def test_claimed_confirmed_without_actual_user_response_abstains(self):
        r=m.triage_pattern(pattern(confirmation_status="generally_correct_with_scope"))
        self.assertFalse(r["eligible_for_source_review"])

    def test_actual_user_confirmation_only_proceeds_to_source_review(self):
        r=m.triage_pattern(pattern(
            confirmation_status="generally_correct_with_scope",
            participant_response_private_source_id="owner_private_response_123"))
        self.assertTrue(r["eligible_for_source_review"])
        self.assertFalse(r["eligible_for_automatic_natal_scoring"])
        self.assertIn("not_predictive_validation",r["profile_inference_certainty"])

    def test_partial_correction_requires_revised_hypothesis(self):
        r=m.triage_pattern(pattern(
            confirmation_status="partly_correct_needs_revision",
            participant_response_private_source_id="owner_private_response_123"))
        self.assertFalse(r["eligible_for_source_review"])

    def test_unknown_or_rejected_abstains(self):
        for status in ("cannot_assess","mostly_incorrect","proposed_unconfirmed"):
            r=m.triage_pattern(pattern(
                confirmation_status=status,participant_response_private_source_id="owner_private_response_123"))
            self.assertFalse(r["eligible_for_source_review"])

    def test_no_exceptions_review_rejected(self):
        with self.assertRaises(ValueError):
            m.triage_pattern(pattern(counterexample_status=None))

    def test_no_unscoped_trait(self):
        with self.assertRaises(ValueError):
            m.triage_pattern(pattern(scope_conditions=""))

    def test_unknown_status_rejected(self):
        with self.assertRaises(ValueError):
            m.triage_pattern(pattern(confirmation_status="automatically_assume_positive"))

    def test_private_identifiers_not_baked_into_protocol(self):
        s=(ROOT/"reference/research/behavioral_pattern_confirmation_protocol_v01.json").read_text()
        self.assertNotIn("PRIVATE birth UTC",s)
        self.assertIn("confirmation of a personality self-description",s.lower())

if __name__=="__main__":unittest.main()
