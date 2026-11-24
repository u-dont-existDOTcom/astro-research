import sys
import unittest
from collections import Counter,defaultdict
from itertools import product
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_multitradition_intersections_v01 as s

def make(rows,known=None):
    a=s.Extrema(len(rows[0]))
    for i,r in enumerate(rows):
        a.add(str(i),np.array(r,dtype=float),np.ones(len(r),bool) if known is None else np.array(known[i],bool))
    return a

class TestSameRow(unittest.TestCase):
    def test_not_marginal_probability(self):
        a=make([[1,0,-1,-1]])
        b=make([[-1,-1,1,0]])
        h=np.zeros(4);common=np.ones(4,bool)
        x=s.cross([a,b],common,h)
        self.assertEqual(x["hd_tied_others_strict_any"],0)
        self.assertEqual(x["weak_dominance_any"],0)
        self.assertEqual(s.metrics(a,common,h)["higher_any"],1)
        self.assertEqual(s.metrics(b,common,h)["higher_any"],1)

    def test_hd_ceiling_distinguishes_weak_and_strict(self):
        a=make([[1,0,1,1]])
        b=make([[1,0,0,1]])
        h=np.array([0,0,0,-.1])
        x=s.cross([a,b],np.ones(4,bool),h)
        self.assertEqual(x["all_strict_including_hd_any"],0)
        self.assertEqual(x["hd_tied_others_strict_any"],1)
        self.assertEqual(x["weak_dominance_any"],3)
        self.assertEqual(x["pareto_any"],2)
        self.assertEqual(x["all_systems_tied_some_variant"],1)

    def test_cartesian_extrema_match_literal_combinations(self):
        rng=np.random.default_rng(34)
        arms=[rng.choice([-1.,-.25,0,.25,1.],size=(k,40)) for k in (3,4,2)]
        h=rng.choice([-.5,0,.25],size=40);common=np.arange(40)%7!=0
        e=[make(a) for a in arms]
        x=s.cross(e,common,h)
        cases=[np.stack(q) for q in product(*arms)]
        check={"non_hd_all_strict":[(q>s.EPS).all(axis=0) for q in cases],
               "all_strict_including_hd":[(h>s.EPS)&(q>s.EPS).all(axis=0) for q in cases],
               "hd_tied_others_strict":[(np.abs(h)<=s.EPS)&(q>s.EPS).all(axis=0) for q in cases],
               "weak_dominance":[(h>=-s.EPS)&(q>=-s.EPS).all(axis=0) for q in cases],
               "pareto":[(h>=-s.EPS)&(q>=-s.EPS).all(axis=0)&((h>s.EPS)|(q>s.EPS).any(axis=0)) for q in cases],
               "hd_plus_each_higher":[(h+q>2*s.EPS).all(axis=0) for q in cases],
               "equal_family_higher":[(h+q.sum(axis=0))/4>s.EPS for q in cases],
               "equal_family_ge":[(h+q.sum(axis=0))/4>=-s.EPS for q in cases]}
        for k,v in check.items():
            self.assertEqual(x[k+"_any"],int((common&np.any(v,axis=0)).sum()),k)
            self.assertEqual(x[k+"_all"],int((common&np.all(v,axis=0)).sum()),k)
        ties=[(np.abs(h)<=s.EPS)&(np.abs(q)<=s.EPS).all(axis=0) for q in cases]
        self.assertEqual(x["all_systems_tied_some_variant"],int((common&np.any(ties,axis=0)).sum()))
        self.assertEqual(x["all_systems_tied_every_variant"],int((common&np.all(ties,axis=0)).sum()))

    def test_unknown_is_not_lower_or_tied(self):
        a=make([[0,1,-1],[1,1,1]],[[1,1,1],[0,1,1]])
        self.assertFalse(a.known[0])
        x=s.metrics(a,np.ones(3,bool),np.zeros(3))
        self.assertEqual(x["rows"],2)
        self.assertEqual(x["equal_any"],0)
        self.assertEqual(x["higher_any"],2)
        with self.assertRaises(ValueError):a.add("1",np.ones(3),np.ones(3,bool))

    def test_western_alternatives_not_double_weighted(self):
        p=make([[.5,0,0]]);l=make([[-.5,0,1]])
        a=s.group_options({"ptolemy_blend":p,"lilly":l})
        np.testing.assert_allclose(a.lo,[-.5,0,0])
        np.testing.assert_allclose(a.hi,[.5,0,1])
        self.assertTrue(a.any_tie[2])
        x=s.cross([a,make([[0,0,0]]),make([[0,0,0]])],np.ones(3,bool),np.zeros(3))
        self.assertEqual(x["equal_family_higher_any"],2)
        self.assertEqual(x["equal_family_higher_all"],0)

if __name__=="__main__":unittest.main()
