"""Same-UTC alignment fixtures, abstentions and privacy-neutral set cardinality."""
import sys
from pathlib import Path
import unittest
import numpy as np
import swisseph as swe

SCRIPTS=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(SCRIPTS))
import ptolemy_lilly_hd_same_instant_century_v01 as m


class HDAlignment(unittest.TestCase):
    def make_source(self,n=3):
        jd=swe.julday(2020,1,1,0.)
        lat,lon=39.,-75.
        p=np.empty((n,8))
        p[:,:]=np.array([5.,90.,180.,65.,270.,120.,300.,10.])
        a=np.zeros((n,17))
        a[:,4]=40.
        for i in range(n):
            reg,arms=swe.houses_ex(jd+i/96.,lat,lon,b"R")
            a[i,0]=reg[0]
        return p,a,jd,lat,lon

    def test_exact_same_sample_hd_index_and_boundary_abstention(self):
        p,a,jd,lat,lon=self.make_source()
        bags={}
        counts=m.chunk_compute(p,a,start_jd=jd,first_index=0,
                               latitude=lat,longitude=lon,
                               hd_ids=np.array([-1,5,6],dtype="<i4"),hd_sets=bags)
        self.assertEqual(counts["total_samples"],3)
        self.assertEqual(counts["hd_join_boundary_abstain_same_instant"],1)
        self.assertEqual(counts["hd_join_known_same_instant"],2)
        for values in bags.values():
            self.assertNotIn(-1,values)
            self.assertTrue(set(values).issubset({5,6}))

    def test_hd_indices_require_exact_row_count(self):
        p,a,jd,lat,lon=self.make_source()
        for invalid in (np.array([1,2]),np.array([-3,1,2])):
            with self.assertRaises(ValueError):
                m.chunk_compute(p,a,start_jd=jd,first_index=0,
                    latitude=lat,longitude=lon,hd_ids=invalid,hd_sets={})

    def test_legacy_private_output_never_required(self):
        # Nothing in the source-schema join accepts a survey or natal path.
        import inspect
        params=inspect.signature(m.run).parameters
        self.assertEqual(set(params),{"west","angles","hd_cache","hd_join","verify_hashes"})
        self.assertFalse(any(k in params for k in ("birth","subject","responses","target_score")))


if __name__=="__main__": unittest.main()
