"""Original first-print Lilly p535 source-primary versus secondary-role tests.

Only invented seven-planet zodiac positions, never people/natal profiles.
"""
from pathlib import Path
from collections import Counter
import inspect
import json
import sys
import unittest
import numpy as np
import swisseph as swe

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import lilly_cvii_p535_secondary_dignity_participants_century_v01 as m

def source_primary(selected,n):
    mask=np.zeros((n,7),dtype=bool)
    mask[:,selected]=True
    return {mode:mask.copy() for mode in m.MODES}

class FirstEditionSecondaryParticipants(unittest.TestCase):
    def test_sun_in_aries_source_mars_domicile_is_secondary(self):
        # Primary Sun 5° Aries, other Mars owns Aries (its domicile).
        p=np.array([[5.,130.,80.,190.,150.,230.,320.]])
        source=source_primary(0,1)
        L,U=m.participant_rights_at_primary_places(p,np.array([40.]),source)
        for mode in m.MODES:
            for term in m.TERMS:
                self.assertTrue(L[(mode,term)][0,4])
                self.assertTrue(U[(mode,term)][0,4])
                self.assertFalse(L[(mode,term)][0,0])
                self.assertTrue(np.array_equal(L[(mode,term)],U[(mode,term)]))
    def test_another_primary_is_not_double_counted_as_secondary(self):
        p=np.array([[5.,130.,80.,190.,8.,230.,320.]])
        src=source_primary(0,1)
        for mask in src.values():mask[0,4]=True
        L,U=m.participant_rights_at_primary_places(p,np.array([40.]),src)
        for mode in m.MODES:
            for term in m.TERMS:
                self.assertFalse(L[(mode,term)][0,4])
                self.assertFalse(U[(mode,term)][0,4])
                self.assertTrue(np.all(~(L[(mode,term)]&src[mode])))
    def test_sect_near_horizon_retains_jupiter_as_possible_only(self):
        # Saturn at 6.5° Aries, when Saturn alone is primary;
        # Aries has Mars domicile, Sun exaltation, Venus term.
        # Jupiter at this Aries degree gains rights by nocturnal triplicity
        # but not daylight, so it is possible, NOT certain, if sect is unknown.
        p=np.array([[120.,130.,80.,190.,150.,230.,6.5]])
        primary=source_primary(6,1)
        L,U=m.participant_rights_at_primary_places(p,np.array([0.]),primary)
        for mode in m.MODES:
            k=(mode,m.essential.LILLY_SCHEME)
            self.assertFalse(L[k][0,5])
            self.assertTrue(U[k][0,5])
            self.assertTrue(L[k][0,4])  # Mars domicile
            self.assertFalse(L[k][0,6]) # Saturn already primary
            self.assertFalse(np.array_equal(L[k],U[k]))
    def test_no_primary_has_zero_secondary_even_with_all_positive_dignities(self):
        p=np.array([[5.,130.,80.,190.,150.,230.,320.]])
        E={key:np.zeros((1,7),bool) for key in m.MODES}
        L,U=m.participant_rights_at_primary_places(p,np.array([25.]),E)
        for k in L:
            self.assertFalse(L[k].any())
            self.assertFalse(U[k].any())
    def test_source_scope_rejects_bad_shapes_unknown_modes_and_invalid_zodiac(self):
        p=np.array([[5.,130.,80.,190.,150.,230.,320.]])
        E=source_primary(0,1)
        with self.assertRaises(ValueError):
            m.participant_rights_at_primary_places(p,np.array([1.,2.]),E)
        with self.assertRaises(ValueError):
            m.participant_rights_at_primary_places(p+360.,np.array([20.]),E)
        with self.assertRaises(ValueError):
            m.participant_rights_at_primary_places(p,np.array([20.]),{"rising":E[m.MODES[0]]})
        with self.assertRaises(ValueError):
            m.participant_rights_at_primary_places(p,np.array([20.]),{key:np.ones((1,7),dtype=np.int8) for key in m.MODES})
    def test_synthetic_source_clock_and_original_modes_are_exhaustive(self):
        n=4
        p=np.tile([5.,130.,80.,190.,150.,230.,320.,.2],(n,1)).astype(float)
        jd=swe.julday(2023,5,10,0.)
        a=np.zeros((n,17),float)
        r1=np.empty(n);r2=np.empty(n)
        for i in range(n):
            RC,_=swe.houses_ex(jd+i/96.,39.,-75.,b"R")
            PC,_=swe.houses_ex(jd+i/96.,39.,-75.,b"P")
            r1[i]=RC[0];r2[i]=RC[1]
            a[i,0]=RC[0];a[i,4]=40.;a[i,5:17]=PC
        c=Counter();HD={}
        m.scan_chunk(p,a,np.array([0,-1,1,2],np.int32),
                     cusp1=r1,cusp2=r2,counts=c,HDsets=HD)
        self.assertEqual(c["original_UTC_samples"],4)
        self.assertEqual(c["original_HD_margin_unknown"],1)
        for mode in m.MODES:
            self.assertEqual(sum(c[mode+"|source_S1_"+x] for x in
                ("no_primary","sole_primary","multiple_primary")),4)
            for term in m.TERMS:
                key=mode+"|"+term+"|"
                self.assertGreaterEqual(c[key+"extra_secondary_possible_any"],
                                        c[key+"extra_secondary_certain_any"])
    def test_no_personality_or_private_birth_input(self):
        self.assertEqual(set(inspect.signature(m.run).parameters),
                         {"west","angles","hd_cache","hd_join","verify_sha"})
        self.assertEqual(m.METHODS,9)
    def test_full_source_grid_receipt_when_available(self):
        p=ROOT/"reference/research/lilly_cvii_p535_secondary_participants_full_century_public_v01.json"
        if not p.exists():self.skipTest("Full original source census not yet completed")
        j=json.loads(p.read_text());c=j["counts"]
        self.assertEqual(j["sample_UTC_count"],3506400)
        self.assertEqual(j["original_HD_structural_intervals"],288908)
        self.assertEqual(c["original_HD_margin_unknown"],125)
        self.assertEqual(c["original_sector_uncertain"],5049)
        self.assertEqual(c["original_Ptolemy_fourmode_common_conditional"],4553)
        self.assertFalse(j["historically_complete_Lilly_manners_ruler_computed"])
        self.assertFalse(j["independent_human_behavior_validation"])
        self.assertFalse(j["private_natal_or_interview_evidence_used"])
        for mode in m.MODES:
            self.assertEqual(sum(c[mode+"|source_S1_"+z] for z in
                        ("no_primary","sole_primary","multiple_primary")),3506400)
            for term in m.TERMS:
                prefix=mode+"|"+term+"|"
                self.assertEqual(c[prefix+"primary_sole_with_certain_secondary"]+
                                 c[prefix+"primary_multi_with_certain_secondary"],
                                 c[prefix+"extra_secondary_certain_any"])
                self.assertLessEqual(c[prefix+"extra_secondary_certain_any"],
                                     c[prefix+"extra_secondary_possible_any"])
if __name__=="__main__":unittest.main()
