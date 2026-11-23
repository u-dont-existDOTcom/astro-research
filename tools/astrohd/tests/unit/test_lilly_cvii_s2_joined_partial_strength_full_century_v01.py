"""Invented-only classical natal longitudes, no participant or interview input."""
from pathlib import Path
from collections import Counter
import inspect
import json
import sys
import unittest
import numpy as np
import swisseph as swe

SCRIPTS=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(SCRIPTS))
import lilly_cvii_s2_joined_partial_strength_full_century_v01 as m

class S2SourceQualifiedPartialStrength(unittest.TestCase):
    def test_method_product_and_source_categories(self):
        self.assertEqual(m.SCENARIOS,864)
        self.assertEqual(m.PARTIAL_METHOD_COUNT,72)
        self.assertEqual(len(m.ORBS),2)
        self.assertEqual(set(m.MODES),set(m.s2.MODES))
        self.assertEqual(len(m.SCOPES),2)
        self.assertEqual(tuple(m.STATIONS),(.01,.02,.05))
        self.assertEqual(set(inspect.signature(m.run).parameters),
                         {"west","angles","hd_cache","hd_join","verify_sha"})

    def test_selection_ignores_numerically_stronger_ineligible_classical_planet(self):
        low=np.array([[50,0,-10,20,5,0,0],
                      [50,0,-10,8,5,0,0]],np.int16)
        high=low.copy()
        eligible=np.array([[0,0,0,1,1,0,0],
                           [0,0,0,1,1,0,0]],bool)
        chosen,sole,multi=m.select_joined_source_candidate(low,high,eligible,np.array([True,True]))
        self.assertEqual(chosen.tolist(),[3,3])
        self.assertTrue(multi.all())
        self.assertFalse(sole.any())
        eligible[0,4]=False
        chosen,sole,multi=m.select_joined_source_candidate(low,high,eligible,np.array([False,False]))
        self.assertEqual(chosen.tolist(),[3,-1])
        self.assertTrue(sole[0])
        self.assertTrue(multi[1])

    def test_finite_station_bounds_can_prevent_false_winner(self):
        lo=np.array([[0,0,0,10,8,0,0]],np.int16)
        hi=np.array([[0,0,0,10,12,0,0]],np.int16)
        mask=np.array([[0,0,0,1,1,0,0]],bool)
        chosen,_,multi=m.select_joined_source_candidate(lo,hi,mask,np.array([True]))
        self.assertTrue(multi[0])
        self.assertEqual(chosen[0],-1)

    def test_no_joined_candidates_is_unknown_not_a_weak_planet(self):
        scores=np.ones((2,7),np.int16)*10
        empty=np.zeros((2,7),bool)
        res,sole,multi=m.select_joined_source_candidate(scores,scores,empty,np.array([True,True]))
        self.assertEqual(res.tolist(),[-1,-1])
        self.assertFalse(sole.any())
        self.assertFalse(multi.any())

    def test_synthetic_same_time_full_864_policy_partition_and_baselines(self):
        n=4
        jd=swe.julday(2022,1,20,0.)
        P=np.tile([275.,110.,115.,112.,220.,240.,270.,.2],(n,1)).astype(float)
        A=np.zeros((n,17),float)
        R=np.empty((n,12),float)
        for i in range(n):
            rc,_=swe.houses_ex(jd+i/96.,39.,-75.,b"R")
            pc,_=swe.houses_ex(jd+i/96.,39.,-75.,b"P")
            R[i]=rc
            A[i,0]=rc[0]
            A[i,4]=40.
            A[i,5:17]=pc
        IDs=np.array([0,1,-1,2],dtype=np.int32)
        speeds=np.zeros((n,7),float)
        speeds[:,2]=.2
        speeds[:,3:]=[.2,-.1,.3,-.1]
        counts=Counter()
        HD={key:np.zeros(m.HD_STATE_COUNT,dtype=bool) for key in
            [*("|".join((a,b,c)) for a in m.MODES for b in m.ORBS for c in m.SCOPES),
             *("Ptolemy_"+"|".join((a,b,c)) for a in m.MODES for b in m.ORBS for c in m.SCOPES),
             "all_864_same"]}
        m.scan_chunk(P,A,IDs,R=R,velocities=speeds,edges=np.zeros(n,bool),counts=counts,HD=HD)
        self.assertEqual(counts["original_UTC_clock_samples"],n)
        self.assertEqual(counts["HD_root_unknown"],1)
        self.assertEqual(counts["near_sun_horizon_sect_unknown"],0)
        for mode in m.MODES:
            for orb in m.ORBS:
                for scope in m.SCOPES:
                    key="|".join((mode,orb,scope))
                    self.assertEqual(counts[key+"|S2_empty_go_to_later"]+
                                     counts[key+"|S2_sole"]+
                                     counts[key+"|S2_multi"],
                                     counts[mode+"|S1_empty"])
                    self.assertEqual(counts[key+"|stable_all72_sole"],counts[key+"|S2_sole"])
                    self.assertLessEqual(counts[key+"|stable_all72_any"],n)

    def test_immutable_complete_actual_source_census_when_published(self):
        p=Path(__file__).resolve().parents[2]/"reference/research/lilly_cvii_s2_joined_partial_strength_full_century_public_v01.json"
        if not p.exists():self.skipTest("Full original century source calculation not yet performed")
        x=json.loads(p.read_text());c=x["counts"]
        self.assertEqual(x["samples"],3506400)
        self.assertEqual(x["HD_structural_intervals"],288908)
        self.assertEqual(c["HD_root_unknown"],125)
        self.assertEqual(c["near_sun_horizon_sect_unknown"],5049)
        self.assertEqual(c["ptolemy_conditional_fourmode_common"],4553)
        self.assertEqual(x["all_eligibility_x_partial_strength_policy_count"],864)
        self.assertFalse(x["original_all_stage_Lilly_manners_ruler_computed"])
        self.assertFalse(x["individual_personality_predictive_accuracy_established"])
        self.assertFalse(x["private_natal_or_interview_data_loaded"])
        orig=Path(__file__).resolve().parents[2]/"reference/research/lilly_cvii_s2_original_joining_full_century_public_v01.json"
        old=json.loads(orig.read_text())["counts"]
        for mode in m.MODES:
            for orb in m.ORBS:
                for scope in m.SCOPES:
                    key="|".join((mode,orb,scope))
                    self.assertEqual(c[key+"|S2_sole"],old[key+"|S2_one_joined_planet"])
                    self.assertEqual(c[key+"|S2_multi"],old[key+"|S2_multiple_joined_planets"])
                    self.assertEqual(c[key+"|S2_empty_go_to_later"],old[key+"|S2_zero_proceed_to_S3"])
                    self.assertEqual(c[key+"|stable_all72_sole"],c[key+"|S2_sole"])
                    self.assertEqual(c[key+"|stable_all72_any"],c[key+"|stable_all72_sole"]+
                                     c[key+"|stable_all72_multi_strict"])
        self.assertLessEqual(c["all_864_source_scenarios_same_strict_conditional_S2"],3506400)

if __name__=="__main__":unittest.main()
