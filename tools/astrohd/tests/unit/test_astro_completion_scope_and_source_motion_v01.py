"""Regression: completion claim granularity and source-neutral motion only."""
import copy
import json
import sys
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/"tools/astrohd/scripts"))
import audit_astrology_completion_scope_v01 as coverage
import lilly_1647_source_direct_retro_motion_century_v01 as motion

class SourceCompletionAndMotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=ROOT
        cls.matrix=json.loads((ROOT/"state/RESEARCH-COMPLETION-SCOPE.json").read_text())
        cls.house=json.loads((ROOT/"tools/astrohd/reference/research/lilly_1647_house_accidental_fortitude_full_century_public_v01.json").read_text())
        cls.ptolemy=json.loads((ROOT/"tools/astrohd/reference/research/ptolemy_lilly_hd_same_instant_public_census_v01.json").read_text())
    def audit(self,value):
        return coverage.audit(value,self.house,self.ptolemy,self.root)
    def test_root_still_open_and_finite_grid_scope_preserved(self):
        result=self.audit(self.matrix)
        self.assertEqual(result["root_status"],"OPEN")
        self.assertFalse(result["root_human_predictive_validity_established"])
        self.assertFalse(result["root_unique_natal_rank_established"])
        self.assertTrue(result["finite_grid_not_all_locations_or_continuous_births"])
    def test_cannot_promote_source_milestone_to_owner_completion(self):
        case=copy.deepcopy(self.matrix)
        case["root_status"]="SATISFIED"
        with self.assertRaisesRegex(ValueError,"Root owner outcome"):
            self.audit(case)
        case=copy.deepcopy(self.matrix)
        case["coverage_layers"][3]["status"]="COMPLETE"
        with self.assertRaisesRegex(ValueError,"Unverified completion"):
            self.audit(case)
    def test_reading_documentary_not_behavioral_algorithm(self):
        x=self.matrix["coverage_layers"]
        self.assertEqual(next(a for a in x if a["id"]=="source_documentary_intake")["status"],"PARTIAL_OVERALL")
        self.assertEqual(next(a for a in x if a["id"]=="whole_century_behavioral_scorer")["status"],"NOT_RUN")
    def test_finite_diff_zodiac_wrap_and_speed_per_day(self):
        prior=np.array([[359.98,3.,180.,250.,100.,40.,290.],
                        [130.,130.,130.,130.,130.,130.,130.]])
        after=np.array([[.02,3.2,179.9,249.9,100.5,40.1,290.04],
                        [130.1,130.1,130.1,130.1,130.1,130.1,130.1]])
        speed=motion.wrapped_speed(prior,after)
        self.assertAlmostEqual(speed[0,0],1.92,places=5)
        self.assertAlmostEqual(speed[0,2],-4.8,places=5)
        self.assertTrue(np.all(np.isfinite(speed)))
    def test_motion_unknown_stations_and_absolute_boundaries(self):
        speed=np.array([9.,1.2,-1.0,0.,0.005,0.5])
        d,r,u=motion.status(speed,0.02,np.array([1,0,0,0,0,1],dtype=bool))
        self.assertEqual(d.tolist(),[False,True,False,False,False,False])
        self.assertEqual(r.tolist(),[False,False,True,False,False,False])
        self.assertEqual(u.tolist(),[True,False,False,True,True,True])
        with self.assertRaises(ValueError):motion.status(speed,-1)
        with self.assertRaises(ValueError):motion.wrapped_speed(prior_row=np.ones((2,7))*-1,next_row=np.ones((2,7)))
    def test_original_Sun_Moon_p115_not_graded_as_retrograde(self):
        self.assertEqual(motion.MOVING,(2,3,4,5,6))
        self.assertEqual(motion.PLANET_NAMES[:2],("Sun","Moon"))
    def test_actual_same_instant_source_report_when_published(self):
        path=ROOT/"tools/astrohd/reference/research/lilly_1647_direct_retrograde_full_century_public_v01.json"
        if not path.exists():self.skipTest("Numerical original source scan not yet completed")
        j=json.loads(path.read_text())
        c=j["counts"]
        self.assertEqual(j["samples"],3506400)
        self.assertEqual(c["HD_transition_margin_unknown"],125)
        self.assertEqual(c["prior_conditional_ptolemy_common"],4553)
        self.assertEqual(c["mercury_cached_speed_comparison_samples"],3506398)
        self.assertGreater(c["Swiss_verified_frozen_longitude_and_speed_controls"],0)
        self.assertFalse(j["complete_historic_accidental_strength"])
        self.assertFalse(j["human_predictive_validity_established"])
        self.assertFalse(j["personal_natal_interview_data_used"])
        for name in motion.PLANET_NAMES[2:]:
            for t in motion.THRESHOLDS:
                key=f"{name}|threshold={t:.2f}|"
                self.assertEqual(sum(c[key+s] for s in ("direct","retrograde","unknown")),3506400)
                self.assertEqual(sum(c[key+"conditional_ptolemy_"+s] for s in ("direct","retrograde","unknown")),4553)
                self.assertGreaterEqual(c[key+"unknown"],2)

if __name__=="__main__":unittest.main()
