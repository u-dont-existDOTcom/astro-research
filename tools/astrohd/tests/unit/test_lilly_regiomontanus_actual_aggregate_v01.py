"""Public source-neutral verified Regiomontanus and joining diagnostic integrity."""
from __future__ import annotations
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[2]
RESEARCH=ROOT/"reference/research"
SRC=RESEARCH/"lilly_cvii_ordered_manners_fallback_source_register_v01.json"
AGG=RESEARCH/"lilly_cvii_regio_house_and_joined_fallback_public_aggregate_v01.json"
H=ROOT/"scripts/lilly_cvii_regiomontanus_house_century_v01.py"

class LillyRegiomontanusRealCenturyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=json.loads(AGG.read_bytes())
  cls.r=json.loads(SRC.read_bytes())
  cls.c=cls.a["counts"]
 def test_reproducible_real_source_cache_denominators(self):
  a=self.a;c=self.c;n=a["source_clock_sample_count"]
  self.assertEqual(n,3506400)
  self.assertEqual(c["regio_first_house_any"],1409411)
  self.assertEqual(c["regio_first_house_none"],2096989)
  self.assertEqual(c["asc_sign_any"],1428060)
  self.assertEqual(c["placidus_first_house_any"],1407259)
  self.assertEqual(c["regio_first_house_any"]+c["regio_first_house_none"],n)
 def test_actual_house_changes_earlier_sign_proxy_for_many_instants(self):
  s=self.a["switch_counts"]
  self.assertEqual(s["Regiomontanus_first_house_vs_ASC_sign_symmetric_difference"],835699)
  self.assertEqual(s["Regiomontanus_vs_Placidus_first_house_symmetric_difference"],84004)
  self.assertEqual(s["ASC_sign_vs_Placidus_first_house_symmetric_difference"],844727)
  self.assertEqual(self.c["regio_only_not_sign"]+self.c["sign_only_not_regio"],835699)
 def test_crosschecked_source_cusp_geometry(self):
  self.assertTrue(self.a["old_72_original_source_shards_all_SHA256_rechecked"])
  self.assertEqual(self.a["Regiomontanus_against_original_Placidus_crosschecks"],14176)
  self.assertLess(self.a["maximum_angular_discrepancy_original_cache_deg"],0.00000001)
  self.assertEqual(self.a["swisseph_library_version"],"2.10.03")
 def test_thresholds_follow_history_order_but_are_not_lilly_authentic_orbs(self):
  c=self.c
  self.assertEqual([c[f"{t}deg_joined_4_externals_when_regio_house_empty"] for t in (1,3,5,10)],
                   [137535,379725,597721,1029627])
  self.assertEqual([c[f"{t}deg_joined_4_externals_when_ASC_sign_empty"] for t in (1,3,5,10)],
                   [135965,377008,592895,1020813])
  self.assertEqual([c[f"{t}deg_joined_4_externals_when_placidus_house_empty"] for t in (1,3,5,10)],
                   [137534,379926,598174,1030533])
 def test_methodological_abstention_and_nonpredictive_scope(self):
  a=self.a
  self.assertFalse(a["full_Lilly_manners_significator_computed"])
  self.assertFalse(a["human_predictive_accuracy_verified"])
  self.assertIsNone(a["source_human_personality_score"])
  self.assertTrue(a["historical_qualifiers_remain_missing"])
  self.assertIn("Regiomontanus",self.r["source_methods"]["historical_house_system_primary"])
 def test_earlier_yearly_source_manifest_checksums_preserved(self):
  for d in self.a["source_original_manifests_SHA256"].values():
   self.assertEqual(len(d),64);int(d,16)
  for d in self.a["privacy"]["private_exact_receipt_SHA256"].values():
   self.assertEqual(len(d),64);int(d,16)
 def test_public_methods_have_no_owner_birth_record(self):
  for f in (SRC,AGG,H):
   body=f.read_text()
   self.assertNotRegex(body,r"/home/[^/\s]+/(?:Documents|Downloads)/")
   self.assertNotRegex(body,r"[\w.+%-]+@(?:gmail|outlook|yahoo)\.com")
   self.assertNotIn("private_participant_birth_record",body)
  self.assertFalse(self.a["privacy"]["real_natal_or_interview_records_included"])

if __name__=="__main__":unittest.main()
