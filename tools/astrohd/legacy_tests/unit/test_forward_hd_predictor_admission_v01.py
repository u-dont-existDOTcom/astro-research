"""Forward exclusion of untestable Splenic Authority from any NEW scored HD model."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("hd_admit",ROOT/"scripts/audit_forward_hd_predictor_admission_v01.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
POLICY=json.loads((ROOT/"reference/research/forward_scoring_predictor_admission_policy_v01.json").read_bytes())
ORIGINAL_GENERIC=json.loads((ROOT/"mappings/mapping_library_v1.json").read_bytes())
ORIGINAL_44=json.loads((ROOT/"reference/core/profile_v3_6_v43_mapping_frozen_2026_08_22.json").read_bytes())

class NewHdPolicyTests(unittest.TestCase):
    def test_original_known_splenic_mappings_blocked_for_new_scores(self):
        result=m.audit(POLICY,ORIGINAL_GENERIC,ORIGINAL_44)
        self.assertTrue(result["old_sources_preserved"])
        for x in ("MAP-AUTH-SPLENIC-D01","MAP-AUTH-SPLENIC-D02","AUTH_SPLENIC_SIGNAL"):
            self.assertIn(x,result["new_scored_source_ids_excluded"])
        self.assertTrue(result["not_yet_connected_to_new_scoring_runtime"])

    def test_synthetic_alias_blocks_splenic_as_source(self):
        self.assertTrue(m.source_excluded({"id":"custom_id","chart_feature_predicate":{
            "feature":"authority","operator":"equals_any","values":["Splenic"]}},POLICY))
        self.assertEqual(m.admit({"id":"custom_id","predicate":{"feature":"authority","equals":"Splenic"}},
                                 POLICY,"new_hd_personality_score")["disposition"],
                         "EXCLUDED_FROM_NEW_BEHAVIORAL_SCORE")

    def test_new_emotional_and_selfprojected_same_validation_standard(self):
        for a in ("Emotional","Self Projected"):
            result=m.admit({"id":a,"predicate":{"feature":"authority","equals":a}},
                           POLICY,"new_hd_personality_score")
            self.assertEqual(result["disposition"],
                             "QUARANTINE_ALL_OTHER_AUTHORITY_PROCESSES_UNTIL_COMPARABLE_VALIDATION")

    def test_gateway_to_gate57_somatic_claim_closed(self):
        result=m.admit({"id":"GATE_57_SOMATIC_ALT",
                        "predicate":{"feature":"gate","equals":57}},POLICY,
                       "new_hd_personality_score")
        self.assertEqual(result["disposition"],"EXCLUDED_FROM_NEW_BEHAVIORAL_SCORE")

    def test_historical_and_source_only_still_available(self):
        item={"id":"AUTH_SPLENIC_SIGNAL","predicate":{"feature":"authority","equals":"Splenic"}}
        self.assertEqual(m.admit(item,POLICY,"historical_read_only")["disposition"],
                        "HISTORICAL_READ_ONLY_NEVER_RESCORING")
        self.assertEqual(m.admit(item,POLICY,"source_only_registry")["disposition"],
                        "KEEP_AS_HISTORICAL_DOCTRINAL_DESCRIPTION")

    def test_unknown_operation_rejected(self):
        with self.assertRaises(ValueError):
            m.admit({"id":"UNKNOWN"},POLICY,"legacy_score_mutation")

    def test_original_source_hashes_remain(self):
        self.assertEqual(m.sha(ROOT/"mappings/mapping_library_v1.json"),m.ORIGINAL_GENERIC_SHA)
        self.assertEqual(m.sha(ROOT/"reference/core/profile_v3_6_v43_mapping_frozen_2026_08_22.json"),m.ORIGINAL_44_SHA)

if __name__=="__main__":unittest.main()
