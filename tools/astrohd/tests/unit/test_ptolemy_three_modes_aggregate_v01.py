"""Ptolemy source-incomplete three-mode full-century numerical report sanity checks.

A test of provenance and mechanical aggregation, NEVER a natal accuracy test.
"""
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/"reference/research/ptolemy_iii13_three_modes_century_aggregate_v01.json"
MODES=ROOT/"reference/research/ptolemy_iii13_five_domination_mode_source_adjudication_v01.json"


class PtolemyThreeModePublicAggregateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads(EVIDENCE.read_text(encoding="utf8"))
        cls.sources=json.loads(MODES.read_text(encoding="utf8"))

    def test_own_research_is_not_a_character_governor_calculator(self):
        self.assertTrue(self.report["no_source_complete_personality_model"])
        self.assertEqual(self.report["independently_verified_natal_personality_predictions"],0)
        self.assertEqual(self.report["source_types"]["unresolved"][:2],["terms","phase_or_aspect"])
        self.assertEqual(self.sources["behavioral_claims_licensed_for_automated_rank"],0)

    def test_frozen_binary_provenance(self):
        self.assertTrue(self.report["source_binary_shards_SHA256_verified"])
        for digest in list(self.report["private_verified_receipt_sha256"].values())+list(
            self.report["source_verified_manifests"].values()):
            self.assertEqual(len(digest),64)
            int(digest,16)

    def test_ruler_mode_counts_reconcile(self):
        c=self.report["counts"]
        n=self.report["sample_population"]["n"]
        self.assertEqual(n,3506400)
        self.assertEqual(c["same_Mercury_Moon_sign"],288789)
        self.assertEqual(c["same_domicile_ruler"],534191)
        self.assertEqual(c["any_shared_domicile_or_exaltation_candidate"],1026641)
        self.assertEqual(c["three_mode_primary_triplicity_candidate_certain"],1844501)
        self.assertEqual(c["three_mode_any_source_coruler_candidate_certain"],2142360)
        self.assertEqual(c["co_ruler_v_primary_difference_certain"],297859)
        self.assertEqual(c["sect_horizon_undecidable_at_0_1_degree"],5049)
        self.assertEqual(
            c["three_mode_any_source_coruler_candidate_certain"]-
            c["three_mode_primary_triplicity_candidate_certain"],
            c["co_ruler_v_primary_difference_certain"])

    def test_horizon_unknown_is_not_false_negative(self):
        c=self.report["counts"]
        self.assertGreater(c["sect_horizon_undecidable_at_0_1_degree"],0)
        self.assertLess(c["earlier_two_mode_shared_within_sect_horizon_undecidable"],
            c["sect_horizon_undecidable_at_0_1_degree"])
        self.assertIn("5,049" ,(ROOT.parent.parent/"docs/astrohd/ptolemy_iii13_three_mode_century_source_audit_20261122.md").read_text())

    def test_all_five_families_registered_and_two_unsatisfied(self):
        modes=self.sources["five_domination_modes"]
        self.assertEqual(len(modes),5)
        self.assertEqual({x["id"] for x in modes},
             {"DOMICILE","EXALTATION","TRIPLICITY","TERMS","PHASE_OR_ASPECT"})
        self.assertIn("MISSING",next(x for x in modes if x["id"]=="TERMS")["status"])
        self.assertIn("MISSING",next(x for x in modes if x["id"]=="PHASE_OR_ASPECT")["status"])
        self.assertFalse(self.sources["old_automated_scores_updated"])

    def test_no_personal_birth_data_in_new_public_registries(self):
        for s in (EVIDENCE.read_text(),MODES.read_text()):
            self.assertNotRegex(s, r"/home/[^/\s]+/(?:Documents|Downloads)/")
            self.assertNotIn("@gmail.com",s)
            self.assertNotIn("1985",s)
        self.assertFalse(self.report["owner_or_thirdparty_birth_details"])
        self.assertTrue(self.sources["no_public_birth_or_personal_case_data"])

if __name__=="__main__":unittest.main()
