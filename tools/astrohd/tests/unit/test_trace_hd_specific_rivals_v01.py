import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import trace_hd_specific_rivals_v01 as t

class TestSpecificTrace(unittest.TestCase):
    def test_signed_item_contributions_reproduce_capped_score(self):
        keys=("x","y","z","u")
        domains={"x":"communication","y":"communication","z":"work","u":"relationship"}
        obs={"x":1,"y":-1,"z":1,"u":None}
        bits=(np.array([1,3,7,9,0],np.uint64),np.array([0,0,1,0,2],np.uint64))
        items=t.item_scores(bits,t.item_weights(keys,domains,obs))
        expected=t.s.score(bits,t.q.masks(keys,domains,obs))["score"]
        np.testing.assert_allclose(items.sum(axis=1),expected,rtol=0,atol=1e-15)
        self.assertEqual(items[2,0],0)
        self.assertEqual(items[4,1],.125)
    def test_unobserved_never_contributes(self):
        keys=("a","b")
        domains={"a":"work","b":"motivation"}
        self.assertEqual(t.item_weights(keys,domains,{"a":None,"b":None}).tolist(),[0.,0.])
        z=t.item_scores((np.array([3],np.uint64),np.array([0],np.uint64)),np.zeros(2))
        np.testing.assert_array_equal(z,np.zeros((1,2)))

if __name__=="__main__":unittest.main()
