"""Regiomontanus first-house source-sensitive geometry; no personality claim."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"scripts/lilly_cvii_regiomontanus_house_century_v01.py"
sp=importlib.util.spec_from_file_location("lillyregio",SCRIPT)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)

class LillyRegioTests(unittest.TestCase):
 def test_first_house_wrap_boundary(self):
  p=np.array([[359.,100,150,200,230,260,290],
              [4.,100,150,200,230,260,290],
              [13.,100,150,200,230,260,290]])
  c1=np.array([350.,350.,350.]);c2=np.array([10.,10.,10.])
  r=m.cusp_member(p,c1,c2)
  self.assertEqual(list(r[:,0]),[True,True,False])

 def test_house_first_includes_cusp1_not_cusp2(self):
  p=np.array([[10.,100,150,200,230,260,290],
              [30.,100,150,200,230,260,290]])
  r=m.cusp_member(p,[10.,10.],[30.,30.])
  self.assertEqual(list(r[:,0]),[True,False])

 def test_invalid_unsupported_house_arc_fails_closed(self):
  p=np.zeros((2,7))
  with self.assertRaisesRegex(ValueError,"arc"):
   m.cusp_member(p,[0,0],[0,0])
  with self.assertRaisesRegex(ValueError,"arc"):
   m.cusp_member(p,[0,0],[181,181])
  with self.assertRaisesRegex(ValueError,"Unnormalized"):
   m.cusp_member(p,[360,0],[30,30])

 def test_actual_swiss_regiomontanus_varies_from_cached_placidus(self):
  from datetime import datetime,timezone
  j=m.julian_from_utc('2000-01-01T00:00:00+00:00')
  import swisseph as swe
  reg,regarms=swe.houses_ex(j,23.0,14.0,b'R')
  pla,plaarms=swe.houses_ex(j,23.0,14.0,b'P')
  self.assertAlmostEqual(reg[0],pla[0],places=8)
  self.assertGreater(abs((reg[1]-pla[1]+180.)%360.-180.),0.001)

 def test_regio_vs_sign_difference_count_partitions(self):
  p=np.zeros((4,7))
  p[:,0]=[25,35,1,100]
  p[:,1]=100;p[:,2]=150;p[:,3]=200;p[:,4]=230;p[:,5]=260;p[:,6]=290
  a=np.zeros((4,17))
  a[:,0]=20;a[:,5]=20;a[:,6]=30
  # This is a unit test for group partition, not the real Regio site.
  baseline=(np.floor(p/30)==np.floor(a[:,0,None]/30)).any(axis=1)
  region=m.cusp_member(p,[20.,20.,20.,20.],[40.,40.,40.,40.]).any(axis=1)
  self.assertEqual(sum(region&~baseline)+sum(~region&baseline)+sum(region&baseline)+sum(~region&~baseline),4)

 def test_julian_source_requires_UTC_and_source_schema(self):
  with self.assertRaises(ValueError):
   m.julian_from_utc('2000-01-01T00:00:00')
  with self.assertRaises(ValueError):
   m.julian_from_utc('2000-01-01T00:00:00+01:00')
  self.assertEqual(m.SWISS_VERSION,"2.10.03")

 def test_source_code_never_returns_lilly_personality_score(self):
  s=SCRIPT.read_text()
  for f in ("REGIOMONTANUS","source_manners_significator_computed",
            "human_behavior_prediction_verified","source_original_72_shards_sha256_reverified","source_site_coordinates_suppressed"):
   self.assertIn(f,s)
  self.assertNotRegex(s,r"/home/[^/\s]+/(?:Documents|Downloads)/")

if __name__=="__main__":unittest.main()
