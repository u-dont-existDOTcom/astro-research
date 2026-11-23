import sys, unittest
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_full_grid_behavior_v01 as s
import compare_bounded_behavior_v01 as b

def row(i,cluster,feature,op,vals):
    return {"mapping_id":i,"dependency_cluster":cluster,"chart_feature_predicate":
            {"feature":feature,"operator":op,"values":vals}}

def unit(i,profile,lon,alt):
    return {"private_id":i,"chart_midpoint":{
      "HD":{"type":"Projector","profile":profile,"defined_centers":["Heart"]},
      "Western":{"source_witness":{"traditional_planets":{
          bdy:{"longitude_degrees":float(l)} for bdy,l in zip(b.PLANETS,lon)},
          "sun_true_altitude_degrees":float(alt)}}}}

class TestFullGrid(unittest.TestCase):
    def test_vector_phase_and_modes(self):
        p=np.array([[350,10,95,40,30,90,120],
                    [10,350,50,100,120,170,250],
                    [20,200,20,5,10,15,90]])
        obs={"mercury_solstitial":1,"moon_fixed":-1,"moon_waxing_frankness":1,
             "moon_waning_caution":-1}
        m,l,ph=s.vote_arrays(p,obs)
        for n,r in enumerate(p):
            d=b.direct(r,obs)
            self.assertEqual((m[n,2],l[n,1],ph[n]),(d["mercury"],d["moon_mode"],d["moon_phase"]))
    def test_vector_scores_match_scalar_64_branches(self):
        rng=np.random.default_rng(82376)
        n=19;lon=rng.uniform(0,360,(n,7));alt=rng.uniform(-50,50,n);alt[5]=0
        profiles=["2/5","3/5","1/4","6/2","4/6"]
        ids=["REFERENCE"]+[str(i) for i in range(1,n)]
        units=[unit(i,profiles[k%len(profiles)],lon[k],alt[k]) for k,i in enumerate(ids)]
        mappings=[row("a","p","profile","profile_has_line",["2"]),
                  row("b","p","profile","profile_has_line",["3"]),
                  row("c","g","defined_centers","contains_any",["Heart"])]
        evidences=[{"hd":{"a":1,"b":-1,"c":1},
                    "western":{"mercury_fixed":-1,"mercury_solstitial":1,
                               "moon_bicorporeal":1,"moon_waxing_frankness":-1}},
                   {"hd":{"a":1,"b":None},
                    "western":{"mercury_bicorporeal":1,"moon_fixed":-1,"moon_waning_caution":1}}]
        refs=[b.compare(units,mappings,e["hd"],e["western"]) for e in evidences]
        lookup=[np.array([b.hd_score(u["chart_midpoint"]["HD"],mappings,e["hd"])["score"]
                         for u in units]) for e in evidences]
        lookup_ids=np.arange(n,dtype=np.int32);lookup_ids[7]=-1
        counts=[defaultdict(Counter) for e in evidences]
        s.scan_chunk(lon,alt,lookup_ids,lookup,evidences,refs,counts)
        known=[i for k,i in enumerate(ids) if lookup_ids[k]>=0]
        for r,co in zip(refs,counts):
            self.assertEqual(co["coverage"]["known"],n-1)
            for metric,key in (("HD_direct","hd"),("Western_direct","western_direct"),("joint_direct","joint_direct")):
                v=lambda i:r["cases"][i][key]["score"] if key=="hd" else r["cases"][i][key]
                expect=Counter(higher=0,tied=0,lower=0)
                for i in known: expect["higher" if v(i)>v("REFERENCE")+s.EPS else
                                      "lower" if v(i)<v("REFERENCE")-s.EPS else "tied"]+=1
                self.assertEqual(co[metric],expect)
            for tag,sc in r["scenarios"].items():
                cases=sc["cases"];target=cases["REFERENCE"]
                for metric,key in (("possible_joint","joint_possible"),
                                   ("conservative_joint","joint_conservative"),
                                   ("conservative_western","western_conservative")):
                    lo,hi=target[key]
                    want=Counter(certainly_higher=0,could_equal_or_exceed=0,certainly_lower=0)
                    for i in known:
                        a,z=cases[i][key]
                        want["certainly_higher"]+=a>hi+s.EPS
                        want["could_equal_or_exceed"]+=z>=lo-s.EPS
                        want["certainly_lower"]+=z<lo-s.EPS
                    self.assertEqual(co[tag+"|"+metric],want,tag)
                strict=Counter(higher=0,tied=0,lower=0)
                for i in known:
                    v=cases[i]["joint_strict"]; t=target["joint_strict"]
                    strict["higher" if v>t+s.EPS else "lower" if v<t-s.EPS else "tied"]+=1
                self.assertEqual(co[tag+"|strict_joint"],strict,tag)
    def test_unknown_candidate_bounds(self):
        v=np.array([[1,-1,0,0,1,1,0],[1,1,1,1,1,1,1]])
        leader=np.array([-1,-1])
        possible=np.array([[True,True,False,False,False,False,False],[False]*7])
        g,lo,hi=s.place_values(v,leader,possible)
        self.assertEqual(list(g),[0,0]);self.assertEqual(list(lo),[-1,0]);self.assertEqual(list(hi),[1,0])
    def test_counts_not_probability(self):
        k=np.array([True,True,False]);v=np.array([.5,.25,1.])
        self.assertEqual(s.exact_counts(v,.25,k),{"higher":1,"tied":1,"lower":0})
        self.assertEqual(s.bound_counts(v-.1,v+.1,[.2,.4],k),
                         {"certainly_higher":0,"could_equal_or_exceed":2,"certainly_lower":0})

if __name__=="__main__":unittest.main()
