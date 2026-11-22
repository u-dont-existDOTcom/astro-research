"""Placidus house-boundary sensitivity ONLY, not historical Lilly selection."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"scripts/lilly_cvii_house_vs_asc_sign_placidus_diagnostic_v01.py"
sp=importlib.util.spec_from_file_location("house",SCRIPT)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)

class LillyHouseSensitivityTests(unittest.TestCase):
 def test_planet_in_pl_house_but_not_asc_sign(self):
  planet=np.array([[35,100,150,200,230,260,290]],dtype=float)
  a=np.zeros((1,17));a[:,0]=2.;a[:,5]=2.;a[:,6]=41.
  result=m.flags(planet,a)
  self.assertTrue(result["first_house_only"][0])
  self.assertFalse(result["any_ASC_zodiac_sign"][0])

 def test_planet_ASC_sign_but_outside_first_house(self):
  planet=np.array([[1,100,150,200,230,260,290]],dtype=float)
  a=np.zeros((1,17));a[:,0]=20.;a[:,5]=20.;a[:,6]=35.
  result=m.flags(planet,a)
  self.assertTrue(result["asc_zodiac_sign_only"][0])
  self.assertFalse(result["any_placidus_first_house"][0])

 def test_house_arc_across_aries_start_and_ending(self):
  planet=np.array([[359.,100,150,200,230,260,290],
                   [2.,100,150,200,230,260,290],
                   [15.,100,150,200,230,260,290]],dtype=float)
  a=np.zeros((3,17));a[:,0]=350.;a[:,5]=350.;a[:,6]=10.
  r=m.flags(planet,a)
  self.assertTrue(r["any_placidus_first_house"][0])
  self.assertTrue(r["any_placidus_first_house"][1])
  self.assertFalse(r["any_placidus_first_house"][2])

 def test_exact_cusp_boundary_inclusion_and_exclusion(self):
  p=np.array([[10,100,150,200,230,260,290],[30,100,150,200,230,260,290]],float)
  a=np.zeros((2,17));a[:,0]=10.;a[:,5]=10.;a[:,6]=30.
  r=m.flags(p,a)
  self.assertTrue(r["any_placidus_first_house"][0])
  self.assertFalse(r["any_placidus_first_house"][1])

 def test_invalid_planets_or_house_arcs_rejected(self):
  p=np.zeros((3,7));a=np.zeros((3,17))
  with self.assertRaises(ValueError):
   m.flags(p,a)
  a[:,6]=200
  with self.assertRaises(ValueError):
   m.flags(p,a)
  a[:,6]=30.;p[0,0]=360.
  with self.assertRaises(ValueError):
   m.flags(p,a)

 def test_joint_threshold_counts_use_two_exclusive_cohorts(self):
  p=np.zeros((4,8))
  p[:,0]=100
  p[:,1]=[70,80,100,110]
  p[:,2]=[200,201,205,210]
  p[:,3]=[71,80.5,109,120]
  p[:,4]=250;p[:,5]=270;p[:,6]=310
  a=np.zeros((4,17));a[:,0]=20.;a[:,5]=20.;a[:,6]=50.
  z=m.scan(p,a)
  self.assertEqual(z["any_ASC_zodiac_sign"]+z["no_ASC_sign_planet"],4)
  self.assertEqual(z["any_placidus_first_house"]+z["no_placidus_house_planet"],4)
  self.assertEqual(z["first_house_only"]+z["asc_zodiac_sign_only"]+
                   z["both_have_planet"]+z["neither_has_planet"],4)

 def test_does_not_promote_placidus_to_lilly_historical_method(self):
  s=SCRIPT.read_text()
  self.assertIn("not_historically_substitutable",s)
  self.assertIn("REGIOMONTANUS_ORIGINAL_NOT_CALCULATED_HERE",s)
  self.assertIn("no_human_behavior_score_or_prediction",s)
  self.assertNotRegex(s,r"/home/[^/\s]+/(?:Documents|Downloads)/")

if __name__=="__main__":unittest.main()
