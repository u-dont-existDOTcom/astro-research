"""Synthetic chart/Authority evidence overlay tests; no real birth or names."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("source_auth",ROOT/"scripts/compare_source_authority_evidence_v01.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def source():
    labels=["REFERENCE"]+[f"C{i:02d}" for i in range(1,15)]
    types=["Splenic"]+["Self Projected"]*4+["Emotional Solar Plexus"]*9+["Self Projected"]
    return {"schema":m.INVENTORY_SCHEMA,
            "comparison_units":[{"private_id":id,
             "chart_midpoint":{"HD":{"authority":authority,"profile":"2/5"}}}
              for id,authority in zip(labels,types)]}
def evidence(**updates):
    return {"status":m.EVIDENCE_STATUS,
            "strict_authority_eligible_episode_counts":{"HD_SPLENIC":0,"HD_EMOTIONAL":0,
                                                         "HD_SELF_PROJECTED":0},
            "episodes_reporting_immediate_bodily_awareness":2,
            **updates}
class SourceAuthorityTests(unittest.TestCase):
    def test_incomplete_body_examples_do_not_create_source_authority_winner(self):
        out=m.study(source(),evidence())
        self.assertFalse(out["any_global_decision_authority_winner"])
        self.assertTrue(all(not r["source_claim_conclusive"] for r in out["outcomes"]))
        self.assertEqual(out["non_decision_immediate_bodily_impressions_reported"],2)
        self.assertEqual(len(out["outcomes"]),15)

    def test_source_strictly_met_does_not_still_declare_true_natal(self):
        ev=evidence()
        ev["strict_authority_eligible_episode_counts"]={"HD_SPLENIC":3,"HD_EMOTIONAL":0,
                                                        "HD_SELF_PROJECTED":0}
        out=m.study(source(),ev)
        self.assertEqual(out["outcomes"][0]["strict_important_decision_condition_episodes"],3)
        self.assertFalse(out["any_global_decision_authority_winner"])

    def test_unsupported_missing_chart_authority_fails_not_negative(self):
        inv=source();inv["comparison_units"][0]["chart_midpoint"]["HD"]["authority"]="Unknown"
        with self.assertRaises(ValueError):m.study(inv,evidence())

    def test_ambiguously_absent_source_counts_fail(self):
        ev=evidence(strict_authority_eligible_episode_counts={"HD_SPLENIC":0})
        with self.assertRaises(ValueError):m.study(source(),ev)

    def test_incomplete_14_candidates_fail(self):
        inv=source();inv["comparison_units"].pop()
        with self.assertRaises(ValueError):m.study(inv,evidence())

    def test_wrong_source_status_fail(self):
        with self.assertRaises(ValueError):m.study(source(),evidence(status="scientifically_validated"))

    def test_never_updates_historical_score(self):
        out=m.study(source(),evidence())
        self.assertFalse(out["historical_hd_23_rule_scores_changed"])
        self.assertIsNone(out["new_western_personality_score"])

if __name__=="__main__":unittest.main()
