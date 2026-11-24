import sys
import unittest
from pathlib import Path
from itertools import product
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_saravali_lunar_solar_century_v01 as s

class TestLunarSolar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg,cls.prior,cls.shared=s.load_map()
        cls.rules=cls.reg["rules"]
        cls.edges=s.old.rule_edges(cls.prior["rules"])

    def active(self,signs,cause="exact_cause",scope="exclude_moon_both"):
        row=s.active_rules(np.array([signs]),self.rules,cause,scope)[0]
        return [q for q,a in zip(self.rules,row,strict=True) if a]

    def test_complete_source_map(self):
        self.assertEqual(len(self.rules),48)
        self.assertEqual(sum(len(r["direct"]) for r in self.rules),32)
        self.assertEqual(sum(len(r["proxy"]) for r in self.rules),64)
        self.assertEqual(len(s.ARMS),80)
        self.assertEqual(sum(r["family"]=="moon_sign" for r in self.rules),12)

    def test_exclusive_lunar_categories_and_named_opposite_pair(self):
        # Moon at 0, Mercury after, Mars before, other bodies far away.
        a=self.active([4,0,1,5,11,7,8])
        lunar=[r["selector"] for r in a if r["family"]=="lunar_yoga"]
        self.assertEqual(len(lunar),2)
        self.assertTrue(all(r["yoga"]=="durudhura" for r in lunar))
        self.assertIn({"yoga":"durudhura","opposite_pair":["Mars","Mercury"]},lunar)
        # Additional Venus before rules out exact two-body cause only.
        signs=[4,0,1,11,11,7,8]
        exact=[r["selector"] for r in self.active(signs) if r["family"]=="lunar_yoga"]
        inclusive=[r["selector"] for r in self.active(signs,"inclusive_causes") if r["family"]=="lunar_yoga"]
        self.assertEqual(exact,[{"yoga":"durudhura"}])
        self.assertGreater(len(inclusive),len(exact))

    def test_luminaries_and_solar_moon_exclusion(self):
        signs=[0,11,4,5,6,7,8]
        a=[r for r in self.active(signs) if r["family"]=="solar_yoga"]
        self.assertEqual(a,[])
        a=[r["selector"] for r in self.active(signs,scope="allow_moon_twelfth") if r["family"]=="solar_yoga"]
        self.assertEqual(a,[{"yoga":"vasi"}])
        # Sun alone adjacent to Moon does not create lunar yoga.
        a=[r for r in self.active([1,0,4,5,6,7,8]) if r["family"]=="lunar_yoga"]
        self.assertEqual(a,[])
        # If both solar sides present, use only Ubhayachari.
        a=[r["selector"] for r in self.active([0,6,11,1,4,7,8]) if r["family"]=="solar_yoga"]
        self.assertEqual(a,[{"yoga":"ubhayachari"}])

    def test_bitset_union_caps_and_conflicts(self):
        p=np.array([1,1,0],np.uint64)
        n=np.array([0,1,1],np.uint64)
        obs=[(np.uint64(1),np.uint64(0),.5)]
        z=s.score((p,n),obs)
        np.testing.assert_allclose(z["score"],[.5,0,-.5])
        np.testing.assert_allclose(z["lo"],[0,-.5,-.5])
        np.testing.assert_allclose(z["hi"],[.5,.5,0])
        np.testing.assert_array_equal(z["conflicting_items"],[0,1,0])
        combined=s.union((p,n),(p,n))
        for a,b in zip(combined,(p,n)):np.testing.assert_array_equal(a,b)

    def test_prior_counts_bitset_equivalent_to_original_compiler(self):
        rng=np.random.default_rng(11)
        signs=rng.integers(0,12,(120,7))
        signs[5:10]=signs[0]
        lon=signs*30.+5.
        graph,_=s.old.graph_from_signs(lon,np.zeros(len(signs)))
        evidence={"learning":1,"eloquence":1,"leadership":-1,"work":1,"pleasure":-1}
        t,obs=s.make_tables(self.reg,self.prior,self.shared,evidence)
        v=s.compute(signs,graph,self.reg,self.edges,t)
        self.assertEqual(len(v),42)
        prior=s.old.evaluate_graphs(graph,self.edges,s.old.observation_tables(self.prior,self.shared,evidence))
        for mode in s.MAPS:
            old=prior["both_inclusive|"+mode]
            new=s.score(v["prior|"+mode],obs)
            for k in ("score","lo","hi","known_items","conflicting_items"):
                np.testing.assert_allclose(old[k],new[k])
        for cause,scope,mode in product(s.CAUSES,s.SCOPES,s.MAPS):
            tags=[v["|".join((cause,scope,mode,f))] for f in s.FAMILIES[:3]]
            expected=s.union(*tags,v["prior|"+mode])
            actual=v["|".join((cause,scope,mode,"all_union"))]
            for a,b in zip(expected,actual,strict=True):np.testing.assert_array_equal(a,b)

if __name__=="__main__":unittest.main()
