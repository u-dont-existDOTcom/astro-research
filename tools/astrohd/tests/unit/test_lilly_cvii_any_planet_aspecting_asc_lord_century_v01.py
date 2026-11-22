"""Synthetic original-source ambiguity tests: zero personal records."""
import sys
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[2]/"scripts"
sys.path.insert(0,str(ROOT))
import lilly_cvii_any_planet_aspecting_asc_lord_century_v01 as x

class AllOtherPlanetTests(unittest.TestCase):
    @staticmethod
    def source_orbs():
        return x.prior.SOURCE_ORBS["1647_table_smaller_orbs"]

    def test_other_rayed_planet_not_lords_dispositor(self):
        # ASC Aries -> Mars at 15 Taurus. Dispositor Venus Libra is
        # NOT in aspect. Jupiter 15 Virgo trines Mars in Taurus.
        rows=np.array([[15.,15.,15.,200.,45.,165.,15.]])
        asc=np.array([4.])
        d=x.prior.dispositor_see(rows,asc,self.source_orbs())
        self.assertFalse(bool(d["dispositor_sign_ray"][0]))
        self.assertFalse(bool(d["dispositor_orb_near_ray"][0]))
        other=x.aspects_to_asc_lord(rows,asc,self.source_orbs())
        self.assertTrue(bool(other["dispositor_sign_ray"]["rays_only"][0]))
        self.assertTrue(bool(other["dispositor_orb_near_ray"]["rays_only"][0]))

    def test_self_aspect_never_counts_even_if_self_dispositor(self):
        # ASC Aries -> Mars himself in Aries; no OTHER ray.
        rows=np.tile([5.,5.,5.,5.,5.,5.,5.],(2,1))
        asc=np.array([1.,2.])
        d=x.prior.dispositor_see(rows,asc,self.source_orbs())
        self.assertTrue(np.all(d["same_as_own_dispositor"]))
        observed=x.aspects_to_asc_lord(rows,asc,self.source_orbs())
        for name in x.prior.BEHOLDS:
            self.assertFalse(np.any(observed[name]["rays_only"]))
            # Other planets are bodily conjunct, still not self-aspects
            self.assertTrue(np.all(observed[name]["rays_or_bodily"]))

    def test_bodily_sensitivity_not_equated_to_rays(self):
        # Other planets within source-moiety but not aspect rays.
        rows=np.array([[45.,45.,45.,45.,45.,45.,45.]])
        asc=np.array([3.])
        value=x.aspects_to_asc_lord(rows,asc,self.source_orbs())
        self.assertFalse(bool(value["dispositor_sign_ray"]["rays_only"][0]))
        self.assertTrue(bool(value["dispositor_sign_ray"]["rays_or_bodily"][0]))

    def test_many_variants_and_sources_fail_closed(self):
        p=np.ones((2,7))*140
        a=np.array([1.,2.])
        small=self.source_orbs()
        with self.assertRaises(ValueError):
            x.aspects_to_asc_lord(p,a,np.ones(6))
        with self.assertRaises(ValueError):
            x.aspects_to_asc_lord(p,a,np.ones(7)*-1)
        with self.assertRaises(ValueError):
            x.aspects_to_asc_lord(np.ones((2,6)),a,small)
        with self.assertRaises(ValueError):
            x.aspects_to_asc_lord(p,np.array([8.]),small)

    def test_six_way_partition_and_old_lilly_partition_conservation(self):
        f=np.array([1,0,0,0,0,0],dtype=bool)
        j=np.array([0,1,0,0,0,0],dtype=bool)
        d=np.array([0,0,1,0,0,0],dtype=bool)
        anysee=np.array([0,0,1,1,0,0],dtype=bool)
        partile=np.array([0,0,0,1,1,0],dtype=bool)
        categories=x.split_six(f,j,d,anysee,partile)
        self.assertEqual(len(categories),6)
        for i,row in enumerate(categories):
            self.assertEqual(np.flatnonzero(row).tolist(),[i])

    def test_dispositor_cannot_aspect_when_any_other_planet_does_not(self):
        with self.assertRaisesRegex(RuntimeError,"Dispositor"):
            x.split_six(np.zeros(1,bool),np.zeros(1,bool),
                        np.ones(1,bool),np.zeros(1,bool),np.ones(1,bool))

    def test_person_specific_individuals_never_loaded(self):
        import inspect
        params=set(inspect.signature(x.run).parameters)
        self.assertEqual(params,{"west","angles","hd_cache","hd_join","verify_shards"})
        self.assertNotIn("birth_date",params)

    def test_frozen_full_century_receipt_and_all_source_variants(self):
        import json
        root=Path(__file__).resolve().parents[2]/"reference/research"
        current=json.loads((root/"lilly_cvii_all_other_planets_full_century_public_v01.json").read_text())
        previous=json.loads((root/"lilly_cvii_ptolemy_same_instant_ordered_fallback_public_v02.json").read_text())
        c=current["counts"]
        old=previous["counts"]
        self.assertEqual(current["samples"],3506400)
        self.assertEqual(current["HD_states"],288908)
        self.assertEqual(c["HD_boundary_abstained"],125)
        self.assertEqual(c["ptolemy_four_variant_robust_consensus"],4553)
        self.assertEqual(c["ptolemy_consensus_boundary_unknown"],0)
        self.assertTrue(current["original_all_source_shard_sha256_rechecked"])
        self.assertEqual(current["HD_source_audit"]["status"],"PASS_JOINED_SOURCE_NEUTRAL_GRID_SHARD_AUDIT")
        self.assertFalse(current["actual_Lilly_manners_significator_assigned"])
        self.assertFalse(current["human_personal_birth_profile_inputs_used"])
        modes=x.prior.MODES
        for mode in modes:
            for orb in x.prior.SOURCE_ORBS:
                for joined in x.prior.JOINS:
                    for see in x.prior.BEHOLDS:
                        for partile in x.prior.PARTILES:
                            base="|".join((mode,orb,joined,see,partile))
                            for k in range(1,6):
                                oldkey=base+"|S"+str(k)
                                self.assertEqual(c["earlier_"+oldkey],old[oldkey])
                                self.assertEqual(c["earlier_Ptolemy_"+oldkey],old["same_instant_Ptolemy_"+oldkey])
                            for scope in x.CONTACT_CLASSES:
                                p=base+"|all="+scope
                                stages=[p+"|"+k for k in ("S1","S2","S3","SX","S4","S5")]
                                self.assertEqual(sum(c[t] for t in stages),3506400)
                                self.assertEqual(sum(c["Ptolemy_"+t] for t in stages),4553)
                                self.assertEqual(c[stages[3]],c[p+"|blocked_partile"]+c[p+"|blocked_final_dignity"])
                                self.assertEqual(c[stages[4]]+c[p+"|blocked_partile"],old[base+"|S4"])
                                self.assertEqual(c[stages[5]]+c[p+"|blocked_final_dignity"],old[base+"|S5"])
                                for t in stages:
                                    self.assertLessEqual(c["Ptolemy_"+t],c[t])
        target="|".join(("ascending_sign","1647_table_smaller_orbs","four_externals_only","dispositor_sign_ray","partile_Moon_or_Mercury"))
        base=target+"|all=rays_only"
        self.assertEqual([c[base+"|"+k] for k in ("S1","S2","S3","SX","S4","S5")],
                         [1428060,891641,593535,575812,1769,15583])
        self.assertEqual([c["Ptolemy_"+base+"|"+k] for k in ("S1","S2","S3","SX","S4","S5")],
                         [1746,1363,772,649,0,23])

if __name__=="__main__":unittest.main()
