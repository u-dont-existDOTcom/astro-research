"""Invented celestial longitudes only: Lilly's original orbs and fallback branches."""
import sys
from pathlib import Path
import unittest
import numpy as np
SRC=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(SRC))
import lilly_cvii_ptolemy_same_instant_ordered_fallback_v02 as m

class LillyOriginalOrbTests(unittest.TestCase):
    def test_printed_orb_envelopes_and_moiety(self):
        low=m.SOURCE_ORBS["1647_table_smaller_orbs"]
        high=m.SOURCE_ORBS["1647_table_larger_orbs"]
        self.assertEqual(low.tolist(),[15,12,7,7,7,9,9])
        self.assertEqual(high.tolist(),[17,12.5,7,8,7.5,12,10])
        self.assertTrue(np.all(high>=low))
        self.assertEqual((low[3]+low[1])/2,9.5)
        self.assertEqual((high[3]+high[1])/2,10.25)

    def test_orb_join_wide_always_includes_narrow(self):
        p=np.tile(np.array([0.,100.,120.,105.,45.,220.,300.]),(5,1))
        # Venus 105 vs Moon 100 -> joined; no false interpretation from
        # different original source table variants.
        p[:,3]=[108.,109.6,110.,111.,111.2]
        low=m.orb_join(p,m.SOURCE_ORBS["1647_table_smaller_orbs"],
                       scope="four_externals_only")["any_joined"]
        high=m.orb_join(p,m.SOURCE_ORBS["1647_table_larger_orbs"],
                        scope="four_externals_only")["any_joined"]
        self.assertTrue(np.all(~low|high))
        self.assertTrue(high[0])
        self.assertFalse(high[-1])

    def test_mutual_moon_mercury_is_explicit_source_variant(self):
        p=np.array([[245.,30.,31.,78.,150.,220.,310.]],dtype=float)
        for table in m.SOURCE_ORBS.values():
            self.assertFalse(m.orb_join(p,table,scope="four_externals_only")["any_joined"][0])
            self.assertTrue(m.orb_join(p,table,scope="all_other_classical_planets")["any_joined"][0])

    def test_partile_is_same_numbered_degree_and_traditional_sign_ray(self):
        a=np.array([9.2,9.2,9.2,29.9,9.2])
        b=np.array([129.7,129.7,99.7,179.1,130.1])
        # Aries 9 -> Leo 9 yes, Aries9 -> Cancer9 yes,
        # Aries29 -> Virgo29 no (inconjunct);
        # final Leo10 lacks same numbered degree.
        self.assertEqual(m.partile_numbered_ray(a,b).tolist(),
                         [True,True,True,False,False])
        self.assertEqual(m.ray_residual(np.array([10.]),np.array([130.]))[0],0.)

    def test_dispositor_can_be_self_only_as_unknown_not_aspected(self):
        # Aries ASC => Mars ruler; put Mars in Aries so dispositor self.
        p=np.tile(np.array([100.,120.,60.,200.,5.,15.,320.]),(3,1))
        out=m.dispositor_see(p,np.array([4.,5.,6.]),
                            m.SOURCE_ORBS["1647_table_smaller_orbs"])
        self.assertTrue(np.all(out["same_as_own_dispositor"]))
        self.assertFalse(np.any(out["dispositor_sign_ray"]))
        self.assertFalse(np.any(out["dispositor_orb_near_ray"]))

    def test_sequential_fallbacks_disjoint_complete(self):
        s=m.stage_masks(
            np.array([1,0,0,0,0],bool),
            np.array([1,1,0,0,0],bool),
            np.array([0,1,1,0,0],bool),
            np.array([0,0,0,1,0],bool))
        self.assertEqual([v.tolist() for v in s],
                         [[True,False,False,False,False],
                          [False,True,False,False,False],
                          [False,False,True,False,False],
                          [False,False,False,True,False],
                          [False,False,False,False,True]])

    def test_source_reporting_has_no_name_or_outcome_inputs(self):
        import inspect
        self.assertEqual(set(inspect.signature(m.run).parameters),
                         {"west","angles","hd_cache","hd_join","hashes"})
        self.assertNotIn("name",str(inspect.signature(m.run)))

if __name__=="__main__":unittest.main()
