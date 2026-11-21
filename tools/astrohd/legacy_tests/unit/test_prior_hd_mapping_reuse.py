"""Verify no prior HD mapping source has been dropped or promoted implicitly."""
from __future__ import annotations
import copy,importlib.util,json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"scripts/audit_prior_hd_mapping_reuse.py"
sp=importlib.util.spec_from_file_location("prior_hd_reuse",SRC)
audit=importlib.util.module_from_spec(sp)
sp.loader.exec_module(audit)
LEDGER=ROOT/"reference/research/prior_hd_mapping_reuse_ledger_20261119.json"

class PriorHDMappingPreservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=json.loads(LEDGER.read_text())

    def test_all_prior_mappings_are_accounted_for(self):
        result=audit.audit(ROOT,self.ledger)
        self.assertEqual(result["all_entries_accounted_for"],110)
        self.assertEqual(result["source_counts"],{"v1":82,"v43_aug":24,"v2_candidates":4})
        self.assertTrue(result["no_automatic_source_promotion"])

    def test_missing_source_id_is_fail_closed(self):
        x=copy.deepcopy(self.ledger)
        x["entries"]=x["entries"][:-1]
        with self.assertRaisesRegex(RuntimeError,"coverage incomplete"):
            audit.audit(ROOT,x)

    def test_duplicate_source_id_fails(self):
        x=copy.deepcopy(self.ledger)
        x["entries"].append(x["entries"][0])
        with self.assertRaisesRegex(RuntimeError,"Duplicate"):
            audit.audit(ROOT,x)

    def test_no_unreviewed_promotion_allowed(self):
        x=copy.deepcopy(self.ledger)
        x["entries"][0]["accepted_into_new_model"]=True
        with self.assertRaisesRegex(RuntimeError,"improperly promoted"):
            audit.audit(ROOT,x)

    def test_historical_status_cannot_be_rewritten(self):
        x=copy.deepcopy(self.ledger)
        x["entries"][0]["source_status"]="validated_blind"
        with self.assertRaisesRegex(RuntimeError,"status was changed"):
            audit.audit(ROOT,x)

    def test_historical_source_digest_required(self):
        x=copy.deepcopy(self.ledger)
        x["source_reference"][0]["digest"]="0"*64
        with self.assertRaisesRegex(RuntimeError,"Source HD mapping changed"):
            audit.audit(ROOT,x)

if __name__=="__main__":unittest.main()
