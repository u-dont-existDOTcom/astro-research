import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_lilly_character_panel_v01 as l

class TestLillyCharacter(unittest.TestCase):
    def test_lilly_source_specific_directions(self):
        reg,shared=l.load_map()
        self.assertEqual(len(reg["profiles"]),5)
        self.assertEqual(sum(len(p[c]) for p in reg["profiles"] for c in l.CLAUSES),44)
        a,den,_=l.table(reg,shared,{"reflection":1,"work":1,"leadership":-1})
        self.assertEqual(den,[2,1])
        self.assertGreater(a[0,l.BODIES.index("Saturn")],0)
        self.assertLess(a[0,l.BODIES.index("Jupiter")],0)
        self.assertTrue((a[:,l.BODIES.index("Sun")]==0).all())

    def test_primary_plural_and_uncertain_secondary(self):
        primary=np.array([[False,False,True,False,False,True,False]])
        outer=primary.copy()
        outer[0,4]=True
        values=np.zeros((2,7))
        values[0,2]=.8
        values[0,5]=.2
        values[1,4]=-.8
        out=l.score(primary,np.array([-1]),outer,values,np.array([.5]))
        self.assertEqual(out["single_strong"]["western"][0],0)
        self.assertEqual(out["mean_strong"]["western"][0],.5)
        self.assertEqual(out["envelope"]["western_lo"][0],-.8)
        self.assertEqual(out["envelope"]["western_hi"][0],.8)

    def test_preserved_ordered_stage_alternatives(self):
        lon=np.array([[20.,45.,95.,5.,80.,155.,300.]])
        allrows=list(l.branches(lon,np.array([20.]),np.array([0.]),np.array([30.])))
        self.assertEqual(len({x[0] for x in allrows}),96)
        for tag,st,single,p,certain,possible,outer in allrows:
            self.assertTrue(np.array_equal(p.sum(axis=1)==1,single>=0))
            self.assertFalse(np.any(certain&~possible))
            self.assertFalse(np.any(possible&p))
            self.assertFalse(np.any(p&~outer))
