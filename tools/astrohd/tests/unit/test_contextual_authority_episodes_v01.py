"""Synthetic episodes, no owner details: source-compatible ≠ actual natal Authority."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("auth_context",ROOT/"scripts/audit_contextual_authority_episodes_v01.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
CONTRACT=mod.load_contract(json.loads((ROOT/"reference/research/contextual_behavior_and_authority_observation_contract_v01.json").read_bytes()))
def event(**updates):
    return {"episode_id":"CASE_A","context":"relationship",
            "decision_or_impression":"person_impression",
            "decision_completed":False,"evidence_type":"verbatim_first_person",
            "generality_assessment":"single_illustration",
            "context_qualifier":"toy unrelated interpersonal encounter",**updates}

class ContextualAuthorityTests(unittest.TestCase):
    def test_person_impression_even_immediate_bodily_feeling_not_strict_decision(self):
        r=mod.triage(event(instant_body_signal=True),CONTRACT)
        self.assertFalse(any(r["source_compatibility_conditions_met"].values()))
        self.assertIn("INSTANTANEOUS_BODILY_AWARENESS_REPORTED",r["partial_or_competing_explanations"])
        self.assertIn("SOCIAL_PERSON_IMPRESSION_NOT_DIRECT_EVIDENCE_OF_DECISION_AUTHORITY",r["partial_or_competing_explanations"])

    def test_someone_else_voice_does_not_count_self_projected(self):
        r=mod.triage(event(instant_body_signal=True,
                          own_spoken_words_heard=False,
                          trusted_listener_present=True),CONTRACT)
        self.assertFalse(r["source_compatibility_conditions_met"]["HD_SELF_PROJECTED"])

    def test_months_of_reasoning_without_emotional_wave_is_not_emotional_authority(self):
        r=mod.triage(event(context="long_horizon_planning",
                          decision_or_impression="important_decision",
                          prolonged_reasoning=True,information_missing=True),CONTRACT)
        self.assertFalse(r["source_compatibility_conditions_met"]["HD_EMOTIONAL"])
        self.assertIn("INFORMATION_LIMITATION_REPORTED",r["partial_or_competing_explanations"])

    def test_cognitive_insight_does_not_imply_instant_body_source(self):
        r=mod.triage(event(decision_or_impression="insight_or_answer",
                          prolonged_reasoning=True,instant_body_signal=None),CONTRACT)
        self.assertFalse(r["source_compatibility_conditions_met"]["HD_SPLENIC"])
        self.assertIn("SUDDEN_INSIGHT_NOT_SPECIFIC_TO_ANY_HD_AUTHORITY",r["partial_or_competing_explanations"])

    def test_full_splenic_source_conditions_are_classified_not_scored(self):
        r=mod.triage(event(decision_or_impression="important_decision",
                          decision_completed=True,instant_body_signal=True,
                          brief_nonrepeating_signal=True,signal_decided_choice=True,
                          result_independently_observable=None),CONTRACT)
        self.assertTrue(r["source_compatibility_conditions_met"]["HD_SPLENIC"])
        self.assertFalse(r["source_specific_authority_not_established_by_one_episode"] is False)
        self.assertIsNone(r["natal_score_delta"])
        self.assertFalse(r["outcome_validated"])

    def test_self_projected_requires_own_speaking_and_actual_choice(self):
        r=mod.triage(event(decision_or_impression="important_decision",
                          decision_completed=True,own_spoken_words_heard=True,
                          trusted_listener_present=True,own_speech_decided_choice=True),CONTRACT)
        self.assertTrue(r["source_compatibility_conditions_met"]["HD_SELF_PROJECTED"])
        self.assertFalse(r["source_compatibility_conditions_met"]["HD_SPLENIC"])

    def test_emotional_requires_wave_not_just_delay(self):
        r=mod.triage(event(decision_or_impression="important_decision",
                          decision_completed=True,emotional_wave_over_time=True,
                          wave_settled_choice=True),CONTRACT)
        self.assertTrue(r["source_compatibility_conditions_met"]["HD_EMOTIONAL"])

    def test_multiple_processes_can_cooccur(self):
        r=mod.triage(event(decision_or_impression="important_decision",
                          decision_completed=True,instant_body_signal=True,
                          brief_nonrepeating_signal=True,signal_decided_choice=True,
                          emotional_wave_over_time=True,wave_settled_choice=True),CONTRACT)
        self.assertTrue(r["source_compatibility_conditions_met"]["HD_SPLENIC"])
        self.assertTrue(r["source_compatibility_conditions_met"]["HD_EMOTIONAL"])
        self.assertIsNone(r["natal_score_delta"])

    def test_unsafe_causal_conclusions_rejected(self):
        with self.assertRaises(ValueError):
            mod.triage(event(signal_decided_choice=True),CONTRACT)
        with self.assertRaises(ValueError):
            mod.triage(event(result_independently_observable=True),CONTRACT)

    def test_null_unknown_and_string_bool_handling(self):
        r=mod.triage(event(brief_nonrepeating_signal=None),CONTRACT)
        self.assertFalse(any(r["source_compatibility_conditions_met"].values()))
        with self.assertRaises(ValueError):
            mod.triage(event(brief_nonrepeating_signal="yes"),CONTRACT)

    def test_audit_never_proves_global_authority(self):
        a=event(instant_body_signal=True)
        b=event(episode_id="CASE_B",context="professional_screening",
                decision_or_impression="important_decision",decision_completed=False,
                prolonged_reasoning=True)
        summary=mod.audit_episodes({"schema":"private_or_synthetic_contextual_authority_episodes_v01",
             "episodes":[a,b]},CONTRACT)
        self.assertEqual(summary["total_episodes"],2)
        self.assertEqual(summary["episodes_reporting_immediate_bodily_awareness"],1)
        self.assertEqual(summary["episodes_reporting_prolonged_analysis"],1)
        self.assertFalse(summary["any_reliable_long_run_authority_claim_proven"])
        self.assertEqual(sum(summary["strict_authority_eligible_episode_counts"].values()),0)

    def test_duplicate_episode_rejected_not_independent_evidence(self):
        with self.assertRaises(ValueError):
            mod.audit_episodes({"schema":"private_or_synthetic_contextual_authority_episodes_v01",
                               "episodes":[event(),event()]},CONTRACT)

    def test_source_contract_has_official_authorities_and_non_hd_baseline(self):
        src=(ROOT/"reference/research/contextual_behavior_and_authority_observation_contract_v01.json").read_text()
        self.assertIn("10.1111/j.1751-9004.2009.00170.x",src)
        self.assertIn("self-projected-authority",src)
        self.assertIn("emotional-authority",src)
        self.assertIn("no_natal_score_from_source_familiarity",src)
        self.assertNotIn("self_referential_birth_time",src)

if __name__=="__main__":unittest.main()
