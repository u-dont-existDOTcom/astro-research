"""Invented-data regression tests for fixed model selection and transfer."""
import sys
import importlib.util
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import select_fixed_transfer_models_v01 as s

def model(family,tag,higher,tied):
    return {"family":family,"tag":tag,"rank_counts":{"higher":higher,"tied":tied,"lower":s.N-higher-tied},"reference":.5}

class TestSelection(unittest.TestCase):
    def test_rank_end_penalizes_large_tie(self):
        a=model("a","a",0,1000);b=model("b","b",50,10)
        self.assertEqual(s.choose([a,b])["primary"],b)
    def test_tied_models_preserved_before_lexical_choice(self):
        a=model("a","z",30,20);b=model("a","a",30,20);c=model("b","x",20,30)
        self.assertEqual(s.choose([a,b,c])["co_winners"],[c])
        self.assertEqual(s.choose([a,b])["co_winners"],[b,a])
    def test_rank_denominator_and_counts(self):
        s.validate_rank({"higher":1,"tied":2,"lower":s.N-3})
        with self.assertRaises(ValueError):s.validate_rank({"higher":1,"tied":2,"lower":s.N})
        with self.assertRaises(ValueError):s.validate_rank({"higher":-1,"tied":2,"lower":s.N-1})

@unittest.skipUnless(importlib.util.find_spec("hdmatch"),"exact transfer runner uses separately authorized chart engine")
class TestTransfer(unittest.TestCase):
    def test_same_row_not_marginal_rank(self):
        import compare_fixed_transfer_models_v01 as t
        x=np.array([.9,.3,.7,.4,.9]);y=np.array([.3,.9,.7,.4,.9])
        r=t.pair_counts(x,y,.5,.5,np.array([1,1,1,1,0],bool))
        self.assertEqual(r["HD"]["higher"],2)
        self.assertEqual(r["Western"]["higher"],2)
        self.assertEqual(r["strict_both"],1)
        self.assertEqual(r["no_lower_both"],1)
        self.assertEqual(r["equal_mean"]["higher"],3)
    def test_selected_branch_matches_original_full_dispatch(self):
        import compare_fixed_transfer_models_v01 as t
        rng=np.random.default_rng(20261125)
        lon=rng.uniform(0,360,(24,7));alt=rng.uniform(-60,60,24)
        reg=t.pc.load_registry()
        obs={k:(1 if i%3 else -1) for i,k in enumerate(k for d in t.pc.DOMAINS for k in reg["domains"][d])}
        signs={k:1 for k in t.b.WEST_KEYS}
        tab=t.co.score_table(reg,obs)
        for i,(tag,gm,pm,gl,pl) in enumerate(t.pc.branches(lon,alt)):
            if i not in (0,17,43,63):continue
            for policy in t.co.POLICIES:
                cond=t.co.all_conditions(lon,alt)[policy]
                _,_,v=t.co.evaluate(gm,pm,gl,pl,cond,tab[0],tab[1],t.g.vote_arrays(lon,signs),np.zeros(len(lon)))
                for kind in ("character","sign","blend"):
                    actual,_,_=t.selected_west(lon,alt,tag+"|"+policy+"|"+kind,tab,signs)
                    np.testing.assert_allclose(actual,v[kind],rtol=0,atol=1e-14)
if __name__=="__main__":unittest.main()
