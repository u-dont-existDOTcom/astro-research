"""Invented and source-neutral regression cases for Wolf 1559 textual attribution."""
from pathlib import Path
from copy import deepcopy
import importlib.util
import json
import unittest

HERE=Path(__file__).resolve().parents[2]
P=HERE/"scripts/audit_ptolemy_wolf1559_source_adjudication_v01.py"
spec=importlib.util.spec_from_file_location("wolf1559audit",P)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SRC=HERE/"reference/research"

class WitnessContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_raw=(SRC/mod.SOURCE_V03).read_bytes()
        cls.new_raw=(SRC/mod.SOURCE_V04).read_bytes()
    def test_newly_direct_collected_original_and_old_source_unchanged(self):
        audit=mod.audit(self.old_raw,self.new_raw)
        self.assertEqual(audit["status"],"PASS_DIRECT_1559_GREEK_LATIN_WOLF_SOURCE_SEPARATION")
        self.assertEqual(audit["source_1559_pages"],[50,51,52])
        self.assertFalse(audit["human_predictive_validation"])
    def test_original_Ptolemy_has_no_15_degree_orb_licensed(self):
        v=json.loads(self.new_raw)
        w=v["wolf1559_primary_print_source_scan"]
        self.assertFalse(w["licensed_unique_fifth_mode_orb"])
        self.assertFalse(w["source_licensed_universal_15degree_maximum"])
        self.assertEqual(v["wolf1559_relation_to_earlier_editor_report"]["ptolemy_I24_author_own_numeric_cutoff"],"UNSPECIFIED")
    def test_disallow_attribution_laundering_to_original_author(self):
        v=json.loads(self.new_raw)
        v["wolf1559_primary_print_source_scan"]["licensed_unique_fifth_mode_orb"]=True
        with self.assertRaisesRegex(ValueError,"orb"):
            mod.audit(self.old_raw,json.dumps(v).encode())
    def test_disallow_old_historical_evidence_overwrite(self):
        v=json.loads(self.new_raw)
        v["fixed_computational_scope"]["total_times"]=10
        with self.assertRaisesRegex(ValueError,"Prior historical source evidence"):
            mod.audit(self.old_raw,json.dumps(v).encode())
    def test_disallow_deleted_greek_latin_source_page(self):
        v=json.loads(self.new_raw)
        v["wolf1559_primary_print_source_scan"]["page_images_original_sha256"].pop("50")
        with self.assertRaisesRegex(ValueError,"source image"):
            mod.audit(self.old_raw,json.dumps(v).encode())
    def test_disallow_editor_and_commentator_collapsing(self):
        v=json.loads(self.new_raw)
        v["historical_numeric_cutoff_variant_dispositions"][0]["kind"] = v["historical_numeric_cutoff_variant_dispositions"][1]["kind"]
        with self.assertRaisesRegex(ValueError,"source layers collapsed"):
            mod.audit(self.old_raw,json.dumps(v).encode())
    def test_source_register_privacy_and_no_human_score(self):
        v=json.loads(self.new_raw)
        self.assertTrue(v["no_public_birth_or_personal_case_data"])
        self.assertFalse(v["old_automated_scores_updated"])
        self.assertEqual(v["behavioral_claims_licensed_for_automated_rank"],0)
        self.assertEqual(v["human_predictions_prospectively_verified"],0)

if __name__=="__main__":unittest.main()
