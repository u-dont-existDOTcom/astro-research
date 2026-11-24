#!/usr/bin/env python3
"""Bounded Saravali XV/XVI development scoring on the original finite grid.
All individual evidence and output are private. No historical unique
conjunction, strength, empirical accuracy or complete Vedic model claimed.
"""
from __future__ import annotations
import argparse,json,os
from collections import Counter,defaultdict
from itertools import combinations
from pathlib import Path
import numpy as np
import swisseph as swe
import compare_planet_character_century_v01 as pc
import compare_bounded_behavior_v01 as b
import compare_full_grid_behavior_v01 as g

ROOT=b.ROOT
MAP=pc.MAP.parent/"saravali_xv_xvi_shared_observable_v01.json"
MAP_SHA="80eeea6ef31ec7a82242cb5ee83c58d049d0b023673ffab8cd4da15362e59beb"
BODIES=tuple(pc.BODIES)
EDGES=tuple(combinations(range(7),2))
EBITS=np.left_shift(np.int64(1),np.arange(21,dtype=np.int64))
GEOMS=("lahiri_same_sign","raman_same_sign","degree_3","degree_10")
OVERLAP=("pairs_inclusive","triples_inclusive","both_inclusive","isolated_exact_groups")
MAPS=("direct","with_proxies")
TOL=1e-5
PLANETS=(swe.SUN,swe.MOON,swe.MERCURY,swe.VENUS,swe.MARS,swe.JUPITER,swe.SATURN)

def load_map():
    if b.digest(MAP)!=MAP_SHA:raise ValueError("Frozen Saravali mapping changed")
    x=json.loads(MAP.read_text());shared=pc.load_registry()
    if x["schema"]!="saravali_xv_xvi_shared_observable_v01" or x["shared_vocabulary_sha256"]!=pc.MAP_SHA:
        raise ValueError("Shared vocabulary mismatch")
    rules=x["rules"]
    keys=set().union(*(set(v) for v in shared["domains"].values()))
    for ch,size,first,last in ((15,2,2,22),(16,3,1,35)):
        rr=[r for r in rules if r["chapter"]==ch]
        if [r["verse"] for r in rr]!=list(range(first,last+1)) or {frozenset(r["bodies"]) for r in rr}!={frozenset(q) for q in combinations(BODIES,size)}:
            raise ValueError("Incomplete historical catalogue")
    if len(rules)!=56:raise ValueError("Unexpected catalogue count")
    for r in rules:
        if set(r["direct"])&set(r["proxy"]):raise ValueError("Duplicate item direction")
        for k in ("direct","proxy"):
            if set(r[k])-keys or any(type(v)!=int or v not in (-1,1) for v in r[k].values()):
                raise ValueError("Invalid source direction")
    return x,shared

def rule_edges(rules):
    req=[];external=[];sizes=[]
    for r in rules:
        group={BODIES.index(n) for n in r["bodies"]}
        req.append(sum(int(w) for (a,c),w in zip(EDGES,EBITS,strict=True) if a in group and c in group))
        external.append(sum(int(w) for (a,c),w in zip(EDGES,EBITS,strict=True) if (a in group)!=(c in group)))
        sizes.append(len(group))
    return np.array(req),np.array(external),np.array(sizes)

def graph_from_signs(lon,ayanamsa):
    sid=(lon-ayanamsa[:,None])%360
    signs=np.floor(sid/30).astype(np.int8)
    near=np.minimum(sid%30,30-sid%30)<=TOL
    code=np.zeros(len(lon),np.int64)
    for (a,c),w in zip(EDGES,EBITS,strict=True):
        code|=np.where(signs[:,a]==signs[:,c],w,0)
    return code,near.any(axis=1)

