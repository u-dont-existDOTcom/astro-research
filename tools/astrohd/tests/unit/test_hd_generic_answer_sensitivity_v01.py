import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import hd_generic_answer_sensitivity_v01 as s

def row(i,q,group,support,contra=()):
    return {"mapping_id":i,"question_ids":[q],"dependency_cluster":group,
            "predicted_response":{"support_answer_tokens":list(support)},
            "contradiction_rule":{"answer_tokens":list(contra)}}

class TestGenericAnswerSensitivity(unittest.TestCase):
    def test_same_question_cannot_have_inconsistent_complementary_answers(self):
        rows=[row("a","Q","energy",["renew"],["deplete"]),
              row("b","Q","energy",["deplete"],["renew"])]
        opts=s.options(rows,["Q"])
        self.assertEqual(len(opts[0]),3)
        self.assertEqual({x[1] for x in opts[0]},{(None,None),(1,-1),(-1,1)})

    def test_equivalent_tokens_count_once(self):
        r=[row("a","Q","group",["yes","always"])]
        opts=s.options(r,["Q"])
        self.assertEqual(len(opts[0]),2)
        self.assertEqual(opts[0][0],(None,(None,)))

    def test_cluster_numerators_match_literal_means(self):
        r=[row("a","A","one",["yes"]),row("b","B","one",["yes"]),
           row("c","C","two",["yes"]),row("d","D","two",["yes"]),
           row("e","E","two",["yes"])]
        a=np.array([[1,1,1,0,1],[0,1,0,1,1],[1,0,1,1,0]],np.int64)
        o={"a":1,"b":-1,"c":1,"d":1,"e":-1}
        n,den=s.score_numerators(a,r,o)
        expected=((a[:,0]-a[:,1])/2+(a[:,2]+a[:,3]-a[:,4])/3)/2
        np.testing.assert_allclose(n/den,expected,rtol=0,atol=1e-15)
        n,den=s.score_numerators(a,r,{"a":None,"b":None})
        np.testing.assert_array_equal(n,0)
        self.assertEqual(den,1)

    def test_weighted_ranks_include_reference_and_all_rivals(self):
        r=[row("a","A","profile",["yes"]),row("b","B","energy",["yes"],["no"])]
        a=np.array([[1,0],[1,1],[0,1]],np.int64)
        o=[{"a":1},{"a":1}]
        v=s.evaluate(a,0,r,o,["B"],s.options(r,["B"]),np.array([2,3,7]),np.array([1,2,0]))
        self.assertEqual(len(v),3)
        self.assertEqual(v[0]["both_codings"]["prior_rivals_equal"],3)
        yes=next(x for x in v if x["hypothetical_tokens"]["B"]=="yes")
        self.assertEqual(yes["both_codings"]["full_grid_strictly_higher"],3)
        self.assertEqual(yes["both_codings"]["prior_rivals_strictly_higher"],2)
        no=next(x for x in v if x["hypothetical_tokens"]["B"]=="no")
        self.assertEqual(no["both_codings"]["prior_rivals_no_lower"],1)

    def test_version_bound_question_packet_and_immutable_baseline(self):
        q={"id":"Q","domain":"energy","prompt":"Original question","response_format":"text",
           "followups":["An example?"],"minimum_evidence":"one example"}
        bank={"questions":[q]}
        packet={"source_question_bank_sha256":"original",
                "questions":[{**q,"qualified_id":"question_bank_v1::Q","answer":None}]}
        rows=[row("a","Q","one",["yes"])]
        self.assertEqual(s.packet_questions(packet,bank,"original",rows,[{}]),["Q"])
        with self.assertRaises(ValueError):s.packet_questions(packet,bank,"different",rows,[{}])
        with self.assertRaises(ValueError):s.packet_questions(packet,bank,"original",rows,[{"a":1}])
        packet["questions"][0]["prompt"]="Reused ID with different prompt"
        with self.assertRaises(ValueError):s.packet_questions(packet,bank,"original",rows,[{}])
        packet["questions"][0]["prompt"]=q["prompt"];packet["questions"][0]["answer"]="yes"
        with self.assertRaises(ValueError):s.packet_questions(packet,bank,"original",rows,[{}])

if __name__=="__main__":unittest.main()
