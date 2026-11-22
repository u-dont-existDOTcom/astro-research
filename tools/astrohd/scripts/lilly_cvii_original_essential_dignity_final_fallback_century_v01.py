#!/usr/bin/env python3
"""Lilly 1647 pp101-105, p536: final essential-dignity candidate census.

READ MODE: actual source first-print edition p101 PDF135, p102 PDF136,
p103 PDF137, table p104 PDF138, usage p105 PDF139; direct page images.
Domicile 5, exaltation 4, sect triplicity 3, terms 2, face 1.
The original 1647 table headed "according to Ptolomy" is NOT identical to
the separate Ptolemaic and Egyptian tables in Robbins's 1940 Loeb edition.
All three original printed witnesses are independent, never conflated.

The source p536 says a planet with most essential dignities "in the place
of Mercury and Luna" at the LAST fallback, but does NOT unambiguously say
whether to combine the two places with a SUM or strongest single place.
Both are separate modern declared RECONSTRUCTIONS, NOT a complete original
Lilly manners significator. Accidentals, fortification, tie priorities,
antiscions, Sun proximity, fixed stars, any source planetary strength, and
the original Ptolemy III.13 final governing planet remain OPEN.

Full independently SHA-verified 3,506,400 original 15-minute UTC sample
century with 288,908 certified HD structural intervals; 125 ambiguous
root-boundary HD assignments abstain. No natal, interview or human scores.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
import swisseph as swe

import lilly_cvii_any_planet_aspecting_asc_lord_century_v01 as broad
import lilly_cvii_ptolemy_same_instant_ordered_fallback_v02 as old

FOUR=old.base.four
PRIOR=old
PLANETS=tuple(FOUR.PLANETS)
TOTAL=3506400
HD_STATES=old.HD_STATES
SECT_UNCERTAIN_DEG=old.base.SUN_ALT_UNCERTAINTY

# Reading from the actual FIRST 1647 printing p104, one-based PDF page 138.
# Each sign's 5 terms are planet and DURATION in degrees. Some individual
# boundaries differ materially from BOTH Robbins 1940 Loeb term tables.
# Never 'repair' the original printed rows by silently substituting another
# printed source edition.
LILLY1647_ORIGINAL_TERMS={
 "Aries":(("Jupiter",6),("Venus",8),("Mercury",7),("Mars",5),("Saturn",4)),
 "Taurus":(("Venus",8),("Mercury",7),("Jupiter",7),("Saturn",4),("Mars",4)),
 "Gemini":(("Mercury",7),("Jupiter",7),("Venus",7),("Saturn",4),("Mars",5)),
 "Cancer":(("Mars",6),("Jupiter",7),("Mercury",7),("Venus",7),("Saturn",3)),
 "Leo":(("Saturn",6),("Venus",7),("Jupiter",6),("Mercury",6),("Mars",5)),
 "Virgo":(("Mercury",7),("Venus",6),("Jupiter",5),("Saturn",6),("Mars",6)),
 "Libra":(("Saturn",6),("Venus",5),("Jupiter",8),("Mercury",5),("Mars",6)),
 "Scorpio":(("Mars",6),("Jupiter",8),("Venus",7),("Mercury",6),("Saturn",3)),
 "Sagittarius":(("Jupiter",8),("Mercury",6),("Venus",5),("Saturn",6),("Mars",5)),
 "Capricorn":(("Venus",6),("Mercury",6),("Jupiter",7),("Mars",6),("Saturn",5)),
 "Aquarius":(("Saturn",6),("Mercury",6),("Venus",8),("Jupiter",5),("Mars",5)),
 "Pisces":(("Venus",8),("Jupiter",6),("Mercury",6),("Mars",6),("Saturn",4)),
}
LILLY_SCHEME="Lilly_1647_original_first_print_p104"
TERMS={
 LILLY_SCHEME:FOUR.build_table(LILLY1647_ORIGINAL_TERMS),
 **FOUR.TABLES,
}
# Face/decans in Lilly's actual 1647 printed p104 table.
# Rows are 12 ordered signs; entries 1st/2nd/3rd ten degrees in that sign.
FACE_NAMES=(
 ("Mars","Sun","Venus"),
 ("Mercury","Moon","Saturn"),
 ("Jupiter","Mars","Sun"),
 ("Venus","Mercury","Moon"),
 ("Saturn","Jupiter","Mars"),
 ("Sun","Venus","Mercury"),
 ("Moon","Saturn","Jupiter"),
 ("Mars","Sun","Venus"),
 ("Mercury","Moon","Saturn"),
 ("Jupiter","Mars","Sun"),
 ("Venus","Mercury","Moon"),
 ("Saturn","Jupiter","Mars"),
)
FACES=np.array([[PLANETS.index(name) for name in row] for row in FACE_NAMES],dtype=np.int8)

# Direct source p104/p105 + p102: fire Sun day/Jupiter night,
# earth Venus day/Moon night, air Saturn day/Mercury night,
# water Mars regardless of day/night. No third co-ruler silently added.
TRIP_DAY=np.array([0,3,6,4]*3,dtype=np.int8)
TRIP_NIGHT=np.array([5,1,2,4]*3,dtype=np.int8)
DIGNITY_WEIGHTS={"domicile":5,"exaltation":4,"triplicity":3,"term":2,"face":1}
AGGREGATES=("sum_of_both_places","strongest_of_two_places")

def _terms(longitudes,scheme):
    if scheme not in TERMS:raise ValueError("Unlicensed printed terms witness")
    x=np.asarray(longitudes,dtype=np.float64)
    if x.ndim!=1 or not np.all(np.isfinite(x)) or np.any((x<0)|(x>=360)):
        raise ValueError("Normalized longitude required")
    signs=np.floor(x/30).astype(np.int8)
    deg=x-30.*signs
    rulers,cum=TERMS[scheme]
    col=np.sum(deg[:,None]>=cum[signs],axis=1)
    if np.any(col>=5):raise RuntimeError("Term out of original zodiac range")
    return rulers[signs,col]

def dignity_scores_at_place(longitudes,solar_alt,scheme):
    """Points owed by every candidate classical lord AT a specified place."""
    x=np.asarray(longitudes,dtype=np.float64)
    alt=np.asarray(solar_alt,dtype=np.float64)
    if x.ndim!=1 or alt.shape!=x.shape or np.any(~np.isfinite(alt)):
        raise ValueError("Aligned source place and solar altitude required")
    if np.any(~np.isfinite(x)) or np.any((x<0)|(x>=360)):
        raise ValueError("Normalized longitudes required")
    n=len(x)
    sign=np.floor(x/30).astype(np.int8)
    face=np.floor(((x-30.0*sign)/10.0)).astype(np.int8)
    if np.any((face<0)|(face>2)):raise ValueError("Invalid decan")
    src=FOUR.pt3.ptolemy2
    day=alt>SECT_UNCERTAIN_DEG
    night=alt< -SECT_UNCERTAIN_DEG
    # All rows are sparse: one candidate per mode, or no exaltation.
    # No additive scores at unresolved near-horizon source instant.
    points=np.zeros((n,7),dtype=np.uint8)
    row=np.arange(n)
    points[row,src.DOMICILE[sign]]+=5
    ex=src.EXALTATION[sign]
    valid_ex=ex>=0
    points[row[valid_ex],ex[valid_ex]]+=4
    sect_lord=np.where(day,TRIP_DAY[sign],
                       np.where(night,TRIP_NIGHT[sign],-1))
    valid_trip=sect_lord>=0
    points[row[valid_trip],sect_lord[valid_trip]]+=3
    points[row,_terms(x,scheme)]+=2
    points[row,FACES[sign,face]]+=1
    # 5+4+3+2+1 can at most sum 15, uint8 is sufficient.
    if np.any(points>15):raise RuntimeError("Original point ceiling broken")
    return points

def candidate_score_winners(mercury,moon,alt):
    """6 SOURCE-CONDITIONED candidate winners per timestamp, no actual ruler."""
    m=np.asarray(mercury,dtype=np.float64)
    l=np.asarray(moon,dtype=np.float64)
    a=np.asarray(alt,dtype=np.float64)
    if m.shape!=l.shape or m.shape!=a.shape or m.ndim!=1:
        raise ValueError("Aligned source observations required")
    known=np.abs(a)>SECT_UNCERTAIN_DEG
    wins={}
    scores={}
    for scheme in TERMS:
        M=dignity_scores_at_place(m,a,scheme)
        L=dignity_scores_at_place(l,a,scheme)
        for method in AGGREGATES:
            pts=M.astype(np.int16)+L if method==AGGREGATES[0] else np.maximum(M,L).astype(np.int16)
            max_pts=pts.max(axis=1)
            winners=(pts==max_pts[:,None])
            unique=(winners.sum(axis=1)==1)&(max_pts>0)&known
            pl=np.argmax(pts,axis=1).astype(np.int8)
            pl[~unique]=-1
            tag=scheme+"|"+method
            wins[tag]=pl
            scores[tag]={"unknown_sect":~known,
                         "no_positive_claim":(max_pts==0)&known,
                         "positive_score_tied":(max_pts>0)&(winners.sum(axis=1)>1)&known,
                         "unique":unique}
    stack=np.stack([wins[key] for key in wins],axis=0)
    consensus=(stack>=0).all(axis=0)&(stack==stack[0]).all(axis=0)
    return wins,scores,np.where(consensus,stack[0],-1)

def run(west,angles,hd_cache,hd_join,verify_shards=True):
    if swe.version!="2.10.03":raise RuntimeError("Swiss engine version drift")
    wp=west/"plan.json";wm=west/"verified_manifest.json"
    ap=angles/"plan.json";am=angles/"verified_manifest.json"
    wj=json.loads(wp.read_bytes()); wjm=json.loads(wm.read_bytes())
    aj=json.loads(ap.read_bytes()); ajm=json.loads(am.read_bytes())
    samples=PRIOR.base.reg.initial.check_manifest(wj,wjm,aj,ajm)
    if samples!=TOTAL:raise RuntimeError("Original 3.5m sample denominator drift")
    if (wjm["plan_sha256"]!=PRIOR.base.reg.initial.source_hash(wp)
        or ajm["plan_sha256"]!=PRIOR.base.reg.initial.source_hash(ap)):
        raise RuntimeError("Original source plan hash drift")
    hdproof=PRIOR.hd_source.hdverify.audit_join(west,hd_cache,hd_join)
    hdj=json.loads((hd_join/"manifest.json").read_bytes())
    if (hdj["total_utc_grid_samples"]!=samples or
        hdj["unresolved_near_boundary_samples"]!=125 or
        hdj["total_hd_structural_intervals"]!=HD_STATES):
        raise RuntimeError("HD time universe changed")
    jd0=PRIOR.base.reg.julian_from_utc(wj["utc_start_inclusive"])
    lat=float(aj["latitude"]);lon=float(aj["longitude"])
    counts=Counter()
    state_sets={}
    current=0
    former=json.loads((Path(__file__).resolve().parents[1]/"reference/research/lilly_cvii_all_other_planets_full_century_public_v01.json").read_bytes())
    ref=former["counts"]
    for w,a,h in zip(wjm["chunks"],ajm["shards"],hdj["shards"],strict=True):
        n=w["count"]
        if (w["first_index"]!=current or a["first_index"]!=current or
            h["index_first"]!=current or h["count"]!=n):
            raise RuntimeError("Source shuffled or differently aligned")
        bp=west/"chunks"/w["file"];ba=angles/"shards"/a["file"]
        bh=hd_join/"shards"/h["file"]
        if bp.stat().st_size!=64*n or ba.stat().st_size!=136*n or bh.stat().st_size!=4*n:
            raise RuntimeError("Source shard byte count drift")
        if verify_shards and (
            PRIOR.base.reg.initial.source_hash(bp)!=w["sha256"] or
            PRIOR.base.reg.initial.source_hash(ba)!=a["sha256"] or
            PRIOR.base.reg.initial.source_hash(bh)!=h["sha256"]
        ):raise RuntimeError("SHA mismatch original source shard")
        p=np.memmap(bp,dtype="<f8",shape=(n,8),mode="r")
        q=np.memmap(ba,dtype="<f8",shape=(n,17),mode="r")
        ids=np.memmap(bh,dtype="<i4",shape=(n,),mode="r")
        known_hd=ids>=0
        ptolemy=PRIOR.ptolemy_source.conditional_all_four_common_leader(p,q[:,4])>=0
        wins,elig,consensus=candidate_score_winners(p[:,2],p[:,1],q[:,4])
        counts["total_samples"]+=n
        counts["unknown_HD_root_margin"]+=int((~known_hd).sum())
        counts["ptolemy_four_mode_common"]+=int(ptolemy.sum())
        # Source-dependent original published table differs from old Loeb
        for col in (1,2):
            new=_terms(p[:,col],LILLY_SCHEME)
            for old_scheme in FOUR.TABLES:
                counts[f"whole_grid_{PLANETS[col]}_term_disagreement_Lilly_v_{old_scheme}"]+=int(
                    np.count_nonzero(new!=_terms(p[:,col],old_scheme)))
        # Every historical branch computes S5 ONLY after original
        # Lilly's 6-stage source-text-sensitive fallback sequence.
        cusps=np.empty((n,2),dtype=np.float64)
        for i in range(n):
            z,_=swe.houses_ex(jd0+(current+i)/96,lat,lon,b"R")
            cusps[i]=z[:2]
        if np.max(PRIOR.angle_distance(cusps[:,0],q[:,0]))>0.0002:
            raise RuntimeError("Original Ascendant source drift")
        classes=PRIOR.base.first_house_and_intercepted(p[:,:7],cusps[:,0],cusps[:,1])
        part=PRIOR.partile_candidates(p[:,:7])
        for orbname,orbs in PRIOR.SOURCE_ORBS.items():
            disp=PRIOR.dispositor_see(p[:,:7],q[:,0],orbs)
            all_aspect=broad.aspects_to_asc_lord(p[:,:7],q[:,0],orbs)
            for joinname in PRIOR.JOINS:
                joining=PRIOR.orb_join(p[:,:7],orbs,scope=joinname)
                for first in PRIOR.MODES:
                    for behold in PRIOR.BEHOLDS:
                        for partile in PRIOR.PARTILES:
                            for contact in broad.CONTACT_CLASSES:
                                prefix="|".join((first,orbname,joinname,behold,partile,"all="+contact))
                                stages=broad.split_six(classes[first],joining["any_joined"],
                                         disp[behold],all_aspect[behold][contact],part[partile])
                                final=stages[-1]
                                if not np.any(final):continue
                                counts[prefix+"|S5"]+=int(final.sum())
                                counts[prefix+"|S5_Ptolemy"]+=int((final&ptolemy).sum())
                                for tag,pl in wins.items():
                                    key=prefix+"|term_and_aggregation="+tag
                                    source=elig[tag]
                                    for kind,mask in source.items():
                                        counts[key+"|"+kind]+=int((final&mask).sum())
                                    selected=final&(pl>=0)
                                    counts[key+"|Ptolemy_unique"]+=int((selected&ptolemy).sum())
                                robust=final&(consensus>=0)
                                counts[prefix+"|six_source_winner_agreement"]+=int(robust.sum())
                                counts[prefix+"|six_source_agreement_Ptolemy"]+=int((robust&ptolemy).sum())
                                if np.any(robust&known_hd):
                                    dest=state_sets.setdefault(prefix,np.zeros(HD_STATES,dtype=bool))
                                    dest[ids[robust&known_hd]]=True
        current+=n
    if (current!=TOTAL or counts["total_samples"]!=TOTAL or
        counts["unknown_HD_root_margin"]!=125 or counts["ptolemy_four_mode_common"]!=4553):
        raise RuntimeError("Historical census inputs changed")
    if not verify_shards:raise RuntimeError("Cannot publish unverified historical source data")
    for first in PRIOR.MODES:
      for orb in PRIOR.SOURCE_ORBS:
       for join in PRIOR.JOINS:
        for behold in PRIOR.BEHOLDS:
         for partile in PRIOR.PARTILES:
          for contact in broad.CONTACT_CLASSES:
            prefix="|".join((first,orb,join,behold,partile,"all="+contact))
            original=ref[prefix+"|S5"]
            if counts[prefix+"|S5"]!=original:
                raise RuntimeError("Prior six-stage actual source S5 result mismatched")
            if counts[prefix+"|S5_Ptolemy"]!=ref["Ptolemy_"+prefix+"|S5"]:
                raise RuntimeError("Prior six-stage Ptolemy S5 result mismatched")
            for tag in wins:
                key=prefix+"|term_and_aggregation="+tag
                if sum(counts[key+"|"+kind] for kind in
                         ("unknown_sect","no_positive_claim","positive_score_tied","unique"))!=original:
                    raise RuntimeError("Dignity candidate output fails honest total partition")
            if counts[prefix+"|six_source_winner_agreement"]>original:
                raise RuntimeError("Consensus cannot exceed eligible source stage")
    return {
      "schema":"lilly_1647_original_p101_104_five_essential_dignity_votes_full_century_v01",
      "status":"ORIGINAL_PRINTED_5_4_3_2_1_POINTS_AT_MERCURY_MOON_FINAL_STAGE_CANDIDATE_NOT_MANNERS_RULER",
      "samples":TOTAL,"minute_step":15,
      "UTC_horizon":[wj["utc_start_inclusive"],wj["utc_end_exclusive"]],
      "original_108_source_shards_sha256_rechecked":verify_shards,
      "HD_source_audit":hdproof,"HD_structural_interval_total":HD_STATES,
      "source_manifest_sha256":{"west":PRIOR.base.reg.initial.source_hash(wm),
                                "angles":PRIOR.base.reg.initial.source_hash(am),
                                "HD_index":PRIOR.hd_source.hdverify.digest(hd_join/"manifest.json")},
      "source":"Original William Lilly Christian Astrology (1647) pp101-105 and p536; vs printed Loeb Robbins 1940 two term tables",
      "source_values":DIGNITY_WEIGHTS,
      "historical_term_scheme_names":list(TERMS),
      "Lilly1647_first_print_term_source":LILLY1647_ORIGINAL_TERMS,
      "face_order":FACE_NAMES,
      "source_sect_lords":{"day":["Sun","Venus","Saturn","Mars"]*3,
                           "night":["Jupiter","Moon","Mercury","Mars"]*3},
      "candidate_place_aggregation_variants":list(AGGREGATES),
      "actual_Lilly_manners_ruler_computed":False,
      "actual_Ptolemy_soul_governor_computed":False,
      "personal_birth_or_interview_used":False,
      "what_is_still_unknown":["Lilly p536 how to aggregate dignity rights across Mercury and Moon",
          "source printed 1647 term variants and historical corruptions / later alternative Loeb editions",
          "sect near horizon and older Pluto-free classical astrology",
          "actual strength and dignity of planetary occupants and all earlier stages",
          "partile force, Accidental dignities and fixed stars",
          "whether this chart symbol system predicts any human behavior"],
      "sample_counts":dict(counts),
      "HD_distinct_intervals_with_six_source_agreement":{k:int(v.sum()) for k,v in state_sets.items()}
    }

def main():
    parser=argparse.ArgumentParser()
    for key in ("west","angles","hd-cache","hd-join","out"):
        parser.add_argument("--"+key,required=True,type=Path)
    a=parser.parse_args()
    if a.out.exists():raise FileExistsError("Cannot overwrite source-bound receipt")
    res=run(a.west,a.angles,a.hd_cache,a.hd_join)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(res,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":res["status"],"samples":res["samples"],
                      "checks":"old 96-stage S5 plus source SHA verified"},sort_keys=True))
if __name__=="__main__":main()
