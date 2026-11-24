#!/usr/bin/env python3
"""First bounded BaZi elemental-temperament and Zi Wei principal-star comparison.
Calendar evidence and person-specific outputs stay private. Not a complete
historical interpretation, validation, or new birth-data collection.
"""
from __future__ import annotations
import argparse,json,os
from collections import Counter,defaultdict
from itertools import product
from datetime import timedelta
from pathlib import Path
import numpy as np
import chinese_calendar_grid_v01 as cal
import compare_saravali_lunar_solar_century_v01 as s
import compare_planet_character_century_v01 as pc
import compare_full_grid_behavior_v01 as g
import compare_bounded_behavior_v01 as b

ROOT=b.ROOT
MAP=pc.MAP.parent/"chinese_bazi_ziwei_observable_v01.json"
MAP_SHA="af8b03d7cd4fc1ec88dce745141d1dfc40c80dc69ec6e264b1facb3219192900"
ELEMENTS=("wood","fire","earth","metal","water")
STARS=("Zi Wei","Tian Ji","Tai Yang","Wu Qu","Tian Tong","Lian Zhen","Tian Fu","Tai Yin","Tan Lang","Ju Men","Tian Xiang","Tian Liang","Qi Sha","Po Jun")
SCOPES=("day_stem","day_hour_stems","day_hour_stems_branches")
CONDITIONS=("flourishing_assumed","season_literal","season_deficiency_proxy")
SEASONS={"sixth_month_earth":np.array([4,4,0,0,0,1,1,2,3,3,3,4]),
         "transition_months_earth":np.array([4,2,0,0,2,1,1,2,3,3,2,4])}
