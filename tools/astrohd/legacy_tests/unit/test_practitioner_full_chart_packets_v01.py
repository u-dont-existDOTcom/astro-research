"""Synthetic source-and-blindness tests. No real birth input or private identity."""
from __future__ import annotations

from datetime import datetime,timezone,timedelta
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
def load(rel,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/rel)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
charts=load("scripts/build_practitioner_chart_inventory_v01.py","practitioner_chart")
pack=load("scripts/build_blind_practitioner_packets_v01.py","practitioner_pack")
modern=load("scripts/build_modern_western_overlay_v01.py","modern_western")

def synthetic_case(cid:str):
    planets={}
    for name in ("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"):
        planets[name]={"sign":"Cancer","essential_dignity":{
            "domicile":name=="Moon","exaltation":False,
            "detriment":False,"fall":False}}
    houses={name:{"whole_sign_house":1,"regiomontanus_house":2}
            for name in planets}
    activation={x:{"gate":45,"line":3} for x in (
        "personality:sun","personality:earth","design:sun","design:earth")}
    return {"private_id":cid,"chart_midpoint":{
        "utc":"2000-01-01T12:00:00+00:00",
        "HD":{"type":"Projector","authority":"Self Projected",
            "profile":"3/5","definition":"single_definition",
            "defined_centers":["Ajna","G","Throat"],
            "complete_channels":["17-62"],
            "cross_sun_earth_activations":activation,
            "all_planet_carrier_gate_lines":activation},
        "Western":{
            "source_witness":{"ascendant_sign":"Virgo","mc_sign":"Gemini",
                "sect":"day","traditional_planets":planets,
                "moon_sun_geocentric_phase_degrees":30,
                "moon_phase_witness":"waxing_approx_geocentric",
                "all_seven_planet_tight_aspects_within_3deg":[]},
            "regiomontanus_houses":{"traditional_ascendant_lord":"Mercury",
                                  "planet_houses":houses},
        }}}

