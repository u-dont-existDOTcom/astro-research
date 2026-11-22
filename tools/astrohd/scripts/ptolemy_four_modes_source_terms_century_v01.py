#!/usr/bin/env python3
"""Ptolemy III.13 FOUR-OF-FIVE partial governor-candidate astronomical census.

Historical table input is transcribed from PHOTOGRAPHED/RENDERED original
Robbins (1940) Loeb Tetrabiblos printed pages 96-97 (Egyptian terms), 106-107
(terms Ptolemy reports from an ancient manuscript). Distinct variants; never
merge them and never treat the modern HTML digitization as authoritative.

The Egyptian table is preserved as an *alternative source sensitivity*, not
a replacement for the printed "Terms according to Ptolemy" table. The
printed source records textual variants; using 1940 edition is NOT a complete
Greek manuscript adjudication.

Other source modes from previous scripts: domicile, exaltation, and
sect-conditioned principal/all triplicity rulers. 5th mode phase/aspect and
complete Moon applying/separating testimony remain unimplemented, as do
final soul governor and behavioral interpretation. No individual data.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location(
    "ptolemy3",HERE/"ptolemy_three_modes_triplicity_sect_century_v01.py")
pt3=importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt3)
pt2=pt3.ptolemy2

# Planet indexes: Sun=0 Moon=1 Mercury=2 Venus=3 Mars=4 Jupiter=5 Saturn=6
# Every row is a thirty-degree zodiac sign, five consecutive (ruler, degrees).
# Direct source: photographed Loeb Robbins 1940 pp.106-107 and pp.96-97.
PTOLEMY_PRINTED={
"Aries":(("Jupiter",6),("Venus",8),("Mercury",7),("Mars",5),("Saturn",4)),
"Taurus":(("Venus",8),("Mercury",7),("Jupiter",7),("Saturn",2),("Mars",6)),
"Gemini":(("Mercury",7),("Jupiter",6),("Venus",7),("Mars",6),("Saturn",4)),
"Cancer":(("Mars",6),("Jupiter",7),("Mercury",7),("Venus",7),("Saturn",3)),
"Leo":(("Jupiter",6),("Mercury",7),("Saturn",6),("Venus",6),("Mars",5)),
"Virgo":(("Mercury",7),("Venus",6),("Jupiter",5),("Saturn",6),("Mars",6)),
"Libra":(("Saturn",6),("Venus",5),("Mercury",5),("Jupiter",8),("Mars",6)),
"Scorpio":(("Mars",6),("Venus",7),("Jupiter",8),("Mercury",6),("Saturn",3)),
"Sagittarius":(("Jupiter",8),("Venus",6),("Mercury",5),("Saturn",6),("Mars",5)),
"Capricorn":(("Venus",6),("Mercury",6),("Jupiter",7),("Saturn",6),("Mars",5)),
"Aquarius":(("Saturn",6),("Mercury",6),("Venus",8),("Jupiter",5),("Mars",5)),
"Pisces":(("Venus",8),("Jupiter",6),("Mercury",6),("Mars",5),("Saturn",5)),
}
EGYPTIAN_PRINTED={
"Aries":(("Jupiter",6),("Venus",6),("Mercury",8),("Mars",5),("Saturn",5)),
"Taurus":(("Venus",8),("Mercury",6),("Jupiter",8),("Saturn",5),("Mars",3)),
"Gemini":(("Mercury",6),("Jupiter",6),("Venus",5),("Mars",7),("Saturn",6)),
"Cancer":(("Mars",7),("Venus",6),("Mercury",6),("Jupiter",7),("Saturn",4)),
"Leo":(("Jupiter",6),("Venus",5),("Saturn",7),("Mercury",6),("Mars",6)),
"Virgo":(("Mercury",7),("Venus",10),("Jupiter",4),("Mars",7),("Saturn",2)),
"Libra":(("Saturn",6),("Mercury",8),("Jupiter",7),("Venus",7),("Mars",2)),
"Scorpio":(("Mars",7),("Venus",4),("Mercury",8),("Jupiter",5),("Saturn",6)),
"Sagittarius":(("Jupiter",12),("Venus",5),("Mercury",4),("Saturn",5),("Mars",4)),
"Capricorn":(("Mercury",7),("Jupiter",7),("Venus",8),("Saturn",4),("Mars",4)),
"Aquarius":(("Mercury",7),("Venus",6),("Jupiter",7),("Mars",5),("Saturn",5)),
"Pisces":(("Venus",12),("Jupiter",4),("Mercury",3),("Mars",9),("Saturn",2)),
}
SIGNS=pt2.SIGN_NAMES
PLANETS=pt2.PLANET_NAMES

def build_table(source):
    if set(source)!=set(SIGNS) or len(source)!=12:
        raise ValueError("Exactly 12 source zodiacal signs required")
    rulers=np.zeros((12,5),dtype=np.int8)
    cum=np.zeros((12,5),dtype=np.int8)
    for s,sign in enumerate(SIGNS):
        entries=source[sign]
        if len(entries)!=5:
            raise ValueError("Five terms for each sign required")
        if len(set(name for name,_ in entries))!=5:
            raise ValueError("Terms must use distinct rulers per printed row")
        if set(name for name,_ in entries)!={"Mercury","Venus","Mars","Jupiter","Saturn"}:
            raise ValueError("Wrong term-governing planets")
        sizes=[size for _,size in entries]
        if any(not isinstance(x,int) or x<=0 for x in sizes) or sum(sizes)!=30:
            raise ValueError("Each sign must sum exactly to 30 degrees")
        rulers[s]=[PLANETS.index(name) for name,_ in entries]
        cum[s]=np.cumsum(sizes)
    return rulers,cum

TABLES={s:build_table(t) for s,t in {
    "ptolemy_printed_1940":PTOLEMY_PRINTED,
    "egyptian_printed_1940":EGYPTIAN_PRINTED,
}.items()}

def term_lords(longitudes,scheme):
    if scheme not in TABLES:
        raise ValueError("Unknown, explicitly frozen source-table scheme")
    a=np.asarray(longitudes,dtype=np.float64)
    if a.ndim!=1 or not np.all(np.isfinite(a)) or np.any((a<0)|(a>=360)):
        raise ValueError("Normalized tropical longitudes required")
    signs=np.floor(a/30).astype(np.int8)
    degrees=a-30.0*signs
    rulers,ends=TABLES[scheme]
    # side=right means the exact degree boundary belongs to the NEW term,
    # e.g. first Aries 6° Jupiter is [0,6), Venus starts [6,14).
    indices=np.sum(degrees[:,None]>=ends[signs],axis=1)
    if np.any(indices>=5):
        raise RuntimeError("Term lookup outside source sign")
    return rulers[signs,indices]


def classification(mercury,moon,solar_altitude):
    p=np.asarray(mercury,dtype=np.float64)
    q=np.asarray(moon,dtype=np.float64)
    alt=np.asarray(solar_altitude,dtype=np.float64)
    prior=pt3.classifications(p,q,alt)
    near=prior["near_solar_horizon_unknown_triplicity"]
    baseP_M=pt3.mask_for_ruler_modes(prior_sign(p),alt,all_triplicity_members=False)
    baseP_L=pt3.mask_for_ruler_modes(prior_sign(q),alt,all_triplicity_members=False)
    baseC_M=pt3.mask_for_ruler_modes(prior_sign(p),alt,all_triplicity_members=True)
    baseC_L=pt3.mask_for_ruler_modes(prior_sign(q),alt,all_triplicity_members=True)
    result={
        "three_modes_primary_certain":prior["three_modes_principal_only_shared_certain"],
        "three_modes_corulers_certain":prior["three_modes_all_corulers_shared_certain"],
        "near_horizon_abstain":near,
    }
    for scheme in TABLES:
        tm=term_lords(p,scheme)
        tl=term_lords(q,scheme)
        tmbits=np.left_shift(np.uint16(1),tm.astype(np.uint16))
        tlbits=np.left_shift(np.uint16(1),tl.astype(np.uint16))
        union_primary=((baseP_M|tmbits)&(baseP_L|tlbits))!=0
        union_corulers=((baseC_M|tmbits)&(baseC_L|tlbits))!=0
        # A near-horizon contact may still have overlap from domicile,
        # exaltation and term independent of unknown triplicity. This
        # bottom-line subset is CERTAIN; *absence* remains UNDETERMINED.
        source2m=two_mode_terms_mask(p,scheme)
        source2l=two_mode_terms_mask(q,scheme)
        determined_near=(source2m&source2l)!=0
        result.update({
            scheme+"_same_term_lord":tm==tl,
            scheme+"_shared_primary_certain":union_primary&~near,
            scheme+"_shared_corulers_certain":union_corulers&~near,
            scheme+"_new_v_three_corulers_certain":union_corulers&~prior["three_modes_all_corulers_shared_certain"]&~near,
            scheme+"_known_two_modes_plus_term_with_near_horizon":determined_near&near,
        })
    p_name="ptolemy_printed_1940"
    e_name="egyptian_printed_1940"
    result["different_term_lord_for_Mercury"]=term_lords(p,p_name)!=term_lords(p,e_name)
    result["different_term_lord_for_Moon"]=term_lords(q,p_name)!=term_lords(q,e_name)
    result["source_scheme_changes_four_mode_coruler_shared_certain"]=(
        result[p_name+"_shared_corulers_certain"]!=
        result[e_name+"_shared_corulers_certain"]
    )&~near
    return result

def prior_sign(a):
    arr=np.asarray(a,dtype=np.float64)
    return np.floor(arr/30).astype(np.int8)

def two_mode_terms_mask(lon,scheme):
    signs=prior_sign(lon)
    out=(np.uint16(1)<<pt2.DOMICILE[signs].astype(np.uint16))
    exalt=pt2.EXALTATION[signs]
    out|=np.where(exalt>=0,np.uint16(1)<<np.maximum(exalt,0).astype(np.uint16),np.uint16(0))
    term=term_lords(lon,scheme)
    out|=(np.uint16(1)<<term.astype(np.uint16))
    return out

def sha(path):
    return pt2.sha(path)

def run(west,angles,verify_sha=True):
    wplan=json.loads((west/"plan.json").read_bytes())
    wman=json.loads((west/"verified_manifest.json").read_bytes())
    aplan=json.loads((angles/"plan.json").read_bytes())
    aman=json.loads((angles/"verified_manifest.json").read_bytes())
    n=pt3.check_two_cache_manifests(wplan,wman,aplan,aman)
    if wman.get("plan_sha256")!=sha(west/"plan.json") or aman.get("plan_sha256")!=sha(angles/"plan.json"):
        raise RuntimeError("Source manifest plan hash mismatch")
    counts=Counter()
    for w,a in zip(wman["chunks"],aman["shards"]):
        wp=west/"chunks"/w["file"]
        ap=angles/"shards"/a["file"]
        k=w["count"]
        if wp.stat().st_size!=64*k or ap.stat().st_size!=136*k:
            raise RuntimeError("Source binary shard size mismatch")
        if verify_sha and (sha(wp)!=w["sha256"] or sha(ap)!=a["sha256"]):
            raise RuntimeError("Source shard SHA256 mismatch")
        pa=np.memmap(wp,dtype="<f8",mode="r",shape=(k,8))
        an=np.memmap(ap,dtype="<f8",mode="r",shape=(k,17))
        z=classification(pa[:,2],pa[:,1],an[:,4])
        for key,mask in z.items():
            counts[key]+=int(mask.sum())
    pre=counts["three_modes_corulers_certain"]
    post=counts["ptolemy_printed_1940_shared_corulers_certain"]
    if post<pre or counts["ptolemy_printed_1940_new_v_three_corulers_certain"]!=post-pre:
        raise RuntimeError("Terms cannot remove source candidate in known-sect time grid")
    if counts["ptolemy_printed_1940_shared_corulers_certain"]<counts["ptolemy_printed_1940_shared_primary_certain"]:
        raise RuntimeError("Co-rulers cannot remove shared candidate")
    return {
      "schema":"ptolemy_III13_four_of_five_mode_candidate_census_20261122_v01",
      "status":"FOUR_PARTIAL_MODES_ASTRONOMICAL_CANDIDATES_ONLY_NOT_PTOLEMAIC_SOUL_GOVERNOR",
      "data_samples":n,
      "step_minutes":15,
      "horizon_utc":[wplan["utc_start_inclusive"],wplan["utc_end_exclusive"]],
      "source_manifests_sha256":{"western":sha(west/"verified_manifest.json"),"angles":sha(angles/"verified_manifest.json")},
      "source_binary_shard_sha256_rechecked":verify_sha,
      "printed_source":"Loeb 1940 pp. 96-97 Egyptians and 106-107 Ptolemy, English/Greek printed original rendered directly (private research scan)",
      "terms_scheme_ids":list(TABLES),
      "terms_source_variant_status":"Loeb printed tables are fixed historical edition witnesses; other manuscripts/term arrangements not claimed resolved",
      "source_historical_families":["Ptolemy printed terms","Egyptian printed terms","Chaldaean historical terms (not computed)"],
      "term_boundary_convention":"0-inclusive, upper boundary exclusive; exactly on term boundary belongs to next term",
      "near_horizon_sect_abstention_degrees":0.1,
      "counts":dict(counts),
      "source_modes_computed":["domicile","exaltation","triplicity","terms"],
      "remaining_source_modes":["phase_or_aspect"],
      "further_source_conditions_missing":["Moon applying/separating contact chronology","governor strengths and contrary testimony","historical phase/aspect scope","actual character behavior scoring"],
      "actual_soul_governor_assigned":False,
      "human_predictive_success_established":False,
      "continuous_time_coverage":False,
      "no_personal_birth_or_profile_inputs":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--west",required=True,type=Path)
    p.add_argument("--angles",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--skip-source-sha",action="store_true")
    a=p.parse_args()
    if a.out.exists():raise FileExistsError("Versioned result cannot be overwritten")
    z=run(a.west,a.angles,not a.skip_source_sha)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(z,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":z["status"],"samples":z["data_samples"],"counts":z["counts"],
                      "source_hash_rechecked":z["source_binary_shard_sha256_rechecked"]},sort_keys=True))
if __name__=="__main__":main()
