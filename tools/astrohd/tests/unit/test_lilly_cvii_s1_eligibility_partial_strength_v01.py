"""Invented zodiac positions only, source eligibility vs partial fortitude."""
import json
from pathlib import Path
import sys
import unittest

import numpy as np
import swisseph as swe

SRC=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(SRC))
import lilly_cvii_s1_eligible_partial_strength_century_v01 as a


class FirstOriginalMannersOccupants(unittest.TestCase):
    def test_rising_sign_and_real_quadrant_house_are_distinct(self):
        planet=np.array([[5.,20.,40.,65.,75.,89.,100.]],dtype=float)
        masks=a.first_stage_eligible(planet,np.array([10.]),np.array([80.]))
        self.assertEqual(masks["ascending_sign"][0].tolist(),[1,1,0,0,0,0,0])
        self.assertEqual(masks["regiomontanus_first_house"][0].tolist(),[0,1,1,1,1,0,0])
        self.assertEqual(masks["ascending_sign_or_intercepted_sign"][0].tolist(),[1,1,1,0,0,0,0])
        self.assertEqual(set(masks),set(a.MODES))
    def test_source_geometric_clock_and_no_first_stage(self):
        p=np.tile(np.array([100.,110.,120.,130.,150.,170.,200.]),(2,1))
        m=a.first_stage_eligible(p,np.array([10.,10.]),np.array([80.,80.]))
        self.assertTrue(all(not v.any() for v in m.values()))
        with self.assertRaises(ValueError):
            a.first_stage_eligible(p,np.array([10.]),np.array([80.,80.]))
        with self.assertRaises(ValueError):
            a.first_stage_eligible(p,np.array([10.,10.]),np.array([10.,80.]))
    def test_single_qualified_occupant_even_if_original_sect_unknown(self):
        low=np.array([[6,5,4,3,2,1,0]],dtype=np.int16)
        high=low.copy()
        elig=np.array([[0,0,1,0,0,0,0]],dtype=bool)
        who,sole,multi=a.select_conditional_principal(low,high,elig,np.array([False]))
        self.assertEqual(who.tolist(),[2])
        self.assertTrue(sole[0]);self.assertFalse(multi[0])
    def test_multiple_source_occupants_require_interval_robustness(self):
        lo=np.array([[10,8,0,0,0,0,0],
                     [10,8,0,0,0,0,0],
                     [10,8,0,0,0,0,0]],np.int16)
        hi=np.array([[10,9,0,0,0,0,0],
                     [10,12,0,0,0,0,0],
                     [10,9,0,0,0,0,0]],np.int16)
        eligible=np.tile([1,1,0,0,0,0,0],(3,1)).astype(bool)
        who,sole,multi=a.select_conditional_principal(lo,hi,eligible,np.array([1,1,0],bool))
        self.assertEqual(who.tolist(),[0,-1,-1])
        self.assertEqual(sole.tolist(),[False,False,False])
        self.assertTrue(multi.all())
    def test_not_select_globally_strong_but_noneligible_planet(self):
        lo=np.array([[0,0,50,5,0,0,0]],np.int16)
        hi=lo.copy()
        eligible=np.array([[1,1,0,0,0,0,0]],bool)
        selected,_,_=a.select_conditional_principal(lo,hi,eligible,np.array([True]))
        self.assertEqual(selected.tolist(),[-1])
        eligible[0,0]=False
        selected,_,_=a.select_conditional_principal(lo,hi,eligible,np.array([True]))
        self.assertEqual(selected.tolist(),[1])
    def test_multiple_unknown_sole_luminary_not_final_historic_ruler(self):
        # The candidate mask is only a preliminary principal occupant.
        self.assertIn("source-scoped partial strength",a.__doc__)
        self.assertEqual(a.TOTAL_SOURCE_INTERPRETATIONS,216)
        self.assertEqual(a.SCENARIOS,72)
    def test_full_chunk_synthetic_source_conservation(self):
        jd=swe.julday(2020,5,14,0.)
        n=4
        source=np.tile([30.,40.,50.,60.,70.,80.,90.,0.4],(n,1)).astype(float)
        site=np.zeros((n,17),float)
        R=np.zeros((n,12))
        for i in range(n):
            reg,_=swe.houses_ex(jd+i/96,39.,-75.,b"R")
            plac,_=swe.houses_ex(jd+i/96,39.,-75.,b"P")
            R[i]=reg
            site[i,0]=reg[0]
            site[i,4]=40.
            site[i,5:17]=plac
        speed=np.zeros((n,7),float)
        speed[:,2:]=np.array([.4,-.1,.4,.2,.1])
        from collections import Counter
        c=Counter()
        h={k:np.zeros(a.HD_STATES,dtype=bool) for k in (*a.MODES,*(f"Ptolemy_{m}" for m in a.MODES),"all_three_same","all_three_same_Ptolemy")}
        a.scan_chunk(source,site,np.array([0,1,-1,2],np.int32),
                     R=R,velocities=speed,edges=np.zeros(n,dtype=bool),
                     counts=c,HD_presence=h)
        self.assertEqual(c["source_samples"],n)
        self.assertEqual(c["HD_root_margin_unassigned"],1)
        for mode in a.MODES:
            self.assertEqual(sum(c[mode+"|"+s] for s in
               ("empty_go_to_later_stages","sole_primary_occupant","multiple_principal_occupants")),n)
            self.assertEqual(c[mode+"|stable_all72_any_conditional_candidate"],
               c[mode+"|stable_all72_sole_occupant"]+
               c[mode+"|stable_all72_multi_partial_candidate"])
    def test_published_full_century_cannot_be_called_historical_final(self):
        path=Path(__file__).resolve().parents[2]/"reference/research/lilly_cvii_s1_eligible_partial_strength_full_century_public_v01.json"
        if not path.exists():self.skipTest("Actual complete original full source run not yet finished")
        j=json.loads(path.read_text());c=j["counts"]
        self.assertEqual(j["source_UTC_samples"],3506400)
        self.assertEqual(j["source_sensitive_S1_x_partial_strength_policy_count"],216)
        self.assertEqual(c["HD_root_margin_unassigned"],125)
        self.assertEqual(c["conditional_ptolemy_4mode_sample"],4553)
        self.assertEqual(j["HD_structural_interval_total"],288908)
        self.assertFalse(j["historically_final_Lilly_manners_significator_computed"])
        self.assertFalse(j["owner_or_third_party_private_birth_records_loaded"])
        for mode in a.MODES:
            empt=c[mode+"|empty_go_to_later_stages"]
            sole=c[mode+"|sole_primary_occupant"]
            multi=c[mode+"|multiple_principal_occupants"]
            self.assertEqual(empt+sole+multi,3506400)
            self.assertEqual(c[mode+"|stable_all72_sole_occupant"],sole)
            for terms in a.base.TERMS:
                for pol in a.base.ESSENTIAL_POLICIES:
                    for t in a.base.STATIONS:
                        for house in a.base.HOUSE_NAMES:
                            k="|".join((mode,terms,pol,house,f"station={t:.2f}"))
                            self.assertEqual(c[k+"|conditional_candidate"]+c[k+"|multi_unresolved"]+empt,3506400)

if __name__=="__main__":unittest.main()
