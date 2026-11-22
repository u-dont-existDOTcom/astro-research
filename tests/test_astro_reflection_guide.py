"""Public astrology reader-practice guidance: source and privacy regression.

This confirms authoring documentation and risk disclosures exist; it does NOT
validate astrology, the effectiveness of therapy, or a privately published page.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
GUIDE=ROOT/"docs/astrohd/reflective-practice/USING_ASTROLOGY_WISELY.md"

class AstrologicalReflectionGuidanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=GUIDE.read_text(encoding="utf8")
    def test_guide_and_permanent_entry_points(self):
        self.assertTrue(GUIDE.is_file())
        self.assertIn("USING_ASTROLOGY_WISELY.md",(ROOT/"AGENTS.md").read_text())
        self.assertIn("reflective-practice/USING_ASTROLOGY_WISELY.md",(ROOT/"docs/INDEX.md").read_text())
        self.assertIn("reflective-practice/USING_ASTROLOGY_WISELY.md",(ROOT/"docs/astrohd/README.md").read_text())
    def test_illustrated_owner_intended_cue_not_truth_model(self):
        for content in ("questions", "not a verdict", "communicat", "evidence", "against", "other explanations", "small"):
            self.assertIn(content.lower(),self.text.lower())
    def test_prompted_action_not_counted_as_prediction_hit(self):
        self.assertIn("prompted",self.text.lower())
        self.assertIn("predictive success",self.text.lower())
        self.assertIn("birth",self.text.lower())
    def test_high_stakes_and_distress_safety(self):
        t=self.text.lower()
        for content in ("health", "safety", "money", "relationships", "compulsive", "leave", "pressure"):
            self.assertIn(content,t)
    def test_evidence_and_barnum_sources_not_fake_astrological_validation(self):
        self.assertIn("nhs.uk",self.text.lower())
        self.assertIn("dictionary.apa.org/barnum-effect",self.text.lower())
        self.assertIn("not evidence that astrology",self.text.lower())
        self.assertIn("chart-free",self.text.lower())
    def test_public_reader_copy_does_not_contain_private_birth_or_person_ids(self):
        import re
        for pattern in (r"/home/[^/\s]+/(?:Documents|Downloads)/",r"@[A-Za-z0-9.-]+\.com",r"\bprivate_participant_birth_record\b"):
            self.assertIsNone(re.search(pattern,self.text,re.I),pattern)

if __name__=="__main__":
    unittest.main()
