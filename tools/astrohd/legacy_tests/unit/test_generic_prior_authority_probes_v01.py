"""Source-exact audit of existing unresolved questions. No person or birth chart."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"mappings/mapping_library_v1.json"
PROBES=ROOT/"reference/research/generic_prior_authority_probes_reuse_v01.json"
REPORT=json.loads(PROBES.read_bytes())
MAPS=json.loads(SOURCE.read_bytes())

class GenericProbeTests(unittest.TestCase):
    def test_source_sha_and_ids(self):
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                         REPORT["source_sha256"])
        self.assertEqual({x["id"] for x in REPORT["questions"]},
                         {"R03","R06","R07","R08"})

    def test_all_old_items_are_unresolved_no_chart_predicate(self):
        byid={m["mapping_id"]:m for m in MAPS["mappings"]}
        for item in REPORT["questions"]:
            old=byid[item["mapping_id"]]
            self.assertEqual(old["status"],"unresolved")
            self.assertIsNone(old.get("chart_feature_predicate"))
            self.assertIn(item["id"],old["question_ids"])
            self.assertFalse(item["scored"])

    def test_source_questions_preserved_and_relevant(self):
        byid={m["mapping_id"]:m for m in MAPS["mappings"]}
        tokens={"R03":"after","R06":"reasoning","R07":"sleep","R08":"reversible"}
        for item in REPORT["questions"]:
            self.assertIn(tokens[item["id"]],byid[item["mapping_id"]]["behavioral_statement"].lower())

    def test_no_implicit_promotion_from_an_episode(self):
        self.assertFalse(REPORT["requirements"]["new_frozen_chart_mapping_added"])
        self.assertTrue(REPORT["requirements"]["do_not_claim_splenic_authority_if_reported_yes"])
        self.assertIsNone(REPORT["requirements"]["chart_feature_predicate"])
        self.assertIsNone(REPORT["requirements"]["contradiction_rule"])

if __name__=="__main__":unittest.main()
