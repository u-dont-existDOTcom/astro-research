import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import audit_expanded_hd_arm_robustness_v01 as a

class TestAcrossHD(unittest.TestCase):
    def test_groups(self):
        self.assertEqual({k:len(v) for k,v in a.arm_groups().items()},
                         {"all_point_arms":40,"all_blends":20,"all_archetype_only":20,
                          "full_union_blends":6,"full_union_archetypes":6})

    def test_same_row_and_same_arm_both_codings(self):
        x=np.array([[1,1,0,1],[0,1,1,1]])
        y=np.array([[0,1,1,1],[1,1,0,1]])
        z=a.summarize(np.full(4,65535,np.uint16),np.array([True,True,True,False]),x,y)
        self.assertEqual(z["any_HD_arm"]["HD_strict"],1)
        self.assertEqual(z["every_HD_arm"]["all_primary"]["HD_strict_others_strict_any"],1)
        self.assertEqual(z["every_HD_arm"]["all_primary"]["HD_no_lower_others_ge_all"],3)
        y[1,1]=0
        z=a.summarize(np.full(4,65535,np.uint16),np.array([True,True,True,False]),x,y)
        self.assertEqual(z["any_HD_arm"]["HD_strict"],1)
        self.assertEqual(z["every_HD_arm"]["HD_strict"],0)
if __name__=="__main__":unittest.main()
