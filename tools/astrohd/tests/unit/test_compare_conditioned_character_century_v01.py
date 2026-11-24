import sys,unittest
from collections import Counter,defaultdict
from itertools import product
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_conditioned_character_century_v01 as s
import compare_planet_character_condition_pilot_v01 as p

class TestConditionedGrid(unittest.TestCase):
    def test_condition_truth_table_matches_pilot(self):
        for pol in s.POLICIES:
            a=s.condition_lut(pol)
            for own,match,opp,contrary in product((False,True),repeat=4):
                if match and opp:continue
                x=p.condition(own,match,opp,contrary,pol)
                self.assertEqual(a[8*own+4*match+2*opp+contrary],s.UNKNOWN if x is None else x)

    def test_vectorized_matches_scalar_conditions(self):
        rng=np.random.default_rng(2026)
        lon=rng.uniform(0,360,(20,7));alt=rng.uniform(-80,80,20);alt[0]=0
        out=s.all_conditions(lon,alt)
        for pol in s.POLICIES:
            for i,k in product(range(len(lon)),range(7)):
                v=p.place_condition(lon[i:i+1],alt[i:i+1],k,pol)
                self.assertEqual(out[pol][i,k],s.UNKNOWN if v is None else v)

    def test_mapped_zero_is_not_missing(self):
        reg=s.s.load_registry()
        a,n,_=s.score_table(reg,{"work":1,"firmness":-1,"reflection":None})
        sat=s.s.BODIES.index("Saturn")
        self.assertEqual(a[0,0,sat],0)
        self.assertEqual(n[0,0,sat],2)
        self.assertEqual(n[s.UNKNOWN,0,sat],0)

    def test_fixed_place_admission_and_bounds(self):
        lead=np.array([2,3,-1]);possible=np.zeros((3,7),bool)
        possible[0,[2,3]]=True;possible[1,[3]]=True;possible[2,[2,3]]=True
        cond=np.full((3,7),s.UNKNOWN,np.int8);cond[:,2]=0;cond[0,3]=1
        t=np.zeros((3,2,7));n=np.zeros((3,2,7),np.int8)
        t[0,0,2]=.5;t[1,0,3]=-.5;n[0,0,2]=2;n[1,0,3]=3
        sign=np.zeros((3,7));sign[:,2]=1;sign[:,3]=-1
        x=s.fixed_place(lead,possible,cond,t,n,sign,0)
        np.testing.assert_array_equal(x["mapped"],[2,0,0])
        np.testing.assert_allclose(x["character"],[.5,0,0])
        np.testing.assert_allclose(x["sign"],[1,-1,0])
        np.testing.assert_allclose(x["character_lo"],[-.5,0,0])
        np.testing.assert_allclose(x["character_hi"],[.5,0,.5])
        np.testing.assert_allclose(x["sign_lo"],[-1,-1,-1])
        np.testing.assert_allclose(x["sign_hi"],[1,0,1])

    def test_family_cap_and_outer_bounds(self):
        m={"character":np.array([1.]),"sign":np.array([1.]),
           "character_lo":np.array([0.]),"character_hi":np.array([1.]),
           "sign_lo":np.array([0.]),"sign_hi":np.array([1.])}
        l={k:a.copy() for k,a in m.items()}
        v=s.model_arrays(m,l,np.array([1.]),np.array([1.]))
        for k in ("joint_character","joint_sign","joint_blend"):
            self.assertEqual(v[k][0],1.)
        self.assertEqual(v["joint_blend_lo"][0],.5)
        self.assertEqual(v["joint_blend_hi"][0],1.)
        m["character"]=np.array([-1.]);m["character_lo"]=np.array([-1.])
        v=s.model_arrays(m,l,np.array([1.]),np.array([1.]))
        self.assertEqual(v["joint_blend"][0],.75)

    def test_full_historical_policy_accounting(self):
        reg=s.s.load_registry()
        table,ct,_=s.score_table(reg,{"work":1,"firmness":1,"leadership":-1,"compassion":1})
        sign={"mercury_fixed":1,"moon_bicorporeal":1}
        lon=np.array([[20.,45.,95.,5.,80.,155.,300.],[20.,150.,50.,5.,80.,155.,300.],[5.,10.,20.,40.,80.,180.,300.]])
        alt=np.array([20.,0.,-20.])
        ref=s.reference(lon[:1],alt[:1],.5,table,ct,sign)
        co=defaultdict(Counter)
        s.scan(lon,alt,np.array([0,1,-1]),[np.array([.5,.25])],[{"table":table,"ct":ct,"signobs":sign}],[ref],[co])
        s.validate(co,ref,2)
        self.assertEqual(len(ref),128)
        for tag in ref:
            self.assertEqual(sum(co[tag+"|joint_blend"].values()),2)
            self.assertGreaterEqual(co[tag+"|joint_blend"]["tied"],1)
            self.assertGreaterEqual(co[tag+"|matched_joint_blend"]["tied"],1)
            self.assertEqual(co[tag+"|bounds_joint_blend"]["certainly_higher"],0)
        self.assertGreaterEqual(co["across_all|joint_blend"]["tied_every"],1)
        tag=next(t for t in ref if "|phase_envelope|" in t)
        co[tag+"|joint_character"]["tied"]+=1
        with self.assertRaises(ValueError):s.validate(co,ref,2)

if __name__=="__main__":unittest.main()
