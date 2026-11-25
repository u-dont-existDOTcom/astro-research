#!/usr/bin/env python3
"""Execute a frozen development-selected HD/Western pair on another profile.

No re-selection on the transfer subject. Entire original UTC grid; Western
sect recomputed at the supplied site. Separate birth-record alternatives and
evidence codings are reported, never chosen by their scores.
"""
from __future__ import annotations
import argparse,gzip,json,os,re,zipfile,xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import swisseph as swe
import select_fixed_transfer_models_v01 as sel
import compare_hd_archetype_century_v01 as h
import compare_hd_specific_observables_v01 as q
import compare_conditioned_character_century_v01 as co
import compare_planet_character_century_v01 as pc
from hdmatch.chart import SwissEphemerisProvider,calculate_chart
b=h.b;g=h.g
BODIES=(swe.SUN,swe.MOON,swe.MERCURY,swe.VENUS,swe.MARS,swe.JUPITER,swe.SATURN)
FLAGS=swe.FLG_SWIEPH|swe.FLG_SPEED

def exact_rank(a,ref,known):
    return dict(g.exact_counts(a,ref,known))

def pair_counts(hd,w,hr,wr,known):
    x=hd-hr;y=w-wr;e=g.EPS
    return {"HD":exact_rank(hd,hr,known),"Western":exact_rank(w,wr,known),
            "equal_mean":exact_rank((hd+w)/2,(hr+wr)/2,known),
            "strict_both":int((known&(x>e)&(y>e)).sum()),
            "no_lower_both":int((known&(x>=-e)&(y>=-e)).sum()),
            "tied_both":int((known&(np.abs(x)<=e)&(np.abs(y)<=e)).sum())}

def add(a,z):
    for k,v in z.items():
        if isinstance(v,dict):add(a.setdefault(k,{}),v)
        else:a[k]=a.get(k,0)+v

def jd(at):
    return swe.julday(at.year,at.month,at.day,at.hour+at.minute/60+at.second/3600+at.microsecond/3.6e9)

def planet(j,body):
    v,f=swe.calc_ut(j,body,FLAGS)
    if f&(swe.FLG_JPLEPH|swe.FLG_SWIEPH|swe.FLG_MOSEPH)!=swe.FLG_SWIEPH:
        raise ValueError("Ephemeris fallback")
    return v

def altitude(j,site,sun):
    return swe.azalt(j,swe.ECL2HOR,site,0.,0.,sun[:3])[1]

def exact_west(at,site):
    j=jd(at);p=[planet(j,k) for k in BODIES]
    return np.asarray([[v[0] for v in p]]),np.asarray([altitude(j,site,p[0])])

def selected_west(lon,alt,tag,tables,signobs):
    scheme,co0,tol,mp,scope,geometry,policy,kind=tag.split("|")
    if co0 not in ("True","False") or geometry not in ("geometry","phase_envelope") or policy not in co.POLICIES or kind not in ("sign","character","blend"):
        raise ValueError("Unsupported selected Western branch")
    src=pc.src;tol=float(tol);valid=np.abs(alt)>b.base.SUN_ALT_UNCERTAINTY
    ml,mh,_=src.aspect_bounds(lon,2,tol,mp,scope)
    ll,lh,_=src.aspect_bounds(lon,1,tol,"degree_near_rays",scope)
    bm=b.base.four_mode_votes(lon[:,2],alt,scheme,co0=="True").astype(np.int16)
    bl=b.base.four_mode_votes(lon[:,1],alt,scheme,co0=="True").astype(np.int16)
    gm,pm=src.interval_leader(bm+ml,bm+(mh if geometry=="geometry" else 1),valid)
    gl,pl=src.interval_leader(bl+ll,bl+(lh if geometry=="geometry" else 1),valid)
    table,ct,_=tables;votes=g.vote_arrays(lon,signobs)
    condition=co.all_conditions(lon,alt)[policy]
    m,l,v=co.evaluate(gm,pm,gl,pl,condition,table,ct,votes,np.zeros(len(lon)))
    ms,ls,ph=votes
    direct=b.family(ms[:,2],ls[:,1],ph,np.zeros(len(lon)))[0]
    return v[kind],direct,{"mercury":gm,"moon":gl,"character_mercury":m["character"],"character_moon":l["character"],"sign_mercury":m["sign"],"sign_moon":l["sign"],"phase":ph}

