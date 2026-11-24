import sys
import unittest
from collections import Counter
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_lilly_character_century_v01 as c
import compare_lilly_character_panel_v01 as l
import compare_full_grid_behavior_v01 as g

class TestLillyFullGrid(unittest.TestCase):
    def test_histogram_scores_match_rowwise_and_unknowns(self):
        rng=np.random.default_rng(2345)
        vals=rng.uniform(-1,1,(2,7))
        hd_values=np.array([-.5,0.,.25,1.])
        code=rng.integers(0,4,100)
        primary=rng.random((100,7))<.25
        outer=primary|(rng.random((100,7))<.25)
        single=np.where(primary.sum(axis=1)==1,np.argmax(primary,axis=1),-1)
        known=np.arange(100)%11!=0
        row=l.score(primary,single,outer,vals,hd_values[code])
        t={k:{f:float(v[1]) for f,v in arm.items()} for k,arm in row.items()}
        ph=np.bincount((128*code+c.encode(primary))[known],minlength=512)
        oh=np.bincount((128*code+c.encode(outer))[known],minlength=512)
        result=c.compare_hist(ph,oh,c.lookup(vals,hd_values),t,int(primary[1].sum()))
        matched=known&(primary.sum(axis=1)==primary[1].sum())
        for arm in l.ARMS:
            for k in ("western","joint"):
                self.assertEqual(result[arm+"|"+k],g.exact_counts(row[arm][k],t[arm][k],known))
            self.assertEqual(result[arm+"|matched_primary_count"],g.exact_counts(row[arm]["joint"],t[arm]["joint"],matched))
        for k in ("western","joint"):
            self.assertEqual(result["envelope|"+k],g.bound_counts(row["envelope"][k+"_lo"],row["envelope"][k+"_hi"],(t["envelope"][k+"_lo"],t["envelope"][k+"_hi"]),known))

    def test_two_shards_all_96_scenarios_and_histogram_coverage(self):
        reg,shared=l.load_map()
        vals,_,_=l.table(reg,shared,{"work":1,"reflection":1,"leadership":-1})
        lon=np.array([[20.,45.,95.,5.,80.,155.,300.],[20.,150.,50.,5.,80.,155.,300.],[5.,10.,20.,40.,80.,180.,300.]])
        alt=np.array([20.,0.,-20.])
        cusp=np.array([[0.,30.],[90.,130.],[15.,45.]])
        ids=np.array([0,1,-1]);codes=[np.array([0,1]),np.array([1,0])]
        hists=[{},{}];st=Counter();cv=Counter()
        for sl in (slice(0,1),slice(1,3)):
            c.scan_chunk(lon[sl],alt[sl],cusp[sl],ids[sl],codes,[2,2],st,hists,cv)
        self.assertEqual(cv,{"rows":3,"ranked":2,"unknown_HD":1})
        self.assertEqual(len(st),96*11)
        self.assertEqual(sum(st.values()),96*3)
        targets={}
        for tag,status,single,primary,sc,sp,outer in l.branches(lon[:1],alt[:1],cusp[:1,0],cusp[:1,1]):
            z=l.score(primary,single,outer,vals,np.array([0.]))
            targets[tag]={"primary":np.flatnonzero(primary[0]).tolist(),"scores":{k:{f:float(v[0]) for f,v in vv.items()} for k,vv in z.items()}}
        result=c.finalize(hists[0],c.lookup(vals,np.array([0.,1.])),targets,2)
        self.assertEqual(len(result),96)
        for v in result.values():
            self.assertEqual(sum(v["mean_strong|joint"].values()),2)
            self.assertGreaterEqual(v["mean_strong|joint"]["tied"],1)
            self.assertEqual(sum(v["mean_strong|matched_primary_count"].values()),v["coverage"]["matched_primary_count"])
        hists[0][next(iter(targets))][0][0]+=1
        with self.assertRaises(ValueError):
            c.finalize(hists[0],c.lookup(vals,np.array([0.,1.])),targets,2)

if __name__=="__main__":unittest.main()
