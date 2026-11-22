"""Source-neutral regression fixtures; no natal, biographical or outcome records."""
import importlib.util
from pathlib import Path
import sys
import unittest
import numpy as np

SCRIPTS=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(SCRIPTS))
import ptolemy_lilly_same_instant_century_v01 as m


class SameInstantWitness(unittest.TestCase):
    def test_margin_is_only_conditional_one_vote_robustness(self):
        v=np.array([
          [4,2,0,0,0,0,0],
          [3,2,1,0,0,0,0],
          [2,2,1,0,0,0,0],
          [0,0,0,4,0,0,2]
        ],dtype=np.uint8)
        leaders,ties,robust,margins=m.rank_state(v)
        self.assertEqual(leaders.tolist(),[0,0,-1,3])
        self.assertEqual(ties.tolist(),[False,False,True,False])
        self.assertEqual(robust.tolist(),[True,False,False,True])
        self.assertEqual(margins.tolist(),[2,1,0,2])

    def test_vote_is_mode_not_multiple_triplicity_votes(self):
        lng=np.array([0.,30.,60.,90.,120.,150.,180.,210.,240.,270.,300.,330.])
        alt=np.full(12,40.)
        for scheme in m.SCHEMES:
            for co in (False,True):
                v=m.four_mode_votes(lng,alt,scheme,co)
                self.assertEqual(v.shape,(12,7))
                self.assertTrue(np.all(v>=0))
                self.assertTrue(np.all(v<=4))
                self.assertTrue(np.all(v.sum(axis=1)>=3))
                if not co:self.assertTrue(np.all(v.sum(axis=1)<=4))

    def test_existing_term_variants_remain_distinct(self):
        # The printed tables differ within Aries between 6° and 12°.
        lng=np.array([7.,11.,28.,300.])
        alt=np.full(4,35.)
        left=m.four_mode_votes(lng,alt,"ptolemy_printed_1940",False)
        right=m.four_mode_votes(lng,alt,"egyptian_printed_1940",False)
        self.assertFalse(np.array_equal(left,right))

    def test_intercepted_sign_is_not_any_planet_inside_first_house(self):
        # House 5° Aries -> 15° Gemini. Full Taurus is intercepted;
        # the partial Gemini strip and early Aries strip are not intercepted.
        p=np.full((4,7),345.,dtype=float)
        p[0,3]=40.   # Venus in fully contained Taurus
        p[1,3]=70.   # Venus in cusp-2 Gemini portion, inside but not intercepted
        p[2,3]=2.    # Venus in ascending Aries sign but outside this house
        p[3,3]=80.   # Venus in later Gemini, outside house
        c1=np.full(4,5.)
        c2=np.full(4,75.)
        q=m.first_house_and_intercepted(p,c1,c2)
        self.assertEqual(q["planet_in_intercepted_first_house_sign"].tolist(),
                          [True,False,False,False])
        self.assertEqual(q["regiomontanus_first_house"].tolist(),
                          [True,True,False,False])
        self.assertEqual(q["ascending_sign"].tolist(),[False,False,True,False])
        self.assertEqual(q["ascending_sign_or_intercepted_sign"].tolist(),
                          [True,False,True,False])

    def test_no_false_interception_at_cusp(self):
        # Aries is ascending at exact cusp, Taurus ends on cusp 2;
        # neither must be counted as *intercepted*.
        p=np.full((1,7),250.,dtype=float);p[0,3]=40.
        q=m.first_house_and_intercepted(p,np.array([0.]),np.array([60.]))
        self.assertFalse(q["planet_in_intercepted_first_house_sign"][0])
        self.assertFalse(q["intercepted_first_house_sign_exists"][0])
        self.assertTrue(q["regiomontanus_first_house"][0])

    def test_bad_inputs_rejected(self):
        with self.assertRaises(ValueError):
            m.four_mode_votes(np.array([5.,6.]),np.array([0.]),m.SCHEMES[0],True)
        with self.assertRaises(ValueError):
            m.rank_state(np.ones((2,6),dtype=np.uint8))
        with self.assertRaises(ValueError):
            m.first_house_and_intercepted(np.ones((2,7)),np.zeros(1),np.ones(2))

    def test_source_scoped_legacy_regiomontanus_geometry(self):
        p=np.array([[0.,30.,60.,90.,120.,150.,180.]],dtype=float)
        c1=np.array([5.]);c2=np.array([75.])
        q=m.first_house_and_intercepted(p,c1,c2)
        self.assertTrue(q["regiomontanus_first_house"][0])


if __name__=="__main__": unittest.main()
