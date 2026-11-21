"""Synthetic regression tests for source-anchored post-interview triage.

No participant's actual words, DOB, private questions or chart classifications.
"""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/"scripts/audit_interview_response_provenance_v1.py"
s=importlib.util.spec_from_file_location("interview_provenance",P)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def fixture():
    qid="Q-HDB2"
    text="I use both methods and switch between them when projects change."
    raw={"schema":m.RAW_SCHEMA,"responses":{qid:text}}
    model={"schema":m.QUESTION_SCHEMA,"questions":[{
        "id":qid,"source_ids":["CHANNEL_ALPHA","CHANNEL_BETA"]}]}
    annotation={"schema":m.ADJ_SCHEMA,"previous_frozen_rank_sha256":m.PREVIOUS_RANK_SHA,
        "target_profile_version":"V3.7+interview-dev-20261120-001",
        "prior_target_profile_sha256":m.PROFILE_V37_SHA,
        "new_scoring_mapping_status":m.NO_NEW_MODEL,
        "decisions":{qid:{
            "evidence_status":"both_mechanisms_contextual",
            "score_delta_policy":m.NO_SCORE,
            "numerical_score_delta":0,
            "exact_user_excerpt_anchors":["I use both methods"],
            "observed_propositions":["Both mechanisms reported contextually"],
            "not_established":["Which mechanism dominates over the full life span"],
            "scoring_mapping_ids":["CHANNEL_ALPHA","CHANNEL_BETA"],
        }}}
    return raw,annotation,model

class InterviewProvenanceTests(unittest.TestCase):
    def test_contextual_both_kept_zero_delta(self):
        raw,annotation,bank=fixture()
        result=m.triage(raw,annotation,bank)
        self.assertFalse(result["score_change_authorized"])
        self.assertTrue(result["all_old_HD_rankings_and_maps_unchanged"])
        self.assertEqual(result["responses_reviewed"],1)
        self.assertEqual(result["items"][0]["score_delta"],0)

    def test_invented_quotation_rejected(self):
        raw,annotation,bank=fixture()
        annotation["decisions"]["Q-HDB2"]["exact_user_excerpt_anchors"]=["I am always creative"]
        with self.assertRaisesRegex(ValueError,"quotation"):
            m.triage(raw,annotation,bank)

    def test_silent_score_gain_is_forbidden(self):
        raw,annotation,bank=fixture()
        annotation["decisions"]["Q-HDB2"]["score_delta_policy"]="PLUS_ONE_FOR_PREFERRED_CHART"
        with self.assertRaisesRegex(RuntimeError,"unauthorized"):
            m.triage(raw,annotation,bank)

    def test_nonzero_numeric_score_delta_rejected(self):
        raw,annotation,bank=fixture()
        annotation["decisions"]["Q-HDB2"]["numerical_score_delta"]=.5
        with self.assertRaisesRegex(RuntimeError,"points"):
            m.triage(raw,annotation,bank)

    def test_non_preregistered_mapping_rejected(self):
        raw,annotation,bank=fixture()
        annotation["decisions"]["Q-HDB2"]["scoring_mapping_ids"].append("NEW_SOURCE_MADE_UP")
        with self.assertRaisesRegex(ValueError,"Unapproved"):
            m.triage(raw,annotation,bank)

    def test_no_auto_frozen_model_epoch(self):
        raw,annotation,bank=fixture()
        annotation["new_scoring_mapping_status"]="CONFIRMATORY_PROVEN"
        with self.assertRaisesRegex(RuntimeError,"cannot be declared frozen"):
            m.triage(raw,annotation,bank)

    def test_profile_or_response_scope_mutation_rejected(self):
        raw,annotation,bank=fixture()
        annotation["prior_target_profile_sha256"]="0"*64
        with self.assertRaisesRegex(RuntimeError,"V3.7"):
            m.triage(raw,annotation,bank)
        raw,annotation,bank=fixture()
        raw["responses"]["Q-HDB6"]="Unreviewed second response"
        with self.assertRaisesRegex(ValueError,"exactly one"):
            m.triage(raw,annotation,bank)

    def test_answer_and_mapping_source_ids_must_agree(self):
        raw,annotation,bank=fixture()
        bank["questions"][0]["id"]="Q-OTHER"
        with self.assertRaisesRegex(ValueError,"Unknown"):
            m.triage(raw,annotation,bank)

if __name__=="__main__":
    unittest.main()
