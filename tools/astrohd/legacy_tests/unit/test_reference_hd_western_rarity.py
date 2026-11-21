"""Check source-neutral selected-five and any-five rarity calculations."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
p=ROOT/"scripts/audit_reference_hd_western_rarity.py"
spec=importlib.util.spec_from_file_location("ref_rarity",p)
rarity=importlib.util.module_from_spec(spec);spec.loader.exec_module(rarity)

class MechanicalRarityTests(unittest.TestCase):
    def test_all_five_pair_geometry_invented_synthetic(self):
        # Geometry with a close 5-body major-aspect network but deliberately
        # missing all exact natal calendar input or real source biography.
        bodies=np.array([[12.,65.,280.,340.,341.,282.,222.]],dtype=float)
        anyfive,groups=rarity.five_group_masks(bodies,3.)
        self.assertTrue(bool(anyfive[0]))
        self.assertEqual(len(groups),21)
        self.assertEqual(len(rarity.ALL_PAIRS),21)

    def test_arbitrary_signs_do_not_falsely_qualify(self):
        bodies=np.array([[5.,19.,73.,121.,163.,205.,269.]],dtype=float)
        flags,_=rarity.five_group_masks(bodies,3.)
        self.assertFalse(bool(flags[0]))

    def test_selected_geometry_is_contained_in_any_five_union(self):
        rng=np.random.default_rng(20261119)
        positions=rng.uniform(0,360,size=(200,7))
        union,groups=rarity.five_group_masks(positions,3.)
        self.assertTrue(all(np.all(g<=union) for g in groups))

    def test_major_aspect_boundaries(self):
        fake=np.array([[10.,70.,130.,190.,250.,310.,10.]],dtype=float)
        orb=rarity.nearest_major_orb(fake)[0]
        # 10 and 70: exact sextile; two 10° positions exact conjunction.
        self.assertAlmostEqual(orb[rarity.ALL_PAIRS.index((0,1))],0.)
        self.assertAlmostEqual(orb[rarity.ALL_PAIRS.index((0,6))],0.)

    def test_explicit_utc_rejects_naive_or_shifted(self):
        self.assertEqual(rarity.utc("2000-01-01T00:00:00Z").hour,0)
        for s in ["2000-01-01T00:00:00","2000-01-01T00:00:00+02:00"]:
            with self.assertRaises(ValueError):rarity.utc(s)

if __name__=="__main__":unittest.main()
