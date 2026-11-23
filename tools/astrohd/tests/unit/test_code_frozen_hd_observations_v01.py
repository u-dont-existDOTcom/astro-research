import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
from code_frozen_hd_observations_v01 import code

def mapping(i,q,s,c=()):
    return {"mapping_id":i,"question_ids":[q],
        "predicted_response":{"support_answer_tokens":list(s)},
        "contradiction_rule":{"answer_tokens":list(c)} if c else None}

class TestExactResponses(unittest.TestCase):
    def test_support_contra_missing_neutral(self):
        rows=[mapping("A","Q",["yes"],["no"]),
              mapping("B","Q",["no"],["yes"]),
              mapping("C","Q",["other"]),
              mapping("D","R",["yes"])]
        out=code(rows,{"Q":"yes"})
        self.assertEqual([x["observation"] for x in out.values()],[1,-1,None,None])
        self.assertEqual(out["C"]["status"],"UNMAPPED_OR_NEUTRAL_RESPONSE")
        self.assertEqual(out["D"]["status"],"NO_RESPONSE")
    def test_no_inference_from_prose(self):
        r=code([mapping("A","Q",["yes"])],{"Q":"Yes, mostly."})
        self.assertIsNone(r["A"]["observation"])
    def test_conflicting_tokens_refused(self):
        with self.assertRaises(ValueError):code([mapping("A","Q",["yes"],["yes"])],{"Q":"yes"})
    def test_reject_nested_answer_shape(self):
        with self.assertRaises(ValueError):code([],{"Q":{"token":"yes"}})

if __name__=="__main__":unittest.main()
