"""Nonpersonal full-century Ptolemy III.13 dual-configuration sensitivity tests."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
LEDGER=ROOT/"reference/research/ptolemy_iii13_dual_configuration_angular_sensitivity_public_v01.json"
SOURCES=ROOT/"reference/research/ptolemy_iii13_dual_relation_source_contract_v01.json"
PREV=ROOT/"reference/research/ptolemy_iii13_four_mode_terms_aggregate_v01.json"
SCRIPT=ROOT/"scripts/ptolemy_iii13_mercury_lunar_dual_aspect_century_v01.py"
spec=importlib.util.spec_from_file_location("dual_source_geometric",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SourceDualWitnessActualAggregateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=json.loads(LEDGER.read_bytes())
  cls.rules=json.loads(SOURCES.read_bytes())
  cls.prev=json.loads(PREV.read_bytes())

 def test_source_scope_is_from_real_chapter_not_synthetic_governor_claim(self):
  self.assertEqual(self.r["real_15_minute_uniform_utc_samples"],3506400)
  self.assertFalse(self.r["fifth_original_mode_fully_adjudicated"])
  self.assertIsNone(self.r["human_behavior_score"])
  self.assertEqual(self.r["validated_human_prediction_count"],0)
  self.assertTrue(self.r["anonymous_commentator_15_deg_is_not_original_Ptolemy_orb"])
  self.assertTrue(self.rules["fifth_original_mode_not_fully_computed"])
  self.assertTrue(self.rules["no_personality_ranking"])

 def test_four_mode_broad_candidates_retained_not_changed(self):
  r=self.r
  self.assertEqual(r["prior_four_mode_1940_source_candidate_baseline"]["ptolemy_1940_printed_all_corulers"],
     self.prev["counts"]["ptolemy_printed_1940_shared_corulers_certain"])
  self.assertEqual(r["prior_four_mode_1940_source_candidate_baseline"]["egyptian_1940_printed_all_corulers"],
     self.prev["counts"]["egyptian_printed_1940_shared_corulers_certain"])
  self.assertEqual(r["nonMercury_external_common_rule_candidate_counts"]["ptolemy_printed"],2753325)

 def test_nonbody_double_aspect_threshold_monotonic_and_numerically_reproduced(self):
  rows=self.r["threshold_rows"]
  self.assertEqual([r["max_abs_degrees_for_each_two_aspect_configuration"] for r in rows],[1,3,5,10,15])
  self.assertEqual([r["p_printed_nonbody_witness"] for r in rows],
      [5294,46006,123192,463182,968436])
  self.assertEqual([r["e_printed_nonbody_witness"] for r in rows],
      [4881,45176,120306,449595,943172])
  self.assertEqual([r["source_terms_scheme_disagreement_for_nonconjunction"] for r in rows],
      [2143,17374,43254,148953,292086])

 def test_unverified_conjunctions_not_mislabelled_source_valid(self):
  for row in self.r["threshold_rows"]:
   self.assertLess(row["p_printed_nonbody_witness"],
                   row["p_including_uncertified_bodily_conjunctions"])
   self.assertLess(row["e_printed_nonbody_witness"],
                   row["e_including_uncertified_bodily_conjunctions"])
  self.assertTrue(self.r["anonymous_commentator_15_deg_is_not_original_Ptolemy_orb"])

 def test_missing_data_and_source_shards_never_silently_zeroed(self):
  self.assertEqual(self.r["near_horizon_unknown"],5049)
  self.assertEqual(self.r["angular_derivative_shard_edge_unknown_samples"],72)
  self.assertEqual(self.r["screened_interior_samples"],3501279)
  self.assertTrue(self.r["original_72_source_binary_shards_sha256_reverified"])

 def test_angular_proxy_consistent_with_independent_ephemeris_neutral_test(self):
  check=self.r["finite_difference_moon_relative_velocity_private_check"]
  self.assertEqual(check["planetary_comparisons"],36)
  self.assertTrue(check["relative_motion_direction_agreement"])
  self.assertFalse(check["source_binary_identical_to_original_century"])
  self.assertLess(check["max_abs_difference_deg_per_day_from_new_strict_swieph"],0.0001)

 def test_source_glyphs_remain_public_safe_no_person_details(self):
  for obj in (self.r,self.rules):
   self.assertNotIn("private_person",str(obj))
   self.assertTrue(obj["no_private_participant_data"] if "no_private_participant_data" in obj else True)
  for fn in (LEDGER,SOURCES,SCRIPT):
   txt=fn.read_text()
   self.assertNotRegex(txt,r"/home/[^/\s]+/(?:Documents|Downloads)/")
   self.assertNotRegex(txt,r"[\w+.%-]+@(?:gmail|outlook|yahoo)\.com")

 def test_positive_synthetic_jupiter_dual_sextile_trine_one_polarity_each(self):
  # Fixed source choices: Mercury Aries 20° day has Jupiter as fire
  # co-ruler, Moon Libra 20° has Jupiter term. Jupiter at Gemini 20°
  # sextile Mercury and trine Moon. Relative Moon trajectory crosses
  # exact trine, showing both applying and separating geometry.
  rows=np.zeros((5,8));rows[:,0]=40
  rows[:,2]=20
  rows[:,1]=[199,199.5,200,200.5,201]
  rows[:,3]=95;rows[:,4]=250;rows[:,5]=80;rows[:,6]=320
  angles=np.zeros((5,17));angles[:,4]=60.
  c=m.scan_chunk(rows,angles)
  for scheme in m.SCHEMES:
   self.assertGreaterEqual(c[f"{scheme}_1deg_nonbody_only"],1)
   self.assertGreaterEqual(c[f"{scheme}_1deg_applying_nonbody_only"],1)
   self.assertGreaterEqual(c[f"{scheme}_1deg_separating_nonbody_only"],1)
   self.assertEqual(c["shard_derivative_unknown_samples"],2)


if __name__=="__main__":
 unittest.main()
