import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import audit_transfer_observation_coverage_v01 as a

class TestCoverage(unittest.TestCase):
    def test_null_absence_and_negative_observation_are_distinct(self):
        z=a.compare_items({"a":1,"b":-1,"c":None},{"b":1,"c":-1,"d":None},("a","b","c","d","e"))
        self.assertEqual(z["development_observed"],2)
        self.assertEqual(z["transfer_observed"],2)
        self.assertEqual(z["common_observed"],1)
        self.assertEqual(z["development_only"],["a"])
        self.assertEqual(z["transfer_only"],["c"])
        self.assertEqual(z["opposite_sign_common_items"],["b"])
        self.assertEqual(z["both_unobserved"],["d","e"])

    def test_reject_wrong_version_or_boolean(self):
        with self.assertRaises(ValueError):a.compare_items({"other":1},{},{"a"})
        with self.assertRaises(ValueError):a.compare_items({"a":True},{},{"a"})

    def test_family_namespace_preserved(self):
        x={k:{"same":1} for k in a.FAMILIES}
        y={k:{"same":None} for k in a.FAMILIES}
        y["western"]["same"]=-1
        z=a.audit(x,y,{k:{"same"} for k in a.FAMILIES})
        self.assertEqual(z["western"]["common_observed"],1)
        self.assertEqual(z["hd"]["common_observed"],0)
        with self.assertRaises(ValueError):a.audit(x,y,{"hd":{"same"}})

if __name__=="__main__":unittest.main()
