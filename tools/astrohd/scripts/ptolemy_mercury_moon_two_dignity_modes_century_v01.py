#!/usr/bin/env python3
"""Ptolemy III.13 Mercury/Moon *partial* ruler-candidate census.

This evaluates at most TWO of Ptolemy's FIVE kinds of domination:
zodiacal domicile and exaltation. It does not adjudicate triplicity, bounds
(terms), phase/aspect, applying or separating Moon contacts, sect, angularity,
honourability, or multi-planets' contrary testimony. Thus a shared candidate
in this output is NOT 'Ptolemy's soul governor', and absence of a shared
candidate is not evidence that such a governor is absent in the full source.

Compute on the existing source-neutral UTC 15-minute Swiss tropical grid,
where record 1 = Moon and record 2 = Mercury, exact within declared samples.
Original 36 data shard SHA256 values are verified unless explicitly skipped
for exploratory debugging; public production receipts require verification.

References: Ptolemy III.2 (five forms) and III.13 (character investigation),
1940 Loeb English translation, LacusCurtius online edition.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

PLANET_NAMES=("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn")
PLANET_COLUMN={"Sun":0,"Moon":1,"Mercury":2,"Venus":3,"Mars":4,"Jupiter":5,"Saturn":6}
SIGN_NAMES=("Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces")
# Tropical traditional domiciles, as specified in the original source scheme.
DOMICILE=np.array((4,3,2,1,0,2,3,4,5,6,6,5),dtype=np.int8)
# Ptolemy standard exaltation signs: Aries Sun, Taurus Moon, Cancer Jupiter,
# Virgo Mercury, Libra Saturn, Capricorn Mars, Pisces Venus.
# -1 means no exaltation lord for that SIGN (not a missing chart ruler).
EXALTATION=np.array((0,1,-1,5,-1,2,6,-1,-1,4,-1,3),dtype=np.int8)
SCHEMA="western-source-neutral-utc-grid-float64-pilot-v1-NONCANONICAL"


def sha(path:Path)->str:
    h=sha256()
    with path.open("rb") as inp:
        for b in iter(lambda:inp.read(1<<20),b""):
            h.update(b)
    return h.hexdigest()


def validate_manifest(plan:dict,manifest:dict)->int:
    if plan.get("schema")!=SCHEMA or manifest.get("schema")!=SCHEMA:
        raise ValueError("Wrong source-grid schema")
    if plan.get("record_order")!=list(PLANET_NAMES)+["Mercury_lon_speed"]:
        raise ValueError("Unexpected source-planet order")
    n=plan.get("total_samples")
    if not isinstance(n,int) or n<1 or n!=manifest.get("total_samples"):
        raise ValueError("Invalid total sample count")
    if plan.get("step_minutes")!=15 or plan.get("record_bytes")!=64:
        raise ValueError("Unsupported source sampling/record shape")
    chunks=manifest.get("chunks")
    if not isinstance(chunks,list) or not chunks:
        raise ValueError("Source manifest has no shards")
    cursor=0
    for chunk in chunks:
        if chunk.get("first_index")!=cursor or not isinstance(chunk.get("count"),int) or chunk["count"]<=0:
            raise ValueError("Missing or duplicated chronological source samples")
        if chunk.get("size_bytes")!=chunk["count"]*64 or not isinstance(chunk.get("sha256"),str) or len(chunk["sha256"])!=64:
            raise ValueError("Malformed source shard length/hash")
        cursor+=chunk["count"]
    if cursor!=n:
        raise ValueError("Incomplete source-century coverage")
    return n


def source_geometry(mercury_lon,moon_lon)->dict:
    ml=np.asarray(mercury_lon,dtype=np.float64)
    ll=np.asarray(moon_lon,dtype=np.float64)
    if ml.ndim!=1 or ll.ndim!=1 or ml.shape!=ll.shape:
        raise ValueError("Mercury and Moon arrays must be aligned")
    if not np.all(np.isfinite(ml)) or not np.all(np.isfinite(ll)):
        raise ValueError("Nonfinite longitude")
    if np.any((ml<0)|(ml>=360)) or np.any((ll<0)|(ll>=360)):
        raise ValueError("Invalid tropical longitude")
    ms=np.floor(ml/30).astype(np.int8)
    ls=np.floor(ll/30).astype(np.int8)
    md=DOMICILE[ms]
    ld=DOMICILE[ls]
    me=EXALTATION[ms]
    le=EXALTATION[ls]
    # This is an OR over two source modes, NOT the final soul-dominator
    # assignment. Multiple different candidate planets may qualify.
    dd=(md==ld)
    de=(md==le)&(le>=0)
    ed=(me==ld)&(me>=0)
    ee=(me==le)&(me>=0)
    shared=dd|de|ed|ee
    return {
        "mercury_sign":ms,
        "moon_sign":ls,
        "same_zodiac_sign":ms==ls,
        "same_domicile_lord":dd,
        "mercury_domicile_moon_exaltation_lord":de,
        "mercury_exaltation_moon_domicile_lord":ed,
        "same_exaltation_lord":ee,
        "any_shared_candidate_in_two_modes":shared,
        "distinct_domicile_lords":md!=ld,
    }


def run(root:Path,verify_hashes=True)->dict:
    plan_p=root/"plan.json";manifest_p=root/"verified_manifest.json"
    plan=json.loads(plan_p.read_bytes())
    manifest=json.loads(manifest_p.read_bytes())
    n=validate_manifest(plan,manifest)
    if manifest.get("plan_sha256")!=sha(plan_p):
        raise RuntimeError("Plan SHA256 does not match source manifest")
    counts=Counter()
    pairs=np.zeros((12,12),dtype=np.int64)
    for c in manifest["chunks"]:
        path=root/"chunks"/c["file"]
        if path.stat().st_size!=c["size_bytes"]:
            raise RuntimeError("Source shard file size changed")
        if verify_hashes and sha(path)!=c["sha256"]:
            raise RuntimeError("Source shard SHA256 binding failed")
        a=np.memmap(path,dtype="<f8",mode="r",shape=(c["count"],8))
        z=source_geometry(a[:,2],a[:,1])
        for key in ("same_zodiac_sign","same_domicile_lord",
                    "mercury_domicile_moon_exaltation_lord",
                    "mercury_exaltation_moon_domicile_lord",
                    "same_exaltation_lord","any_shared_candidate_in_two_modes",
                    "distinct_domicile_lords"):
            counts[key]+=int(z[key].sum())
        codes=z["moon_sign"].astype(np.int16)*12+z["mercury_sign"].astype(np.int16)
        pairs+=np.bincount(codes,minlength=144).reshape(12,12)
    if int(pairs.sum())!=n:
        raise RuntimeError("Sign-pair coverage mismatched")
    if counts["any_shared_candidate_in_two_modes"]<counts["same_domicile_lord"]:
        raise RuntimeError("Union smaller than subset")
    return {
        "schema":"ptolemy_III13_partial_two_dignity_modes_century_census_v01",
        "source_scope":"Tetrabiblos III.2 + III.13; domicile and exaltation candidate intersections ONLY",
        "source_uri_III2":"https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3A%2A.html",
        "source_uri_III13":"https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3D%2A.html",
        "source_english_edition":"Robbins (1940), original Greek comparison not completed",
        "status":"COMPLETE_TWO_OF_FIVE_DOMINATION_MODES_CANDIDATE_GEOMETRY_ONLY",
        "sample_count":n,"step_minutes":15,
        "source_sample_range_utc":[plan["utc_start_inclusive"],plan["utc_end_exclusive"]],
        "source_manifest_sha256":sha(manifest_p),
        "source_grid_plan_sha256":sha(plan_p),
        "source_shard_sha256_verified":verify_hashes,
        "counts":dict(counts),
        "all_144_moon_sign_by_mercury_sign_counts":pairs.tolist(),
        "five_ptolemaic_modes":["triplicity","domicile","exaltation","term","phase_or_aspect"],
        "modes_calculated":["domicile","exaltation"],
        "modes_missing":["triplicity","term","phase_or_aspect"],
        "missing_behavior_conditions":["lunar applications and separations","full planetary aspects and phase","sect, angularity and face","honorable vs contrary status","co-ruler reconciliation and strength","source-specific relevance and alternate testimony"],
        "does_not_assign_full_ptolemaic_governor":True,
        "does_not_score_human_personality":True,
        "does_not_validate_astrological_prediction":True,
        "does_not_prove_all_continuous_instants":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--grid",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--skip-source-shard-shas",action="store_true")
    a=p.parse_args()
    if a.out.exists():
        raise FileExistsError("Immutable receipt exists")
    output=run(a.grid,not a.skip_source_shard_shas)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":output["status"],
        "samples":output["sample_count"],
        "mode_counts":output["counts"],
        "data_hashes_verified":output["source_shard_sha256_verified"],
        "personality_scored":not output["does_not_score_human_personality"]
    },sort_keys=True))


if __name__=="__main__":
    main()
