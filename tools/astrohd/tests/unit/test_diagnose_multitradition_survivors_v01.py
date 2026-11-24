import sys
import unittest
from collections import Counter
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import diagnose_multitradition_survivors_v01 as d
import trace_multitradition_survivor_items_v01 as t

class TestSurvivorDiagnostics(unittest.TestCase):
    def test_rational_capture_preserves_supported_weights(self):
        scale=d.rational_scale([13,8])
        a=d.Capture(3,scale)
        z=np.array([1/(4*13),-1/(2*8*7),1/8])
        a.add("one",z,np.ones(3,bool))
        np.testing.assert_allclose(a.values["one"]/scale,z,atol=1e-15,rtol=0)
        with self.assertRaises(ValueError):
            a.add("two",np.array([np.sqrt(2),0.,0.]),np.ones(3,bool))

    def test_chunk_dominance_matches_brute_force(self):
        rng=np.random.default_rng(5)
        x=rng.integers(-100,100,(80,55),dtype=np.int32)
        for i in range(10):
            target=x[i]
            np.testing.assert_array_equal(d.dominating(x,target),np.flatnonzero((x>=target).all(axis=1)))
        target=np.full(55,-100)
        eligible=np.arange(80)%3==0
        np.testing.assert_array_equal(d.dominating(x,target,eligible),np.flatnonzero(eligible))

    def test_near_and_distant_control_self_and_strict(self):
        core=np.array([[0,1],[1,1],[1,0],[1,1],[0,1]])
        extra=np.array([[0],[1],[1],[-1],[0]])
        ix=np.array([10,50,70,1000,2000])
        r=[Counter()]
        d.update_controls(core,extra,core[:1],extra[:1],ix,ix[:1],r)
        self.assertEqual(r[0]["core_weak"],4)
        self.assertEqual(r[0]["core_pareto"],2)
        self.assertEqual(r[0]["core_weak_outside_24h"],2)
        self.assertEqual(r[0]["all_weak"],3)
        self.assertEqual(r[0]["all_pareto"],1)
        self.assertEqual(r[0]["all_weak_outside_24h"],1)

    def test_same_arm_both_codings_and_all_variant_scope(self):
        a=np.array([[1,0],[1,1],[0,0]])
        b=np.array([[0,1],[1,0],[0,0]])
        mats={k:(a,b) for k in d.CORE}
        np.testing.assert_array_equal(d.rival_mask(mats),[False,True,False])
        np.testing.assert_array_equal(d.universal(mats,d.CORE),[True,True,True])
        mats["extra"]=(np.array([[-1],[0],[0]]),np.zeros((3,1),int))
        np.testing.assert_array_equal(d.universal(mats,tuple(mats)),[False,True,True])

    def test_eastern_item_decomposition_caps_and_cancels(self):
        pos=np.array([1,3,0],np.uint64);neg=np.array([0,1,2],np.uint64)
        w=np.array([.25,-.125])
        a=t.bits_items((pos,neg),w)
        np.testing.assert_allclose(a,[[.25,0],[0,-.125],[0,.125]])
        t.verify_sum(a,np.array([.25,-.125,.125]))
        with self.assertRaises(ValueError):t.verify_sum(a,np.zeros(3))

    def test_trace_counts_all_shared_wins_without_switching_arms(self):
        r=t.Trace(2,("x","y"))
        # Candidate 0 wins arm one under both codings with a loss on y;
        # candidate 1 wins only in one coding. A second arm admits it.
        a=np.array([[0.,0.],[.3,-.1],[.2,0.]])
        b=np.array([[0.,0.],[.2,-.1],[-.1,0.]])
        r.add("one",[a,b],[a.sum(axis=1),b.sum(axis=1)],[0,0])
        a=np.array([[0.,0.],[-.1,0.],[0.,.2]])
        r.add("two",[a,a],[a.sum(axis=1),a.sum(axis=1)],[0,0])
        out=r.finish()
        self.assertEqual(out["shared_winning_arm_count_histogram"],{"1":2})
        self.assertEqual(out["profiles"][0]["x"]["rival_rows_gain_any"],1)
        self.assertEqual(out["profiles"][0]["y"]["rival_rows_loss_any"],1)
        self.assertAlmostEqual(out["profiles"][0]["x"]["mean_score_delta_per_rival"],.15)
if __name__=="__main__":unittest.main()
