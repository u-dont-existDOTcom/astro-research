"""Mars–Venus retrospective source witness: synthetic alternatives only."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("marsvenus",ROOT/"scripts/audit_ptolemy_mars_venus_conditional_witness_v01.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
SOURCE=json.loads((ROOT/"reference/research/ptolemy_iii13_natal_character_claims_v1.json").read_bytes())

def data(reforb=.45,with_alternative=False):
    records=[]
    for i in range(15):
        label="REFERENCE" if i==0 else f"SYNTH_{i:02d}"
        on=i==0 or (with_alternative and i==4)
        orb=reforb if i==0 else 2.9
        asp=[{"aspect":"conjunction","planets":["Mars","Venus"],
              "orb_degrees":orb}] if on else []
        records.append({"private_id":label,"chart_midpoint":{"Western":{
            "source_witness":{"all_seven_planet_tight_aspects_within_3deg":asp}}}})
    return {"schema":m.INVENTORY_SCHEMA,"comparison_units":records}

class MarsVenusTests(unittest.TestCase):
    def test_mars_venus_source_is_preexisting_and_unscored(self):
        r=m.source_eligibility(SOURCE)
        self.assertFalse(r["automatically_scored"])
        self.assertEqual(r["eligibility"],"UNRESOLVED_CONDITIONAL_GOVERNANCE")

    def test_15_sources_and_candidate_count(self):
        r=m.audit(SOURCE,data(with_alternative=True))
        self.assertEqual(r["candidate_midpoints_scanned"],14)
        self.assertEqual(r["old_hd_selected_candidate_midpoints_close_conjunction"],1)
        self.assertTrue(r["feature_examination_selected_after_owner_personal_report"])
        self.assertTrue(r["no_natal_score_change"])
        self.assertFalse(r["no_proof_of_western_or_joint_rank_one"] is False)

    def test_no_bespoke_winner_from_an_exact_aspect(self):
        r=m.audit(SOURCE,data(reforb=.1))
        self.assertTrue(r["actual_reference_close_conjunction"])
        self.assertEqual(r["reference_orb_degrees"],.1)
        self.assertEqual(r["old_hd_selected_candidate_midpoints_close_conjunction"],0)
        self.assertTrue(r["no_proof_of_western_or_joint_rank_one"])

    def test_invalid_doubled_aspect_fails(self):
        inv=data()
        v=inv["comparison_units"][0]["chart_midpoint"]["Western"]["source_witness"]["all_seven_planet_tight_aspects_within_3deg"]
        v.append(dict(v[0]))
        with self.assertRaises(ValueError):m.audit(SOURCE,inv)

    def test_invalid_source_promotion_fails(self):
        src=json.loads(json.dumps(SOURCE))
        for rule in src["rules"]:
            if rule["id"]==m.SOURCE_RULE_ID:rule["automatically_scored"]=True
        with self.assertRaisesRegex(RuntimeError,"could not enter"):m.audit(src,data())

    def test_missing_fourteen_fails(self):
        inv=data();inv["comparison_units"].pop()
        with self.assertRaises(ValueError):m.audit(SOURCE,inv)

    def test_private_identifiers_absent_from_generic_code(self):
        src=(ROOT/"scripts/audit_ptolemy_mars_venus_conditional_witness_v01.py").read_text()
        for secret_field in ("owner_dob_exact","private_owner_verbalevent","personal_email"):
            self.assertNotIn(secret_field,src)

if __name__=="__main__":unittest.main()
