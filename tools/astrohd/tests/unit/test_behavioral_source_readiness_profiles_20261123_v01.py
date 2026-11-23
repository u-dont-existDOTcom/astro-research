"""Development-only source coverage admission, NEVER human chart scoring."""
from pathlib import Path
import copy
import json
import sys
import unittest
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/"tools/astrohd/scripts"))
import audit_behavioral_source_readiness_20261123_v01 as m

class ExistingReadinessGateReused(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=json.loads((ROOT/m.PROFILE).read_text())
        cls.registry=json.loads((ROOT/cls.src["source_registry_path"]).read_text())
    def test_registry_sha_explicit_and_public_source_only(self):
        self.assertEqual(m.source_sha(ROOT/self.src["source_registry_path"]),
                         self.src["source_registry_sha256"])
        self.assertFalse(self.src["human_prediction_validated"])
        self.assertFalse(self.src["full_chart_rank_computed"])
        self.assertFalse(self.src["source_personal_birth_or_interview_records_used"])
        self.assertTrue(all(self.src["source_boundaries"].values()))
    def test_reference_mechanical_source_presence_pass_is_not_human_prediction(self):
        p=self.src["profiles"][0]
        j=m.coverage(self.registry,{key:p[key] for key in
                                    ("model_version","precision_claim","required_features")})
        self.assertEqual(j["status"],"PASS_MECHANICAL_COVERAGE")
        self.assertEqual(j["required_feature_failures"],[])
        self.assertFalse(j["certified_predictive_human_personality"])
        self.assertFalse(j["v4_3_complete_model_certified"])
    def test_specific_source_governor_plus_human_model_fails_three_declared_gaps(self):
        p=self.src["profiles"][1]
        j=m.coverage(self.registry,{key:p[key] for key in
                                    ("model_version","precision_claim","required_features")})
        self.assertEqual(j["status"],"FAIL_MISSING_OR_UNCERTIFIED_REQUIRED_FEATURES")
        self.assertEqual(j["required_feature_failures"],[
            "PTOL_EMPOWERED_MERCURY_MOON_SOUL_LORDSHIP",
            "FULL_TIME_CONTRADICTION_AWARE_BEHAVIOR_MAP",
            "VALID_FINAL_SCORE_UPPER_BOUNDS_ALL_FEATURES"])
        self.assertFalse(j["certified_predictive_human_personality"])
    def test_comprehensive_pressure_test_not_frozen_or_mandatory_trait_model(self):
        p=self.src["profiles"][2]
        self.assertIn("NOT hereby made mandatory",p["interpretation"])
        j=m.coverage(self.registry,{key:p[key] for key in
                                    ("model_version","precision_claim","required_features")})
        self.assertEqual(len(p["required_features"]),22)
        self.assertEqual(len(j["required_feature_failures"]),8)
        self.assertEqual(j["required_feature_failures"],p["expected_uncertified"])
        self.assertFalse(j["certified_predictive_human_personality"])
    def test_wrong_pretend_predictive_feature_status_cannot_pass_against_frozen_provenance(self):
        p=copy.deepcopy(self.src)
        p["profiles"][1]["expected_coverage_status"]="PASS_MECHANICAL_COVERAGE"
        # Direct source coverage remains a FAIL despite fake desired status.
        row=p["profiles"][1]
        j=m.coverage(self.registry,{key:row[key] for key in
                                     ("model_version","precision_claim","required_features")})
        self.assertNotEqual(j["status"],row["expected_coverage_status"])
        other=copy.deepcopy(self.registry)
        for x in other["features"]:
            if x["id"]=="PTOL_EMPOWERED_MERCURY_MOON_SOUL_LORDSHIP":
                x["status"]="ready"
        # A floating 'ready' status cannot certify a required original
        # governor when no source compiler/provenance is registered.
        row=self.src["profiles"][1]
        j=m.coverage(other,{key:row[key] for key in
                            ("model_version","precision_claim","required_features")})
        self.assertIn("PTOL_EMPOWERED_MERCURY_MOON_SOUL_LORDSHIP",j["required_feature_failures"])
    def test_actual_readiness_receipt_when_published(self):
        receipt=ROOT/m.RECEIPT
        if not receipt.exists():self.skipTest("Source-bound audit not yet run")
        r=json.loads(receipt.read_text())
        self.assertEqual(r["status"],"PASS_READINESS_AUDIT_CORRECTLY_IDENTIFIES_INCOMPLETE_HUMAN_MODEL")
        self.assertEqual(len(r["source_profiles"]),3)
        self.assertFalse(r["preregistered_full_cross_system_human_behavioral_model_frozen"])
        self.assertFalse(r["independent_private_blinded_human_validation_executed"])
        self.assertTrue(r["no_private_natal_birth_interview_case_data_read"])
        self.assertEqual(r["root_project_status"],"OPEN")
        self.assertEqual(r,m.build(ROOT))
if __name__=="__main__":unittest.main()
