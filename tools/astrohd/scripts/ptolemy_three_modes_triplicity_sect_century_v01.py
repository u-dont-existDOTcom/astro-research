#!/usr/bin/env python3
"""Ptolemy III.13 preliminary 3-of-5 domination modes, sensitivity to co-rulers.

Read Ptolemy's Book I.17–19 for DOMICILE, TRIPLICITY (day/night) and
EXALTATION, III.2 for the five forms, III.13 for application to the mind.
This algorithm does NOT compute Ptolemy's actual soul ruler or personality
predictions. We never map a shared candidate to a positive trait.

Preserve:
* day/night primary triplicity ruler (one per element/sect)
* all day/night triplicity co-rulers where text says so
* 0.1 degree solar-altitude horizon sensitivity as unknown
* identical UTC 15-minute sample indices for planet and ASC/solar altitude
* independent SHA256 verification of ALL source binary shards
* exact two-mode baseline; no retroactive change to previous 2-of-5 receipts
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
spec=importlib.util.spec_from_file_location("ptolemy2",
                  HERE/"ptolemy_mercury_moon_two_dignity_modes_century_v01.py")
ptolemy2=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ptolemy2)

# Seven planet bitmap index 0=Sun,1=Moon,2=Mercury,3=Venus,4=Mars,
# 5=Jupiter,6=Saturn. In I.18 first three triangles have diurnal/nocturnal
# primary preferences. Water is dominated by Mars with Moon by night or
# Venus by day as co-governor. The "principal-only" variant treats Mars
# as first even though neither sect's co-ruler should be dismissed in
# the all-co-ruler variant.
FIRE=(0,4,8)
EARTH=(1,5,9)
AIR=(2,6,10)
WATER=(3,7,11)
PRIMARY_DAY=np.empty(12,dtype=np.int8)
PRIMARY_NIGHT=np.empty(12,dtype=np.int8)
CO_DAY=np.empty(12,dtype=np.uint16)
CO_NIGHT=np.empty(12,dtype=np.uint16)
for signs,pday,pnight,day_members,night_members in [
    (FIRE,0,5,(0,5),(0,5)),
    (EARTH,3,1,(3,1),(3,1)),
    (AIR,6,2,(6,2),(6,2)),
    (WATER,4,4,(4,3),(4,1)),
]:
    for x in signs:
        PRIMARY_DAY[x]=pday
        PRIMARY_NIGHT[x]=pnight
        CO_DAY[x]=sum(1<<i for i in day_members)
        CO_NIGHT[x]=sum(1<<i for i in night_members)


def mask_for_ruler_modes(signs,solar_altitude,*,all_triplicity_members:bool):
    s=np.asarray(signs)
    alt=np.asarray(solar_altitude,dtype=np.float64)
    if s.shape!=alt.shape or s.ndim!=1:
        raise ValueError("Aligned sign and solar altitude arrays required")
    if np.any((s<0)|(s>=12)) or not np.all(np.isfinite(alt)):
        raise ValueError("Invalid sign or Sun altitude")
    # The first two sign-based rulership modes are known even when the
    # sect status cannot be resolved near sunrise/sunset.
    out=(np.uint16(1)<<ptolemy2.DOMICILE[s].astype(np.uint16))
    exalt=ptolemy2.EXALTATION[s]
    valid_exalt=exalt>=0
    out|=np.where(valid_exalt,np.uint16(1)<<np.maximum(exalt,0).astype(np.uint16),np.uint16(0))
    day=alt>0.1
    night=alt< -0.1
    if all_triplicity_members:
        tday=CO_DAY[s]
        tnight=CO_NIGHT[s]
    else:
        tday=np.uint16(1)<<PRIMARY_DAY[s].astype(np.uint16)
        tnight=np.uint16(1)<<PRIMARY_NIGHT[s].astype(np.uint16)
    out|=np.where(day,tday,np.uint16(0))
    out|=np.where(night,tnight,np.uint16(0))
    return out


def classifications(mercury_lon,moon_lon,solar_altitude)->dict:
    first=ptolemy2.source_geometry(mercury_lon,moon_lon)
    alt=np.asarray(solar_altitude,dtype=np.float64)
    if alt.shape!=first["mercury_sign"].shape or not np.all(np.isfinite(alt)):
        raise ValueError("Sun altitude must align with planets")
    near=np.abs(alt)<=0.1
    dom_exalt_shared=first["any_shared_candidate_in_two_modes"]
    mc=mask_for_ruler_modes(first["mercury_sign"],alt,all_triplicity_members=True)
    lc=mask_for_ruler_modes(first["moon_sign"],alt,all_triplicity_members=True)
    mp=mask_for_ruler_modes(first["mercury_sign"],alt,all_triplicity_members=False)
    lp=mask_for_ruler_modes(first["moon_sign"],alt,all_triplicity_members=False)
    # On near-horizon records, these masks include two earlier modes only.
    # We ABSTAIN on whether triplicity adds any co- or primary ruler.
    cs=(mc&lc)!=0
    ps=(mp&lp)!=0
    return {
        "two_modes_shared":dom_exalt_shared,
        "three_modes_all_corulers_shared_certain":cs&~near,
        "three_modes_principal_only_shared_certain":ps&~near,
        "three_modes_new_common_via_corulers_certain":cs&~dom_exalt_shared&~near,
        "three_modes_new_common_via_principal_only_certain":ps&~dom_exalt_shared&~near,
        "near_solar_horizon_unknown_triplicity":near,
        "two_modes_shared_on_near_horizon":near&dom_exalt_shared,
        "coruler_vs_primary_difference_certain":(cs!=ps)&~near,
    }


def sha(path:Path)->str:
    return ptolemy2.sha(path)


def check_two_cache_manifests(wp,wm,ap,am):
    n=ptolemy2.validate_manifest(wp,wm)
    if ap.get("schema")!="location-conditioned-western-angles-utc-grid-v1-NONCANONICAL":
        raise ValueError("Wrong source angle-grid schema")
    if ap.get("sample_count")!=n or am.get("total_samples")!=n:
        raise ValueError("Mismatch in declared time population")
    if ap.get("step_minutes")!=15 or ap.get("record_bytes")!=136:
        raise ValueError("Wrong angle source sampling")
    if wp.get("utc_start_inclusive")!=ap.get("utc_start") or wp.get("utc_end_exclusive")!=ap.get("utc_end_exclusive"):
        raise ValueError("Source calendars are not identical")
    if ap.get("cols",[])[4]!="true_sun_altitude":
        raise ValueError("Sun altitude absent/moved")
    w=wm.get("chunks",[])
    a=am.get("shards",[])
    if len(w)!=len(a) or not w:
        raise ValueError("Misaligned shards")
    for x,y in zip(w,a):
        if x.get("first_index")!=y.get("first_index") or x["count"]!=y.get("count"):
            raise ValueError("Shard sample indices differ")
    return n


def run(west:Path,angles:Path,verify_binary_hashes=True):
    wp_p=west/"plan.json";wm_p=west/"verified_manifest.json"
    ap_p=angles/"plan.json";am_p=angles/"verified_manifest.json"
    wp=json.loads(wp_p.read_bytes());wm=json.loads(wm_p.read_bytes())
    ap=json.loads(ap_p.read_bytes());am=json.loads(am_p.read_bytes())
    n=check_two_cache_manifests(wp,wm,ap,am)
    if wm.get("plan_sha256")!=sha(wp_p) or am.get("plan_sha256")!=sha(ap_p):
        raise RuntimeError("Plan SHA did not match expected manifest")
    counters=Counter()
    for w,a in zip(wm["chunks"],am["shards"]):
        planet=west/"chunks"/w["file"]
        angle=angles/"shards"/a["file"]
        count=w["count"]
        if planet.stat().st_size!=count*64 or angle.stat().st_size!=count*136:
            raise RuntimeError("Unexpected source shard byte size")
        if verify_binary_hashes and (sha(planet)!=w["sha256"] or sha(angle)!=a["sha256"]):
            raise RuntimeError("Data source hash verification failed")
        z=np.memmap(planet,dtype="<f8",mode="r",shape=(count,8))
        g=np.memmap(angle,dtype="<f8",mode="r",shape=(count,17))
        result=classifications(z[:,2],z[:,1],g[:,4])
        for k,v in result.items():counters[k]+=int(np.asarray(v).sum())
    if counters["three_modes_all_corulers_shared_certain"]<counters["three_modes_principal_only_shared_certain"]:
        raise RuntimeError("Co-rulers cannot reduce the union of candidates")
    if counters["three_modes_new_common_via_corulers_certain"]<counters["three_modes_new_common_via_principal_only_certain"]:
        raise RuntimeError("Co-rulers cannot decrease new shared candidates")
    if counters["near_solar_horizon_unknown_triplicity"]>=n:
        raise RuntimeError("All signs have ambiguous sect")
    return {
        "schema":"ptolemy_III13_three_of_five_dignity_modes_source_candidate_census_v01",
        "status":"THREE_SOURCE_MODES_MECHANICAL_CANDIDATES_ONLY_NOT_PTOLEMAIC_SOUL_GOVERNORS",
        "source_scope":"Ptolemy Tetrabiblos I.17-I.19, III.2, III.13 (1940 Robbins English)",
        "source_uri":"https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/1B%2A.html",
        "total_samples":n,
        "sample_step_minutes":15,
        "source_time_horizon":[wp["utc_start_inclusive"],wp["utc_end_exclusive"]],
        "angles_fixed_location":True,
        "original_manifests_sha256":{"planet":sha(wm_p),"angle":sha(am_p)},
        "every_binary_shard_hash_rechecked":verify_binary_hashes,
        "solar_altitude_ambiguous_within_degrees":0.1,
        "mechanical_counts":dict(counters),
        "mode_scope":{"computed":["domicile","exaltation","triplicity"],
                       "not_computed":["terms","phase_or_aspect"]},
        "triplicity_variant":"primary-only and all source-declared co-rulers separately",
        "no_human_chart_or_personality_data":True,
        "no_full_governor_selection":True,
        "no_human_predictive_validation":True,
        "not_continuous_utc_time_coverage":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--west",required=True,type=Path)
    p.add_argument("--angles",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--skip-binary-hashes",action="store_true")
    a=p.parse_args()
    if a.output.exists():raise FileExistsError("Immutable prior result")
    result=run(a.west,a.angles,not a.skip_binary_hashes)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"samples":result["total_samples"],
                      "mechanical_counts":result["mechanical_counts"],
                      "all_shards_rechecked":result["every_binary_shard_hash_rechecked"]},sort_keys=True))
if __name__=="__main__":main()
