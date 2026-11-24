import copy,sys,unittest
from collections import Counter,defaultdict
from pathlib import Path
from itertools import product
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_planet_character_century_v01 as s

class TestCharacter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg=s.load_registry()
        cls.obs={"reflection":1,"work":1,"leadership":-1,"anger":-1,
                 "compassion":1,"deception":None,"faith_practice":1,
                 "firmness":1,"deliberation":1,"solitude":1}
        cls.a,cls.den,cls.trace=s.tables(cls.reg,cls.obs)
        cls.m,cls.l=s.arm_tables(cls.a)
        cls.env=s.envelopes(cls.m,cls.l)

    def test_all_historical_profiles_and_source_clause_conditions(self):
        self.assertEqual(len(s.FIVE),5)
        self.assertEqual(len(self.reg["profiles"]),15)
        self.assertEqual(sum(len(v) for v in self.reg["domains"].values()),37)
        self.assertEqual(sum(len(x[c]) for x in self.reg["profiles"] for c in s.CONDITIONS),155)
        self.assertEqual(sum(x["source_relation"]=="single ruler" for x in self.reg["profiles"]),5)
        self.assertEqual(sum(x["source_relation"]=="allied" for x in self.reg["profiles"]),10)
        bad=copy.deepcopy(self.reg);bad["profiles"].pop()
        with self.assertRaises(ValueError):s.validate(bad)
        bad=copy.deepcopy(self.reg);bad["profiles"][0]["opposite"]={}
        with self.assertRaises(ValueError):s.validate(bad)

    def test_counterevidence_and_favorable_not_moral_good(self):
        mars=s.BODIES.index("Mars")
        self.assertLess(self.a[0,1,mars,mars],0) # negative leadership/anger in dignified Mars
        v=self.trace["Mars/Mars"]["dignified"]["sensory_affective"]
        self.assertEqual(v["contributions"]["anger"],-1)
        self.assertEqual(v["contributions"]["leadership"],-1)
        self.assertNotIn("deception",v["contributions"])
        self.assertEqual(self.den,[5,4])

    def test_fixed_denominator_symmetry_and_luminary_abstention(self):
        for body in ("Moon","Sun"):
            n=s.BODIES.index(body)
            self.assertTrue((self.a[:,:,n,:]==0).all())
            self.assertTrue((self.a[:,:,:,n]==0).all())
        self.assertTrue(np.array_equal(self.a,self.a.transpose(0,1,3,2)))
        self.assertTrue((self.a[:,:,s.U,:]==0).all())
        self.assertTrue(np.all(np.abs(self.a)<=1))
        empty,den,_=s.tables(self.reg,{})
        self.assertEqual(den,[0,0]);self.assertTrue((empty==0).all())

    def test_separate_faculties_and_assumed_alliance(self):
        sat=s.BODIES.index("Saturn");mer=s.BODIES.index("Mercury")
        k="separate_dignified_opposite"
        self.assertEqual(self.m[k][sat,mer],self.a[0,0,sat,sat])
        self.assertEqual(self.l[k][sat,mer],self.a[1,1,mer,mer])
        k="assumed_alliance_dignified"
        self.assertEqual(self.m[k][sat,mer],self.a[0,0,sat,mer])
        self.assertEqual(self.l[k][sat,mer],self.a[0,1,sat,mer])
        # No asserted alliance when the other place is unresolved or a luminary.
        self.assertEqual(self.m[k][sat,s.U],0)
        self.assertEqual(self.l[k][sat,s.U],0)

    def test_envelope_contains_every_candidate_condition_and_abstention(self):
        rng=np.random.default_rng(4)
        for _ in range(100):
            i,j=map(int,rng.integers(0,128,2))
            left=[a for a in range(7) if i&(1<<a)]+[s.U]
            right=[a for a in range(7) if j&(1<<a)]+[s.U]
            for family,(lo,hi) in self.env.items():
                self.assertLessEqual(lo[i,j],0)
                self.assertGreaterEqual(hi[i,j],0)
                for x,y,k in product(left,right,[a for a in s.ARMS if a.startswith(family)]):
                    t=(self.m[k][x,y]+self.l[k][x,y])/2
                    self.assertLessEqual(lo[i,j]-1e-12,t)
                    self.assertGreaterEqual(hi[i,j]+1e-12,t)

    def test_64_historical_variants_exact_and_bounded_scores(self):
        lon=np.array([[20,45,95,5,80,155,300],[20,150,50,5,80,155,300]])
        alt=np.array([20.,0.]);h=np.array([.5,.25])
        count=0
        for tag,gm,pm,gl,pl in s.branches(lon,alt):
            count+=1
            out=s.score_arrays(gm,pm,gl,pl,h,self.m,self.l,self.env)
            self.assertEqual(gm[1],-1);self.assertEqual(gl[1],-1)
            for k in s.ARMS:
                a=out[k];env=out[("separate" if k.startswith("separate") else "assumed_alliance")+"_envelope"]
                self.assertTrue((a["joint"]>=env["joint_lo"]-1e-12).all())
                self.assertTrue((a["joint"]<=env["joint_hi"]+1e-12).all())
                self.assertEqual(a["western"][1],0)
        self.assertEqual(count,64)

    def test_phase_envelope_tag_is_an_exact_score_scenario(self):
        co={}
        for t in ("branch|geometry","branch|phase_envelope"):
            for a in s.ARMS:
                for k in ("western","joint"):
                    co[t+"|"+a+"|"+k]=Counter(higher=1,tied=2,lower=3)
            for a in ("separate_envelope","assumed_alliance_envelope"):
                for k in ("western","joint"):
                    co[t+"|"+a+"|"+k]=Counter(certainly_higher=1,could_equal_or_exceed=4,certainly_lower=2)
        s.validate_counts(co,6,2)
        co.pop("branch|phase_envelope|separate_dignified_dignified|joint")
        with self.assertRaises(ValueError):s.validate_counts(co,6,2)

    def test_unregistered_or_nonbinary_observation_rejected(self):
        with self.assertRaises(ValueError):s.tables(self.reg,{"unknown":1})
        with self.assertRaises(ValueError):s.tables(self.reg,{"work":True})

if __name__=="__main__":unittest.main()
