import _paths
"""Public-safe fixtures: no actual names, birth data or keyword corpus."""
from fractions import Fraction
import tempfile
from pathlib import Path
import unittest

from reassignment_null import (prepare, observed_statistics, enumerate_tiny,
    simulate, precision, validate_full, build_matrices, verify_evidence_unchanged, PROTOCOL)
from cohort_analysis import analyze
from test_cohort_analysis import subject,write_pair,HERE


class ReassignmentTests(unittest.TestCase):
    def test_exhaustive_two_by_two_preserves_pairs_self_assignments_and_half_ties(self):
        north=prepare([[1,-1],[-1,1]])
        south=prepare([[2,0],[0,2]])
        observed=observed_statistics(north,south)
        self.assertEqual(observed["binary"],0)
        self.assertEqual(observed["continuous"],1)
        result=enumerate_tiny(north,south)
        self.assertEqual(result["assignments"],4) # both self and swapped assignments
        self.assertEqual(result["binary_upper_tail"],3)
        self.assertEqual(result["continuous_upper_tail"],3) # includes exact boundary
        self.assertEqual(result["binary_exact_p"],.75)

    def test_three_identity_permutations_and_exact_rational_boundaries(self):
        north=prepare([[0,0],[0,0]])
        south=prepare([[0,1,1],[1,0,1],[1,1,0]])
        result=enumerate_tiny(north,south)
        self.assertEqual(result["assignments"],12)
        self.assertEqual(result["binary_upper_tail"],12)
        self.assertEqual(result["continuous_upper_tail"],12)
        # Every permutation is exactly at the boundary, despite decimal roundoff.
        a=prepare([[Fraction(1,10**30)]*2]*2)
        b=prepare([[Fraction(1,10**30)]*3]*3)
        mc=simulate(a,b,draws=31,seed=7,batch_size=7)
        self.assertEqual(mc["continuous_exact_fallback_count"],31)
        self.assertEqual(mc["continuous"]["upper_tail_count"],31)
        self.assertEqual(mc["binary"]["upper_tail_count"],31)

    def test_monte_carlo_repeatability_and_plus_one_precision(self):
        a=prepare([[1,-1],[-1,1]]);b=prepare([[2,0],[0,2]])
        x=simulate(a,b,draws=100,seed=11,batch_size=32)
        y=simulate(a,b,draws=100,seed=11,batch_size=32)
        self.assertEqual(x["binary"],y["binary"])
        self.assertEqual(x["continuous"],y["continuous"])
        self.assertEqual(precision(0,100)["plus_one_p"],1/101)
        self.assertGreater(precision(0,100)["mc_tail_probability_95_wilson_interval"][1],0)
        self.assertEqual(PROTOCOL["draws"],1000000)
        self.assertEqual(PROTOCOL["seed"],20261117)

    def test_full_cohort_gate_rejects_partial_before_inference(self):
        with tempfile.TemporaryDirectory(dir=HERE) as folder:
            with self.assertRaisesRegex(ValueError,"complete intended"):
                validate_full([subject()],Path(folder))
            manifest=[subject(f"N{i:03d}") for i in range(1,74)]+[subject(f"S{i:03d}","South") for i in range(1,69)]
            with self.assertRaisesRegex(ValueError,"0 / 141"):
                validate_full(manifest,Path(folder))

    def test_cross_scoring_uses_whole_pairs_first_match_and_all_bio_occurrences(self):
        with tempfile.TemporaryDirectory(dir=HERE) as folder:
            root=Path(folder)
            a,b=subject(),subject("S001","South")
            a["comparison_input"]["records"]=[{"word":"x"},{"word":"X"}]
            a["comparison_input"].update(standard_global=2.,inverted_global=4.)
            write_pair(root,a,standard=[("x",2),("X",9)],inverted=[("x",3),("z",0),("z",0)])
            write_pair(root,b)
            guarded=analyze([a,b],root,descriptive_only=True)
            matrix=build_matrices([a,b],root,guarded)
            self.assertEqual(matrix["North"]["exact"],[[Fraction(0)]])
            self.assertEqual(matrix["North"]["win2"].tolist(),[[1]])
            verify_evidence_unchanged(root,guarded)
            (root/"N001"/"input.json").write_text("changed after validation")
            with self.assertRaisesRegex(ValueError,"Validated evidence changed"):
                verify_evidence_unchanged(root,guarded)


if __name__=="__main__":unittest.main()
