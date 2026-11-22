"""Original printed Ptolemy/Egyptian terms, boundaries and model limitations."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"scripts/ptolemy_four_modes_source_terms_century_v01.py"
sp=importlib.util.spec_from_file_location("fourterms",SRC)
m=importlib.util.module_from_spec(sp)
sp.loader.exec_module(m)

class PtolemyTermPrintedSourceTests(unittest.TestCase):
 def test_each_source_row_contains_all_five_distinct_nonluminaries_and_30_degrees(self):
  for tbl in (m.PTOLEMY_PRINTED,m.EGYPTIAN_PRINTED):
   rul,cum=m.build_table(tbl)
   self.assertEqual(rul.shape,(12,5))
   self.assertTrue(np.all(cum[:,-1]==30))
   for name in m.SIGNS:
    self.assertEqual(len(set(x[0] for x in tbl[name])),5)
    self.assertEqual(sum(x[1] for x in tbl[name]),30)
 def test_original_1940_print_fixes_libra_final_mars_and_virgo_jupiter(self):
  p=m.PTOLEMY_PRINTED
  self.assertEqual(p["Libra"][-1],("Mars",6))
  self.assertEqual(p["Virgo"][2],("Jupiter",5))
  self.assertEqual([x[1] for x in p["Libra"]],[6,5,5,8,6])
  self.assertEqual([x[1] for x in p["Virgo"]],[7,6,5,6,6])
 def test_1940_egyptian_not_confused_with_ptolemy_third_source_arrangement(self):
  self.assertNotEqual(m.EGYPTIAN_PRINTED["Libra"],m.PTOLEMY_PRINTED["Libra"])
  self.assertEqual(m.EGYPTIAN_PRINTED["Libra"][-1],("Mars",2))
  self.assertEqual(m.PTOLEMY_PRINTED["Libra"][-1],("Mars",6))
 def test_exact_term_boundaries_match_printed_length_half_open_rules(self):
  scheme="ptolemy_printed_1940"
  degrees=[0,5.99999,6,13.99999,14,20.99999,21,25.999,26,29.999]
  vals=m.term_lords(np.array(degrees),scheme)
  expected=["Jupiter","Jupiter","Venus","Venus","Mercury",
           "Mercury","Mars","Mars","Saturn","Saturn"]
  self.assertEqual([m.PLANETS[int(i)] for i in vals],expected)
 def test_virgo_jupiter_term_is_recovered_and_libra_mars(self):
  scheme="ptolemy_printed_1940"
  values=[150,156.999,157,162.999,163,167.999,168,179.999,204,209.99]
  rulers=[m.PLANETS[int(i)] for i in m.term_lords(values,scheme)]
  self.assertEqual(rulers[:8],["Mercury","Mercury","Venus","Venus","Jupiter","Jupiter","Saturn","Mars"])
  self.assertEqual(rulers[8:10],["Mars","Mars"]) # 24° Libra = 204° longitude
 def test_libra_separate_schemes_change_term_rulers_at_seven_degrees(self):
  lon=np.array([187.0])
  a=m.PLANETS[int(m.term_lords(lon,"ptolemy_printed_1940")[0])]
  b=m.PLANETS[int(m.term_lords(lon,"egyptian_printed_1940")[0])]
  self.assertEqual(a,"Venus")
  self.assertEqual(b,"Mercury")
 def test_invalid_source_table_rejected(self):
  bad=dict(m.PTOLEMY_PRINTED)
  bad["Libra"]=(("Saturn",6),("Venus",5),("Mercury",5),("Jupiter",8),("Saturn",6))
  with self.assertRaisesRegex(ValueError,"distinct"):
   m.build_table(bad)
  bad=dict(m.PTOLEMY_PRINTED)
  bad["Virgo"]=(("Mercury",7),("Venus",6),("Jupiter",0),("Saturn",6),("Mars",6))
  with self.assertRaisesRegex(ValueError,"thirty|30"):
   m.build_table(bad)
 def test_bad_longitudes_and_missing_scheme_rejected(self):
  for values in ([-1.0],[360.0],[float("nan")]):
   with self.assertRaises(ValueError):
    m.term_lords(values,"ptolemy_printed_1940")
  with self.assertRaisesRegex(ValueError,"Unknown"):
   m.term_lords([1.],"chaldaean_unverified")
 def test_four_mode_never_subtracts_three_mode_common_candidate(self):
  rng=np.random.default_rng(791)
  ml=rng.uniform(0,360,4000)
  mo=rng.uniform(0,360,4000)
  alt=rng.uniform(-85,85,4000)
  z=m.classification(ml,mo,alt)
  self.assertTrue(np.all(~z["three_modes_primary_certain"]|
    z["ptolemy_printed_1940_shared_primary_certain"]))
  self.assertTrue(np.all(~z["three_modes_corulers_certain"]|
    z["ptolemy_printed_1940_shared_corulers_certain"]))
  self.assertTrue(np.all(~z["ptolemy_printed_1940_shared_primary_certain"]|
    z["ptolemy_printed_1940_shared_corulers_certain"]))
 def test_sect_horizon_carries_lower_bound_not_false_negative(self):
  z=m.classification([5.0,187.0],[5.0,187.0],[0.0,0.05])
  self.assertTrue(np.all(z["near_horizon_abstain"]))
  self.assertFalse(np.any(z["ptolemy_printed_1940_shared_primary_certain"]))
  self.assertTrue(np.all(z["ptolemy_printed_1940_known_two_modes_plus_term_with_near_horizon"]))
 def test_source_never_promotes_terms_into_personality_success(self):
  s=SRC.read_text()
  for word in ("actual_soul_governor_assigned","human_predictive_success_established",
               "remaining_source_modes","phase_or_aspect","no_personal_birth_or_profile_inputs"):
   self.assertIn(word,s)
  self.assertNotRegex(s,r"/home/[^/\s]+/(?:Documents|Downloads)/")
if __name__=="__main__":
 unittest.main()
