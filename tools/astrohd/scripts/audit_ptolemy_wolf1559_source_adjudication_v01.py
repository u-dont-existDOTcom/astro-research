#!/usr/bin/env python3
"""Fail-closed provenance gate for Ptolemy original vs Wolf/Robbins 15 degrees.

Historical I.24 says sufficiently close, not exactly 15°.
The anonymous commentator's 1559 printed Greek/Latin p51 is a separate
witness about 15 zodiacal parts with speed-dependent qualifications;
the editor Robbins p113 note129 abbreviated it as a maximum.
This gate does not authenticate a unique source-defined numerical orb.
It proves source-version history is preserved; no person/chart data used.
"""
from __future__ import annotations
import json
import hashlib
from pathlib import Path
import argparse

HERE=Path(__file__).resolve().parents[1]/"reference/research"
SOURCE_V03="ptolemy_iii13_five_domination_mode_source_adjudication_v03.json"
SOURCE_V04="ptolemy_iii13_five_domination_mode_source_adjudication_v04.json"
EXPECTED_SOURCE_SHA="c32b809e7ca49456260ebb6364916ab71e5ce2298d889c11e1726cd1bc788ccc"
ORIGINAL_PAGE_IMAGES={
    "50":"a9ba1c57fbe357245952b51519fbcde00f04c0da1110449c5fca65ac1936d209",
    "51":"1996a430eb23ee1fa443dc67deccfc7e0dae77c3e6d58b28e6dc0a6db350db9a",
    "52":"0bd016f77498947ca62278295540cf97f16ce4650a35440f543b6dfe3a32f48a",
}

def audit(v03:bytes,v04:bytes):
    old=json.loads(v03);new=json.loads(v04)
    digest=hashlib.sha256(v03).hexdigest()
    if digest!=EXPECTED_SOURCE_SHA or new.get("supersedes_v03_sha256")!=digest:
        raise ValueError("Historical original source register edited or supersession hash drift")
    allowed={
      "schema","status","supersedes_v03_sha256","wolf1559_primary_print_source_scan",
      "wolf1559_relation_to_earlier_editor_report","new_wolf1559_source_report",
      "newly_read_original_commentary_cannot_choose_old_thresholds",
      "historical_numeric_cutoff_variant_dispositions","textual_sources"
    }
    for key,value in old.items():
        if key not in allowed and new.get(key)!=value:
            raise ValueError("Prior historical source evidence overwritten: "+key)
    if new["textual_sources"][:-1]!=old["textual_sources"] or len(new["textual_sources"])!=len(old["textual_sources"])+1:
        raise ValueError("Prior original textual witness overwritten")
    wolf=new["wolf1559_primary_print_source_scan"]
    if wolf.get("page_images_original_sha256")!=ORIGINAL_PAGE_IMAGES:
        raise ValueError("Direct original p50-52 source image identities altered")
    if wolf.get("first_print_image_citation")!="https://ptolemaeus.badw.de/print/11/2/51":
        raise ValueError("Direct printed p51 stable permalink changed")
    if wolf["source_licensed_universal_15degree_maximum"] is not False or wolf["licensed_unique_fifth_mode_orb"] is not False:
        raise ValueError("Unjustified original 15 degree numerical orb promoted to Ptolemy rule")
    if wolf["new_astro_grid_recalculation_required"] is not False:
        raise ValueError("Editorial source correction is not a new astronomy calculation")
    if not new["newly_read_original_commentary_cannot_choose_old_thresholds"]:
        raise ValueError("Numeric source uncertainty must remain unresolved")
    if "speed" not in wolf["p51_context"] and "fast" not in wolf["p51_context"]:
        raise ValueError("Missing source speed contextual qualification")
    if new["wolf1559_relation_to_earlier_editor_report"]["ptolemy_I24_author_own_numeric_cutoff"]!="UNSPECIFIED":
        raise ValueError("Original Ptolemy I.24 cutoff falsely fixed")
    if old["human_predictions_prospectively_verified"]!=0 or new["human_predictions_prospectively_verified"]!=0:
        raise ValueError("Historical source does not validate human personality prediction")
    if old["fixed_computational_scope"]!=new["fixed_computational_scope"]:
        raise ValueError("No new full-century run: frozen source geometry was altered")
    if old["current_double_config_public_aggregate"]!=new["current_double_config_public_aggregate"]:
        raise ValueError("Reproduction pointer to historical source aggregate mutated")
    if new["old_automated_scores_updated"] or new["behavioral_claims_licensed_for_automated_rank"]!=0:
        raise ValueError("Non-source human personality score entered")
    if new["no_public_birth_or_personal_case_data"] is not True:
        raise ValueError("Source-private-person separation violated")
    options=new["historical_numeric_cutoff_variant_dispositions"]
    if len(options)!=4 or len({x["kind"] for x in options})!=4:
        raise ValueError("Ptolemy/commentator/editor/modern source layers collapsed")
    return {"status":"PASS_DIRECT_1559_GREEK_LATIN_WOLF_SOURCE_SEPARATION",
            "source_1559_pages":[50,51,52],"old_source_sha256":digest,
            "historical_variants":len(options),"old_source_records_unchanged":True,
            "human_predictive_validation":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=HERE)
    args=ap.parse_args()
    a=args.root/SOURCE_V03;b=args.root/SOURCE_V04
    print(json.dumps(audit(a.read_bytes(),b.read_bytes()),sort_keys=True))

if __name__=="__main__":main()
