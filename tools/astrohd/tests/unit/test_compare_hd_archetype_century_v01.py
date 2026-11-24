import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
import compare_hd_archetype_century_v01 as h
import compare_expanded_hd_multitradition_v01 as m

def fake(gates,profile):
    keys=sorted(h.ACT_KEYS)
    activ={k:gates[i%len(gates)] for i,k in enumerate(keys)}
    present=set(activ.values())
    channels=[x for x in h.CHANNELS if set(map(int,x.split("-")))<=present]
    centers={h.GATE_CENTER[int(y)] for x in channels for y in x.split("-")}
    return {"activation_gates":activ,"channels":channels,"defined_centers":list(centers),"profile":profile}

class TestHDArchetype(unittest.TestCase):
    def test_full_catalogue_and_exclusions(self):
        reg,groups,shared=h.load_map()
        self.assertEqual([len(groups[k]) for k in ("gate","channel","ordered_profile","line")],[64,36,12,6])
        self.assertEqual(len(h.ARMS),20)
        self.assertEqual(len(h.SCORES),40)
        self.assertEqual(sum(len(r["direct"]) for r in reg["rules"]),38)
        self.assertEqual(sum(len(r["proxy"]) for r in reg["rules"]),125)

    def test_geometry_conscious_defined_hanging_dormant(self):
        f=fake([1,8,7,64],"2/5")
        a,d,c,ch,p=h.geometry(f)
        self.assertEqual(a,h.mask([1,8,7,64]))
        self.assertEqual(d,h.mask([1,8,7]))
        self.assertEqual(c,d & h.mask(v for k,v in f["activation_gates"].items() if k.startswith("personality:")))
        self.assertEqual(ch,1<<h.CHANNELS.index("1-8"))
        self.assertEqual(p,h.PROFILES.index("2/5"))
        f["channels"]=[]
        with self.assertRaises(ValueError):h.geometry(f)

    def test_uint64_gate_64_and_bitset_lut_exact(self):
        rng=np.random.default_rng(87)
        pp=rng.integers(0,256,64,dtype=np.uint64)
        nn=rng.integers(0,256,64,dtype=np.uint64)
        masks=np.asarray([0,1,1<<63,(1<<64)-1,17,17|(1<<63)],np.uint64)
        out=h.bitlookup(masks,h.byte_lut((pp,nn)))
        active=np.array([[bool(int(x)&(1<<i)) for i in range(64)] for x in masks])
        for a,b in zip(out,h.s.bitset(active,(pp,nn)),strict=True):np.testing.assert_array_equal(a,b)

    def test_ordered_profile_and_line_ablation(self):
        _,groups,shared=h.load_map()
        keys=tuple(k for d in h.pc.DOMAINS for k in shared["domains"][d])
        geo=np.asarray([h.geometry(fake([1,8,7,64],p)) for p in ("2/5","5/2")],np.uint64)
        z=h.model_bits(geo,groups,keys,"with_proxies")
        self.assertEqual(z["line_union"][0][0],z["line_union"][0][1])
        self.assertNotEqual(z["ordered_profile"][0][0],z["ordered_profile"][0][1])
        for kind in h.GATES:
            np.testing.assert_array_equal(z[kind][0],z[kind][0][0])

    def test_union_does_not_repeat_same_observable(self):
        _,groups,shared=h.load_map();keys=tuple(k for d in h.pc.DOMAINS for k in shared["domains"][d])
        geo=np.asarray([h.geometry(fake([1,8,7,64],"1/3"))],np.uint64)
        z=h.model_bits(geo,groups,keys,"with_proxies")
        for a,b in zip(z["union_any"],h.s.union(z["ordered_profile"],z["channels"],z["gate_any"]),strict=True):
            np.testing.assert_array_equal(a,b)
        self.assertEqual(h.ranks(np.array([0.,.2,.4]),.2,np.array([2,3,4])),{"higher":4,"tied":3,"lower":2})

class TestCrossCodingFlags(unittest.TestCase):
    def test_same_variant_not_switching(self):
        f=m.Flags(3)
        f.add("a",np.array([1,1,0]),np.array([0,1,0]),np.ones(3,bool))
        f.add("b",np.array([0,1,0]),np.array([1,1,0]),np.ones(3,bool))
        np.testing.assert_array_equal(f.strict_any,[False,True,False])
        np.testing.assert_array_equal(f.ge_all,[True,True,True])

    def test_flags_and_dominance(self):
        # Arm bits for all 4 groups, 16 bits set on second row.
        p=np.array([0,65535,65535],np.uint16)
        x=np.array([0,.5,0]);y=np.array([0,.4,0]);known=np.array([True,True,False])
        z=m.aggregate(p,known,x,y)
        self.assertEqual(z["HD_no_lower"],2)
        self.assertEqual(z["HD_strict_both"],1)
        self.assertEqual(z["all_primary"]["HD_strict_and_others_strict_any"],1)
        self.assertEqual(z["all_primary"]["HD_equal_others_strict_any"],0)
        self.assertEqual(z["all_primary"]["HD_no_lower_others_ge_all"],1)

if __name__=="__main__":unittest.main()