def hd_values(geo,base,profile,tag,groups,shared,specific_groups,keys,domains):
    fam,mode,kind=tag.split("|")
    shared_keys=tuple(k for d in pc.DOMAINS for k in shared["domains"][d])
    bb=h.model_bits(geo,groups,shared_keys,mode)[fam]
    sb=h.model_bits(geo,specific_groups,keys,mode)[fam]
    v=h.s.score(bb,h.s.obs_masks(shared,profile["shared"])[1])
    t=h.s.score(sb,q.masks(keys,domains,profile["specific"]))
    vals=q.components(base,v["score"],t["score"])
    return vals[kind],v,t

def exact_hd(at,provider):
    comp=calculate_chart(provider,at);bg=comp.bodygraph
    return {"activation_gates":{f"{a.side}:{a.body.value}":a.gate for a in comp.activations},
            "profile":bg.profile,"channels":list(bg.channels),"defined_centers":[x.value for x in bg.defined_centers],"type":bg.type.value}

def verify_transfer_evidence(a,selection,rows,shared,keys):
    z=json.loads(a.transfer_evidence.read_text())
    if z["selection_sha256"]!=b.digest(a.selection) or z["source_maps"]!={"generic":b.digest(a.mapping_library),"shared":pc.MAP_SHA,"specific":q.MAP_SHA}:raise ValueError("Transfer evidence binding")
    p=Path(z["source_file"])
    if p.resolve().is_relative_to(b.ROOT) or b.digest(p)!=z["source_sha256"]:raise ValueError("Transfer interview drift")
    ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(p) as f:r=ET.fromstring(f.read("word/document.xml"))
    lines=["".join(t.text or "" for t in x.findall(".//w:t",ns)).strip() for x in r.findall(".//w:p",ns)]
    turns=[int(m[1]) for l in lines if (m:=re.match(r"^(\d+)\. (.*\?)$",l))]
    if turns!=list(range(1,97)) or z["source_count"]!=len(turns):raise ValueError("Incomplete transfer interview")
    allowed={"hd":{r["mapping_id"] for r in rows},"western":b.WEST_KEYS,"shared":set().union(*(set(v) for v in shared["domains"].values())),"specific":set(keys)}
    for i,pr in enumerate(z["profiles"]):
        label=("broad","narrow")[i]
        if pr["label"]!=label:raise ValueError("Profile order")
        for f,ks in allowed.items():
            if set(pr[f])!=ks:raise ValueError("Transfer item coverage")
            b.checked_obs(pr[f],ks)
            for k,v in pr[f].items():
                evidence=z["adjudication"][f].get(k)
                if v is not None and (not evidence or evidence[label]!=v or not evidence["rationale"] or not evidence["questions"] or set(evidence["questions"])-set(turns)):raise ValueError("Missing evidence anchor")
                if evidence and evidence[label]!=v:raise ValueError("Evidence adjudication drift")
    return z["profiles"]

