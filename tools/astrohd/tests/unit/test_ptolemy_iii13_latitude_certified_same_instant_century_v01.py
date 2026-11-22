"""Source-neutral synthetic tests for the original I.24 bodily latitude screen."""
import sys
from pathlib import Path
import unittest
import numpy as np
S=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(S))
import ptolemy_iii13_latitude_certified_same_instant_century_v01 as m

class LatitudeWitness(unittest.TestCase):
    def test_same_side_excludes_ecliptic_and_opposite(self):
        a=np.array([2.,-0.2,0.,1.,-1.,np.nan])
        b=np.array([0.3,-3.,1.,-1.,1.,4.])
        self.assertEqual(m.same_ecliptic_side(a,b).tolist(),
                         [True,True,False,False,False,False])
    def test_conjunction_requires_latitude(self):
        selected=np.array([1,1,1,1],dtype=bool)
        # 0=body Mercury + Moon ray (qualifies), 1=body Mercury + Moon ray
        # but opposite lat; 2=two rays; 3=Moon body + Mercury ray.
        mr=np.array([70.,70.,1.,1.])
        lr=np.array([-1.,-1.,-1.,70.])
        mb=np.array([0.2,0.2,70.,70.])
        lb=np.array([70.,70.,70.,0.1])
        ml=np.array([True,False,False,False])
        ll=np.array([False,False,False,True])
        velocity=np.ones(4)
        r=m.classify_dual(selected,mr,lr,mb,lb,ml,ll,velocity,3)
        self.assertEqual(r["possible"].tolist(),[True,True,True,True])
        self.assertEqual(r["verified"].tolist(),[True,False,True,True])
        self.assertEqual(r["nonbody"].tolist(),[False,False,True,False])
        self.assertEqual(r["body_latitude_unsupported_or_opposite"].tolist(),[False,True,False,False])
        self.assertTrue(r["apply_by_zodiacal_precedence"][0])
    def test_direction_disagreement_is_preserved_not_relabelled(self):
        a=m.classify_dual(np.array([True,True]), np.ones(2),np.array([-1.,1.]),
              np.ones(2)*45,np.ones(2)*45,
              np.ones(2,dtype=bool),np.ones(2,dtype=bool),
              np.array([-1.,1.]),3)
        self.assertEqual(a["apply_by_zodiacal_precedence"].tolist(),[True,False])
        self.assertEqual(a["apply_by_relative_velocity_proxy"].tolist(),[False,False])
        self.assertEqual(a["direction_disagreement"].tolist(),[True,False])
    def test_bad_shapes_refused(self):
        with self.assertRaises(ValueError):
            m.classify_dual(np.ones(2,dtype=bool),np.ones(1),*([np.ones(2)]*6),3)
        with self.assertRaises(ValueError):
            m.same_ecliptic_side(np.array([1.]),np.array([1.,2.]))
    def test_condition_uses_four_independent_historical_variants(self):
        p=np.tile([0.,120.,40.,55.,190.,230.,290.,0.],(7,1))
        alt=np.ones(7)*10.
        g=m.conditional_all_four_common_leader(p,alt)
        self.assertEqual(g.shape,(7,))
        self.assertTrue(np.all((g>=-1)&(g<=6)))

if __name__=="__main__": unittest.main()
