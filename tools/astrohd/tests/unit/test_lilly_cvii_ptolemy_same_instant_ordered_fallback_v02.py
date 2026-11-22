"""Synthetic same-UTC Ptolemy–Lilly source geometry, never person data."""
import sys
from pathlib import Path
import unittest
from collections import Counter
import numpy as np
import swisseph as swe
SRC=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(SRC))
import lilly_cvii_ptolemy_same_instant_ordered_fallback_v02 as model

class CrossSchoolSameInstant(unittest.TestCase):
    def test_conservative_source_overlap_is_disjoint_and_accounted_for(self):
        jd=swe.julday(2020,1,1,0.)
        lat,lon=39.,-75.
        p=np.tile(np.array([110.,44.,79.,100.,5.,222.,303.,50.]),(3,1))
        p[1,3]=170.
        q=np.zeros((3,17))
        q[:,4]=45.
        for i in range(3):
            houses,_=swe.houses_ex(jd+i/96,lat,lon,b'R')
            q[i,0]=houses[0]
        ids=np.array([5,-1,6],dtype=np.int32)
        c=Counter();h={}
        model.calc_chunk(p,q,ids,jd0=jd,index_first=0,lat=lat,
                         lon=lon,counts=c,hd_sets=h)
        self.assertEqual(c["rows"],3)
        self.assertEqual(c["HD_boundary_abstentions"],1)
        for mode in model.MODES:
            for orb in model.SOURCE_ORBS:
                for join in model.JOINS:
                    for behold in model.BEHOLDS:
                        for partile in model.PARTILES:
                            tag="|".join((mode,orb,join,behold,partile))
                            self.assertEqual(sum(c[tag+"|S"+str(i)] for i in range(1,6)),3)
                            self.assertEqual(sum(c["same_instant_Ptolemy_"+tag+"|S"+str(i)]
                                                  for i in range(1,6)),
                                             c["ptolemy_robust_all_four_variant_common"])
                            for i in range(1,6):
                                k="same_instant_Ptolemy_"+tag+"|S"+str(i)
                                self.assertLessEqual(c[k],c[tag+"|S"+str(i)])
                                if k in h:
                                    self.assertFalse(h[k][-1]) # 288907 never seen
    def test_authoritative_published_output_remains_natal_free(self):
        import inspect
        params=inspect.signature(model.run).parameters
        self.assertEqual(set(params),{"west","angles","hd_cache","hd_join","hashes"})
        self.assertNotIn("subject",str(params))

    def test_public_full_century_and_same_instant_source_contract(self):
        import json
        source=Path(__file__).resolve().parents[2]/"reference/research/lilly_cvii_ptolemy_same_instant_ordered_fallback_public_v02.json"
        j=json.loads(source.read_text())
        c=j["counts"]
        self.assertEqual(j["original_UTC_grid_samples"],3506400)
        self.assertEqual(c["rows"],3506400)
        self.assertEqual(c["HD_boundary_abstentions"],125)
        self.assertEqual(c["ptolemy_robust_all_four_variant_common"],4553)
        self.assertEqual(c["ptolemy_robust_common_HD_unknown"],0)
        self.assertFalse(j["actual_manners_significator_selected"])
        self.assertFalse(j["personal_natal_interview_inputs_loaded"])
        self.assertEqual(j["hd_source_join"]["status"],"PASS_JOINED_SOURCE_NEUTRAL_GRID_SHARD_AUDIT")
        for mode in model.MODES:
            for orb in model.SOURCE_ORBS:
                for join in model.JOINS:
                    for behold in model.BEHOLDS:
                        for partile in model.PARTILES:
                            prefix="|".join((mode,orb,join,behold,partile))
                            self.assertEqual(sum(c[prefix+"|S"+str(i)] for i in range(1,6)),3506400)
                            self.assertEqual(sum(c["same_instant_Ptolemy_"+prefix+"|S"+str(i)] for i in range(1,6)),4553)
        narrow="|".join(("ascending_sign","1647_table_smaller_orbs","four_externals_only",
                         "dispositor_sign_ray","partile_Moon_or_Mercury"))
        wide=narrow.replace("smaller_orbs","larger_orbs")
        self.assertEqual([c[narrow+"|S"+str(i)] for i in range(1,6)],
                         [1428060,891641,593535,88670,504494])
        self.assertEqual([c[wide+"|S"+str(i)] for i in range(1,6)],
                         [1428060,950944,565796,84473,477127])
        self.assertEqual([c["same_instant_Ptolemy_"+narrow+"|S"+str(i)] for i in range(1,6)],
                         [1746,1363,772,88,584])

if __name__=="__main__":unittest.main()
