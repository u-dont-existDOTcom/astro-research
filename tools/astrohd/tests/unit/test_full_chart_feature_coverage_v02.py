"""Original v01 migration SHA must remain exact; active v02 refuses fake source readiness."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import audit_full_chart_feature_coverage_v02 as m

class SourceBoundReadinessSuccessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_registry=json.loads((ROOT/"reference/research/whole_chart_feature_coverage_registry_dev_20261119.json").read_text())
        cls.id="PTOL_EMPOWERED_MERCURY_MOON_SOUL_LORDSHIP"
        cls.model={"model_version":"synthetic-v02-provenance-check",
                   "precision_claim":"FINITE_GRID_15M",
                   "required_features":[cls.id]}
    def check_fail(self,registry):
        result=m.coverage(registry,self.model)
        self.assertEqual(result["status"],"FAIL_MISSING_OR_UNCERTIFIED_REQUIRED_FEATURES")
        self.assertEqual(result["required_feature_failures"],[self.id])
        self.assertFalse(result["certified_for_required_mechanics_only"])
        self.assertFalse(result["certified_predictive_human_personality"])
        self.assertTrue(result["source_missing_for_ready_is_not_certified"])
    def test_untouched_historical_source_and_migration_inventory_exact_hash(self):
        old=(ROOT/"scripts/audit_full_chart_feature_coverage.py")
        self.assertEqual(sha256(old.read_bytes()).hexdigest(),m.ORIGINAL_SHA256)
        # An original development archive test is also SHA-pinned.
        original_test=ROOT/"tests/unit/test_full_chart_feature_coverage_gate.py"
        self.assertEqual(sha256(original_test.read_bytes()).hexdigest(),
                         "c44deb54efdaed66b6e70460fb903460f0817a5a08c6babd7601071de59d65d1")
    def test_fake_ready_source_none_fails(self):
        x=deepcopy(self.original_registry)
        for row in x["features"]:
            if row["id"]==self.id:
                row["status"]="ready";row["src"]=None
        self.check_fail(x)
    def test_fake_derivable_empty_source_fails(self):
        x=deepcopy(self.original_registry)
        for row in x["features"]:
            if row["id"]==self.id:
                row["status"]="derivable";row["src"]=""
        self.check_fail(x)
    def test_missing_source_field_fails_without_crashing_and_input_immutable(self):
        x=deepcopy(self.original_registry)
        for row in x["features"]:
            if row["id"]==self.id:
                row["status"]="ready";row.pop("src")
        frozen=deepcopy(x)
        self.check_fail(x)
        self.assertEqual(x,frozen)
    def test_fake_registered_source_digests_fail(self):
        for bad in ("missing_src_id","western_fake"):
            x=deepcopy(self.original_registry)
            for row in x["features"]:
                if row["id"]==self.id:
                    row["status"]="ready";row["src"]=bad
            if bad=="western_fake":
                x["source_register"][bad]={"manifest_sha256":" "}
            self.check_fail(x)
    def test_real_manifested_source_still_passes_mechanics_only(self):
        x=deepcopy(self.original_registry)
        test={"model_version":"real-synthetic-v02-mechanics",
              "precision_claim":"FINITE_GRID_15M",
              "required_features":["TROPICAL_7_LONGITUDES",
                                   "HD_TYPE_AUTHORITY_PROFILE_STRATEGY"]}
        out=m.coverage(x,test)
        self.assertEqual(out["status"],"PASS_MECHANICAL_COVERAGE")
        self.assertEqual(out["required_feature_failures"],[])
        self.assertTrue(out["certified_for_required_mechanics_only"])
        self.assertFalse(out["certified_predictive_human_personality"])
    def test_registered_source_digest_missing_fails(self):
        x=deepcopy(self.original_registry)
        x["source_register"]["western_planets"]["manifest_sha256"]=None
        t={"model_version":"synthetic-missing-digest",
           "precision_claim":"FINITE_GRID_15M",
           "required_features":["TROPICAL_7_LONGITUDES"]}
        out=m.coverage(x,t)
        self.assertFalse(out["certified_for_required_mechanics_only"])
        self.assertIn("TROPICAL_7_LONGITUDES",out["required_feature_failures"])
    def test_sampled_UTC_source_never_claims_continuous_or_behavioral(self):
        model={"model_version":"synthetic-invalid-continuous",
               "precision_claim":"CONTINUOUS_STRUCTURAL",
               "required_features":["TROPICAL_7_LONGITUDES","HD_TYPE_AUTHORITY_PROFILE_STRATEGY"]}
        out=m.coverage(self.original_registry,model)
        self.assertEqual(out["required_feature_failures"],["TROPICAL_7_LONGITUDES"])
        self.assertFalse(out["certified_predictive_human_personality"])
if __name__=="__main__":unittest.main()
