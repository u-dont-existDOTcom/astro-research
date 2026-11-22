"""Synthetic source-condition checks for III.18 triplicity and sect branches."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
import numpy as np

HERE=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location(
 "pt3",HERE/"scripts/ptolemy_three_modes_triplicity_sect_century_v01.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class PtolemyTriplicityTests(unittest.TestCase):
 def test_source_day_night_triplicity_primary_rulers(self):
  self.assertEqual(int(m.PRIMARY_DAY[0]),0)  # Sun fire day
  self.assertEqual(int(m.PRIMARY_NIGHT[0]),5) # Jupiter fire night
  self.assertEqual(int(m.PRIMARY_DAY[1]),3)  # Venus earth day
  self.assertEqual(int(m.PRIMARY_NIGHT[1]),1)# Moon earth night
  self.assertEqual(int(m.PRIMARY_DAY[2]),6)  # Saturn air day
  self.assertEqual(int(m.PRIMARY_NIGHT[2]),2)# Mercury air night
  self.assertEqual(int(m.PRIMARY_DAY[3]),4)  # Mars water day
  self.assertEqual(int(m.PRIMARY_NIGHT[3]),4)# Mars water night

 def test_water_co_ruler_switches_with_sect(self):
  wd=int(m.CO_DAY[3])
  wn=int(m.CO_NIGHT[3])
  self.assertTrue(wd&(1<<4)) # Mars
  self.assertTrue(wd&(1<<3)) # Venus
  self.assertFalse(wd&(1<<1))
  self.assertTrue(wn&(1<<1)) # Moon
  self.assertFalse(wn&(1<<3))

 def test_fire_co_ruler_presence_not_posthoc_chosen(self):
  # Aries day: includes Sun + Jupiter as source-known co-rulers.
  day=int(m.CO_DAY[0])
  self.assertTrue(day&(1<<0))
  self.assertTrue(day&(1<<5))
  # The principal-only variant is restricted but never more inclusive.
  r=m.classifications([5.0],[235.0],[30.0])
  self.assertFalse(r["near_solar_horizon_unknown_triplicity"][0])

 def test_horizon_zero_abstains_triplicity(self):
  # With unknown sect, the three-mode stats cannot assert an additional
  # common candidate even if an earlier domicile/exaltation candidate exists.
  r=m.classifications([15.0],[15.0],[0.0])
  self.assertTrue(r["two_modes_shared"][0])
  self.assertTrue(r["near_solar_horizon_unknown_triplicity"][0])
  self.assertFalse(r["three_modes_all_corulers_shared_certain"][0])

 def test_co_rulers_do_not_remove_principal(self):
  rng=np.random.default_rng(11)
  mercury=rng.uniform(0,360,1000)
  moon=rng.uniform(0,360,1000)
  alt=rng.uniform(-75,75,1000)
  r=m.classifications(mercury,moon,alt)
  self.assertTrue(np.all(~r["three_modes_principal_only_shared_certain"]|r["three_modes_all_corulers_shared_certain"]))
  self.assertTrue(np.all(~r["three_modes_new_common_via_principal_only_certain"]|r["three_modes_new_common_via_corulers_certain"]))

 def test_near_horizon_abstention_is_symmetric(self):
  r=m.classifications([100.0,220.0,100.0],[210.0,11.0,210.0],[-0.099,0.099,0.0])
  self.assertTrue(np.all(r["near_solar_horizon_unknown_triplicity"]))
  self.assertFalse(np.any(r["three_modes_new_common_via_corulers_certain"]))

 def test_sign_and_solar_altitude_input_errors(self):
  with self.assertRaises(ValueError):
   m.mask_for_ruler_modes([2],[float("nan")],all_triplicity_members=True)
  with self.assertRaises(ValueError):
   m.mask_for_ruler_modes([12],[20.0],all_triplicity_members=True)
  with self.assertRaises(ValueError):
   m.classifications([12.0],[12.0],[float("inf")])

 def test_misaligned_source_manifests_rejected(self):
  w={"schema":m.ptolemy2.SCHEMA,"record_order":list(m.ptolemy2.PLANET_NAMES)+["Mercury_lon_speed"],
    "total_samples":2,"record_bytes":64,"step_minutes":15,
    "utc_start_inclusive":"2026-01-01T00:00:00Z",
    "utc_end_exclusive":"2026-01-01T00:30:00Z"}
  wm={"schema":m.ptolemy2.SCHEMA,"total_samples":2,
      "chunks":[{"first_index":0,"count":2,"size_bytes":128,"sha256":"0"*64}]}
  a={"schema":"location-conditioned-western-angles-utc-grid-v1-NONCANONICAL",
     "sample_count":2,"step_minutes":15,"record_bytes":136,
     "utc_start":"2026-01-01T00:00:00Z",
     "utc_end_exclusive":"2026-01-01T00:30:00Z",
     "cols":["asc","mc","armc","true_obliquity","true_sun_altitude"]}
  am={"total_samples":2,"shards":[{"first_index":0,"count":2}]}
  self.assertEqual(m.check_two_cache_manifests(w,wm,a,am),2)
  a["utc_start"]="2026-01-02T00:00:00Z"
  with self.assertRaisesRegex(ValueError,"calendars"):
   m.check_two_cache_manifests(w,wm,a,am)

 def test_source_is_neither_private_natal_nor_model_validation(self):
  text=(HERE/"scripts/ptolemy_three_modes_triplicity_sect_century_v01.py").read_text()
  self.assertIn("no_human_predictive_validation",text)
  self.assertIn("no_full_governor_selection",text)
  self.assertNotRegex(text, r"/home/[^/\s]+/(?:Documents|Downloads)/")
  self.assertNotIn("1985",text)

if __name__=="__main__":unittest.main()
