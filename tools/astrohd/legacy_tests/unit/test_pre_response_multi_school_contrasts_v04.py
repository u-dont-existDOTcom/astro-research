"""Synthetic source-witness contrasts: multiple Western schools and HD, no real chart or owner."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("multi_school",ROOT/"scripts/build_pre_response_multi_school_source_crosswalk_v04.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
BANK=json.loads((ROOT/"reference/research/astrohd_multi_school_contrast_question_bank_v04.json").read_bytes())

def synthetic_chart(name, profile="2/5", moon="Taurus",merc="Capricorn",asc="Capricorn",channels=(),cross=(19,33,44,24),square=False):
    h={"type":"Projector","profile":profile,"authority":"Splenic",
       "complete_channels":list(channels),
       "cross_sun_earth_activations":dict(zip(("personality:sun","personality:earth","design:sun","design:earth"),
                                               ({"gate":g,"line":2} for g in cross)))}
    planets={x:{"sign":"Aries","essential_dignity":{"domicile":False,"exaltation":False,"detriment":False,"fall":False}}
             for x in ("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn")}
    planets["Moon"]["sign"]=moon;planets["Mercury"]["sign"]=merc;planets["Saturn"]["sign"]="Scorpio"
    aspects=[{"planets":["Mars","Sun"],"aspect":"square","orb_degrees":.5}] if square else []
    return {"private_id":name,"chart_midpoint":{"HD":h,"Western":{"source_witness":{
        "traditional_planets":planets,"ascendant_sign":asc,
        "all_seven_planet_tight_aspects_within_3deg":aspects}}}}
def collection():
    items=[synthetic_chart("REFERENCE")]
    items.extend(synthetic_chart(f"C{i:02}") for i in range(1,15))
    return {"schema":"private_astrologer_complete_western_hd_14_better_hd_intervals_inventory_v01",
            "comparison_units":items}

class MultiSchoolTests(unittest.TestCase):
    def test_ten_questions_are_unique_nonleading_and_unscored(self):
        m.audit_question_bank(BANK)
        ids=[x["id"] for x in BANK["questions"]]
        self.assertEqual(ids,list(f"C{i:02}" for i in range(1,11)))
        self.assertTrue(all("counterexample" in x["response_shape"].lower() or
                            "exception" in x["response_shape"].lower() or
                            "opposite" in x["response_shape"].lower()
                            for x in BANK["questions"] if x["id"] in ("C01","C02","C03","C04","C07","C08","C09","C10")))

    def test_full_old_shortlist_all_15_required(self):
        x=collection()
        result=m.run(BANK,x)
        self.assertEqual(result["case_count"],15)
        self.assertFalse(result["source_years_or_exact_private_birth_metadata_included"])
        self.assertTrue(result["no_scored_new_model"])
        self.assertFalse(result["full_continuous_Western_interval_coverage"])
        x["comparison_units"].pop()
        with self.assertRaisesRegex(ValueError,"Missing old-chart"):
            m.run(BANK,x)

    def test_hd_frozen_source_carriers_not_trait_predictions(self):
        c=synthetic_chart("REFERENCE",profile="3/5",
                          channels=("13-33","17-62","19-49","30-41"))
        r=m.case_witness(c)
        self.assertTrue(r["source_feature_tags"]["HD_EXPERIENCE_PRIVACY_CH13_33"])
        self.assertTrue(r["source_feature_tags"]["HD_RECIPROCITY_VALUES_CH19_49"])
        self.assertTrue(r["source_feature_tags"]["HD_EXPERIENCE_CYCLE_CH30_41"])
        self.assertTrue(r["source_feature_tags"]["HD_DETAILS_CH17_62"])
        self.assertTrue(r["source_feature_tags"]["HD_3rd_line_profile"])
        self.assertEqual(r["chart_to_behavior_fit"],"UNSCORED")

    def test_ptolemy_sign_modes_distinguish_solstitial_from_equinoctial(self):
        actual=m.case_witness(synthetic_chart("REFERENCE",moon="Taurus",merc="Capricorn"))
        old=m.case_witness(synthetic_chart("C01",moon="Aries",merc="Virgo"))
        self.assertEqual(actual["PTOLEMY_III13_PARTIAL"]["Moon_sign_class"],"fixed")
        self.assertEqual(actual["PTOLEMY_III13_PARTIAL"]["Mercury_sign_class"],"solstitial")
        self.assertEqual(old["PTOLEMY_III13_PARTIAL"]["Moon_sign_class"],"equinoctial")
        self.assertEqual(old["PTOLEMY_III13_PARTIAL"]["Mercury_sign_class"],"bicorporeal")

    def test_lilly_asc_ruler_not_manners_ruler(self):
        r=m.case_witness(synthetic_chart("REFERENCE",asc="Capricorn"))
        z=r["LILLY_MANNERS_PARTIAL"]
        self.assertEqual(z["ASC_ruler"],"Saturn")
        self.assertTrue(z["manner_significator_not_necessarily_ASC_ruler"])
        self.assertEqual(z["exact_house_boundary_coverage"],"ONE_ILLUSTRATIVE_MIDPOINT")

    def test_modern_tight_sun_mars_square_is_geometry_not_personality(self):
        r=m.case_witness(synthetic_chart("C10",square=True))
        self.assertTrue(r["source_feature_tags"]["WEST_CLOSE_SUN_MARS_SQUARE"])
        self.assertIsNone(r["negative_survey_evidence"])
        self.assertEqual(r["MODERN_WESTERN_PARTIAL"]["outer_planet_source"],
                         "SEPARATE_PINNED_OPTIONAL_V01_NOT_REEVALUATED_BY_THIS_CROSSWALK")

    def test_question_bank_avoids_retrying_previous_answers(self):
        qtxt=" ".join(q["text"].lower() for q in BANK["questions"])
        for phrase in ("what percentage of your effort went into inventing",
                       "where does your immediate splenic yes",
                       "after meaningful social interaction do you need to be alone",
                       "have you ever persuaded someone"):
            self.assertNotIn(phrase,qtxt)
        self.assertTrue(BANK["method_scope"].startswith("The 14 historical"))

    def test_new_profile_questions_do_not_claim_human_prediction(self):
        result=m.run(BANK,collection())
        self.assertTrue(result["no_behavioral_prediction_probability"])
        self.assertTrue(result["no_chart_absence_is_behavioral_negation"])
        self.assertTrue(result["no_natal_chart_priority_from_essential_dignity"])

if __name__=="__main__":
    unittest.main()
