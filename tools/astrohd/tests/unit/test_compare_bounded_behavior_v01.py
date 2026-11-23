import unittest
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_bounded_behavior_v01 as s

def row(i,g,feature,op,vals):
    return {"mapping_id":i,"dependency_cluster":g,
            "chart_feature_predicate":{"feature":feature,"operator":op,"values":vals}}

def unit(i,profile,lon,alt=20):
    return {"private_id":i,"chart_midpoint":{
        "HD":{"profile":profile,"type":"Projector","defined_centers":["Heart"]},
        "Western":{"source_witness":{"traditional_planets":{
            b:{"longitude_degrees":l} for b,l in zip(s.PLANETS,lon)},
            "sun_true_altitude_degrees":alt}}}}

class BoundedComparisonTest(unittest.TestCase):
    def test_cluster_cap_and_fixed_denominator(self):
        rows=[row("x","profile","profile","profile_has_line",["2"]),
              row("y","profile","profile","profile_has_line",["5"]),
              row("z","type","type","equals_any",["Generator"])]
        obs={"x":1,"y":1,"z":-1}
        self.assertEqual(s.hd_score({"profile":"2/5","type":"Projector"},rows,obs)["score"],.5)
        self.assertEqual(s.hd_score({"profile":"2/4","type":"Projector"},rows,obs)["score"],.25)
        self.assertEqual(s.hd_score({"profile":"3/5","type":"Generator"},rows,obs)["score"],-.25)
    def test_unknown_not_negative_and_policy(self):
        a=row("a","AUTHORITY_DECISION","defined_centers","contains_any",["Solar Plexus"])
        b=row("b","other","authority","equals_any",["Splenic"])
        c=row("c","center","defined_centers","not_contains_any",["G"])
        self.assertEqual(s.admitted([a,b,c]),[c])
        out=s.hd_score({},[c],{"c":1})
        self.assertEqual(out["score"],0)
        self.assertEqual(out["unknown_carrier_observed"],1)
        self.assertIsNone(out["trace"]["c"]["active"])
        self.assertTrue(s.hd_active({"defined_centers":["Ego"]},row("x","c","defined_centers","contains_any",["Heart"])["chart_feature_predicate"]))
    def test_mode_and_phase(self):
        self.assertEqual([s.mode(x*30) for x in range(12)],list(s.MODES))
        self.assertEqual(s.phase_key([350,10]),"moon_waxing_frankness")
        self.assertEqual(s.phase_key([10,350]),"moon_waning_caution")
        self.assertIsNone(s.phase_key([10,190]))
        q=s.direct([20,45,95,5,80,155,300],{"mercury_solstitial":1,"moon_fixed":-1})
        self.assertEqual((q["mercury"],q["moon_mode"]),(1,-1))
        self.assertEqual(q["moon_phase"],0)
    def test_intervals_separate_and_missing(self):
        lon=np.array([10,45,95,140,170,200,310])
        p=np.array([False,True,False,False,False,False,True])
        a=s.bounded_place(lon,20,1,{"moon_fixed":1},-1,p)
        self.assertEqual(a["possible"],[1,1])
        self.assertEqual(a["with_abstention"],[0,1])
        self.assertEqual(a["strict"],0)
        self.assertEqual(set(a["candidates"]),{"Moon","Saturn"})
        unknown=s.bounded_place(lon,0,2,{},-1,np.zeros(7,dtype=bool))
        self.assertTrue(unknown["no_governor_admitted"])
    def test_rank_bounds_and_ties(self):
        self.assertEqual(s.ranks({"x":[.5,.7],"y":[.1,.4],"z":[.7,.8]})["x"],[1,2])
        self.assertEqual(s.exact_rank({"a":1,"b":1,"c":0})["a"],{"rank":1,"tied":2})
    def test_all_64_branches_on_invented_data(self):
        rows=[row("x","profile","profile","profile_has_line",["2"])]
        units=[unit("invented_a","2/5",[20,45,95,5,80,155,300]),
               unit("invented_b","3/5",[20,150,50,5,80,155,300],0)]
        result=s.compare(units,rows,{"x":1},{"mercury_solstitial":1,"moon_fixed":-1})
        self.assertEqual(len(result["scenarios"]),64)
        for sc in result["scenarios"].values():
            for k in ("mercury","moon"):
                self.assertTrue(sc["cases"]["invented_b"][k]["no_governor_admitted"])
            for c in sc["cases"].values():
                lo,hi=c["joint_conservative"]
                self.assertLessEqual(lo,c["joint_strict"])
                self.assertGreaterEqual(hi,c["joint_strict"])
                self.assertLessEqual(lo,c["joint_possible"][0])
                self.assertGreaterEqual(hi,c["joint_possible"][1])
    def test_unadmitted_observations_fail(self):
        with self.assertRaises(ValueError):s.checked_obs({"extra":1},{"allowed"})
        with self.assertRaises(ValueError):s.checked_obs({"allowed":True},{"allowed"})

if __name__=="__main__":unittest.main()
