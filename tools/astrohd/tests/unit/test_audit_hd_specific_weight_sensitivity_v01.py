import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import audit_hd_specific_weight_sensitivity_v01 as a

class TestWeightSensitivity(unittest.TestCase):
    def test_preserves_available_mass(self):
        keys=("x","y","z","u")
        domains={"x":"communication","y":"communication","z":"relationship","u":"work"}
        obs={"x":1,"y":-1,"z":1,"u":None}
        old=a.weighted_masks(keys,domains,obs,"equal_domains")
        new=a.weighted_masks(keys,domains,obs,"equal_items_same_mass")
        self.assertAlmostEqual(sum((int(p)|int(m)).bit_count()*w for p,m,w in old),.5)
        self.assertAlmostEqual(sum((int(p)|int(m)).bit_count()*w for p,m,w in new),.5)
        self.assertAlmostEqual(new[0][2],1/6)
        self.assertAlmostEqual(new[3][2],1/6)
    def test_every_omission_keeps_other_weights(self):
        keys=("x","y","z","u");domains=dict(zip(keys,a.q.DOMAINS))
        obs=dict.fromkeys(keys,1)
        self.assertEqual(len(a.POLICIES),6)
        for i,d in enumerate(a.q.DOMAINS):
            m=a.weighted_masks(keys,domains,obs,"omit_"+d)
            self.assertEqual([w for p,n,w in m],[0. if i==j else .25 for j in range(4)])
        with self.assertRaises(ValueError):a.weighted_masks(keys,domains,obs,"favorite")
if __name__=="__main__":unittest.main()
