"""Mechanical century outputs must reconcile exact denominators and scopes."""
from __future__ import annotations

from pathlib import Path
import json
import unittest

DATA=Path(__file__).resolve().parents[2]/"reference/research/century_mechanical_lilly_hd_asc_aggregate_v01.json"

class AstroCenturyActualCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=json.loads(DATA.read_bytes())
    def test_exact_declared_sample_denominators(self):
        l=self.r["lilly_first_rung"];h=self.r["hd_western_rising_overlap"]
        self.assertEqual(l["sample_count"],3506400)
        self.assertEqual(h["sample_count"],3506400)
        self.assertEqual(h["hd_state_count"],288908)
    def test_lilly_disjoint_partition(self):
        l=self.r["lilly_first_rung"];c=l["counts_by_category"]
        names=["none_in_asc_sign","one_nonlum_only","multiple_nonlum_only","luminaries_only","nonlum_and_luminaries"]
        self.assertEqual(sum(c[k] for k in names),3506400)
        self.assertEqual(l["any_classical_planet_in_asc_sign"],3506400-c["none_in_asc_sign"])
    def test_lilly_count_not_a_manners_score(self):
        self.assertFalse(self.r["lilly_first_rung"]["manners_significator_scored"])
        self.assertFalse(self.r["lilly_first_rung"]["complete_lilly_intercepted_sign_or_house_rule"])
    def test_hd_structural_sign_histogram_consistency(self):
        h=self.r["hd_western_rising_overlap"]
        c={int(k):v for k,v in h["unique_state_sampled_asc_sign_histogram"].items()}
        self.assertEqual(sum(c.values()),h["hd_state_count"])
        self.assertEqual(sum(v for k,v in c.items() if k>=2),h["states_with_two_or_more_sampled_asc_signs"])
    def test_unresolved_grid_count_not_disappeared(self):
        h=self.r["hd_western_rising_overlap"]
        self.assertEqual(h["unresolved_samples"],125)
        self.assertLessEqual(h["resolved_samples_with_multi_ASC_state"],h["sample_count"]-h["unresolved_samples"])
        self.assertTrue(h["not_continuous"])
    def test_both_data_shards_hash_checked(self):
        self.assertTrue(self.r["lilly_first_rung"]["source_data_sha256_reverified"])
        self.assertTrue(self.r["hd_western_rising_overlap"]["source_data_sha256_reverified"])
    def test_no_predictive_accuracy_from_mechanical_counts(self):
        self.assertEqual(self.r["human_outcome_validation_count"],0)
        self.assertFalse(self.r["personally_identifiable_records_included"])
        self.assertIn("a probability of correct personality prediction",self.r["stats_are_not"])
    def test_private_source_receipt_hashes_have_frozen_length(self):
        for hashhex in self.r["sources"].values():
            self.assertEqual(len(hashhex),64)
            int(hashhex,16)
if __name__=="__main__":unittest.main()
