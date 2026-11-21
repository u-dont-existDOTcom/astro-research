"""Verify three bounded source waves end with gaps, not invented accuracy rates."""
from __future__ import annotations
import copy,importlib.util,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
sp=importlib.util.spec_from_file_location("closeout",ROOT/"scripts/audit_disputed_predictor_three_wave_closeout_v01.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def load(n):return json.loads((ROOT/"reference/research"/n).read_bytes())
P=load("disputed_predictor_forum_audit_protocol_v01.json")
BASE=load("disputed_predictor_forum_seed_v01.json")
W2=load("disputed_predictor_forum_wave2_v01.json")
W3=load("disputed_predictor_forum_wave3_v01.json")
class ThreeWaveTests(unittest.TestCase):
    def test_real_scope_and_gaps(self):
        x=m.audit(P,BASE,W2,W3)
        self.assertEqual(x["claim_count"],22)
        self.assertEqual(x["observation_units"],59)
        self.assertEqual(x["unique_source_discussions_across_three_waves"],49)
        self.assertTrue(x["source_specific_missing_gaps"])
        self.assertTrue(x["not_a_population_sample"])
        self.assertTrue(x["no_verified_chart_prospective_prediction"])
        self.assertTrue(x["no_calibrated_falsification_rates"])
        self.assertEqual(x["third_full_page_read_units"],2)
        self.assertEqual(x["third_official_excerpt_read_units"],1)
    def test_fake_success_count_fails(self):
        w=copy.deepcopy(W3);w["independent_validated_predictions"]=1
        with self.assertRaises(RuntimeError):m.audit(P,BASE,W2,w)
    def test_unverified_hit_escalation_fails(self):
        w=copy.deepcopy(W3);w["new_evidence"][0]["objective_outcome_verified"]=True
        with self.assertRaises(RuntimeError):m.audit(P,BASE,W2,w)
    def test_missing_tradition_not_disappeared(self):
        x=m.audit(P,BASE,W2,W3)
        self.assertEqual(x["source_school_counts"]["other_astro_traditions_uncovered"]["claims"],1)
    def test_mismatched_read_modes_fails(self):
        w=copy.deepcopy(W3);w["third_full_page_read_units"]=5
        w["full_page_read_count"]=5
        with self.assertRaises(ValueError):m.audit(P,BASE,W2,w)
    def test_technical_vs_event_source_disambiguated(self):
        z={x["id"]:x for x in W3["new_claims"]}
        self.assertEqual(z["MAYA_TZOLKIN_PERSONALITY"]["disposition"],"NOT_A_PREDICTION")
        self.assertEqual(z["ZIWEI_NATAL_EVENT_PREDICTION"]["disposition"],"EMPIRICAL_VALIDATION_NEEDED")
    def test_duplicate_id_fails(self):
        w=copy.deepcopy(W3);w["new_evidence"][0]["id"]=W2["new_evidence"][0]["id"]
        with self.assertRaises(ValueError):m.audit(P,BASE,W2,w)
    def test_provider_scope_not_truth_about_whole_tradition(self):
        x=W3["new_evidence"]
        self.assertTrue(any(e["evidence_type"]=="provider_scope_statement" for e in x))
        self.assertFalse(any(e["objective_outcome_verified"] for e in x))
if __name__=="__main__":unittest.main()
