"""Regression of a new owner-authorized, positive/negative forum audit wave."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("wave4",ROOT/"scripts/audit_disputed_predictor_forum_wave4_v01.py")
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)
SR=ROOT/"reference/research"

def read(n):
    return json.loads((SR/n).read_bytes())

SOURCES=(
    read("disputed_predictor_forum_audit_protocol_v01.json"),
    read("disputed_predictor_forum_seed_v01.json"),
    read("disputed_predictor_forum_wave2_v01.json"),
    read("disputed_predictor_forum_wave3_v01.json"),
    read("disputed_predictor_forum_wave4_v01.json"),
)


class Wave4Tests(unittest.TestCase):
    def test_pilot_consolidation_and_real_read_scope(self):
        result=m.merge(*SOURCES)
        self.assertEqual(result["claims_registered_now"],26)
        self.assertEqual(result["source_observation_units_now"],81)
        self.assertEqual(result["distinct_source_discussions_now"],66)
        self.assertEqual(result["new_wave_sampled_units"],22)
        self.assertEqual(result["read_mode_counts"]["full_original_page"],11)
        self.assertEqual(result["new_distinct_source_discussions"],17)
        self.assertEqual(result["verified_prospective_prediction_records"],0)
        self.assertTrue(result["no_numeric_failure_rate_or_birth_rank_supported"])

    def test_fourth_wave_requires_owner_scope(self):
        docs=list(copy.deepcopy(SOURCES));docs[4]["scope"]="FIFTH_UNAUTHORIZED_WAVE"
        with self.assertRaisesRegex(ValueError,"owner-authorized"):
            m.merge(*docs)

    def test_fake_prospective_accuracy_rejected(self):
        docs=list(copy.deepcopy(SOURCES))
        docs[4]["public_source_observation_units"][0]["prospective_prediction_record_verified"]=True
        with self.assertRaisesRegex(RuntimeError,"promoted"):
            m.merge(*docs)

    def test_fake_population_frequency_rejected(self):
        docs=list(copy.deepcopy(SOURCES));docs[4]["representative_population_denominator"]=True
        with self.assertRaisesRegex(RuntimeError,"population"):
            m.merge(*docs)

    def test_bad_source_documentation_rejected(self):
        docs=list(copy.deepcopy(SOURCES));docs[4]["public_source_observation_units"][0]["read_mode"]="verified_private_chart"
        with self.assertRaisesRegex(ValueError,"read scope"):
            m.merge(*docs)

    def test_no_identifiable_birth_records(self):
        z=SOURCES[-1]
        self.assertTrue(z["anonymous_author_code_only"])
        self.assertTrue(all(not x["profile_or_birth_details_recorded"] for x in z["public_source_observation_units"]))

    def test_both_support_and_mismatch_observed(self):
        res=m.merge(*SOURCES)
        poles=res["new_observation_polarity_counts"]
        self.assertGreater(poles["first_person_mismatch"],0)
        self.assertGreater(poles["first_person_support"],0)

    def test_small_case_series_not_20_independent_validations(self):
        z=SOURCES[-1]
        m20=[x for x in z["public_source_observation_units"] if x["id"]=="W4_15"]
        self.assertEqual(len(m20),1)
        self.assertFalse(m20[0]["prospective_prediction_record_verified"])
        self.assertFalse(m20[0]["independent_person_denominator_available"])

if __name__=="__main__":unittest.main()
