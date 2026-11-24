import sys
import unittest
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_multitradition_cross_coding_v01 as c

def store(rows):
    x=c.Store(len(rows[0]))
    for i,r in enumerate(rows):x.add(str(i),np.array(r,dtype=float),np.ones(len(r),bool))
    return x

class TestBothCodings(unittest.TestCase):
    def test_disjoint_variant_success_not_same_variant(self):
        a=store([[1,1,0],[0,0,1]])
        b=store([[0,1,0],[1,0,0]])
        x=c.both(a,b)
        np.testing.assert_array_equal(x.hi,[0,1,0])
        np.testing.assert_array_equal(x.lo,[0,0,0])
        np.testing.assert_array_equal(x.any_tie,[False,True,True])

    def test_aligned_variant_and_family_intersection(self):
        a=store([[1,1,1],[-1,1,1]])
        b=store([[-1,1,1],[1,1,1]])
        e=[{k:a for k in c.m.PRIMARY},{k:b for k in c.m.PRIMARY}]
        counts=defaultdict(Counter);idx=defaultdict(list)
        c.compare(e,np.ones(3,bool),np.array([10,20,30]),counts,idx)
        name="ptolemy_blend + lilly + vedic_union + chinese_union"
        self.assertEqual(counts[name]["strict_any"],2)
        self.assertEqual(counts[name]["strict_all"],2)
        self.assertEqual(idx[name+"|strict_any"],[20,30])

    def test_missing_variant_is_failure(self):
        with self.assertRaises(ValueError):c.both(store([[1]]),store([[1],[0]]))

if __name__=="__main__":unittest.main()