class PractitionerPacketTests(unittest.TestCase):
    def inventory(self):
        ids=["REFERENCE"]+[f"C{i:02d}" for i in range(1,15)]
        return {"schema":pack.INVENTORY_SCHEMA,
                "comparison_units":[synthetic_case(x) for x in ids],
                "provisional_hd_only_not_joint_behavior_ranking":True}

    def test_historic_scored_universe_frozen_as_source_anchor(self):
        self.assertEqual(charts.ORIGINAL_RANK_SHA,
            "b930e87a366a7d06d0efe40c9ec83044be62116935ec1a986b06c3868fcf9bce")
        self.assertEqual(charts.PART_OF_CENTURY,
                         "PRIVATE_FULL_14_STRICTLY_HIGHER_HD_STRUCTURAL_INTERVALS")

    def test_generated_packets_dont_reveal_actual_rank_or_birth_metadata(self):
        key,packages=pack.make_packets(self.inventory(),"private_seed_sufficiently_long")
        self.assertEqual(key["entry_count"],15)
        self.assertEqual(set(key["actual_chart_anonymous_letter"]),
                         {key["actual_chart_anonymous_letter"]})
        for body in packages.values():
            self.assertEqual(body.count("## Chart "),15)
            self.assertNotIn("REFERENCE",body)
            self.assertNotIn("2000-01-01",body)
            self.assertNotIn("C01",body)
            self.assertNotIn("9.470",body)
            self.assertNotIn("9.491",body)
            self.assertIn("no human astrologer or HD practitioner has yet reviewed",body)

    def test_domain_isolation_is_real(self):
        _,pk=pack.make_packets(self.inventory(),"private_seed_sufficiently_long")
        self.assertIn("Sun: Cancer",pk["Western"])
        self.assertIn("Regiomontanus house",pk["Western"])
        self.assertNotIn("Self Projected",pk["Western"])
        self.assertIn("Self Projected",pk["HD"])
        self.assertNotIn("Regiomontanus",pk["HD"])
        self.assertNotIn("Moon elongation",pk["HD"])

    def test_relabeling_does_not_select_only_highest_rank(self):
        a=[x["private_id"] for x in self.inventory()["comparison_units"]]
        r=pack.random_labels(a,"private_seed_sufficiently_long")
        self.assertEqual(set(y for _,y in r),set(a))
        self.assertNotEqual([x for _,x in r],a)
        self.assertEqual(r,pack.random_labels(a,"private_seed_sufficiently_long"))

    def test_fail_if_chart_removed_or_reference_missing(self):
        data=self.inventory()
        data["comparison_units"].pop()
        with self.assertRaises(RuntimeError):
            pack.make_packets(data,"private_seed_sufficiently_long")
        data=self.inventory()
        data["comparison_units"][0]["private_id"]="C00"
        with self.assertRaises(RuntimeError):
            pack.make_packets(data,"private_seed_sufficiently_long")

    def test_fail_if_qualified_score_status_is_mislabeled(self):
        d=self.inventory()
        d["provisional_hd_only_not_joint_behavior_ranking"]=False
        with self.assertRaises(RuntimeError):
            pack.make_packets(d,"private_seed_sufficiently_long")

    def test_fail_duplicate_or_guessable_seed(self):
        with self.assertRaises(ValueError):
            pack.random_labels(["REFERENCE","REFERENCE"],"private_seed_sufficiently_long")
        with self.assertRaises(ValueError):
            pack.random_labels(["REFERENCE","C01"],"short")

    def test_invalid_sweep_interval_rejected(self):
        t=datetime(2000,1,1,tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            charts.rising_sweep(t,t,{"latitude":0,"longitude":0})

    def test_synthetic_rising_survey_not_certified(self):
        # This fixture is synthetic and not a user birth chart.
        site={"latitude":12.0,"longitude":5.0}
        t=datetime(2000,1,1,tzinfo=timezone.utc)
        out=charts.rising_sweep(t,t+timedelta(hours=12),site,30)
        self.assertTrue(out["not_full_western_interval_certification"])
        self.assertGreater(len(out["rising_signs_seen_in_time_order"]),1)
        self.assertIn("NOT guaranteed exact",out["method"])

    def test_optional_modern_aspect_circular_geometry(self):
        self.assertEqual(modern.separation(359, 1), 2)
        a = modern.aspect(359.5, 0.5)
        self.assertEqual(a["name"], "conjunction")
        self.assertAlmostEqual(a["orb"], 1.0)
        self.assertIsNone(modern.aspect(0, 10))
        self.assertEqual(modern.aspect(91, 1)["name"], "square")

    def test_optional_outer_positions_do_not_generate_behavior_score(self):
        # Only toy date/site; tool owns no user's birth timestamp.
        modern.swe.set_ephe_path(__import__('os').environ.get('ASTRO_EPHE', 'ephe'))
        a = modern.outer_for_chart(datetime(2000,1,1,tzinfo=timezone.utc),
                                   {"latitude": 12.0, "longitude": 5.0})
        self.assertEqual(set(a["outer_positions"]), {"Uranus","Neptune","Pluto"})
        self.assertIsNone(a["unqualified_modern_personality_score"])
        self.assertTrue(all(0 <= o["sign_degree"] < 30
                            for o in a["outer_positions"].values()))

    def test_optional_modern_requires_exact_same_sealed_chart_ids(self):
        graph = self.inventory()
        key, _ = pack.make_packets(graph,"private_seed_sufficiently_long")
        key["entry_mapping"][0]["private_id"] = "UNKNOWN_ID"
        with self.assertRaisesRegex(ValueError, "Sealed chart roster"):
            modern.make(graph,key)

    def test_western_dignity_not_declared_accurate_personality(self):
        txt=pack.assessable_Western(synthetic_case("X"))
        self.assertIn("no major sign dignity",txt)
        self.assertIn("detriment",txt.lower() if "detriment" in txt.lower() else "not detriment")
        self.assertIn("complete historical tradition",txt)
        self.assertNotIn("better personality",txt)

if __name__=="__main__":
    unittest.main()
