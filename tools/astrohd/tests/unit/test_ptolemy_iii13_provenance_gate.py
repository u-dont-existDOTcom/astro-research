"""Source-qualification gates for Ptolemy III.13 behavior hypotheses.

These tests guarantee that no English historical-source passage has silently
been promoted into a validated natal personality score. All fixtures are
generic and contain no participant birth record or survey.
"""
from __future__ import annotations
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"reference/research/ptolemy_iii13_natal_character_claims_v1.json"


class PtolemyNatalSourceEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(SRC.read_bytes())

    def test_all_thirteen_source_records_unpromoted(self):
        xs=self.data["rules"]
        self.assertEqual(len(xs),13)
        self.assertEqual(len({x["id"] for x in xs}),13)
        self.assertTrue(all(x["automatically_scored"] is False for x in xs))
        self.assertTrue(all(x["empirical_validation"]=="none_in_source" for x in xs))
        self.assertEqual(self.data["source"]["runtime_promotions"],0)

    def test_governors_and_conditions_not_silently_equated_to_aspects(self):
        xs=self.data["rules"]
        governors=[x for x in xs if "DOMINATOR" in x["eligibility"]]
        self.assertGreaterEqual(len(governors),3)
        self.assertTrue(all(x["required_conditions"] for x in xs))
        self.assertTrue(any("govern" in x["source_derived_concept"].lower()
                            for x in xs))

    def test_moon_phase_as_only_direct_geometric_witness(self):
        x=next(x for x in self.data["rules"] if x["id"]=="PTOLEMY-III13-MOON-PHASE")
        self.assertEqual(x["eligibility"],"GEOMETRIC_WITNESS_ONLY_NOT_VALIDATED_BEHAVIOR")
        self.assertEqual(x["automatically_scored"],False)

    def test_historical_text_is_not_greek_collated(self):
        self.assertFalse(self.data["source"]["original_language_collated"])
        self.assertEqual(self.data["source"]["independent_predictions"],0)
        self.assertIn("Tetrabiblos",self.data["source"]["title"])

    def test_natal_character_rule_does_not_imply_psychiatric_diagnosis(self):
        self.assertTrue(any("psychiatric diagnosis" in x.lower()
                            for x in self.data["source_limitations"]))

if __name__=="__main__":unittest.main()
