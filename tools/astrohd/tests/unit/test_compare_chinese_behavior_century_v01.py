import sys
import unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_chinese_behavior_century_v01 as c
import chinese_calendar_grid_v01 as cal

class TestChineseBehavior(unittest.TestCase):
    def test_frozen_source_rows(self):
        reg,shared=c.load_map()
        self.assertEqual(len(reg["elements"]),11)
        self.assertEqual(len(reg["main_stars"]),14)
        self.assertEqual(tuple(r["star"] for r in reg["main_stars"]),c.STARS)

    def test_five_element_source_literal_scope(self):
        # spring wood flourishing, fire assisted, earth dead, metal captive,
        # water resting. Nonwood weakness is not automatically deficiency.
        self.assertEqual(c.admitted_condition(0,0,"season_literal"),"flourishing")
        self.assertEqual(c.admitted_condition(1,0,"season_literal"),"flourishing")
        self.assertIsNone(c.admitted_condition(2,0,"season_literal"))
        self.assertIsNone(c.admitted_condition(3,0,"season_literal"))
        self.assertIsNone(c.admitted_condition(4,0,"season_literal"))
        self.assertEqual(c.admitted_condition(2,0,"season_deficiency_proxy"),"deficient")
        self.assertEqual(c.admitted_condition(0,3,"season_literal"),"dead")
        self.assertEqual(c.admitted_condition(0,1,"season_literal"),"rest_captive")

    def test_late_zi_and_historical_wall_clock(self):
        self.assertEqual(cal.hour_formula(4,0),(8,0))
        self.assertEqual(cal.hour_formula(4,23),(0,0))
        b,l=cal.wall_arrays(datetime(2026,3,8,6,45,tzinfo=timezone.utc),3)
        self.assertEqual((l[1]-l[0]),4500)
        self.assertEqual((b[1]-b[0]),900)

    def test_dual_term_boundary_abstention(self):
        a=np.array([[0,1,1,1,1],[1000,2,2,2,2],[2000,3,3,3,3]])
        b=a.copy();b[1,0]=1020
        val,ok=cal.term_features(np.array([800,955,1010,1065,1090]),{"a":a,"b":b})
        np.testing.assert_array_equal(ok,[True,False,False,False,True])
        np.testing.assert_array_equal(val[:,3],[1,1,2,2,2])

    def test_ziwei_original_source_example(self):
        # Vol II 安身命例: Jia first lunar month day 1, Zi hour:
        # Life Palace Yin, Fire bureau, Zi Wei at You.
        f=np.array([[1984,1,1,0]]) # fictional Jia year
        z=c.ziwei_masks(f,"next")
        self.assertEqual(int(z["life"][0]),int(z["life_body_union"][0]))
        # Formula's Zi Wei is in You, therefore not in Life Palace Yin.
        self.assertFalse(int(z["life"][0])&1)
        self.assertTrue(np.all(c.ziwei_masks(np.array([[1984,1,1,1],[1984,1,1,3]]),"next")["life"]>=0))

    def test_leap_policies_and_full_arm_count(self):
        a=np.array([[2001,-4,14,0],[2001,-4,16,1]])
        same=c.ziwei_masks(a,"same");nxt=c.ziwei_masks(a,"next");split=c.ziwei_masks(a,"split15")
        self.assertEqual(split["life"][0],same["life"][0]);self.assertEqual(split["life"][1],nxt["life"][1])
        reg,shared=c.load_map()
        t=c.make_tables(reg,shared,{"learning":1,"generosity":1,"anger":-1,"deception":-1})
        f={"bazi":np.array([[1,1,2,2,4,6,8,0],[1,1,2,2,6,6,0,0]]),"ziwei":a,
           "bazi_known":np.array([True,False]),"ziwei_known":np.array([True,True])}
        rows=list(c.models(f,t));self.assertEqual(len(rows),54)
        self.assertEqual(len({r[0] for r in rows}),54)
        for k,bits,ok in rows:
            v=c.s.score(bits,t[2])
            self.assertTrue(np.all(v["lo"]<=v["score"]+1e-12))
            self.assertTrue(np.all(v["hi"]>=v["score"]-1e-12))
            if k.startswith("union"):np.testing.assert_array_equal(ok,[True,False])

if __name__=="__main__":unittest.main()
