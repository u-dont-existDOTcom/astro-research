"""Original Lilly CVII two-branch source-scope and mathematical subset tests."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
FILE=ROOT/"scripts/lilly_cvii_second_order_conjunction_grid_v01.py"
spec=importlib.util.spec_from_file_location("lilly_second",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class LillyPartialBranchTests(unittest.TestCase):
 def setUp(self):
  self.p=np.array([
    [10,100,150,200,230,260,290], # Sun in Aries ASC; no fallback
    [70,100,150,102,220,250,280], # Venus near Moon
    [70,100,101,200,230,260,310], # Moon/Mercury mutual conjunction
    [100,101,150,250,260,280,310] # Sun near Moon
  ],dtype=np.float64)
  self.asc=np.zeros(4,dtype=np.float64)

 def test_first_branch_is_asc_sign_proxy_not_complete_lilly_house(self):
  z=m.classify_source_proxy(self.p,self.asc)
  self.assertEqual(z["any_planet_in_ASC_ZODIAC_SIGN_PROXY"],1)
  self.assertEqual(z["no_planet_in_ASC_ZODIAC_SIGN_PROXY"],3)
  self.assertIn("ASC_SIGN_ONLY",m.ASCENT_SIGN_PROXY_NOTE)

 def test_second_branch_distinguishes_nonluminaries_sun_and_mutual(self):
  z=m.classify_source_proxy(self.p,self.asc)
  self.assertEqual(z["fallback_1deg_four_nonlum_externals"],0)
  self.assertEqual(z["fallback_3deg_four_nonlum_externals"],1)
  self.assertEqual(z["fallback_1deg_including_Sun"],1)
  self.assertEqual(z["fallback_1deg_including_Sun_and_mutual_Moon_Mercury"],2)
  self.assertEqual(z["fallback_1deg_mutual_Mercury_Moon_conjunction"],1)
  self.assertEqual(z["still_no_joined_candidate_10deg_inclusive_variant"],0)

 def test_each_parameter_inclusion_is_monotone(self):
  z=m.classify_source_proxy(self.p,self.asc)
  for t in (1,3,5,10):
   k=str(t)
   self.assertLessEqual(z[f"fallback_{k}deg_four_nonlum_externals"],
      z[f"fallback_{k}deg_including_Sun"])
   self.assertLessEqual(z[f"fallback_{k}deg_including_Sun"],
      z[f"fallback_{k}deg_including_Sun_and_mutual_Moon_Mercury"])
   self.assertEqual(z[f"fallback_{k}deg_including_Sun_and_mutual_Moon_Mercury"]+
      z[f"still_no_joined_candidate_{k}deg_inclusive_variant"],3)
  for key in ("four_nonlum_externals","including_Sun","including_Sun_and_mutual_Moon_Mercury"):
   vals=[z[f"fallback_{str(t)}deg_{key}"] for t in (1,3,5,10)]
   self.assertEqual(vals,sorted(vals))

 def test_geometric_wrap_and_exact_boundary(self):
  self.assertAlmostEqual(m.separation([359],[1])[0],2)
  self.assertAlmostEqual(m.separation([1],[359])[0],2)
  self.assertAlmostEqual(m.separation([20],[20])[0],0)
  with self.assertRaises(ValueError):
   m.separation([360],[1])

 def test_invalid_source_cache_shapes_fail(self):
  with self.assertRaises(ValueError):
   m.classify_source_proxy(np.zeros((3,8)),np.zeros(3))
  with self.assertRaises(ValueError):
   m.classify_source_proxy(np.zeros((3,7)),np.zeros(2))
  with self.assertRaises(ValueError):
   m.classify_source_proxy(np.full((3,7),-3.),np.zeros(3))

 def test_source_explicitly_not_complete_manners_governor(self):
  s=FILE.read_text()
  for label in ("cannot_assign_true_manners_significator",
                "source_asc_ruler_and_its_dispositor_aspect_COMPLETED",
                "source_fixed_stars_COMPLETED",
                "angular_joining_thresholds_engineering_not_Lilly_source",
                "source_planet_in_asc_house_or_intercepted_sign_COMPLETED"):
   self.assertIn(label,s)
  self.assertNotRegex(s,r"/home/[^/\s]+/(?:Documents|Downloads)/")

if __name__=="__main__":unittest.main()
