import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
from compare_planet_character_condition_pilot_v01 import condition

class TestCondition(unittest.TestCase):
    def test_conditions_are_not_chosen_from_behavior(self):
        for p in ("familiarity_only","fixed_sect_contrast"):
            self.assertEqual(condition(True,False,True,False,p),0)
            self.assertEqual(condition(False,True,False,False,p),0)
            self.assertIsNone(condition(False,True,False,True,p))
            self.assertIsNone(condition(False,False,False,False,p))
        self.assertIsNone(condition(False,False,True,False,"familiarity_only"))
        self.assertEqual(condition(False,False,True,False,"fixed_sect_contrast"),1)
    def test_invalid(self):
        with self.assertRaises(ValueError):condition(False,True,True,False,"familiarity_only")
        with self.assertRaises(ValueError):condition(False,False,False,False,"fit_rank")

if __name__=="__main__":unittest.main()