def graph_from_distance(lon,deg):
    code=np.zeros(len(lon),np.int64);unknown=np.zeros(len(lon),bool)
    for (a,c),w in zip(EDGES,EBITS,strict=True):
        d=np.abs((lon[:,a]-lon[:,c]+180)%360-180)
        code|=np.where(d<=deg,w,0);unknown|=np.abs(d-deg)<=TOL
    return code,unknown

def ayanamsas(jds,mode):
    swe.set_sid_mode(mode)
    # Same standard geocentric ecliptic convention as direct Swiss sidereal.
    out=np.empty(len(jds))
    for i,jd in enumerate(jds):
        flag,out[i]=swe.get_ayanamsa_ex_ut(float(jd),swe.FLG_SWIEPH)
        if not np.isfinite(out[i]):raise ValueError("Nonfinite sidereal correction")
    return out

def parity(lon,jds,a,mode):
    swe.set_sid_mode(mode)
    worst=0.
    for i in sorted({0,len(jds)//2,len(jds)-1}):
        for k,planet in enumerate(PLANETS):
            direct,flag=swe.calc_ut(float(jds[i]),planet,swe.FLG_SWIEPH|swe.FLG_SPEED|swe.FLG_SIDEREAL)
            if not flag&swe.FLG_SWIEPH:raise ValueError("Swiss ephemeris fallback")
            err=abs((float(lon[i,k])-a[i]-direct[0]+180)%360-180)
            worst=max(worst,err)
    if worst>TOL:raise ValueError("Cached tropical to direct sidereal parity exceeded tolerance")
    return worst

def all_graphs(lon,jds,check=True):
    if lon.ndim!=2 or lon.shape[1]!=7 or len(lon)!=len(jds) or np.any(~np.isfinite(lon)) or np.any((lon<0)|(lon>=360)):
        raise ValueError("Seven normalized longitudes at aligned UTC clocks required")
    out={};err={}
    for tag,mode in zip(GEOMS[:2],(swe.SIDM_LAHIRI,swe.SIDM_RAMAN),strict=True):
        a=ayanamsas(jds,mode)
        if check:err[tag]=parity(lon,jds,a,mode)
        out[tag]=graph_from_signs(lon,a)
    for tag,deg in zip(GEOMS[2:],(3.,10.),strict=True):out[tag]=graph_from_distance(lon,deg)
    return out,err

def memberships(graph_codes,edge_spec):
    req,ext,size=edge_spec
    active=(graph_codes[:,None]&req)==req
    isolated=active&((graph_codes[:,None]&ext)==0)
    return {"pairs_inclusive":active&(size==2),
            "triples_inclusive":active&(size==3),
            "both_inclusive":active,
            "isolated_exact_groups":isolated}

def observation_tables(reg,shared,obs):
    keys=tuple(k for d in pc.DOMAINS for k in shared["domains"][d])
    b.checked_obs(obs,set(keys));obsvec=np.array([obs.get(k) or 0 for k in keys],np.int8)
    weights=np.zeros(len(keys))
    for d in pc.DOMAINS:
        index=np.array([k in shared["domains"][d] for k in keys])
        denom=int((index&(obsvec!=0)).sum())
        if denom:weights[index]=.5/denom
    tabs={}
    for mode in MAPS:
        signed=np.array([[r["direct"].get(k,r["proxy"].get(k,0) if mode=="with_proxies" else 0) for k in keys] for r in reg["rules"]],np.int8)
        tabs[mode]=(signed,obsvec,weights)
    return tabs

def evaluate_graphs(graph_codes,edge_spec,tables):
    """Count each shared observable at most once. Opposite claims conflict;
    attenuation envelope admits either sign or no testimony, not reversal."""
    masks=memberships(graph_codes,edge_spec)
    out={}
    for overlap,active in masks.items():
        for mode,(signed,obs,weights) in tables.items():
            pos=(active.astype(np.int16)@(signed==1).astype(np.int16))>0
            neg=(active.astype(np.int16)@(signed==-1).astype(np.int16))>0
            prediction=pos.astype(np.int8)-neg.astype(np.int8)
            agreed=prediction*obs
            has_pos=(pos&(obs[None,:]==1))|(neg&(obs[None,:]==-1))
            has_neg=(neg&(obs[None,:]==1))|(pos&(obs[None,:]==-1))
            out[overlap+"|"+mode]={
                "score":agreed@weights,
                "lo":-(has_neg@weights),
                "hi":has_pos@weights,
                "active_rules":active.sum(axis=1),
                "known_items":((pos|neg)&(obs[None,:]!=0)).sum(axis=1),
                "conflicting_items":(pos&neg&(obs[None,:]!=0)).sum(axis=1)}
    return out

def compact_graph_scores(graph,edge_spec,tables):
    codes,inverse=np.unique(graph,return_inverse=True)
    compact=evaluate_graphs(codes,edge_spec,tables)
    return {k:{f:v[inverse] for f,v in z.items()} for k,z in compact.items()}

def exact_reference(c,graphs,edge_spec,tables,hd):
    result={}
    for geom,(code,near) in graphs.items():
        if bool(near[0]):raise ValueError("Exact reference near tested geometry boundary")
        for tag,z in evaluate_graphs(code,edge_spec,tables).items():
            d={k:float(v[0]) if k in ("score","lo","hi") else int(v[0]) for k,v in z.items()}
            d.update({"joint":(hd+d["score"])/2,"joint_lo":(hd+d["lo"])/2,"joint_hi":(hd+d["hi"])/2})
            result[geom+"|"+tag]=d
    return result

def scan(lon,jds,ids,lookups,tables,refs,edge_spec,counts,geo_count,maxerr):
    if np.any(ids<-1) or np.any(ids>=g.HD_N):raise ValueError("HD join index out of range")
    hd_known=ids>=0
    graphs,err=all_graphs(lon,jds)
    for tag,e in err.items():maxerr[tag]=max(maxerr.get(tag,0.),e)
    # For across-arm intersections require usable geometry under every arm.
    all_known=hd_known.copy()
    for _,near in graphs.values():all_known&=~near
    robust=[{"higher_all":all_known.copy(),"higher_any":np.zeros(len(ids),bool),"tied_all":all_known.copy()} for _ in tables]
    for geom,(code,near) in graphs.items():
        known=hd_known&~near
        geo_count[geom].update({"rows":len(ids),"ranked":int(known.sum()),"unknown_HD":int((~hd_known).sum()),
                               "geometry_unknown_with_known_HD":int((hd_known&near).sum())})
        for i,(tab,lookup,ref,co) in enumerate(zip(tables,lookups,refs,counts,strict=True)):
            h=lookup[np.maximum(ids,0)]
            z=compact_graph_scores(code,edge_spec,tab)
            for tag,v in z.items():
                name=geom+"|"+tag;t=ref[name];out=co[name]
                score=v["score"];joint=(h+score)/2
                matched=known&(v["known_items"]==t["known_items"])
                out["vedic"].update(g.exact_counts(score,t["score"],known))
                out["joint"].update(g.exact_counts(joint,t["joint"],known))
                out["matched_joint"].update(g.exact_counts(joint,t["joint"],matched))
                out["vedic_bounds"].update(g.bound_counts(v["lo"],v["hi"],(t["lo"],t["hi"]),known))
                out["joint_bounds"].update(g.bound_counts((h+v["lo"])/2,(h+v["hi"])/2,(t["joint_lo"],t["joint_hi"]),known))
                out["coverage"].update({"ranked":int(known.sum()),"has_active_rule":int((known&(v["active_rules"]>0)).sum()),
                    "has_known_items":int((known&(v["known_items"]>0)).sum()),
                    "conflict":int((known&(v["conflicting_items"]>0)).sum()),"matched_known_items":int(matched.sum())})
                hi=all_known&(joint>t["joint"]+g.EPS)
                robust[i]["higher_all"]&=hi
                robust[i]["higher_any"]|=hi
                robust[i]["tied_all"]&=all_known&(np.abs(joint-t["joint"])<=g.EPS)
    for co,r in zip(counts,robust,strict=True):
        co["across_all"]["coverage"].update({"ranked":int(all_known.sum()),
               **{k:int(v.sum()) for k,v in r.items()}})

def validate(count,geo,ref):
    if len(ref)!=32 or set(count)-{"across_all"}!=set(ref):raise ValueError("Missing experiment arms")
    for tag,t in ref.items():
        co=count[tag];ranked=geo[tag.split("|")[0]]["ranked"]
        if co["coverage"]["ranked"]!=ranked:raise ValueError("Coverage drift")
        for k in ("vedic","joint"):
            if sum(co[k].values())!=ranked:raise ValueError("Exact count mismatch")
        if sum(co["matched_joint"].values())!=co["coverage"]["matched_known_items"]:raise ValueError("Matched count mismatch")
        for k in ("vedic_bounds","joint_bounds"):
            z=co[k]
            if z["certainly_lower"]+z["could_equal_or_exceed"]!=ranked or z["certainly_higher"]>z["could_equal_or_exceed"]:
                raise ValueError("Bounds accounting mismatch")

def run(a):
    paths=[a.west,a.angles,a.hd_cache,a.join,a.ephemeris,a.mapping_library,a.inventory,a.prior_planet,*a.evidence,*a.hd_evidence,a.output]
    if any(p.resolve().is_relative_to(ROOT) for p in paths):raise ValueError("Private data outside public checkout required")
    if a.output.exists() or len(a.evidence)!=2 or len(a.hd_evidence)!=2:raise ValueError("Two frozen evidence profiles and new output required")
    W,WM,A,AM,H,proof=g.verify_inputs(a)
    if swe.version!=W["swisseph_version"] or W["requested_flags"]!="SWIEPH|SPEED" or W["record_order"][:7]!=list(BODIES):
        raise ValueError("Original source coordinate convention drift")
    for name,h in W["ephe_sha256"].items():
        if b.digest(a.ephemeris/name)!=h:raise ValueError("Original ephemeris SHA drift")
    swe.set_ephe_path(str(a.ephemeris))
    reg,shared=load_map();edge_spec=rule_edges(reg["rules"])
    inv=json.loads(a.inventory.read_text());c=next(u["chart_midpoint"] for u in inv["comparison_units"] if u["private_id"]=="REFERENCE")
    w=c["Western"]["source_witness"];at=g.timestamp(c["utc"])
    if at!=g.timestamp(w["UTC"]):raise ValueError("Reference instant drift")
    if any(float(w["site"][k])!=float(A[k]) for k in ("latitude","longitude","elevation_m")):raise ValueError("Reference comparison site drift")
    jd0=b.base.reg.initial.julian_from_utc(W["utc_start_inclusive"]) if hasattr(b.base.reg.initial,"julian_from_utc") else None
    # Both grid and exact reference use the same explicit UTC-to-Julian conversion.
    start=g.timestamp(W["utc_start_inclusive"])
    def jd(dt):return swe.julday(dt.year,dt.month,dt.day,dt.hour+dt.minute/60+dt.second/3600+dt.microsecond/3.6e9)
    jd0=jd(start);refjd=jd(at)
    lon=np.array([[float(w["traditional_planets"][z]["longitude_degrees"]) for z in BODIES]])
    graphs,maxerr=all_graphs(lon,np.array([refjd]))
    old=json.loads(a.prior_planet.read_text())
    if old["grid_rows"]!=g.N or old["source_map_sha256"]!=pc.MAP_SHA:raise ValueError("Prior comparison receipt drift")
    mappings=b.load_mapping(a.mapping_library);hd_ev=[];tables=[];refs=[];prov=[]
    for k,(hp,ep) in enumerate(zip(a.hd_evidence,a.evidence,strict=True)):
        h=json.loads(hp.read_text());e=json.loads(ep.read_text())
        if h["inventory_sha256"]!=b.digest(a.inventory) or e["map_sha256"]!=pc.MAP_SHA or e["hd_evidence_sha256"]!=b.digest(hp):raise ValueError("Frozen evidence binding drift")
        if old["profiles"][k]["evidence_sha256"]!=b.digest(ep) or old["profiles"][k]["HD_evidence_sha256"]!=b.digest(hp):raise ValueError("Previous frozen evidence changed")
        table=observation_tables(reg,shared,e["observations"])
        hv=b.hd_score(c["HD"],mappings,h["hd"])["score"]
        refs.append(exact_reference(c,graphs,edge_spec,table,hv));tables.append(table);hd_ev.append(h)
        prov.append({"evidence_sha256":b.digest(ep),"HD_evidence_sha256":b.digest(hp),"reference_HD_score":hv})
    lookups,idx,_=g.load_hd_scores(a.hd_cache,mappings,hd_ev,at,c["HD"])
    if any(z[idx]!=p["reference_HD_score"] for z,p in zip(lookups,prov,strict=True)):raise ValueError("HD score drift")
    counts=[defaultdict(lambda:defaultdict(Counter)) for _ in refs]
    geo=defaultdict(Counter);processed=0
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not(wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):
            raise ValueError("Original grid alignment drift")
        p=a.west/"chunks"/wi["file"];hp=a.join/"shards"/hi["file"]
        if p.stat().st_size!=n*64 or hp.stat().st_size!=n*4 or b.digest(p)!=wi["sha256"] or b.digest(hp)!=hi["sha256"]:raise ValueError("Source shard changed")
        P=np.memmap(p,dtype="<f8",mode="r",shape=(n,8))
        ids=np.memmap(hp,dtype="<i4",mode="r",shape=(n,))
        # Limit temporary score arrays and preserve exact clocks.
        for offset in range(0,n,25000):
            stop=min(offset+25000,n)
            jds=jd0+(processed+np.arange(offset,stop,dtype=float))/96.
            scan(np.asarray(P[offset:stop,:7]),jds,np.asarray(ids[offset:stop]),lookups,tables,refs,edge_spec,counts,geo,maxerr)
        processed+=n
        if processed%500000==0 or processed==g.N:print("Saravali scoring:",processed,"/",g.N,flush=True)
    if processed!=g.N:raise ValueError("Incomplete century")
    for z in geo.values():
        if z["rows"]!=g.N or z["unknown_HD"]!=125 or z["ranked"]+z["unknown_HD"]+z["geometry_unknown_with_known_HD"]!=g.N:raise ValueError("Geometry coverage accounting mismatch")
    for co,r in zip(counts,refs,strict=True):validate(co,geo,r)
    result={"status":"EXECUTED_FINITE_GRID_SARAVALI_PAIR_TRIPLE_DEVELOPMENT_NOT_VALIDATION",
         "grid_rows":processed,"geometry_coverage":dict(geo),"sidereal_sample_max_error_degrees":maxerr,
         "source_map_sha256":MAP_SHA,"runner_sha256":b.digest(__file__),"prior_planet_sha256":b.digest(a.prior_planet),"grid_proof":proof,
         "arms":32,"profiles":[{**p,"reference":r,"counts":dict(co)} for p,r,co in zip(prov,refs,counts,strict=True)]}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
    print("Private Saravali result completed; all geometry and score counts reconciled.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","ephemeris","mapping-library","inventory","prior-planet","output"):
        p.add_argument("--"+k,required=True,type=Path)
    for k in ("evidence","hd-evidence"):
        p.add_argument("--"+k,action="append",required=True,type=Path)
    run(p.parse_args())
if __name__=="__main__":main()
