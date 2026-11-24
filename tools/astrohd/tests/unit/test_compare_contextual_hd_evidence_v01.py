import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_contextual_hd_evidence_v01 as c

def row(i,cluster):
    return {"mapping_id":i,"dependency_cluster":cluster}

class TestContextualEvidence(unittest.TestCase):
    def test_existing_observation_and_contextual_cluster_are_separate(self):
        rows=[row("profile","profile"),row("context","social")]
        a=np.array([[1,1],[1,0],[0,1],[0,0]],np.int64)
        old={"profile":1};new={**old,"context":1}
        o,n,d=c.compare_scores(a,0,rows,old,new,np.array([2,3,4,5]))
        np.testing.assert_array_equal(o>=0,[True,True,False,False])
        np.testing.assert_array_equal(n>=0,[True,False,False,False])
        self.assertEqual(d["old_ranks"],{"higher":0,"tied":5,"lower":9})
        self.assertEqual(d["new_ranks"],{"higher":0,"tied":2,"lower":12})
        self.assertEqual(d["new_reference_score"],1)
        self.assertEqual(old,{"profile":1})

    def test_context_does_not_always_shrink_eligibility(self):
        rows=[row("profile","profile"),row("context","social")]
        a=np.array([[1,0],[0,1],[1,1]],np.int64)
        o,n,d=c.compare_scores(a,0,rows,{"profile":1},{"profile":1,"context":1},np.ones(3,np.int64))
        self.assertTrue(np.any((n>=0)&(o<0)))
        self.assertEqual(d["new_ranks"]["higher"],1)

    def test_exact_survivor_clock_identity_and_unknown_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/"shards").mkdir()
            f=p/"shards"/"part.bin"
            np.array([0,1,0,-1,2],dtype="<i4").tofile(f)
            H={"shards":[{"count":5,"index_first":0,"file":"part.bin","sha256":c.b.digest(f)}]}
            a=SimpleNamespace(join=p)
            with patch.object(c.g,"N",5):
                r=c.filter_sets(a,H,np.array([0,1,0]),np.array([True,False]),{"rivals":[0,1,2,4],"empty":[]})
                self.assertEqual(r,{"rivals":[0,2,4],"empty":[]})
                with self.assertRaises(ValueError):
                    c.filter_sets(a,H,np.array([0,1,0]),np.array([True,False]),{"unknown":[3]})
                with self.assertRaises(ValueError):
                    c.filter_sets(a,H,np.array([0,1,0]),np.array([True,False]),{"duplicate":[1,1]})

if __name__=="__main__":unittest.main()
