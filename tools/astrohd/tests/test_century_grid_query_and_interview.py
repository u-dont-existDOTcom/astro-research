"""Generic tests for independent index query & neutral chart-contrast interview.

Optional NumPy-dependent tests skip on a CI runner without that optional tool;
they are executed in the isolated pilot environment where NumPy is pinned.
"""
import importlib.util
import json
from pathlib import Path
import unittest

BASE=Path(__file__).resolve().parents[1]


def load(path,modname):
    s=importlib.util.spec_from_file_location(modname,path)
    mod=importlib.util.module_from_spec(s);s.loader.exec_module(mod)
    return mod

interview=load(BASE/"scripts/contrastive_chart_interview_queue.py","contrastive")
try:
    import numpy as np
    q=load(BASE/"scripts/western_grid_source_profile_query_pilot.py","gridquery")
except ImportError:
    np=None
    q=None


class ContrastQueueTests(unittest.TestCase):
    def test_difference_only_and_no_exposed_direction(self):
        bank={"questions":[
            {"id":"Q01","prompt":"Describe how you solve complicated problems.",
             "evidence_tier":"symbolic","source_ids":["S1"]},
            {"id":"Q02","prompt":"Describe your ordinary emotional baseline.",
             "evidence_tier":"exploratory_bridge","source_ids":["S2"]},
            {"id":"Q14","prompt":"How does domestic activity affect your stamina?",
             "evidence_tier":"abstain","source_ids":[]}
        ]}
        actual={"survey_statuses":{"Q01":"SUPPORT_ONLY","Q02":"ABSTAIN","Q14":"ABSTAIN"}}
        alt={"survey_statuses":{"Q01":"SUPPORT_ONLY","Q02":"SUPPORT_ONLY","Q14":"ABSTAIN"}}
        participant,sealed=interview.make_queue(actual,alt,bank)
        self.assertEqual(len(participant["items"]),1)
        self.assertEqual(participant["items"][0]["item_id"],"Q02")
        self.assertEqual(sealed["comparisons"][0]["reference_status"],"ABSTAIN")
        self.assertNotIn("SUPPORT_ONLY",json.dumps(participant))
        self.assertNotIn("chart",participant["items"][0]["text"].lower())
        self.assertTrue(any(x["code"]=="3" for x in participant["items"][0]["answer_options"]))

    def test_bad_status_and_signature_rejected(self):
        bank={"questions":[{"id":"Q01","prompt":"hello","evidence_tier":"symbolic"}]}
        with self.assertRaises(ValueError):
            interview.make_queue(
               {"survey_statuses":{"Q01":"BROKEN"}},
               {"survey_statuses":{"Q01":"SUPPORT_ONLY"}},bank)
        with self.assertRaises(ValueError):
            interview.make_queue(
               {"survey_statuses":{"Q01":"SUPPORT_ONLY"}},
               {"survey_statuses":{"Q02":"SUPPORT_ONLY"}},bank)

@unittest.skipIf(np is None,"NumPy not installed in this optional scorer environment")
class VectorQueryTests(unittest.TestCase):
    def test_vector_shapes_and_deterministic_flags(self):
        a=np.array([[30.,60.,120.,180.,240.,300.,0.,1.],
                   [70.,285.,48.,47.,146.,110.,290.,-.2]],dtype=float)
        flags=q.data_flags(a)
        self.assertEqual(set(flags),set(q.FIXED_FLAGS))
        self.assertEqual(len(flags["moon_waning"]),2)
        self.assertTrue(flags["moon_waning"][1])
        self.assertTrue(flags["mercury_direct"][0])
        self.assertFalse(flags["mercury_direct"][1])
        self.assertTrue(flags["moon_saturn_close"][1])

    def test_mixed_and_abstain_stay_zero(self):
        status={"Q01":np.array([0,1,2,3],dtype=np.uint8),
                "Q04":np.array([0,1,2,3],dtype=np.uint8),
                "Q18":np.array([0,1,2,3],dtype=np.uint8),
                "Q03":np.array([0,1,2,3],dtype=np.uint8),
                "Q05":np.array([0,1,2,3],dtype=np.uint8),
                "Q02":np.array([0,1,2,3],dtype=np.uint8),
                "Q07":np.array([0,1,2,3],dtype=np.uint8),
                "Q09":np.array([0,1,2,3],dtype=np.uint8)}
        answers={k:True for k in status};answers["Q09"]=False
        result=q.score_status(status,answers)
        self.assertAlmostEqual(result[0],0.)
        self.assertAlmostEqual(result[1],3.5)
        self.assertAlmostEqual(result[2],-2.)
        self.assertAlmostEqual(result[3],0.)

    def test_coarse_sampling_can_provably_miss_narrow_grid_hit(self):
        # Reproduces the search-coverage failure without real subject data.
        values=np.array([0.,3.,0.,0.,2.5,0.,0.,0.])
        fine=values>2.7
        coarse=values[::4]>2.7
        self.assertTrue(np.any(fine))
        self.assertFalse(np.any(coarse))
        # An hourly zero cannot be a sound upper bound on the quarter-hour maximum.
        self.assertGreater(values.reshape(-1,4).max(),values[::4].max())

    def test_out_of_sign_requires_compatible_aspect_signs(self):
        a=np.array([[100.,120.,59.9,60.1,200.,300.,180.,1.]],dtype=float)
        flags=q.data_flags(a)
        self.assertFalse(flags["mercury_venus_favorable"][0])

if __name__=="__main__":unittest.main()
