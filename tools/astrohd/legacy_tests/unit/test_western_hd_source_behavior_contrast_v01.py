"""Source-bound synthetic comparisons; no owner's dates, words or chart in fixtures."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
FILE = ROOT / "scripts/compare_western_hd_behavior_contrast_v01.py"
SPEC = importlib.util.spec_from_file_location("source_behavior_v01", FILE)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

def hd_reference() -> dict:
    return {"type": "Projector", "auth": "Splenic", "profile": "2/5",
            "channels": frozenset({(26, 44), (1, 8)}),
            "gates": frozenset({26, 19, 58}), "centers": frozenset({"Heart"})}

def hd_alternative() -> dict:
    # Deliberately NOT Splenic. Original V3.6 pathway activation depends
    # on channel/gate, while 'parents' are prevalence conditioning only.
    return {"type": "Projector", "auth": "Self Projected", "profile": "3/5",
            "channels": frozenset({(17, 62), (1, 8)}),
            "gates": frozenset({26, 52, 62}), "centers": frozenset({"G"})}

def west(moon_mode: str, aspect: str = "trine") -> dict:
    return {"moon_phase_witness": "waxing_approx_geocentric",
            "character_focus_source_witnesses": [
                {"source_character_focus": "Mercury", "mode": "cardinal", "sign": "Capricorn"},
                {"source_character_focus": "Moon", "mode": moon_mode,
                 "sign": "Taurus" if moon_mode == "fixed" else "Cancer"}],
            "all_seven_planet_tight_aspects_within_3deg": [
                {"planets": ["Mercury", "Jupiter"], "aspect": aspect,
                 "orb_degrees": 1.2}]}

class SourceContrastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph, cls.hd, cls.western = m.load_and_validate(ROOT)
        cls.reference = hd_reference()
        cls.alternative = hd_alternative()

    def result(self):
        return m.compare(self.graph, self.hd, self.western,
                         self.reference, self.alternative,
                         west("fixed", "conjunction"), west("cardinal", "trine"))

    def row(self, result, source_id, facet):
        return next(r for r in result["atomic_source_rules"]
                    if r["source_id"] == source_id and r["facet"] == facet)

    def test_legacy_110_and_western_source_registry_remain_unpromoted(self):
        self.assertEqual(len(self.hd), 44)
        self.assertEqual(len(self.western), 13)
        self.assertEqual(self.graph["original_ranking_sha256"], m.RANK_SHA)
        self.assertTrue(all(r["not_empirically_validated"] for r in self.graph["rules"]))

    def test_1994_like_chart_channel_actives_even_if_prevalence_parent_differs(self):
        mapping = self.hd["CH_17_62_ORGANIZE"]
        rule = next(r for r in self.graph["rules"] if r["source_id"] == mapping["id"])
        report = m.assess_hd(rule, mapping, self.alternative)
        self.assertTrue(report["carrier_present"])
        self.assertFalse(report["requested_prevalence_parent_context_satisfied"])
        self.assertEqual(report["status"], m.HD_ACTIVE)
        self.assertTrue(report["source_parent_context_is_not_carrier_activation_gate"])

    def test_gate_52_is_present_for_self_projected_alternative(self):
        source = self.hd["GATE_52_FOCUS"]
        rule = next(r for r in self.graph["rules"] if r["source_id"] == source["id"])
        self.assertTrue(m.assess_hd(rule, source, self.alternative)["carrier_present"])
        self.assertFalse(m.assess_hd(rule, source, self.reference)["carrier_present"])

    def test_gate_26_persuasion_carrier_shared_no_second_point(self):
        result = self.result()
        row = self.row(result, "GATE_26_PERSUASION_ALT", "persuasive_ability")
        self.assertTrue(row["reference"]["carrier_present"])
        self.assertTrue(row["alternative"]["carrier_present"])
        self.assertEqual(row["contrast"], "SHARED_CARRIER_OR_SHARED_ABSENCE")
        self.assertEqual(row["reference"]["status"], m.HD_PARTIAL)
        self.assertIsNone(row["reference"]["numeric_contribution"])
        self.assertEqual(row["reference"]["dependency_cluster"],
                         self.row(result, "CH_26_44_ENTERPRISE", "persuasive_ability")
                         ["reference"]["dependency_cluster"])

    def test_compound_enterprise_never_auto_satisfies_detection(self):
        report = self.result()
        for facet in ("persuasive_ability", "commercial_leverage",
                      "early_pattern_recognition"):
            row = self.row(report, "CH_26_44_ENTERPRISE", facet)
            self.assertEqual(row["reference"]["status"], m.HD_COMPOUND)
            self.assertIsNone(row["reference"]["behavior_confirmed"])
            self.assertIsNone(row["reference"]["numeric_contribution"])
            self.assertEqual(row["alternative"]["status"], m.HD_ABSENT)

    def test_moon_mode_contrast_cannot_become_a_western_score(self):
        report = self.result()
        fixed = self.row(report, "PTOLEMY-III13-ZODIAC-MODES", "moon_fixed")
        cardinal = self.row(report, "PTOLEMY-III13-ZODIAC-MODES", "moon_solstitial")
        self.assertTrue(fixed["reference"]["carrier_present"])
        self.assertTrue(cardinal["alternative"]["carrier_present"])
        self.assertFalse(fixed["alternative"]["carrier_present"])
        self.assertEqual(fixed["reference"]["status"], m.SOURCE_WITNESS)
        self.assertIsNone(fixed["reference"]["numeric_contribution"])
        self.assertEqual(report["personality_accuracy_comparison"], "NOT_YET_COMPUTABLE")

    def test_solstitial_not_equated_to_every_cardinal_sign(self):
        test = west("cardinal")
        moon = test["character_focus_source_witnesses"][1]
        self.assertEqual(moon["sign"], "Cancer")
        self.assertTrue(m._west_geometry(test, "moon_solstitial", "Cancer|Capricorn"))
        moon["sign"] = "Aries"  # equinoctial, cardinal, but NOT solstitial
        self.assertFalse(m._west_geometry(test, "moon_solstitial", "Cancer|Capricorn"))
        test["character_focus_source_witnesses"][0]["sign"] = "Libra"
        self.assertFalse(m._west_geometry(test, "mercury_solstitial", "Cancer|Capricorn"))

    def test_shared_jupiter_mercury_does_not_prove_soul_governor(self):
        result = self.result()
        a = self.row(result, "PTOLEMY-III13-JUPITER-MERCURY", "philosophical_discourse")
        self.assertEqual(a["contrast"], "SHARED_CARRIER_OR_SHARED_ABSENCE")
        self.assertIn("full_governance", a["reference"]["unresolved_source_conditions"])
        self.assertIsNone(a["reference"]["behavior_confirmed"])

    def test_unresolved_sole_mercury_does_not_create_false_negative(self):
        row = self.row(self.result(), "PTOLEMY-III13-SOLE-MERCURY", "technical_inventiveness")
        self.assertEqual(row["contrast"], "UNRESOLVED_PREDICATE")
        self.assertEqual(row["reference"]["status"], m.WESTERN_ABSTAIN)
        self.assertIsNone(row["alternative"]["carrier_present"])

    def test_absent_carrier_is_not_negative_personality_evidence(self):
        rule = next(x for x in self.graph["rules"] if x["source_id"] == "GATE_19_NEEDS")
        result = m.assess_hd(rule, self.hd["GATE_19_NEEDS"], self.alternative)
        self.assertEqual(result["status"], m.HD_ABSENT)
        self.assertIsNone(result["behavior_contradicted"])

    def test_missing_carrier_feature_requires_abstention(self):
        rule = next(x for x in self.graph["rules"] if x["source_id"] == "GATE_52_FOCUS")
        r = m.assess_hd(rule, self.hd["GATE_52_FOCUS"], {"type": "Projector"})
        self.assertEqual(r["status"], "ABSTAIN_MISSING_HD_FEATURE")
        self.assertIsNone(r["carrier_present"])

    def test_western_source_promotion_rejected(self):
        western_sources = {k: {**v} for k,v in self.western.items()}
        western_sources["PTOLEMY-III13-JUPITER-MERCURY"]["automatically_scored"] = True
        with self.assertRaisesRegex(RuntimeError,"illegally"):
            m.compare(self.graph, self.hd, western_sources, self.reference,
                      self.alternative, west("fixed"), west("cardinal"))

    def test_report_frozen_old_scores_and_no_new_ranking(self):
        r = self.result()
        self.assertEqual(len(r["atomic_source_rules"]), 15)
        self.assertFalse(r["complete_century_joint_coverage"])
        self.assertIsNone(r["combined_rank"])
        self.assertIsNone(r["new_hd_score"])
        self.assertIsNone(r["new_western_score"])
        self.assertEqual(r["frozen_original_ranking_sha256"], m.RANK_SHA)
        self.assertEqual(len(r["unique_dependency_clusters"]), 6)
        self.assertFalse(any(x["reference"]["numeric_contribution"] is not None
                             for x in r["atomic_source_rules"]))

    def synthetic_coding(self):
        return {"schema": "private_v37_profile_review_of_historical_hd_44_rules_v1",
                "source_profile_sha256":
                   "6f3f64143f83757636c34b7265d3980b85bb8643cc2ce975de26636431281295",
                "judgments": {id: {"status": "directly_reported_observable",
                                   "rationale": "synthetic secret not to leak"}
                              for id in self.hd}}

    def test_private_target_overlap_separate_from_source_carrier(self):
        coding = self.synthetic_coding()
        report = m.overlay_private_development_evidence(
            self.result(), self.graph, self.hd, coding)
        source = self.row(report, "CH_17_62_ORGANIZE", "reusable_technical_structure")
        self.assertEqual(source["target_older_coding"],
                         "OLDER_DIRECT_SELF_REPORT_WHOLE_RULE_DEV_ONLY")
        self.assertEqual(source["reference"]["post_exposure_coincidence"],
                         "DIRECT_SELF_REPORT_WITH_NO_CARRIER_NOT_CONTRADICTION")
        self.assertEqual(source["alternative"]["post_exposure_coincidence"],
                         "DIRECT_SELF_REPORT_AND_CARRIER_PRESENT_DEV_ONLY")
        self.assertIsNone(report["combined_rank"])
        self.assertIsNone(report["new_hd_score"])
        self.assertTrue(report["private_coding_layer_has_no_impact_on_ranking"])
        self.assertNotIn("synthetic secret", str(report))

    def test_persuasion_remains_shared_partial_and_compound_abstains(self):
        report = m.overlay_private_development_evidence(
            self.result(), self.graph, self.hd, self.synthetic_coding())
        gate = self.row(report, "GATE_26_PERSUASION_ALT", "persuasive_ability")
        self.assertEqual(gate["target_older_coding"],
                         "DIRECT_PARTIAL_PERSUASION_CAPACITY_NO_NEW_SCORE")
        self.assertEqual(gate["reference"]["post_exposure_coincidence"],
                         gate["alternative"]["post_exposure_coincidence"])
        ch = self.row(report, "CH_26_44_ENTERPRISE", "early_pattern_recognition")
        self.assertEqual(ch["target_older_coding"],
                         "COMPOUND_UNRESOLVED_NO_FULL_RULE_VALIDATION")
        self.assertEqual(ch["reference"]["post_exposure_coincidence"],
                         "ABSTAIN_NO_WHOLE_SOURCE_QUALIFIED_TARGET_MATCH")

    def test_wrong_original_target_profile_and_44_rule_coverage_fail(self):
        coding = self.synthetic_coding()
        coding["source_profile_sha256"] = "0"*64
        with self.assertRaisesRegex(RuntimeError, "profile source"):
            m.overlay_private_development_evidence(
                self.result(), self.graph, self.hd, coding)
        coding = self.synthetic_coding()
        coding["judgments"].pop("GATE_19_NEEDS")
        with self.assertRaisesRegex(RuntimeError, "44 HD"):
            m.overlay_private_development_evidence(
                self.result(), self.graph, self.hd, coding)

    def test_answers_are_not_reasked(self):
        answered = set(self.graph["answered_questions"])
        ids = {x["id"] for x in self.graph["new_unanswered_questions"]}
        self.assertTrue(answered.isdisjoint(ids))
        self.assertTrue({"Q-HDB2", "Q-HDB4", "Q-HDB6"} <= answered)
        self.assertTrue(all("counter" in q["neutral_prompt"] or
                            "mistaken" in q["neutral_prompt"] or
                            "contrasting" in q["neutral_prompt"]
                            for q in self.graph["new_unanswered_questions"]))

if __name__ == "__main__":
    unittest.main()
