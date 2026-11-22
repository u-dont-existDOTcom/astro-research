"""Synthetic Ptolemy double configuration: source scope and angular geometry."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"scripts/ptolemy_iii13_mercury_lunar_dual_aspect_century_v01.py"
spec=importlib.util.spec_from_file_location("dual",SCRIPT)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class DualSourceGeometryTests(unittest.TestCase):
 def test_non_body_aspect_root_and_conjunction_not_silently_accepted(self):
  mercury=[0.,10.,359.]
  venus=[60.,10.,59.]
  residual=m.nearest_residual(venus,mercury,m.ASPECTS_NONBODY)
  self.assertAlmostEqual(residual[0],0.,places=9)
  self.assertGreater(abs(residual[1]),20.)
  body=m.nearest_residual(venus,mercury,m.ASPECTS_WITH_BODY)
  self.assertAlmostEqual(body[1],0.,places=9)

 def test_angular_wrap_and_absolute_longitudes(self):
  x=m.nearest_residual([359.,0.],[59.,60.],m.ASPECTS_NONBODY)
  self.assertTrue(np.allclose(np.abs(x),[0.,0.],atol=1e-9))
  with self.assertRaises(ValueError):
   m.nearest_residual([360.],[0.],m.ASPECTS_NONBODY)
  with self.assertRaises(ValueError):
   m.nearest_residual([10.],[float('nan')],m.ASPECTS_WITH_BODY)

 def test_moon_relative_motion_sampled_edges_abstain(self):
  # Moving Moon approaches fixed Venus's 60-degree exact angle
  # then departs afterwards. Derivative positive every internal sample.
  lunar=np.array([50.,55.,60.,65.,70.])
  venus=np.array([0.,0.,0.,0.,0.])
  v=m.lunar_radial_trend(lunar,venus)
  self.assertTrue(np.isnan(v[0]) and np.isnan(v[-1]))
  self.assertTrue(np.all(v[1:-1]>0))
  residual=m.nearest_residual(lunar,venus,m.ASPECTS_NONBODY)
  self.assertLess(residual[1]*v[1],0)
  self.assertGreater(residual[3]*v[3],0)

 def test_relative_motion_wrap_past_360_is_consistent(self):
  v=m.lunar_radial_trend([359.9,0.1,0.3],[120.,120.,120.])
  self.assertTrue(np.isfinite(v[1]))
  self.assertGreater(v[1],0)

 def test_source_unknown_when_altitude_near_horizon(self):
  # Ptolemy term and domicile source can still be known when sect
  # triplicity is uncertain; mark the combined screen abstaining.
  common,near=m.source_common_lord_bits(
      [10.,10.,10.],[12.,12.,12.],[0.,0.05,-0.05],m.PTOLEMY)
  self.assertTrue(np.all(near))
  self.assertTrue(np.all(common>0))

 def test_co_ruler_candidate_masks_never_impute_personality(self):
  mer=np.array([10.,10.,10.]);moon=np.array([150.,150.,150.])
  c1,_=m.source_common_lord_bits(mer,moon,[45.,45.,45.],m.PTOLEMY)
  c2,_=m.source_common_lord_bits(mer,moon,[45.,45.,45.],m.EGYPTIAN)
  self.assertEqual(len(c1),3)
  self.assertTrue(np.all(c1>=0) and np.all(c2>=0))

 def test_nonbody_witness_positive_and_separating_polarity(self):
  # Venus at 60 from Mercury at 0, Moon approaching Venus's trine
  # around 180? Moon at Venus+120=180. The valid ordinary 120° aspect
  # is continuously approached then surpassed in the middle.
  n=5
  rows=np.zeros((n,8))
  rows[:,2]=0.
  rows[:,1]=[176.,178.,180.,182.,184.]
  rows[:,3]=60.
  rows[:,4]=120.
  rows[:,5]=270.
  rows[:,6]=340.
  rows[:,0]=50.
  ang=np.zeros((n,17));ang[:,4]=50.
  z=m.scan_chunk(rows,ang)
  self.assertEqual(z["shard_derivative_unknown_samples"],2)
  # No assertion of source-governor presence here: eligibility depends
  # on all source rulers, so this is a structural shape-only test.
  self.assertLessEqual(z[m.PTOLEMY+"_5deg_nonbody_only"],3)

 def test_source_sample_shape_fail_closed(self):
  with self.assertRaises(ValueError):
   m.scan_chunk(np.zeros((4,7)),np.zeros((4,17)))
  with self.assertRaises(ValueError):
   m.scan_chunk(np.zeros((4,8)),np.zeros((4,16)))

 def test_threshold_monotonicity_on_synthetic_rows(self):
  rng=np.random.default_rng(23)
  rows=np.zeros((301,8));rows[:,:7]=rng.uniform(0,360,(301,7))
  ang=np.zeros((301,17));ang[:,4]=rng.uniform(-85,85,301)
  z=m.scan_chunk(rows,ang)
  for scheme in m.SCHEMES:
   for scope in ("nonbody_only","including_uncertified_conjunctions"):
    vals=[z[f"{scheme}_{i}deg_{scope}"] for i in (1,3,5,10,15)]
    self.assertEqual(vals,sorted(vals))
    self.assertTrue(all(0<=k<=299 for k in vals))
   for i in (1,3,5,10,15):
    self.assertLessEqual(z[f"{scheme}_{i}deg_nonbody_only"],
                         z[f"{scheme}_{i}deg_including_uncertified_conjunctions"])

 def test_source_scope_never_claims_orb_or_full_ruler(self):
  s=SCRIPT.read_text()
  for v in ("does_not_complete_fifth_domination_mode",
            "does_not_apply_source_defined_orb",
            "does_not_score_personality_or_unique_natal_rank",
            "excluded_mercury_self_relation_not_evidence_against_source",
            "conjunction_latitude_source_unavailable_so_upper_only"):
   self.assertIn(v,s)
  self.assertNotRegex(s,r"/home/[^/\s]+/(?:Documents|Downloads)/")

if __name__=="__main__":
 unittest.main()
