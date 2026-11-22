"""Synthetic natal-FREE original 1647 dignity tables and source-score policies."""
import sys
from pathlib import Path
import unittest
import numpy as np

BASE=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(BASE))
import lilly_cvii_original_essential_dignity_final_fallback_century_v01 as m

class LillyDignityFirstPrintedSource(unittest.TestCase):
    def test_original_points_are_from_printed_101_103(self):
        self.assertEqual(m.DIGNITY_WEIGHTS,{"domicile":5,"exaltation":4,"triplicity":3,"term":2,"face":1})
    def test_five_original_terms_each_sign_and_independent_sources(self):
        self.assertEqual(len(m.LILLY1647_ORIGINAL_TERMS),12)
        self.assertEqual(set(m.TERMS),{m.LILLY_SCHEME,"ptolemy_printed_1940","egyptian_printed_1940"})
        for sign in m.FOUR.pt2.SIGN_NAMES:
            terms=m.LILLY1647_ORIGINAL_TERMS[sign]
            self.assertEqual(len(terms),5)
            self.assertEqual(sum(size for _,size in terms),30)
            self.assertEqual(set(name for name,_ in terms),{"Mercury","Venus","Mars","Jupiter","Saturn"})
        # Original 1647 p104 Taurus Saturn concludes 26°; Robbins 1940
        # Ptolemaic source uses another boundary and lord at 25 Taurus.
        x=np.array([55.])
        a=m._terms(x,m.LILLY_SCHEME)[0]
        b=m._terms(x,"ptolemy_printed_1940")[0]
        self.assertEqual(a,m.PLANETS.index("Saturn"))
        self.assertEqual(b,m.PLANETS.index("Mars"))
        # Leo first term is Saturn in original Lilly, Jupiter in Loeb.
        self.assertEqual(m._terms(np.array([120.5]),m.LILLY_SCHEME)[0],m.PLANETS.index("Saturn"))
        self.assertEqual(m._terms(np.array([120.5]),"ptolemy_printed_1940")[0],m.PLANETS.index("Jupiter"))

    def test_original_face_table_chaldean_sequence(self):
        self.assertEqual(m.FACES.shape,(12,3))
        self.assertEqual([m.PLANETS[int(v)] for v in m.FACES[0]],["Mars","Sun","Venus"])
        self.assertEqual([m.PLANETS[int(v)] for v in m.FACES[6]],["Moon","Saturn","Jupiter"])
        self.assertEqual([m.PLANETS[int(v)] for v in m.FACES[11]],["Saturn","Jupiter","Mars"])

    def test_arbitrary_original_aries_degree_day_source_scoring(self):
        # Lilly Aries5, day: Sun exaltation4 + fire triplicity3=7;
        # Mars domicile5 + face1=6; Jupiter term2.
        a=m.dignity_scores_at_place(np.array([5.]),np.array([40.]),m.LILLY_SCHEME)
        self.assertEqual(a.shape,(1,7))
        self.assertEqual({m.PLANETS[i]:int(v) for i,v in enumerate(a[0]) if v},
                         {"Sun":7,"Mars":6,"Jupiter":2})
        b=m.dignity_scores_at_place(np.array([5.]),np.array([-40.]),m.LILLY_SCHEME)
        self.assertEqual({m.PLANETS[i]:int(v) for i,v in enumerate(b[0]) if v},
                         {"Sun":4,"Mars":6,"Jupiter":5})

    def test_exact_printed_degree_boundary_enters_new_term(self):
        # Aries first 6 degrees Jupiter, the exact 6° begins Venus.
        for place,expected in ((5.999,"Jupiter"),(6.0,"Venus"),(13.999,"Venus"),
                               (14.0,"Mercury"),(25.999,"Mars"),(26.0,"Saturn")):
            v=m._terms(np.array([place]),m.LILLY_SCHEME)[0]
            self.assertEqual(m.PLANETS[v],expected)

    def test_source_sun_near_horizon_abstains_for_final_governor(self):
        mloc=np.array([5.,5.,5.]);lloc=np.array([5.,5.,5.])
        alt=np.array([0.0,40.,-40.])
        wins,state,all6=m.candidate_score_winners(mloc,lloc,alt)
        self.assertEqual(len(wins),6)
        self.assertEqual(len(state),6)
        for tag,candidate in wins.items():
            self.assertEqual(candidate[0],-1)
            self.assertTrue(state[tag]["unknown_sect"][0])
        self.assertEqual(all6[0],-1)

    def test_decan_for_later_signs_no_uint8_overflow(self):
        # Earlier int8 sign*30 overflowed at Leo+ and silently converted
        # later signs to nonexistent 25th faces. Preserve source-faithful
        # cycle and explicit unsigned-safe intermediate arithmetic.
        positions=np.array([5.+30*i for i in range(12)],dtype=float)
        scores=m.dignity_scores_at_place(positions,np.ones(12)*40.,m.LILLY_SCHEME)
        self.assertEqual(scores.shape,(12,7))
        self.assertTrue(np.all(scores.sum(axis=1)>0))
        self.assertTrue(np.all(scores.sum(axis=1)<=15))
        # Each sign has precisely one face assigned in printed p104.
        for i in range(12):
            self.assertGreaterEqual(scores[i,int(m.FACES[i,0])],1)

    def test_scores_are_candidate_not_human_prediction(self):
        scores=m.dignity_scores_at_place(np.array([1.,100.]),np.array([40.,-30.]),m.LILLY_SCHEME)
        self.assertTrue(np.all(scores>=0))
        self.assertTrue(np.all(scores<=15))
        for x in (np.array([-1.]),np.array([360.]),np.array([np.nan])):
            with self.assertRaises(ValueError):
                m.dignity_scores_at_place(x,np.array([10.]),m.LILLY_SCHEME)
        with self.assertRaises(ValueError):
            m._terms(np.array([5.]),"user_chosen_terms")
        import inspect
        self.assertEqual(set(inspect.signature(m.run).parameters),
                         {"west","angles","hd_cache","hd_join","verify_shards"})

    def test_immutable_anonymous_full_grid_receipt_and_all_s5_policies(self):
        import json
        ref=Path(__file__).resolve().parents[2]/"reference/research"
        cur=json.loads((ref/"lilly_cvii_original_essential_dignity_final_fallback_public_v01.json").read_text())
        prev=json.loads((ref/"lilly_cvii_all_other_planets_full_century_public_v01.json").read_text())
        c=cur["sample_counts"];old=prev["counts"]
        self.assertEqual(cur["samples"],3506400)
        self.assertEqual(c["unknown_HD_root_margin"],125)
        self.assertEqual(c["ptolemy_four_mode_common"],4553)
        self.assertTrue(cur["original_108_source_shards_sha256_rechecked"])
        self.assertFalse(cur["actual_Lilly_manners_ruler_computed"])
        self.assertFalse(cur["personal_birth_or_interview_used"])
        self.assertEqual(cur["HD_structural_interval_total"],288908)
        self.assertEqual(set(cur["historical_term_scheme_names"]),set(m.TERMS))
        self.assertEqual(set(cur["candidate_place_aggregation_variants"]),set(m.AGGREGATES))
        self.assertEqual(len(cur["HD_distinct_intervals_with_six_source_agreement"]),96)
        for method in m.PRIOR.MODES:
         for orb in m.PRIOR.SOURCE_ORBS:
          for join in m.PRIOR.JOINS:
           for behold in m.PRIOR.BEHOLDS:
            for partile in m.PRIOR.PARTILES:
             for contact in m.broad.CONTACT_CLASSES:
              key="|".join((method,orb,join,behold,partile,"all="+contact))
              self.assertEqual(c[key+"|S5"],old[key+"|S5"])
              self.assertEqual(c[key+"|S5_Ptolemy"],old["Ptolemy_"+key+"|S5"])
              source_consensus=c[key+"|six_source_winner_agreement"]
              self.assertLessEqual(source_consensus,c[key+"|S5"])
              self.assertLessEqual(c[key+"|six_source_agreement_Ptolemy"],source_consensus)
              for table in m.TERMS:
               for agg in m.AGGREGATES:
                k=key+"|term_and_aggregation="+table+"|"+agg
                categories=("unknown_sect","no_positive_claim","positive_score_tied","unique")
                self.assertEqual(sum(c[k+"|"+stage] for stage in categories),c[key+"|S5"])
                self.assertLessEqual(c[k+"|Ptolemy_unique"],c[k+"|unique"])
        fixed="ascending_sign|1647_table_smaller_orbs|four_externals_only|dispositor_sign_ray|partile_Moon_or_Mercury|all=rays_only"
        self.assertEqual(c[fixed+"|S5"],15583)
        self.assertEqual(c[fixed+"|six_source_winner_agreement"],9089)
        self.assertEqual(c[fixed+"|six_source_agreement_Ptolemy"],23)
        self.assertEqual(cur["HD_distinct_intervals_with_six_source_agreement"][fixed],1562)
        self.assertEqual(c["whole_grid_Moon_term_disagreement_Lilly_v_ptolemy_printed_1940"],818854)
        self.assertEqual(c["whole_grid_Mercury_term_disagreement_Lilly_v_ptolemy_printed_1940"],832853)

if __name__=="__main__":unittest.main()
