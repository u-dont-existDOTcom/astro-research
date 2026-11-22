"""Direct first-edition Lilly 1647 p112 reception/peregrine and p115 debility.

Invented seven-body longitudes only; no personal natal/subject records.
"""
import sys
from pathlib import Path
import unittest
import numpy as np
SCRIPTS=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(SCRIPTS))
import lilly_1647_reception_peregrine_essential_body_century_v01 as m

class OriginalReceptionAndPeregrine(unittest.TestCase):
    def row(self):
        return np.array([[5.,42.,70.,120.,130.,230.,10.]],dtype=np.float64)

    def test_original_p112_house_reception_Sun_Aries_Mars_Leo(self):
        a=self.row()
        h,e=m.potential_receptions(a)
        self.assertTrue(h[0,0])
        self.assertTrue(h[0,4])
        self.assertFalse(e[0,0])
        self.assertEqual(h.shape,(1,7))

    def test_mutual_exaltation_Sun_Capricorn_Mars_Aries(self):
        a=self.row()
        a[0,0]=280.  # Sun in Capricorn: exaltation of Mars
        a[0,4]=5.    # Mars in Aries: exaltation of Sun
        h,e=m.potential_receptions(a)
        self.assertTrue(e[0,0])
        self.assertTrue(e[0,4])
        self.assertFalse(h[0,0])

    def test_one_sided_and_self_dignity_not_mutual_reception(self):
        a=np.zeros((1,7),dtype=float)
        a[0,0]=10.;a[0,4]=10.  # Both Aries: Mars self, Sun Aries not reciprocal
        h,e=m.potential_receptions(a)
        self.assertFalse(h[0,0])
        self.assertFalse(h[0,4])
        self.assertFalse(np.all(h))

    def test_lilly_original_exact_saturn_peregrine_example(self):
        p=np.tile(self.row(),(2,1))
        p[0,6]=10.   # Saturn 10 Aries is peregrine, original p112 example
        p[1,6]=27.   # Saturn 27 Aries has own Saturn term
        s=m.positive_intrinsic(p,np.ones(2)*40.,m.src.LILLY_SCHEME)
        self.assertEqual(s[:,6].tolist(),[0,2])
        h,e=m.potential_receptions(p)
        detr,fall,per,clear=m.debility_masks(p,s,h,e)
        self.assertTrue(per[0,6]);self.assertFalse(per[1,6])
        self.assertTrue(fall[0,6]);self.assertTrue(fall[1,6])

    def test_detriment_and_fall_opposite_domicile_exaltation(self):
        p=np.tile(self.row(),(2,1))
        p[0,0]=315. # Sun Aquarius: detriment opposite Leo domicile
        p[1,0]=195. # Sun Libra: fall opposite Aries exaltation
        s=m.positive_intrinsic(p,np.ones(2)*40.,m.src.LILLY_SCHEME)
        rh,re=m.potential_receptions(p)
        detr,fall,_,_=m.debility_masks(p,s,rh,re)
        self.assertTrue(detr[0,0])
        self.assertFalse(detr[1,0])
        self.assertTrue(fall[1,0])
        self.assertFalse(fall[0,0])

    def test_peregrine_reception_interpretations_distinct(self):
        a=self.row()
        a[0,4]=135. # Mars 15 Leo, no self dignity but in Sun domicile
        alt=np.array([40.])
        s=m.positive_intrinsic(a,alt,m.src.LILLY_SCHEME)
        h,e=m.potential_receptions(a)
        self.assertTrue(h[0,4])
        self.assertEqual(s[0,4],0)
        _,_,peregrine,cleared=m.debility_masks(a,s,h,e)
        self.assertTrue(peregrine[0,4])
        self.assertFalse(cleared[0,4])
        winners,attrs,consensus,recv=m.candidate_models(a,alt)
        self.assertEqual(len(winners),12)
        self.assertEqual(len(attrs),12)
        self.assertEqual(consensus.shape,(1,))

    def test_int8_zodiac_overflow_all_signs_is_prevented(self):
        p=np.stack([np.arange(7)*2.+s*30+3 for s in range(12)]).astype(float)
        score=m.positive_intrinsic(p,np.ones(12)*40.,m.src.LILLY_SCHEME)
        self.assertEqual(score.shape,(12,7))
        self.assertTrue(np.all((score>=0)&(score<=15)))
        rh,re=m.potential_receptions(p)
        self.assertEqual(rh.shape,(12,7))
        self.assertEqual(re.shape,(12,7))

    def test_sect_unknown_produces_no_strict_winner(self):
        p=self.row()
        win,_,common,_=m.candidate_models(p,np.array([0.]))
        self.assertTrue(all(z[0]==-1 for z in win.values()))
        self.assertEqual(common[0],-1)

    def test_untrusted_bad_source_shapes_rejected(self):
        with self.assertRaises(ValueError):
            m.positive_intrinsic(np.ones((2,8)),np.ones(2),m.src.LILLY_SCHEME)
        with self.assertRaises(ValueError):
            m.potential_receptions(np.ones((2,6)))
        with self.assertRaises(ValueError):
            m.potential_receptions(np.ones((1,7))*360)
        with self.assertRaises(ValueError):
            m.positive_intrinsic(np.ones((1,7)),np.ones(1),"retrofit_user_personal_values")

    def test_no_personal_inputs_or_final_manners_ruler(self):
        import inspect
        self.assertEqual(set(inspect.signature(m.run).parameters),
                         {"west","angles","hd_cache","hd_join","verify_sha"})
        self.assertEqual(len(m.POLICIES),4)

    def test_original_century_checksum_regression_when_available(self):
        import json
        p=Path(__file__).resolve().parents[2]/"reference/research/lilly_1647_mutual_reception_peregrine_body_source_century_public_v01.json"
        if not p.exists():
            self.skipTest("Original finite century census not yet run")
        j=json.loads(p.read_text());c=j["counts"]
        self.assertEqual(j["samples"],3506400)
        self.assertEqual(c["HD_transition_samples_abstained"],125)
        self.assertEqual(c["prior_conditional_ptolemy_4mode_common"],4553)
        self.assertEqual(j["HD_intervals"],288908)
        self.assertFalse(j["complete_1647_essential_and_accidental_strength"])
        self.assertFalse(j["actual_Lilly_manners_significator_selected"])
        self.assertFalse(j["human_predictive_validation"])
        for scheme in m.src.TERMS:
            for policy in m.POLICIES:
                prefix=scheme+"|"+policy
                self.assertEqual(c[prefix+"|strict_unique"]+c[prefix+"|tie_or_sect_unknown"],3506400)

if __name__=="__main__":unittest.main()
