"""Invented source coordinates; never natal participants or behavioral outcomes."""
import json
import sys
from pathlib import Path
import unittest
import numpy as np

SRC=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(SRC))
import lilly_1647_integrated_partial_fortitude_full_century_v01 as model

class SourceBoundPartialStrength(unittest.TestCase):
    def test_exact_declared_72_source_sensitivity_conditions(self):
        self.assertEqual(model.NUM_SCENARIOS,72)
        self.assertEqual(len(model.TERMS),3)
        self.assertEqual(len(model.ESSENTIAL_POLICIES),4)
        self.assertEqual(len(model.HOUSE_NAMES),2)
        self.assertEqual(tuple(model.STATIONS),(.01,.02,.05))

    def test_all_four_natal_body_essential_branches_reproduce_earlier_math(self):
        positions=np.array([[5.,40.,75.,123.,135.,235.,15.],
                            [151.,200.,227.,88.,310.,10.,305.]],dtype=float)
        alt=np.array([30.,-15.])
        for term in model.TERMS:
            ours=model.essential_points(positions,alt,term)
            self.assertEqual(set(ours),set(model.ESSENTIAL_POLICIES))
            previous,_,_,_=model.es.candidate_models(positions,alt)
            for policy,points in ours.items():
                best=points.max(axis=1)
                unique=(points==best[:,None]).sum(axis=1)==1
                winners=np.argmax(points,axis=1).astype(np.int8)
                winners[~unique]=-1
                self.assertEqual(winners.tolist(),previous[term+"|"+policy].tolist())

    def test_station_source_bounds_are_conservative_and_sun_moon_exempt(self):
        speed=np.array([[0.,0.,.5,-.2,.01,0.,-.01],
                        [0.,0.,-.1,.9,.001,.03,.04]],dtype=float)
        lo,hi=model.signed_motion_bounds(speed,.02,np.array([False,True]))
        self.assertEqual(lo.shape,(2,7))
        self.assertTrue(np.all(lo<=hi))
        self.assertEqual(lo[0,:2].tolist(),[0,0])
        self.assertEqual(hi[0,:2].tolist(),[0,0])
        self.assertEqual([lo[0,k] for k in range(2,7)],[4,-5,-5,-5,-5])
        self.assertEqual([hi[0,k] for k in range(2,7)],[4,-5,4,4,4])
        self.assertEqual(lo[1,2:7].tolist(),[-5,-5,-5,-5,-5])
        self.assertEqual(hi[1,2:7].tolist(),[4,4,4,4,4])

    def test_strict_interval_winner_only_if_beats_all_competitor_maxima(self):
        lo=np.array([[10,0,0,0,0,0,0],
                     [10,9,0,0,0,0,0],
                     [10,4,0,0,0,0,0],
                     [10,0,0,0,0,0,0]],dtype=np.int16)
        hi=np.array([[10,3,0,0,0,0,0],
                     [10,12,0,0,0,0,0],
                     [10,4,0,0,0,0,0],
                     [10,0,0,0,0,0,0]],dtype=np.int16)
        ans=model.interval_unique_winner(lo,hi,np.array([1,1,0,1],bool))
        self.assertEqual(ans.tolist(),[0,-1,-1,0])
        with self.assertRaises(ValueError):
            model.interval_unique_winner(hi,lo,np.ones(4,dtype=bool))

    def test_robust_winner_candidate_not_human_personality(self):
        import inspect
        self.assertEqual(set(inspect.signature(model.run).parameters),
                         {"west","angles","hd_cache","hd_join","verify_shards"})
        self.assertEqual(len(model.PLANETS),7)

    def test_verified_aggregate_when_available(self):
        p=Path(__file__).resolve().parents[2]/"reference/research/lilly_1647_integrated_partial_fortitude_full_century_public_v01.json"
        if not p.exists():self.skipTest("Full 3.5m source sample scan not yet written")
        z=json.loads(p.read_text());c=z["counts"]
        self.assertEqual(z["samples"],3506400)
        self.assertEqual(c["HD_transition_unknown"],125)
        self.assertEqual(c["conditional_ptolemy_4mode_common"],4553)
        self.assertEqual(c["near_horizon_sect_abstentions"],5049)
        self.assertEqual(z["experimental_source_combination_model_count"],72)
        self.assertEqual(z["HD_structural_interval_count"],288908)
        self.assertFalse(z["historic_source_authorized_unique_total_or_manners_ruler"])
        self.assertTrue(z["not_independently_validated_human_personality"])
        self.assertFalse(z["private_natal_interview_or_personal_criterion_used"])
        for term in model.TERMS:
            for pol in model.ESSENTIAL_POLICIES:
                for t in model.STATIONS:
                    head="|".join((term,pol,f"station={t:.2f}"))
                    self.assertEqual(c[head+"|both_house_systems_unique"],
                        c[head+"|same_unique_between_houses"]+
                        c[head+"|different_unique_between_houses"])
                    for house in model.HOUSE_NAMES:
                        tag="|".join((term,pol,house,f"station={t:.2f}"))
                        self.assertEqual(c[tag+"|strict_unique"]+c[tag+"|uncertain_or_tied"],3506400)
        self.assertLessEqual(c["cross_72_source_method_same_unique_partial_winner"],3506400-5049)

if __name__=="__main__":unittest.main()
