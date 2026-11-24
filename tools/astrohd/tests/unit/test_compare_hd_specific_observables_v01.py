import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_hd_specific_observables_v01 as a

class TestSpecificObservables(unittest.TestCase):
    def test_whole_catalogue_and_authority_exclusions(self):
        _,old,_=a.h.load_map()
        reg,groups,keys,domains=a.load_map(old)
        self.assertEqual(len(keys),22)
        self.assertEqual([len(groups[k]) for k in ("gate","channel","ordered_profile","line")],[64,36,12,6])
        self.assertEqual(len(reg["carriers"]),75)
        for k in a.h.EXCLUDED_GATES:self.assertEqual(groups["gate"][k-1]["direct"],{})
        self.assertEqual(len(a.KINDS)*len(a.h.ARMS),80)

    def test_capacity_use_and_skill_motive_remain_separate(self):
        _,old,_=a.h.load_map()
        _,groups,keys,domains=a.load_map(old)
        ch=groups["channel"][a.h.CHANNELS.index("26-44")]
        self.assertEqual(ch["direct"],{"persuasion_capacity":1})
        self.assertEqual(ch["proxy"],{"persuasion_use":1})
        ch=groups["channel"][a.h.CHANNELS.index("16-48")]
        self.assertEqual(ch["direct"],{"practice_perfection":1})
        self.assertEqual(ch["proxy"],{"mastery_as_end":1})
        m=a.masks(keys,domains,{k:(1 if k=="persuasion_capacity" else -1 if k=="persuasion_use" else None) for k in keys})
        p=1<<keys.index("persuasion_capacity");n=1<<keys.index("persuasion_use")
        v=a.s.score((np.asarray([p,n,p|n,0],np.uint64),np.zeros(4,np.uint64)),m)
        np.testing.assert_allclose(v["score"],[.125,-.125,0.,0.])

    def test_empty_domains_stay_zero(self):
        z=a.masks(("x","y"),{"x":"communication","y":"work"},{"x":1,"y":None})
        v=a.s.score((np.asarray([1,2,3],np.uint64),np.zeros(3,np.uint64)),z)
        np.testing.assert_allclose(v["score"],[.25,0,.25])

    def test_composition_is_fixed_not_rank_selected(self):
        v=a.components(np.array([1.,0.]),np.array([0.,.4]),np.array([-.2,.6]))
        np.testing.assert_allclose(v["specific"],[-.2,.6])
        np.testing.assert_allclose(v["specific_structural"],[.4,.3])
        np.testing.assert_allclose(v["shared_specific"],[-.1,.5])
        np.testing.assert_allclose(v["extended_blend"],[.45,.25])

    def test_weighted_counts_equal_expanded_same_row_counts(self):
        # Multiple timestamps share HD states but different non-HD outcomes.
        ids=np.array([0,1,1,2,2,2,0])
        packed=np.array([0,65535,0,65535,65535,0,65535],np.uint16)
        known=np.array([True,True,True,True,False,True,True])
        x=np.array([.1,.2,-.1]);y=np.array([0,.3,.2])
        def hist(mask):return np.bincount(ids[mask],minlength=3)
        w={"common":hist(known)}
        for k,gs in a.c.COMBOS.items():
            for z in a.c.METRICS:w[k+"|"+z]=hist(known&a.c.combo(packed,gs,z))
        self.assertEqual(a.cross_counts(w,x,y),a.c.aggregate(packed,known,x[ids],y[ids]))
        self.assertEqual(a.cross_counts(w,x,y)["all_primary"]["HD_strict_and_others_strict_any"],1)

if __name__=="__main__":unittest.main()
