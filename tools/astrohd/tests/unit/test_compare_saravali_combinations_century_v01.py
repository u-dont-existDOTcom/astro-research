import sys
import unittest
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_saravali_combinations_century_v01 as s

class TestSaravali(unittest.TestCase):
    def test_source_catalogue_and_mappings(self):
        reg,shared=s.load_map()
        self.assertEqual(len(reg["rules"]),56)
        self.assertEqual(sum(len(r["direct"]) for r in reg["rules"]),17)
        self.assertEqual(sum(len(r["proxy"]) for r in reg["rules"]),47)
        self.assertEqual(sum(bool(r["direct"] or r["proxy"]) for r in reg["rules"]),36)

    def test_wrapped_angles_and_explicit_sign_boundary(self):
        lon=np.array([[359.,1.,40.,100.,130.,200.,250.],[0.,3.,50.,100.,130.,200.,250.]])
        code,unknown=s.graph_from_distance(lon,3.)
        self.assertTrue(code[0]&1)
        self.assertFalse(unknown[0])
        self.assertTrue(unknown[1])
        sign,near=s.graph_from_signs(lon,np.zeros(2))
        self.assertFalse(sign[0]&1)
        self.assertTrue(near[1])

    def test_isolated_triple_and_larger_group_not_double_counted(self):
        reg,_=s.load_map();es=s.rule_edges(reg["rules"])
        lon=np.array([[5.,6.,7.,90.,130.,200.,250.],[5.,6.,7.,8.,130.,200.,250.]])
        code,near=s.graph_from_signs(lon,np.zeros(2))
        m=s.memberships(code,es)
        self.assertEqual(m["pairs_inclusive"].sum(axis=1).tolist(),[3,6])
        self.assertEqual(m["triples_inclusive"].sum(axis=1).tolist(),[1,4])
        self.assertEqual(m["both_inclusive"].sum(axis=1).tolist(),[4,10])
        self.assertEqual(m["isolated_exact_groups"].sum(axis=1).tolist(),[1,0])

    def test_clique_not_transitive_chain(self):
        reg,_=s.load_map();es=s.rule_edges(reg["rules"])
        lon=np.array([[2.,4.,6.,100.,130.,200.,250.]])
        code,_=s.graph_from_distance(lon,3.)
        m=s.memberships(code,es)
        self.assertEqual(int(m["pairs_inclusive"].sum()),2)
        self.assertEqual(int(m["triples_inclusive"].sum()),0)
        self.assertEqual(int(m["isolated_exact_groups"].sum()),0)

    def test_item_cap_and_conflict_envelope(self):
        # Three synthetic rule instances give +,+,- to one observed item.
        es=(np.array([1,1,1]),np.zeros(3,dtype=int),np.array([2,2,2]))
        table={k:(np.array([[1],[1],[-1]],dtype=np.int8),np.array([1]),np.array([.5])) for k in s.MAPS}
        a=s.evaluate_graphs(np.array([1,0]),es,table)["both_inclusive|direct"]
        np.testing.assert_allclose(a["score"],[0,0])
        np.testing.assert_allclose(a["lo"],[-.5,0])
        np.testing.assert_allclose(a["hi"],[.5,0])
        np.testing.assert_equal(a["conflicting_items"],[1,0])
        es=(np.array([1,1]),np.zeros(2,dtype=int),np.array([2,2]))
        table={k:(np.array([[1],[1]],dtype=np.int8),np.array([1]),np.array([.5])) for k in s.MAPS}
        a=s.evaluate_graphs(np.array([1]),es,table)["both_inclusive|direct"]
        self.assertEqual(a["score"][0],.5)

    def test_compact_matches_literal_graphs(self):
        reg,shared=s.load_map();es=s.rule_edges(reg["rules"])
        table=s.observation_tables(reg,shared,{"learning":1,"eloquence":-1,"work":1})
        graphs=np.array([1,17,1,0,17,0],dtype=np.int64)
        a=s.evaluate_graphs(graphs,es,table)
        b=s.compact_graph_scores(graphs,es,table)
        for tag in a:
            for k in a[tag]:
                np.testing.assert_allclose(a[tag][k],b[tag][k])

    def test_32_arm_accounting(self):
        reg,shared=s.load_map();es=s.rule_edges(reg["rules"])
        table=s.observation_tables(reg,shared,{"learning":1,"eloquence":-1})
        import unittest.mock as mock
        lon=np.array([[5.,6.,7.,90.,130.,200.,250.],[5.,6.,7.,8.,130.,200.,250.],[20.,30.,40.,50.,60.,70.,80.]])
        graphs={k:s.graph_from_signs(lon,np.zeros(3)) for k in s.GEOMS}
        # Explicitly retain an HD-unknown row.
        graphs={k:(code,np.array([False,False,False])) for k,(code,near) in graphs.items()}
        ref=s.exact_reference(None,{k:(code[:1],near[:1]) for k,(code,near) in graphs.items()},es,table,1.)
        c=defaultdict(lambda:defaultdict(Counter));geo=defaultdict(Counter)
        with mock.patch.object(s,"all_graphs",return_value=(graphs,{})):
            s.scan(lon,np.arange(3),np.array([0,1,-1]),[np.array([1.,.5])],[table],[ref],es,[c],geo,{})
        s.validate(c,geo,ref)
        self.assertEqual(len(ref),32)
        self.assertEqual(c["across_all"]["coverage"]["ranked"],2)
        self.assertGreaterEqual(c["across_all"]["coverage"]["tied_all"],1)
        tag=next(iter(ref));c[tag]["joint"]["higher"]+=1
        with self.assertRaises(ValueError):s.validate(c,geo,ref)

if __name__=="__main__":unittest.main()
