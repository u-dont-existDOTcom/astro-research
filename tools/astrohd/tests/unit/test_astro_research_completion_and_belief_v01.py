"""Do not confuse a bounded completed report with chart predictive validation."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("finish",ROOT/"scripts/audit_astro_research_completion_v01.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
PLAN=json.loads((ROOT/"reference/research/astro_research_finishline_roadmap_v01.json").read_bytes())
BELIEF=json.loads((ROOT/"reference/research/splenic_belief_vs_accuracy_asymmetry_v01.json").read_bytes())
DONE={k:next(iter(sorted(vals))) for k,vals in m.KNOWN_TERMINAL.items()}

class FinishlineTests(unittest.TestCase):
    def test_roadmap_distinguishes_human_validation_and_bounded_reports(self):
        d=m.assess(PLAN)
        self.assertFalse(d["report_complete"])
        self.assertFalse(d["optional_empirical_validation_complete"])
        self.assertIn("R",d["unfinished_core_tracks"])

    def test_terminal_report_with_explicit_no_rank_is_allowed(self):
        s=dict(DONE)
        s["R"]="NO_DEFENSIBLE_RANK_POSSIBLE_SOURCE_GAPS"
        s["G"]="NOT_SENT_NO_AUTHORIZED_ROUTE_READY_TO_SEND"
        s.pop("V")
        d=m.assess(PLAN,s)
        self.assertTrue(d["report_complete"])
        self.assertFalse(d["gemini_direct_reply_received"])
        self.assertTrue(d["gemini_external_reply_unavailable"])
        self.assertFalse(d["optional_empirical_validation_complete"])

    def test_user_pasted_gemini_is_not_direct_authenticated_reply(self):
        r=m.assess(PLAN)
        self.assertTrue(r["gemini_reply_received_via_user_paste"])
        self.assertFalse(r["gemini_direct_reply_received"])

    def test_false_fake_rank_finish_prohibited(self):
        p=copy.deepcopy(PLAN)
        p["end_definition"]["no_promoting_unreproduced_better_rank_as_finished"]=False
        with self.assertRaisesRegex(RuntimeError,"reproducibility"):m.assess(p)

    def test_old_14_subset_does_not_claim_full_rank(self):
        r=next(x for x in PLAN["tracks"] if x["id"]=="R")
        self.assertTrue(any("no undocumented 14-state pruning" in x for x in r["acceptance"]))
        self.assertTrue(any("no-defensible-unique-ranking" in x for x in r["acceptance"]))

    def test_optional_validation_not_new_owner_blocker(self):
        p=copy.deepcopy(PLAN)
        next(x for x in p["tracks"] if x["id"]=="V")["optional"]=False
        with self.assertRaisesRegex(RuntimeError,"mandatory"):m.assess(p)

    def test_forum_ends_with_documented_missing_sources(self):
        f=next(x for x in PLAN["tracks"] if x["id"]=="F")
        self.assertIn("AUDIT_REPORT_COMPLETE_WITH_RECORDED_EVIDENCE_GAPS",f["terminal_outputs"])
        self.assertTrue(any("THREE" in x for x in f["acceptance"]))

    def test_belief_construct_separate_from_accurate_signal(self):
        ids={x["id"]:x["status"] for x in BELIEF["constructs"]}
        self.assertIn("UNSCORED",ids["BELIEF_IN_INTUITIVE_CUE"])
        self.assertEqual(ids["ACCURATE_SAFETY_PREDICTION"],
                         "EXCLUDED_FROM_NEW_PERSONALITY_SCORE")
        self.assertTrue(BELIEF["controls"]["no_automatic_natal_score_points"])

    def test_nonendorsement_does_not_prove_no_signal(self):
        self.assertTrue(BELIEF["controls"]["no_default_penalty_for_absence"])
        self.assertTrue(BELIEF["controls"]["no_positive_score_for_post_exposure_endorsement"])
        self.assertTrue(BELIEF["controls"]["no_claim_that_nonendorsement_mathematically_never_informative"])

if __name__=="__main__":
    unittest.main()
