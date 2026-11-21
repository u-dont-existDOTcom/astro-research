#!/usr/bin/env python3
"""Private-input, source-neutral mechanical rarity audit for HD + Western charts.

Reports temporal frequency of chart features in ONE DECLARED century, using
already verified caches; does NOT measure a chart's psychological correctness.
Reference birth input is passed at runtime only and must not be committed.
Selected features are chosen AFTER observing that chart and thus their low
frequency cannot be interpreted as a calibrated p value or independent test.
"""
from __future__ import annotations
import argparse,bisect,gzip,itertools,json,hashlib
from collections import Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path

import numpy as np
import swisseph as swe

INDEXES=("Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn")
PLANETS=(swe.SUN,swe.MOON,swe.MERCURY,swe.VENUS,swe.MARS,swe.JUPITER,swe.SATURN)
MAJOR_ANGLES=(0,60,90,120,180)
ALL_PAIRS=tuple(itertools.combinations(range(7),2))
GROUPS=tuple(itertools.combinations(range(7),5))
PAIR_SETS=tuple(tuple(ALL_PAIRS.index(p) for p in itertools.combinations(g,2)) for g in GROUPS)
EPOCH=datetime(1970,1,1,tzinfo=timezone.utc)

def digest(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def utc(s):
    dt=datetime.fromisoformat(s.replace("Z","+00:00"))
    if dt.tzinfo is None or dt.utcoffset()!=timedelta(0):
        raise ValueError("Expected explicit UTC timestamp")
    return dt.astimezone(timezone.utc)
def nearest_major_orb(longitudes):
    # Array Nx7, degrees; 21 pairwise absolute angular deviations.
    n=longitudes.shape[0]
    result=np.empty((n,len(ALL_PAIRS)),dtype=np.float64)
    for idx,(i,j) in enumerate(ALL_PAIRS):
        sep=np.abs((longitudes[:,i]-longitudes[:,j]+180.)%360.-180.)
        result[:,idx]=np.minimum.reduce([np.abs(sep-a) for a in MAJOR_ANGLES])
    return result

def five_group_masks(longitudes,threshold=3.):
    pp=nearest_major_orb(longitudes)<=threshold
    anyfive=np.zeros(len(longitudes),dtype=bool)
    pergroup=[]
    for cols in PAIR_SETS:
        mask=np.all(pp[:,cols],axis=1)
        pergroup.append(mask)
        anyfive|=mask
    return anyfive,pergroup

def strict_sources(west,angles,hd,ephe):
    wm=json.loads((west/"verified_manifest.json").read_bytes())
    wp=json.loads((west/"plan.json").read_bytes())
    am=json.loads((angles/"verified_manifest.json").read_bytes())
    ap=json.loads((angles/"plan.json").read_bytes())
    hm=json.loads((hd/"manifest.json").read_bytes())
    if wm["schema"]!="western-source-neutral-utc-grid-float64-pilot-v1-NONCANONICAL":
        raise ValueError("Unknown Western source grid")
    if wp["total_samples"]!=wm["total_samples"] or am["total_samples"]!=wm["total_samples"]:
        raise ValueError("Incompatible source count")
    if am["source_west_manifest_sha256"]!=digest(west/"verified_manifest.json"):
        raise ValueError("Location source is not the same Western index")
    if wm["plan_sha256"]!=digest(west/"plan.json") or am["plan_sha256"]!=digest(angles/"plan.json"):
        raise ValueError("Source plan no longer matches signed manifest")
    if wp["utc_start_inclusive"].replace("+00:00","Z")!=hm["utc_start"] or wp["utc_end_exclusive"].replace("+00:00","Z")!=hm["utc_end_exclusive"]:
        raise ValueError("HD and Western cache coverage differs")
    if swe.version!=wp["swisseph_version"]:
        raise ValueError("Swiss library version mismatch")
    for name,expected in wp["ephe_sha256"].items():
        if digest(ephe/name)!=expected:raise ValueError("Swiss file differs: "+name)
    swe.set_ephe_path(str(ephe))
    return wp,wm,ap,am,hm

def load_hd_states(hd,manifest):
    rows=[];first=None;last=None;h=hashlib.sha256()
    for shard in manifest["shards"]:
        path=hd/shard["filename"]
        if digest(path)!=shard["sha256"]:raise RuntimeError("HD source shard hash mismatch")
        raw=gzip.decompress(path.read_bytes())
        if len(raw)!=shard["uncompressed_bytes"]:raise RuntimeError("HD uncompressed size mismatch")
        h.update(raw)
        for line in raw.splitlines():
            r=json.loads(line)
            a=utc(r["start_utc"]);b=utc(r["end_utc"])
            if last and a!=last:raise RuntimeError("HD interval gap/overlap")
            rows.append((a,b,r["chart_features"]))
            if first is None:first=a
            last=b
    if len(rows)!=manifest["interval_count"] or h.hexdigest()!=manifest["canonical_rows_sha256"]:
        raise RuntimeError("HD source logical universe mismatch")
    return rows

def run(args):
    if args.out.exists():raise FileExistsError("Reference report already exists")
    reference=utc(args.reference_utc)
    wp,wm,ap,am,hm=strict_sources(args.western,args.location,args.hd,args.ephe)
    first,last=utc(wp["utc_start_inclusive"]),utc(wp["utc_end_exclusive"])
    if not first<=reference<last:raise ValueError("Actual chart outside requested century horizon")
    rows=load_hd_states(args.hd,hm)
    starts=[x[0] for x in rows]
    j=bisect.bisect_right(starts,reference)-1
    if j<0 or not rows[j][0]<=reference<rows[j][1]:
        raise RuntimeError("Actual time not covered by verified HD source states")
    fref=rows[j][2]
    core=(fref["type"],fref["authority"],fref["profile"])
    centers=frozenset(fref["defined_centers"]);channels=frozenset(fref["channels"])
    gates=fref["activation_gates"]
    durations=Counter();counts=Counter();signature_frequencies=Counter()
    hours=(last-first).total_seconds()/3600.
    for a,b,f in rows:
        h=(b-a).total_seconds()/3600.
        triple=(f["type"],f["authority"],f["profile"])==core
        c=frozenset(f["defined_centers"])==centers
        ch=frozenset(f["channels"])==channels
        allg=f["activation_gates"]==gates
        comparisons={
            "type":f["type"]==core[0],
            "type_authority":f["type"]==core[0] and f["authority"]==core[1],
            "type_authority_profile":triple,
            "triple_plus_defined_centers":triple and c,
            "triple_plus_complete_channels":triple and ch,
            "triple_plus_all_carrier_gates":triple and allg,
        }
        for key,flag in comparisons.items():
            if flag:counts[key]+=1;durations[key]+=h
        signature_frequencies[(f["type"],f["authority"],f["profile"],tuple(sorted(f["channels"])))]+=1
    site_lat,site_lon=ap["latitude"],ap["longitude"]
    jd=swe.julday(reference.year,reference.month,reference.day,
                  reference.hour+reference.minute/60.+reference.second/3600.)
    ref_lons=[]
    for planet in PLANETS:
        val,ret=swe.calc_ut(jd,planet,swe.FLG_SWIEPH|swe.FLG_SPEED)
        if (ret&(swe.FLG_SWIEPH|swe.FLG_JPLEPH|swe.FLG_MOSEPH))!=swe.FLG_SWIEPH:
            raise RuntimeError("Swiss fall-back for actual natal planet")
        ref_lons.append(val[0])
    ref_lons=np.asarray(ref_lons,dtype=np.float64)
    cusps,angles=swe.houses_ex(jd,site_lat,site_lon,b'P',swe.FLG_SWIEPH)
    ref_asc_sign=int(angles[0]//30)
    ref_signs=np.floor(ref_lons/30).astype(int)
    _,ref_subgroups=five_group_masks(ref_lons.reshape(1,7))
    good=[i for i,mask in enumerate(ref_subgroups) if bool(mask[0])]
    if not good:
        raise ValueError("Reference chart lacks a five-classical-body ten-major-aspect network within chosen tolerance")
    # Choose strongest of full 10/10 groups on purely chart geometry.
    orbs=nearest_major_orb(ref_lons.reshape(1,7))[0]
    chosen=min(good,key=lambda idx:float(np.sum(orbs[list(PAIR_SETS[idx])])))
    selected=GROUPS[chosen]
    wcounts=Counter();wdates={key:set() for key in ("any_five","same_selected_five",
        "moon_venus_both_exalted","selected_five_both_exalted",
        "selected_five_both_exalted_asc","seven_planet_sign_match","seven_planet_signs_and_asc")}
    for wsh,ash in zip(wm["chunks"],am["shards"],strict=True):
        if wsh["first_index"]!=ash["first_index"] or wsh["count"]!=ash["count"]:
            raise RuntimeError("Western and location index shard chronology differs")
        pw=args.western/"chunks"/wsh["file"]
        pa=args.location/"shards"/ash["file"]
        if digest(pw)!=wsh["sha256"] or digest(pa)!=ash["sha256"]:
            raise RuntimeError("Source cache shard hash changed")
        west=np.memmap(pw,dtype="<f8",mode="r",shape=(wsh["count"],8))
        ang=np.memmap(pa,dtype="<f8",mode="r",shape=(ash["count"],17))
        anyfive,allgroups=five_group_masks(west[:,:7])
        chosen_mask=allgroups[chosen]
        signs=np.floor(west[:,:7]/30).astype(int)
        dual=(signs[:,1]==1)&(signs[:,3]==11)
        ascsign=np.floor(ang[:,0]/30).astype(int)
        same7=np.all(signs==ref_signs.reshape(1,7),axis=1)
        masks={
            "any_five":anyfive,
            "same_selected_five":chosen_mask,
            "moon_venus_both_exalted":dual,
            "selected_five_both_exalted":chosen_mask&dual,
            "selected_five_both_exalted_asc":chosen_mask&dual&(ascsign==ref_asc_sign),
            "seven_planet_sign_match":same7,
            "seven_planet_signs_and_asc":same7&(ascsign==ref_asc_sign)
        }
        for key,mask in masks.items():
            offsets=np.flatnonzero(mask)
            wcounts[key]+=len(offsets)
            wdates[key].update(((wsh["first_index"]+offsets)//96).tolist())
    nstates=len(rows);uniques=sum(v==1 for v in signature_frequencies.values())
    return {
        "status":"POST_EXPOSURE_DESCRIPTIVE_MECHANICAL_RARITY_NOT_VALIDATED_PERSONALITY",
        "reference_utc":reference.isoformat(),"input_reference_private":True,
        "selected_dense_planets":[INDEXES[i] for i in selected],
        "all_10_pairwise_major_aspects_within_degrees":3.,
        "reference_ascendant_sign_index":ref_asc_sign,
        "source_sha256":{
            "western":digest(args.western/"verified_manifest.json"),
            "location":digest(args.location/"verified_manifest.json"),
            "hd":digest(args.hd/"manifest.json")},
        "HD_comparators":{k:{"matching_states":counts[k],
            "matching_duration_hours":round(durations[k],6),
            "fraction_of_century_by_duration":round(durations[k]/hours,9)}
            for k in sorted(counts)},
        "HD_reference_interval_hours":round((rows[j][1]-rows[j][0]).total_seconds()/3600,6),
        "HD_other_signature_baseline":{
           "all_structural_states":nstates,
           "distinct_type_authority_profile_channels_signatures":len(signature_frequencies),
           "singleton_signature_classes":uniques,
           "fraction_states_in_singleton_class":round(uniques/nstates,6)},
        "Western_grid_comparators":{k:{"matching_sample_instants":wcounts[k],
            "matching_UTC_dates":len(wdates[k]),
            "fraction_grid":round(wcounts[k]/wp["total_samples"],9)}
            for k in sorted(wcounts)},
        "total_Western_UTC_grid_samples":wp["total_samples"],
        "cautions":["Post-hoc feature selection from the actual chart prevents treating the rarity fraction as a calibrated probability",
          "Uniform UTC instants are not birth-population frequencies",
          "Western coverage applies only to 15-minute lattice, not intervening instants",
          "Matching a rare chart configuration is not evidence of psychological accuracy",
          "HD structural gate/Sun-line cache omits non-Sun lines and advanced variables"]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--reference-utc",required=True)
    p.add_argument("--ephe",required=True,type=Path)
    p.add_argument("--western",required=True,type=Path)
    p.add_argument("--location",required=True,type=Path)
    p.add_argument("--hd",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    result=run(args)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    b=(json.dumps(result,sort_keys=True,indent=2)+"\n").encode()
    args.out.write_bytes(b)
    print("MECHANICAL_RARITY_AUDIT",json.dumps({
        "HD_exact_full_channel_intervals":result["HD_comparators"]["triple_plus_complete_channels"]["matching_states"],
        "Western_any_five_days":result["Western_grid_comparators"]["any_five"]["matching_UTC_dates"],
        "Western_reference_five_days":result["Western_grid_comparators"]["same_selected_five"]["matching_UTC_dates"],
        "output_sha256":hashlib.sha256(b).hexdigest(),
        "no_personality_prediction":True},sort_keys=True))

if __name__=="__main__":main()
