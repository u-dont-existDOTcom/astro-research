"""Fail-closed full-chart mechanical registry test, no personal DOB or survey."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
sp=importlib.util.spec_from_file_location("chart_feature_coverage",ROOT/"scripts/audit_full_chart_feature_coverage.py")
mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
REG=ROOT/"reference/research/whole_chart_feature_coverage_registry_dev_20261119.json"

class FeatureCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=json.loads(REG.read_bytes())

    def test_declared_grid_with_verified_western_and_hd_passes(self):
        model={"model_version":"development-fixture-v1",
               "precision_claim":"FINITE_GRID_15M",
               "required_features":[
                  "TROPICAL_7_LONGITUDES",
                  "TRADITIONAL_21_MAJOR_ASPECTS_WITH_EXACT_ORBS",
                  "ASCENDANT_AND_MIDHEAVEN",
                  "HD_TYPE_AUTHORITY_PROFILE_STRATEGY",
                  "HD_DEFINITION_CENTERS_COMPLETE_CHANNELS"]}
        r=mod.coverage(self.registry,model)
        self.assertEqual(r["status"],"PASS_MECHANICAL_COVERAGE")
        self.assertFalse(r["certified_predictive_human_personality"])

    def test_non_sun_carrier_lines_are_not_in_historical_cache(self):
        model={"model_version":"unmet-need",
               "precision_claim":"FINITE_GRID_15M",
               "required_features":["HD_PERSONALITY_DESIGN_ALL_NON_SUN_LINES"]}
        r=mod.coverage(self.registry,model)
        self.assertEqual(r["status"],"FAIL_MISSING_OR_UNCERTIFIED_REQUIRED_FEATURES")

    def test_continuous_claim_fails_when_western_source_is_only_grid(self):
        model={"model_version":"overclaim",
              "precision_claim":"CONTINUOUS_STRUCTURAL",
              "required_features":["ASCENDANT_AND_MIDHEAVEN","HD_TYPE_AUTHORITY_PROFILE_STRATEGY"]}
        r=mod.coverage(self.registry,model)
        self.assertEqual(r["required_feature_failures"],["ASCENDANT_AND_MIDHEAVEN"])

    def test_continuous_exact_hd_structural_only_passes(self):
        model={"model_version":"structural",
              "precision_claim":"CONTINUOUS_STRUCTURAL",
              "required_features":["HD_TYPE_AUTHORITY_PROFILE_STRATEGY","HD_DEFINITION_CENTERS_COMPLETE_CHANNELS"]}
        r=mod.coverage(self.registry,model)
        self.assertTrue(r["certified_for_required_mechanics_only"])
        self.assertFalse(r["v4_3_complete_model_certified"])

    def test_unknown_or_duplicate_source_requirement_fails(self):
        for requirements in [["THIS_DOES_NOT_EXIST"],
                             ["TROPICAL_7_LONGITUDES","TROPICAL_7_LONGITUDES"]]:
            with self.assertRaises(ValueError):
                mod.coverage(self.registry,{"model_version":"bad-fixture",
                    "precision_claim":"FINITE_GRID_15M",
                    "required_features":requirements})

    def test_missing_ephemeris_source_digest_fails(self):
        data=json.loads(REG.read_bytes())
        data["source_register"]["western_planets"]["manifest_sha256"]=None
        m={"model_version":"missing-source",
           "precision_claim":"FINITE_GRID_15M",
           "required_features":["TROPICAL_7_LONGITUDES"]}
        r=mod.coverage(data,m)
        self.assertFalse(r["certified_for_required_mechanics_only"])

    def test_unsupported_behavior_mapping_never_pretends_to_predict(self):
        m={"model_version":"misleading",
           "precision_claim":"FINITE_GRID_15M",
           "required_features":["FULL_TIME_CONTRADICTION_AWARE_BEHAVIOR_MAP"]}
        self.assertFalse(mod.coverage(self.registry,m)["certified_for_required_mechanics_only"])

if __name__=="__main__":unittest.main()
