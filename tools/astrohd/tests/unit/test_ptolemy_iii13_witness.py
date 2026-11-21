"""Ptolemy III.13 mechanics-only regression fixtures, with no participant chart."""
from __future__ import annotations
from datetime import datetime,timezone
import importlib.util
from pathlib import Path
import unittest

SOURCE=Path(__file__).resolve().parents[2]/"scripts/ptolemy_iii13_source_condition_witness.py"
spec=importlib.util.spec_from_file_location("ptolemy_fact_adapter",SOURCE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
EPHE=Path(__import__("os").environ.get("ASTRO_EPHE", "ephe"))

class PtolemyWitnessTests(unittest.TestCase):
    def test_zodiac_modes(self):
        self.assertEqual([m.modality(i) for i in range(6)],
                         ["cardinal","fixed","mutable","cardinal","fixed","mutable"])

    def test_traditional_conditions_not_character_scores(self):
        self.assertTrue(m.planet_dignity("Moon",1)["exaltation"])
        self.assertTrue(m.planet_dignity("Moon",3)["domicile"])
        self.assertTrue(m.planet_dignity("Venus",11)["exaltation"])
        self.assertTrue(m.planet_dignity("Jupiter",9)["fall"])
        self.assertTrue(m.planet_dignity("Mars",1)["detriment"])
        self.assertFalse(m.planet_dignity("Mercury",9)["exaltation"])

    def test_tight_aspects_do_not_assert_sole_dominator(self):
        xs={"Sun":10.,"Moon":70.,"Mercury":130.,"Venus":190.,"Mars":250.}
        a=m.pair_aspects(xs,3.)
        self.assertEqual(len(a),10)
        self.assertTrue(any(q["aspect"]=="sextile" for q in a))
        with self.assertRaises(ValueError):
            m.pair_aspects(xs,10.)

    def test_utc_requires_zone_and_accepts_aware(self):
        with self.assertRaises(ValueError):m.utc("2000-01-01T12:00:00")
        self.assertEqual(m.utc("2000-01-01T12:00:00Z"),
                         datetime(2000,1,1,12,tzinfo=timezone.utc))

    def test_complete_generic_chart_has_abstentions(self):
        if not all((EPHE/f).is_file() for f in m.EPHE_HASHES):
            self.skipTest("Swiss source assets unavailable")
        m.swe.set_ephe_path(str(EPHE))
        r=m.chart_facts(m.utc("2000-01-01T12:00:00Z"),
                        {"latitude":39.9526,"longitude":-75.1636,"elevation_m":0.})
        self.assertEqual(len(r["traditional_planets"]),7)
        self.assertEqual(len(r["character_focus_source_witnesses"]),2)
        self.assertEqual([f["source_character_focus"] for f in r["character_focus_source_witnesses"]],
                          ["Mercury","Moon"])
        self.assertIsNone(r["character_behavior_score"])
        self.assertFalse(r["empirical_personality_prediction"])
        self.assertEqual(len(r["source_preconditions_missing"]),5)

if __name__=="__main__":unittest.main()
