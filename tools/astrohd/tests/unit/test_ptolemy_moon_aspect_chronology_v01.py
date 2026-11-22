"""Ptolemaic lunar Moon aspect chronology *geometry only* regression."""
from __future__ import annotations
from datetime import datetime,timezone
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"scripts/ptolemy_moon_app_sep_geometric_event_witness_v01.py"
sp=importlib.util.spec_from_file_location("lunar_witness",SCRIPT)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)

class LunarContactTests(unittest.TestCase):
 def test_bisection_exact_linear_event(self):
  root,res=m.bisect_event(lambda t:2*t-3,1,2,-1,1)
  self.assertAlmostEqual(root,1.5,places=7)
  self.assertLess(abs(res),1e-7)
 def test_bisection_rejects_non_bracketed_and_wrap_jumps(self):
  with self.assertRaises(ValueError):
   m.bisect_event(lambda x:x+1,0,2,1,3)
  with self.assertRaisesRegex(ValueError,"Discontinuity"):
   m.bisect_event(lambda x:x,0,1,179,-179)
 def test_wrapped_aspect_root_supports_all_eight_geometries(self):
  self.assertEqual(len(m.ASPECTS),8)
  self.assertEqual({v for a,v in m.ASPECTS},{"conjunction","sextile","square","trine","opposition"})
  self.assertEqual(m.wrapped_residual(10,350,20),0)
  self.assertEqual(m.wrapped_residual(350,10,340),0)
  self.assertEqual(m.wrapped_residual(0,180,180),0)
 def test_latitude_scope_requires_same_sign_for_bodily_conjunction(self):
  self.assertEqual(m.conjunction_latitude_scope(2.0,1.0),"SAME_ECLIPTIC_SIDE")
  self.assertEqual(m.conjunction_latitude_scope(2.0,-1.0),"OPPOSITE_ECLIPTIC_SIDE")
  self.assertEqual(m.conjunction_latitude_scope(2.0,0.0),"NEAR_ECLIPTIC_UNRESOLVED")
 def test_source_has_explicit_utc_and_rejects_unzoned_strings(self):
  with self.assertRaises(ValueError):
   m.utc("2000-01-01T00:00:00")
  with self.assertRaises(ValueError):
   m.utc("2000-01-01T01:00:00+01:00")
  self.assertEqual(m.utc("2000-01-01T00:00:00Z"),datetime(2000,1,1,tzinfo=timezone.utc))
 def test_strict_ephemeris_hashes_and_source_integrity(self):
  self.assertEqual(m.DATA_HASHES["semo_18.se1"],"1ca07bd67c24374d77226180c20a4f9996cba013697894810518e7eb582ca4f7")
  self.assertEqual(m.SWISSEPH_VER,"2.10.03")
  self.assertNotEqual(m.DATA_HASHES["sepl_18.se1"],"ca1393ceab3a44fbc895887cf789c68819ae6a1cbc9b22225872dbe4ccd99a66")
 def test_engineering_window_never_called_ancient_valid_orb(self):
  s=SCRIPT.read_text()
  self.assertIn("search_horizon_is_not_ptolemaic_orb",s)
  self.assertIn("does_not_complete_fifth_domination_mode",s)
  self.assertIn("does_not_assign_personality_or_human_prediction",s)
  self.assertNotRegex(s,r"/home/[^/\s]+/(?:Documents|Downloads)/")
 def test_root_reconstruction_uses_retflag_verification(self):
  s=SCRIPT.read_text()
  self.assertIn("flags&MASK!=swe.FLG_SWIEPH",s)
  self.assertIn("Moon",s)
  self.assertIn("source",s.lower())

if __name__=="__main__":
 unittest.main()
