"""Source-provenance regression for second independent, non-population forum pass."""
from __future__ import annotations
import copy,importlib.util,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("wave2",ROOT/"scripts/audit_disputed_predictor_wave2_v01.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
PROTO=json.loads((ROOT/"reference/research/disputed_predictor_forum_audit_protocol_v01.json").read_bytes())
BASE=json.loads((ROOT/"reference/research/disputed_predictor_forum_seed_v01.json").read_bytes())
WAVE=json.loads((ROOT/"reference/research/disputed_predictor_forum_wave2_v01.json").read_bytes())
class Wave2Tests(unittest.TestCase):
    def test_source_counts_no_prevalence_and_normalized_overlap(self):
        r=m.merge(PROTO,BASE,WAVE)
        self.assertEqual(r["source_claims_registered"],18)
        self.assertEqual(r["sampled_evidence_units"],48)
        self.assertEqual(r["additional_wave_evidence_units"],20)
        self.assertEqual(r["wave2_full_page_read_units"],4)
        self.assertEqual(r["wave2_excerpt_read_units"],16)
        self.assertGreaterEqual(len(r["overlapping_old_and_wave2_normalized_threads"]),1)
        self.assertFalse(r["any_per_system_top_frequency_rank_supported"])
        self.assertEqual(r["prospective_verified_prediction_records"],0)
    def test_trailing_url_slug_is_same_thread(self):
        u="https://www.reddit.com/r/AstrologyCharts/comments/1wzzuxw"
        v=u+"/why_dont_i_resonate_with_my_rising_sign/"
        self.assertEqual(m.discussion_key(u),m.discussion_key(v))
    def test_missing_actor_field_fails(self):
        b=copy.deepcopy(WAVE);del b["new_evidence"][0]["source_actor_id"]
        with self.assertRaises(ValueError):m.merge(PROTO,BASE,b)
    def test_fake_prospective_receipt_fails(self):
        b=copy.deepcopy(WAVE);b["new_evidence"][0]["prospective_prediction_record_verified"]=True
        with self.assertRaises(RuntimeError):m.merge(PROTO,BASE,b)
    def test_fake_full_page_read_count_fails(self):
        b=copy.deepcopy(WAVE);b["full_page_read_count"]+=1
        with self.assertRaises(ValueError):m.merge(PROTO,BASE,b)
    def test_overwritten_old_claim_fails(self):
        b=copy.deepcopy(WAVE);b["new_claims"][0]["id"]=BASE["claims"][0]["id"]
        with self.assertRaises(ValueError):m.merge(PROTO,BASE,b)
    def test_non_reddit_thread_id_safe(self):
        a=[x for x in WAVE["new_evidence"] if x["id"]=="W2_18"][0]
        self.assertIn("astrologyweekly",m.discussion_key(a["url"]))
    def test_no_claim_outcome_independently_confirmed(self):
        self.assertTrue(all(x["objective_outcome_verified"] is False for x in WAVE["new_evidence"]))
        self.assertEqual(WAVE["verified_prospective_natal_prediction_receipts"],0)
if __name__=="__main__":unittest.main()