BRANCH_ELEMENT=np.array([4,2,0,0,2,1,1,2,3,3,2,4])
LEAPS=("next","split15","same")
PALACES=("life","life_body_union")
MAPS=("direct","with_proxies")
NAYIN="金火木土金火水土金木水土火木水金火木土金火水土金木水土火木水"
BUREAU={"水":2,"木":3,"金":4,"土":5,"火":6}
BUREAU_LUT=np.zeros((10,12),np.int8)
for n in range(60):BUREAU_LUT[n%10,n%12]=BUREAU[NAYIN[n//2]]
# The original Zi Wei placement functions from the owner-authored core
# at archived 8eb6b26a / source blob efbd12627bd0b13215f54e3620d2c856439dbca2.
# Only the general natal main-star core is used here, never private fixtures.

def load_map():
    if b.digest(MAP)!=MAP_SHA:raise ValueError("Frozen Chinese observable map drift")
    x=json.loads(MAP.read_text());shared=pc.load_registry()
    if x["schema"]!="chinese_bazi_ziwei_observable_v01" or tuple(r["star"] for r in x["main_stars"])!=STARS:raise ValueError("Incomplete source catalogue")
    keys=set().union(*(set(v) for v in shared["domains"].values()))
    if len(x["elements"])!=11 or len({(r["element"],r["condition"]) for r in x["elements"]})!=11:raise ValueError("Missing element clauses")
    for r in x["elements"]+x["main_stars"]:
        if set(r["direct"])&set(r["proxy"]):raise ValueError("Conflicting mapping record")
        for k in ("direct","proxy"):
            if set(r[k])-keys or any(type(v)!=int or v not in (-1,1) for v in r[k].values()):raise ValueError("Invalid observable")
    return x,shared

def element_mask(p,scope):
    bits=(1<<(p[:,4]//2)).astype(np.int64)
    if scope!="day_stem":bits|=1<<(p[:,6]//2)
    if scope=="day_hour_stems_branches":bits|=(1<<BRANCH_ELEMENT[p[:,5]])|(1<<BRANCH_ELEMENT[p[:,7]])
    return bits

def admitted_condition(e,season,condition):
    if condition=="flourishing_assumed":return "flourishing"
    phase=(e-season)%5
    if phase in (0,1):return "flourishing"
    if e==0:return "dead" if phase==2 else "rest_captive"
    return "deficient" if condition=="season_deficiency_proxy" else None

def bazi_lut(reg,keys,mode,condition):
    rows=reg["elements"];p,n=s.table(rows,keys,mode)
    ix={(r["element"],r["condition"]):i for i,r in enumerate(rows)}
    out=np.zeros((2,5,32),np.uint64)
    for season,mask in product(range(5),range(32)):
        for e in range(5):
            if not mask&(1<<e):continue
            z=ix.get((ELEMENTS[e],admitted_condition(e,season,condition)))
            if z is not None:out[0,season,mask]|=p[z];out[1,season,mask]|=n[z]
    return out

def ziwei_masks(lunar,policy):
    ly,m,day,h=lunar.T
    leap=m<0;m=np.abs(m)
    m=np.where(leap&((policy=="next")|((policy=="split15")&(day>15))),m%12+1,m)
    ming=(1+m-h)%12;body=(1+m+h)%12
    ys=(ly-4)%10;yin=(ys%5*2+2)%10
    stem=(yin+(ming-2)%12)%10
    bureau=BUREAU_LUT[stem,ming]
    if np.any(bureau==0) or np.any((day<1)|(day>30)):raise ValueError("Zi Wei invalid bureau or lunar date")
    x=(-day)%bureau;zw=(2+(day+x)//bureau-1+np.where(x%2,-x,x))%12
    tf=(4-zw)%12
    pos=np.column_stack([zw,(zw-1)%12,(zw-3)%12,(zw-4)%12,(zw-5)%12,(zw-8)%12,
                         tf,(tf+1)%12,(tf+2)%12,(tf+3)%12,(tf+4)%12,(tf+5)%12,(tf+6)%12,(tf+10)%12])
    weights=1<<np.arange(14,dtype=np.int64)
    return {"life":((pos==ming[:,None])*weights).sum(axis=1),
            "life_body_union":(((pos==ming[:,None])|(pos==body[:,None]))*weights).sum(axis=1)}

def ziwei_lut(reg,keys,mode):
    rows=reg["main_stars"];p,n=s.table(rows,keys,mode)
    active=(np.arange(1<<14)[:,None]&(1<<np.arange(14)))!=0
    return s.bitset(active,(p,n))

def make_tables(reg,shared,evidence):
    keys,obs=s.obs_masks(shared,evidence)
    return ({(mode,condition):bazi_lut(reg,keys,mode,condition) for mode,condition in product(MAPS,CONDITIONS)},
            {mode:ziwei_lut(reg,keys,mode) for mode in MAPS},obs)

def models(feature,table):
    bz,zw,obs=table;p=feature["bazi"]
    for scope,condition,season,mode in product(SCOPES,CONDITIONS,SEASONS,MAPS):
        lut=bz[mode,condition];sel=element_mask(p,scope);se=SEASONS[season][p[:,3]]
        bits=(lut[0,se,sel],lut[1,se,sel])
        yield "bazi|"+"|".join((scope,condition,season,mode)),bits,feature["bazi_known"]
    for leap in LEAPS:
        masks=ziwei_masks(feature["ziwei"],leap)
        for scope,mode in product(PALACES,MAPS):
            bits=tuple(a[masks[scope]] for a in zw[mode])
            yield "ziwei|"+"|".join((leap,scope,mode)),bits,feature["ziwei_known"]
        # Predeclared capped union, no ranking-dependent arm choice:
        # source-native day+hour stems, literal season qualification, explicit
        # sixth-month Earth convention and Life Palace only, all leap variants.
        for mode in MAPS:
            se=SEASONS["sixth_month_earth"][p[:,3]];mask=element_mask(p,"day_hour_stems")
            l=bz[mode,"season_literal"]
            one=(l[0,se,mask],l[1,se,mask])
            two=tuple(a[masks["life"]] for a in zw[mode])
            yield "union|"+leap+"|"+mode,s.union(one,two),feature["bazi_known"]&feature["ziwei_known"]

def reference(beijing,local,cache,tables,hd):
    refs=[{} for _ in tables]
    for clock,wall in zip(cal.CLOCKS,(beijing,local),strict=True):
        f=cal.features(np.array([beijing]),np.array([wall]),cache)
        for table,h,r in zip(tables,hd,refs,strict=True):
            for tag,bits,known in models(f,table):
                if not known[0]:raise ValueError("Exact reference calendar unresolved")
                z=s.score(bits,table[2])
                d={k:float(v[0]) if k in ("score","lo","hi") else int(v[0]) for k,v in z.items()}
                d.update(joint=(h+d["score"])/2,joint_lo=(h+d["lo"])/2,joint_hi=(h+d["hi"])/2)
                r[clock+"|"+tag]=d
    return refs

def scan(start,ids,cache,lookups,tables,refs,counts,coverage,hd_target):
    if np.any(ids<-1) or np.any(ids>=g.HD_N):raise ValueError("Invalid HD index")
    knownHD=ids>=0
    bsec,lsec=cal.wall_arrays(start,len(ids))
    features=[cal.features(bsec,wall,cache) for wall in (bsec,lsec)]
    common=knownHD.copy()
    for f in features:common&=f["bazi_known"]&f["ziwei_known"]
    for clock,f in zip(cal.CLOCKS,features,strict=True):
        for family in ("bazi","ziwei"):
            good=f[family+"_known"]
            coverage[clock+"|"+family].update(rows=len(ids),unknown_HD=int((~knownHD).sum()),
                    calendar_unknown_known_HD=int((knownHD&~good).sum()),ranked=int((knownHD&good).sum()))
    for lookup,table,ref,co,h0 in zip(lookups,tables,refs,counts,hd_target,strict=True):
        h=lookup[np.maximum(ids,0)]
        all_hi=common.copy();any_hi=np.zeros(len(ids),bool);all_tie=common.copy()
        for clock,f in zip(cal.CLOCKS,features,strict=True):
            for tag,bits,good in models(f,table):
                k=clock+"|"+tag;t=ref[k];v=s.score(bits,table[2]);known=knownHD&good
                for metric,c in s.compare_row(v,h,known,t).items():co[k][metric.replace("vedic","chinese")].update(c)
                # Distinguish strictly better in each system from averaged rank.
                hd_ge=known&(h>=h0-g.EPS);ch_ge=known&(v["score"]>=t["score"]-g.EPS)
                hd_gt=known&(h>h0+g.EPS);ch_gt=known&(v["score"]>t["score"]+g.EPS)
                co[k]["pareto"].update(both_strict=int((hd_gt&ch_gt).sum()),both_ge=int((hd_ge&ch_ge).sum()),
                    chinese_strict_hd_ge=int((hd_ge&ch_gt).sum()),both_tied=int((hd_ge&ch_ge&~hd_gt&~ch_gt).sum()))
                if tag.startswith("union|"):
                    j=(h+v["score"])/2;hi=common&(j>t["joint"]+g.EPS)
                    all_hi&=hi;any_hi|=hi;all_tie&=common&(np.abs(j-t["joint"])<=g.EPS)
        co["across_union"]["coverage"].update(ranked=int(common.sum()),higher_all=int(all_hi.sum()),higher_any=int(any_hi.sum()),tied_all=int(all_tie.sum()))

def validate(co,refs,coverage):
    if len(refs)!=108 or set(co)-{"across_union"}!=set(refs):raise ValueError("Missing experiment arms")
    for tag,t in refs.items():
        r=co[tag];n=r["coverage"]["ranked"]
        if any(sum(r[k].values())!=n for k in ("chinese","joint")) or sum(r["matched_joint"].values())!=r["coverage"]["matched_known_items"]:raise ValueError("Rank accounting drift")
        for k in ("chinese_bounds","joint_bounds"):
            z=r[k]
            if z["certainly_lower"]+z["could_equal_or_exceed"]!=n or z["certainly_higher"]>z["could_equal_or_exceed"]:raise ValueError("Interval accounting drift")
        if r["pareto"]["both_strict"]>r["pareto"]["chinese_strict_hd_ge"] or r["pareto"]["both_tied"]>r["pareto"]["both_ge"]:raise ValueError("Pareto accounting drift")
        clock,family,*_=tag.split("|")
        if family in ("bazi","ziwei") and n!=coverage[clock+"|"+family]["ranked"]:raise ValueError("Calendar coverage drift")

def run(a):
    paths=[a.west,a.angles,a.hd_cache,a.join,a.calendar,a.mapping_library,a.inventory,a.prior_vedic,*a.evidence,*a.hd_evidence,a.output]
    if any(p.resolve().is_relative_to(ROOT) for p in paths):raise ValueError("Private data outside public checkout required")
    if a.output.exists() or len(a.evidence)!=2 or len(a.hd_evidence)!=2:raise ValueError("Two frozen profiles and new output required")
    W,WM,A,AM,H,proof=g.verify_inputs(a)
    cal.witnesses()
    with np.load(a.calendar,allow_pickle=False) as f:cache={k:f[k] for k in f.files}
    if str(cache["runner_sha256"])!=b.digest(cal.__file__) or str(cache["grid_plan_sha256"])!=b.digest(a.west/"plan.json"):raise ValueError("Calendar cache provenance drift")
    cacheproof=json.loads(str(cache["proof"]))
    reg,shared=load_map();prev=json.loads(a.prior_vedic.read_text())
    if prev["grid_rows"]!=g.N or prev["source_map_sha256"]!=s.MAP_SHA:raise ValueError("Prior evidence receipt drift")
    inv=json.loads(a.inventory.read_text());c=next(u["chart_midpoint"] for u in inv["comparison_units"] if u["private_id"]=="REFERENCE")
    w=c["Western"]["source_witness"];at=g.timestamp(c["utc"])
    if at!=g.timestamp(w["UTC"]) or any(float(w["site"][k])!=float(A[k]) for k in ("latitude","longitude","elevation_m")):raise ValueError("Reference time/site mismatch")
    # This same research location uses the declared historical America/New_York
    # civil clock, not a location inferred from the behavior or fitted rank.
    from zoneinfo import ZoneInfo
    from datetime import timezone,timedelta
    beijing=cal.wall_seconds(at.astimezone(cal.BEIJING))
    local=cal.wall_seconds(at.astimezone(ZoneInfo(cal.SITE_ZONE)))
    mappings=b.load_mapping(a.mapping_library);hd_ev=[];tables=[];hvs=[];prov=[]
    for i,(hp,ep) in enumerate(zip(a.hd_evidence,a.evidence,strict=True)):
        h=json.loads(hp.read_text());e=json.loads(ep.read_text());pr=prev["profiles"][i]
        if h["inventory_sha256"]!=b.digest(a.inventory) or e["map_sha256"]!=pc.MAP_SHA or e["hd_evidence_sha256"]!=b.digest(hp):raise ValueError("Evidence binding drift")
        if pr["HD_evidence_sha256"]!=b.digest(hp) or pr["evidence_sha256"]!=b.digest(ep):raise ValueError("Previous evidence changed")
        hv=b.hd_score(c["HD"],mappings,h["hd"])["score"]
        hd_ev.append(h);tables.append(make_tables(reg,shared,e["observations"]));hvs.append(hv)
        prov.append({"HD_evidence_sha256":b.digest(hp),"evidence_sha256":b.digest(ep),"reference_HD_score":hv})
    refs=reference(beijing,local,cache,tables,hvs)
    lookups,idx,_=g.load_hd_scores(a.hd_cache,mappings,hd_ev,at,c["HD"])
    if any(z[idx]!=hv for z,hv in zip(lookups,hvs,strict=True)):raise ValueError("Reference HD drift")
    start=g.timestamp(W["utc_start_inclusive"])
    counts=[defaultdict(lambda:defaultdict(Counter)) for _ in refs];coverage=defaultdict(Counter);processed=0
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not(wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):raise ValueError("Original grid alignment drift")
        p=a.west/"chunks"/wi["file"];q=a.angles/"shards"/ai["file"];hp=a.join/"shards"/hi["file"]
        for f,meta,size in zip((p,q,hp),(wi,ai,hi),(64,136,4),strict=True):
            if f.stat().st_size!=n*size or b.digest(f)!=meta["sha256"]:raise ValueError("Original source shard drift")
        ids=np.memmap(hp,dtype="<i4",mode="r",shape=(n,))
        scan(start+timedelta(seconds=900*processed),np.asarray(ids),cache,lookups,tables,refs,counts,coverage,hvs)
        processed+=n
        if processed%500000==0 or processed==g.N:print("Chinese behavior scoring:",processed,"/",g.N,flush=True)
    if processed!=g.N or any(z["rows"]!=g.N or z["unknown_HD"]!=125 or z["ranked"]+z["unknown_HD"]+z["calendar_unknown_known_HD"]!=g.N for z in coverage.values()):raise ValueError("Calendar coverage accounting drift")
    for co,r in zip(counts,refs,strict=True):validate(co,r,coverage)
    out={"status":"EXECUTED_BOUNDED_CHINESE_BEHAVIOR_FINITE_GRID_NOT_VALIDATION","grid_rows":processed,"arms":108,
         "map_sha256":MAP_SHA,"runner_sha256":b.digest(__file__),"calendar_sha256":b.digest(a.calendar),
         "calendar_proof":cacheproof,"calendar_coverage":dict(coverage),"grid_proof":proof,
         "profiles":[{**p,"reference":r,"counts":dict(co)} for p,r,co in zip(prov,refs,counts,strict=True)]}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("Private Chinese full-grid receipt completed; ranks and calendar coverage reconciled.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","calendar","mapping-library","inventory","prior-vedic","output"):
        p.add_argument("--"+k,type=Path,required=True)
    for k in ("evidence","hd-evidence"):p.add_argument("--"+k,action="append",required=True,type=Path)
    run(p.parse_args())
if __name__=="__main__":main()
