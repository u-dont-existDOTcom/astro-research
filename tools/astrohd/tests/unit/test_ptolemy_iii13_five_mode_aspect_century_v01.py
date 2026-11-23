"""Invented longitude and interval fixtures; no personal birth data."""
import itertools
import json
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import ptolemy_iii13_five_mode_aspect_century_v01 as m

class FifthMode(unittest.TestCase):
    def test_interval_witness_matches_brute_force(self):
        low=np.array([[2,1,1,1,0,0,0],[1,2,0,0,0,0,0],[2,2,0,0,0,0,0]])
        high=low+np.array([[0,1,1,0,1,0,0],[0,0,0,0,1,0,0],[0,1,0,0,0,0,0]])
        got, possible=m.interval_leader(low,high,np.ones(3,bool))
        for row in range(3):
            winners=[]
            for completion in itertools.product(*(range(a,b+1) for a,b in zip(low[row],high[row]))):
                mx=max(completion)
                winners.append({i for i,v in enumerate(completion) if v==mx})
            self.assertEqual(set(np.flatnonzero(possible[row])),set.union(*winners))
            sure=next(iter(winners[0])) if len(winners[0])==1 and all(x==winners[0] for x in winners) else -1
            self.assertEqual(got[row],sure)
    def test_fifth_aspect_bodily_uncertain_and_self_excluded(self):
        # Mercury 0, Venus 1, Mars 90, Jupiter 120, Saturn 45.
        p=np.array([[10.,70.,0.,1.,90.,120.,45.]])
        l,u,_=m.aspect_bounds(p,2,3.,"degree_near_rays","all_distinct_classical")
        self.assertFalse(l[0,3]); self.assertTrue(u[0,3])
        self.assertTrue(l[0,4]);self.assertTrue(l[0,5])
        self.assertFalse(u[0,2]);self.assertFalse(u[0,6])
    def test_sign_ray_not_equivalent_to_degree_near(self):
        p=np.array([[40.,60.,1.,75.,91.,240.,350.]])
        l,_,_=m.aspect_bounds(p,2,3.,"sign_rays","four_external")
        near,_,_=m.aspect_bounds(p,2,3.,"degree_near_rays","four_external")
        self.assertTrue(l[0,3]);self.assertFalse(near[0,3])
        self.assertTrue(l[0,4]);self.assertTrue(near[0,4])
    def test_lunar_precedence_and_exact_direction(self):
        p=np.array([[100.,0.,100.,61.,59.,120.,1.]])
        l,u,r=m.aspect_bounds(p,1,3.,"degree_near_rays","four_external")
        self.assertTrue(l[0,3]);self.assertGreater(r[0,3],0)
        self.assertTrue(l[0,4]);self.assertLess(r[0,4],0)
        self.assertEqual(r[0,5],0)
        self.assertFalse(l[0,6]);self.assertTrue(u[0,6])
    def test_unknown_phase_cannot_force_unqualified_candidate(self):
        b=np.array([[0,0,2,1,0,0,0]])
        l=b+np.array([[0,0,0,1,0,0,0]])
        got,_=m.interval_leader(l,b+1,np.array([True]))
        self.assertEqual(got[0],-1)
        got,_=m.interval_leader(b,b,np.array([False]))
        self.assertEqual(got[0],-1)
    def test_fixed_sect_and_own_place_are_distinct_from_strength(self):
        # Venus in Libra, day: own sign, contrary fixed sect. Jupiter
        # in Cancer precedes Venus by a square and has opposite sect.
        p=np.array([[0.,30.,60.,195.,90.,105.,300.]])
        f=m.qualifier_flags(p,np.array([30.]),np.array([3]))
        self.assertTrue(f["own_domicile"][0])
        self.assertTrue(f["fixed_sect_opposite_chart"][0])
        self.assertTrue(f["opposite_fixed_sect_preceding_square_witness"][0])
        f=m.qualifier_flags(p,np.array([30.]),np.array([2]))
        self.assertTrue(f["fixed_sect_unknown"][0])
        self.assertFalse(f["fixed_sect_matches_chart"][0])
    def test_source_receipt(self):
        path=m.ROOT/m.PUBLIC
        if not path.exists():self.skipTest("Century receipt not yet written")
        m.validate(json.loads(path.read_text()))
        j=json.loads(path.read_text())
        self.assertEqual(j["geometry_scenarios"],32)
        self.assertFalse(j["historically_complete_soul_governor"])
        self.assertFalse(j["independent_human_behavior_validation"])

if __name__=="__main__":unittest.main()
