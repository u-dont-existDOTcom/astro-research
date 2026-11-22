"""Ptolemy four-source-mode original printed tables and source-neutral results."""
from __future__ import annotations
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[2]
RESEARCH=ROOT/"reference/research"
AGG=RESEARCH/"ptolemy_iii13_four_mode_terms_aggregate_v01.json"
PROV=RESEARCH/"ptolemy_1940_printed_terms_dual_table_provenance_v01.json"
RULES=RESEARCH/"ptolemy_iii13_five_domination_mode_source_adjudication_v02.json"
PRIOR=RESEARCH/"ptolemy_iii13_three_modes_century_aggregate_v01.json"

class PtolemyPrintedTermsAggregateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads(AGG.read_text())
  cls.prov=json.loads(PROV.read_text())
  cls.rules=json.loads(RULES.read_text())
  cls.prior=json.loads(PRIOR.read_text())
 def test_century_source_exact_denominator_and_baseline_conservation(self):
  c=self.data["counts"]
  self.assertEqual(self.data["sample_count"],3506400)
  self.assertEqual(c["three_modes_corulers_certain"],
    self.prior["counts"]["three_mode_any_source_coruler_candidate_certain"])
  self.assertEqual(c["three_modes_primary_certain"],
    self.prior["counts"]["three_mode_primary_triplicity_candidate_certain"])
 def test_sources_are_distinct_and_counts_differ_by_individual_event_class(self):
  c=self.data["counts"]
  self.assertEqual(c["ptolemy_printed_1940_shared_corulers_certain"],3006871)
  self.assertEqual(c["egyptian_printed_1940_shared_corulers_certain"],2965122)
  self.assertEqual(c["source_scheme_changes_four_mode_coruler_shared_certain"],341721)
  self.assertGreater(c["source_scheme_changes_four_mode_coruler_shared_certain"],
    abs(c["ptolemy_printed_1940_shared_corulers_certain"]-
        c["egyptian_printed_1940_shared_corulers_certain"]))
 def test_terms_must_only_increase_candidates_not_remove_them(self):
  c=self.data["counts"]
  self.assertEqual(c["ptolemy_printed_1940_new_v_three_corulers_certain"],
    c["ptolemy_printed_1940_shared_corulers_certain"]-c["three_modes_corulers_certain"])
  self.assertEqual(c["egyptian_printed_1940_new_v_three_corulers_certain"],
    c["egyptian_printed_1940_shared_corulers_certain"]-c["three_modes_corulers_certain"])
 def test_collected_primary_source_glyph_and_missing_size_corrected(self):
  issues=self.prov["directly_resolved"]
  libra=next(x for x in issues if "Libra" in x["issue"])
  virgo=next(x for x in issues if "Virgo" in x["issue"])
  self.assertEqual((libra["printed_english_page_107"],libra["term_degrees"]),("Mars",6))
  self.assertEqual((virgo["printed_english_page_107"],virgo["term_degrees"]),("Jupiter",5))
  self.assertEqual(self.prov["principal_source"]["pdf_sha256"],
    "10b44f40e47409215aa3d6c4ec2863ebc3982b81d33b4d4e5e2a065761ab7fec")
 def test_fifth_not_claimed_or_source_silent(self):
  self.assertFalse(self.data["fifth_original_mode_phase_or_aspect_completed"])
  self.assertFalse(self.data["source_condition_is_a_personality_score"])
  self.assertEqual(self.data["independently_validated_astrological_predictions"],0)
  self.assertIn("FOUR",self.rules["status"])
  self.assertEqual(self.rules["behavioral_claims_licensed_for_automated_rank"],0)
 def test_private_and_provenance_receipts_have_bounded_hashes(self):
  self.assertTrue(self.data["source_shards_sha256_rechecked"])
  for digest in (self.data["private_immutable_full_receipt_sha256"],
       *self.data["source_manifests_sha256"].values(),
       self.rules["supersedes_v01_sha256"]):
   self.assertEqual(len(digest),64)
   int(digest,16)
 def test_near_horizon_missing_eligibility_not_zeroed(self):
  c=self.data["counts"]
  self.assertEqual(c["near_horizon_abstain"],5049)
  self.assertLess(c["ptolemy_printed_1940_known_two_modes_plus_term_with_near_horizon"],
      c["near_horizon_abstain"])
 def test_no_sensitive_participant_data_in_public_reports(self):
  for p in (AGG,PROV,RULES):
   s=p.read_text()
   self.assertNotRegex(s,r"/home/[^/\s]+/(?:Documents|Downloads)/")
   self.assertNotRegex(s,r"[\w.+%-]+@(?:gmail|outlook|yahoo)\.com")
   self.assertNotIn("private_participant_birth_record",s)

if __name__=="__main__":
 unittest.main()