def run(a):
    files=[getattr(a,k) for k in ("west","angles","hd_cache","join","ephemeris","inventory","mapping_library","selection","transfer_evidence","birth_inputs","context_adjudication","specific_evidence","owner_hd","owner_shared","output")]
    if any(p.resolve().is_relative_to(b.ROOT) for p in files) or a.output.exists():raise ValueError("Private immutable paths required")
    freeze=json.loads(a.selection.read_text())
    if freeze["selector_sha256"]!=b.digest(sel.__file__) or freeze["status"]!="FROZEN_DEVELOPMENT_SELECTION_NOT_VALIDATION":raise ValueError("Development selection drift")
    hs=freeze["HD"]["primary"];ws=freeze["Western"]["primary"]
    if hs["family"]!="hd_specific" or ws["family"]!="western_conditioned":raise ValueError("Selected family requires a different execution adapter")
    W,WM,A,AM,H,proof=g.verify_inputs(a)
    _,groups,shared=h.load_map();_,sg,keys,domains=q.load_map(groups);rows=b.load_mapping(a.mapping_library)
    trans=verify_transfer_evidence(a,freeze,rows,shared,keys)
    oldhd=json.loads(a.owner_hd.read_text());oldshared=json.loads(a.owner_shared.read_text())
    if oldshared["hd_evidence_sha256"]!=b.digest(a.owner_hd) or oldshared["map_sha256"]!=pc.MAP_SHA:raise ValueError("Owner observation binding drift")
    adj=json.loads(a.context_adjudication.read_text())
    extra={k:v["observation"] for k,v in h.ctx.s.coder.code(rows,adj["admission_policy"]["new_contextual_tokens"]).items() if v["observation"] is not None}
    if set(extra)&{k for k,v in oldhd["hd"].items() if v is not None}:raise ValueError("Owner baseline overwrite")
    owner={"hd":{**oldhd["hd"],**extra},"western":oldhd["western"],"shared":oldshared["observations"],"specific":q.load_evidence(a.specific_evidence,keys)[0]}
    profiles=[owner,*trans]
    for n,sha in W["ephe_sha256"].items():
        if b.digest(a.ephemeris/n)!=sha:raise ValueError("Ephemeris drift")
    if swe.version!=W["swisseph_version"]:raise ValueError("Swiss version changed")
    swe.set_ephe_path(str(a.ephemeris))
    inv=json.loads(a.inventory.read_text());ref=next(u["chart_midpoint"] for u in inv["comparison_units"] if u["private_id"]=="REFERENCE")
    owner_at=g.timestamp(ref["utc"]);owner_site=(float(A["longitude"]),float(A["latitude"]),float(A.get("elevation_m",0.)))
    geo,base,ri,_=h.load_states(a.hd_cache,rows,[p["hd"] for p in profiles],ref["HD"],owner_at)
    inputs=json.loads(a.birth_inputs.read_text())
    if inputs["selection_sha256"]!=b.digest(a.selection) or inputs["evidence_sha256"]!=b.digest(a.transfer_evidence):raise ValueError("Birth input freeze binding")
    provider=SwissEphemerisProvider(tuple(sorted(a.ephemeris.glob("*.se1"))))
    site=tuple(inputs["site_lon_lat_elev"])
    cases=[("development",0,owner_at,owner_site,ri,None)]
    exacts={}
    for r in inputs["records"]:
        at=datetime.fromisoformat(r["local"]).replace(tzinfo=ZoneInfo(r["timezone"])).astimezone(timezone.utc)
        if at.isoformat()!=r["utc"]:raise ValueError("Historical timezone drift")
        f=exact_hd(at,provider);exacts[r["label"]]=(at,f)
    # Find cached state for each exact birth, verifying exact recomputation.
    indices={};pos=0
    mf=json.loads((a.hd_cache/"manifest.json").read_text())
    for shard in mf["shards"]:
        for line in gzip.decompress((a.hd_cache/shard["filename"]).read_bytes()).splitlines():
            x=json.loads(line);a0,z=map(g.timestamp,(x["start_utc"],x["end_utc"]))
            for label,(at,f) in exacts.items():
                if a0<=at<z:
                    if label in indices or h.geometry(f)!=tuple(map(int,geo[pos])):raise ValueError("Transfer exact geometry vs cache drift")
                    fc=g.source_hd_chart(f);sc=g.source_hd_chart(x["chart_features"])
                    if any(b.hd_active(fc,r["chart_feature_predicate"])!=b.hd_active(sc,r["chart_feature_predicate"]) for r in rows):raise ValueError("Transfer exact generic predicates vs cache drift")
                    indices[label]=pos
            pos+=1
    if pos!=g.HD_N or set(indices)!=set(exacts):raise ValueError("Exact transfer state not found")
    for label,(at,f) in exacts.items():
        for i in (1,2):cases.append((label+"_"+profiles[i]["label"],i,at,site,indices[label],f))
    tables=[co.score_table(shared,p["shared"]) for p in profiles]
    hd=[];details=[]
    for i,p in enumerate(profiles):
        z,sh,sp=hd_values(geo,base[:,i],p,hs["tag"],groups,shared,sg,keys,domains)
        hd.append(z);details.append((sh,sp))
    targets={}
    for label,i,at,loc,k,f in cases:
        lon,alt=exact_west(at,loc)
        v,vd,meta=selected_west(lon,alt,ws["tag"],tables[i],profiles[i]["western"])
        sh,sp=details[i]
        targets[label]={"HD":float(hd[i][k]),"Western":float(v[0]),"baseline_HD":float(base[k,i]),"baseline_Western":float(vd[0]),
            "HD_components":{"structural":float(base[k,i]),"shared":float(sh["score"][k]),"specific":float(sp["score"][k]),"shared_mapped":int(sh["known_items"][k]),"specific_mapped":int(sp["known_items"][k])},
            "Western_components":{n:(int(x[0]) if n in ("mercury","moon") else float(x[0])) for n,x in meta.items()}}
    for k,model in (("HD",hs),("Western",ws)):
        if abs(targets["development"][k]-model["reference"])>g.EPS:raise ValueError("Development reference score drift: "+k)
    print("Exact transfer chart inputs and frozen development reference reproduced.",flush=True)
    counts={k:{} for k,*_ in cases};same_day={k:{} for k,*_ in cases}
    processed=0;unknown=0
    start=g.timestamp(W["utc_start_inclusive"]);jd0=jd(start)
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not(wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and ai["count"]==hi["count"]==n):raise ValueError("Grid alignment drift")
        paths=(a.west/"chunks"/wi["file"],a.angles/"shards"/ai["file"],a.join/"shards"/hi["file"])
        for p,m,size in zip(paths,(wi,ai,hi),(64,136,4),strict=True):
            if p.stat().st_size!=n*size or b.digest(p)!=m["sha256"]:raise ValueError("Grid shard drift")
        lon=np.asarray(np.memmap(paths[0],dtype="<f8",mode="r",shape=(n,8))[:,:7])
        old_alt=np.asarray(np.memmap(paths[1],dtype="<f8",mode="r",shape=(n,17))[:,4])
        ids=np.memmap(paths[2],dtype="<i4",mode="r",shape=(n,))
        if np.any(ids<-1) or np.any(ids>=g.HD_N):raise ValueError("HD index drift")
        known=ids>=0;unknown+=int((~known).sum());idx=np.maximum(ids,0)
        # Same true solar-altitude convention as original location cache,
        # no approximate sect conversion or reuse of development horizon.
        transfer_alt=np.empty(n)
        for j in range(n):
            d=jd0+(processed+j)/96.
            sun=planet(d,swe.SUN)
            if abs((sun[0]-lon[j,0]+180)%360-180)>1e-8:raise ValueError("Solar longitude source mismatch")
            transfer_alt[j]=altitude(d,site,sun)
        west=[selected_west(lon,old_alt if i==0 else transfer_alt,ws["tag"],tables[i],pr["western"])[:2] for i,pr in enumerate(profiles)]
        for label,i,at,loc,k,f in cases:
            t=targets[label];v,vd=west[i];hh=hd[i][idx];hb=base[idx,i]
            p=pair_counts(hh,v,t["HD"],t["Western"],known);p["baseline"]=pair_counts(hb,vd,t["baseline_HD"],t["baseline_Western"],known)
            add(counts[label],p)
            tz=timezone.utc if label=="development" else ZoneInfo(inputs["records"][0]["timezone"])
            date=at.astimezone(tz).date();lo=datetime.combine(date,datetime.min.time(),tzinfo=tz).astimezone(timezone.utc);hi0=datetime.combine(date+timedelta(days=1),datetime.min.time(),tzinfo=tz).astimezone(timezone.utc)
            l=(lo-start).total_seconds()/900.;r=(hi0-start).total_seconds()/900.
            indexes=processed+np.arange(n);ok=known&(indexes>=l)&(indexes<r)
            add(same_day[label],pair_counts(hh,v,t["HD"],t["Western"],ok))
        processed+=n
        if processed%500000==0 or processed==g.N:print("Frozen-pair transfer grid",processed,"/",g.N,flush=True)
    if processed!=g.N or unknown!=125:raise ValueError("Grid coverage drift")
    if counts["development"]["HD"]!=hs["rank_counts"] or counts["development"]["Western"]!=ws["rank_counts"]:raise ValueError("Selected development full-grid ranks did not replay")
    out={"status":"EXECUTED_FIXED_MODEL_SEPARATE_PERSON_TRANSFER_NOT_INDEPENDENT_VALIDATION","grid_rows":processed,"ranked_rows":processed-unknown,"selection_sha256":b.digest(a.selection),"transfer_evidence_sha256":b.digest(a.transfer_evidence),"birth_inputs_sha256":b.digest(a.birth_inputs),"runner_sha256":b.digest(__file__),"targets":targets,"counts":counts,"same_day_utc_or_local":same_day,
         "selection_scope":"Same preselected HD and Western point-score models, no retuning; alternative reported birth inputs retained separately. Raw score levels not directly comparable across subjects with different observed-item denominators."}
    os.umask(0o077)
    with a.output.open("x") as f:json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("Frozen pair transfer complete; exact development ranks reproduced.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","ephemeris","inventory","mapping-library","selection","transfer-evidence","birth-inputs","context-adjudication","specific-evidence","owner-hd","owner-shared","output"):
        p.add_argument("--"+k,type=Path,required=True)
    run(p.parse_args())
if __name__=="__main__":main()
