#!/usr/bin/env python3
"""Complete-catalogue HD archetype experiment over the original finite grid.

Generic signed shared-item hypotheses, not doctrine certification or human
validation. Original HD observations/authority exclusion remain unchanged.
"""
from __future__ import annotations
import argparse,gzip,json,os
from collections import Counter
from hashlib import sha256
from pathlib import Path
import numpy as np
import compare_bounded_behavior_v01 as b
import compare_full_grid_behavior_v01 as g
import compare_planet_character_century_v01 as pc
import compare_saravali_lunar_solar_century_v01 as s
import compare_contextual_hd_evidence_v01 as ctx

MAP=pc.MAP.parent/"hd_complete_archetype_observable_v01.json"
MAP_SHA="1013b185276cd5a3f2c0235cf5726f5a3dd41011cae2eeaad989590450216ac0"
CENTERS={"head":(64,61,63),"ajna":(47,24,4,17,43,11),"throat":(62,23,56,16,20,31,8,33,35,12,45),
 "g":(1,2,7,10,13,15,25,46),"heart_ego":(21,26,40,51),"sacral":(5,14,29,34,42,3,9,27,59),
 "solar_plexus":(6,37,22,36,30,55,49),"spleen":(48,57,44,50,32,28,18),"root":(58,38,54,53,60,52,19,39,41)}
GATE_CENTER={g:c for c,gs in CENTERS.items() for g in gs}
CHANNELS=("1-8","2-14","3-60","4-63","5-15","6-59","7-31","9-52","10-20","10-34","10-57","11-56","12-22","13-33","16-48","17-62","18-58","19-49","20-34","20-57","21-45","23-43","24-61","25-51","26-44","27-50","28-38","29-46","30-41","32-54","34-57","35-36","37-40","39-55","42-53","47-64")
PROFILES=("1/3","1/4","2/4","2/5","3/5","3/6","4/6","4/1","5/1","5/2","6/2","6/3")
MAPS=("direct","with_proxies")
GATES=("gate_conscious_defined","gate_defined","gate_any")
FAMILIES=("line_union","ordered_profile","channels",*GATES,"profile_channel_union","union_conscious_defined","union_defined","union_any")
ARMS=tuple(f"{f}|{mode}" for mode in MAPS for f in FAMILIES)
SCORES=tuple(f"{a}|{t}" for a in ARMS for t in ("archetypes","blend"))
EXCLUDED_GATES={2,20,34,57}
EXCLUDED_CHANNELS={"10-57","20-34","20-57","34-57"}
BODY_NAMES=("sun","earth","moon","north_node","south_node","mercury","venus","mars","jupiter","saturn","uranus","neptune","pluto")
ACT_KEYS={f"{side}:{body}" for side in ("personality","design") for body in BODY_NAMES}

def mask(gs):
    return sum(1<<(g-1) for g in set(gs))

def channel_id(x):
    a,c=sorted(map(int,x.split("-")))
    return f"{a}-{c}"

def center_id(x):
    y=b.norm(x)
    aliases={"heart":"heart_ego","heartego":"heart_ego","ego":"heart_ego","will":"heart_ego",
             "solarplexus":"solar_plexus","identity":"g"}
    return aliases.get(y,y)

CENTER_MASKS={c:mask(gs) for c,gs in CENTERS.items()}
CHANNEL_MASKS=tuple(mask(map(int,c.split("-"))) for c in CHANNELS)

def load_map():
    if b.digest(MAP)!=MAP_SHA:raise ValueError("Frozen archetype map SHA drift")
    x=json.loads(MAP.read_text());shared=pc.load_registry()
    if x["schema"]!="hd_complete_archetype_observable_v01" or x["shared_vocabulary_sha256"]!=pc.MAP_SHA:
        raise ValueError("Map registry binding drift")
    keys=set().union(*(set(v) for v in shared["domains"].values()))
    groups={k:[r for r in x["rules"] if r["kind"]==k] for k in ("gate","channel","ordered_profile","line")}
    expected={"gate":tuple(map(str,range(1,65))),"channel":CHANNELS,"ordered_profile":PROFILES,"line":tuple(map(str,range(1,7)))}
    if len(x["rules"])!=118:raise ValueError("Missing source catalogue rows")
    for k,rs in groups.items():
        if tuple(r["id"] for r in rs)!=expected[k]:raise ValueError("Catalogue order/coverage drift")
        for r in rs:
            if not r["basis"] or set(r["direct"])&set(r["proxy"]):raise ValueError("Invalid source rationale")
            for f in MAPS:
                z=r["direct"] if f=="direct" else r["proxy"]
                if set(z)-keys or any(type(v)!=int or v not in (-1,1) for v in z.values()):raise ValueError("Invalid source direction")
            if ((k=="gate" and int(r["id"]) in EXCLUDED_GATES) or (k=="channel" and r["id"] in EXCLUDED_CHANNELS)) and (r["direct"] or r["proxy"]):
                raise ValueError("Authority analogue admitted")
    return x,groups,shared

def geometry(f):
    activ=f["activation_gates"]
    if set(activ)!=ACT_KEYS or any(type(v)!=int or not 1<=v<=64 for v in activ.values()):raise ValueError("Incomplete gate activations")
    allmask=mask(activ.values());person=mask(v for k,v in activ.items() if k.startswith("personality:"))
    reported={channel_id(c) for c in f["channels"]}
    cm=0;centers=set()
    for i,(name,m) in enumerate(zip(CHANNELS,CHANNEL_MASKS,strict=True)):
        present=allmask&m==m
        if present!=(name in reported):raise ValueError("Channel vs activated gate drift")
        if present:
            cm|=1<<i;centers.update(GATE_CENTER[int(g)] for g in name.split("-"))
    if len(reported)!=cm.bit_count() or centers!={center_id(c) for c in f["defined_centers"]}:raise ValueError("Derived center mismatch")
    defined=0
    for c in centers:defined|=CENTER_MASKS[c]
    return (allmask,allmask&defined,person&defined,cm,PROFILES.index(f["profile"]))

def reference_geometry(ref):
    activ={k:v["gate"] for k,v in ref["all_planet_carrier_gate_lines"].items()}
    return geometry({"activation_gates":activ,"channels":ref["complete_channels"],"defined_centers":ref["defined_centers"],"profile":ref["profile"]})

def load_states(root,rows,obs,ref,at):
    mf=root/"manifest.json";m=json.loads(mf.read_text())
    if b.digest(mf)!=g.HD_MANIFEST or m["canonical_rows_sha256"]!=g.HD_ROWS:raise ValueError("Original HD manifest drift")
    rawhash=sha256();geo=[];scores=[];seen={};prev=None;ri=None;hit=0;rg=reference_geometry(ref)
    for shard in m["shards"]:
        raw=(root/shard["filename"]).read_bytes()
        if sha256(raw).hexdigest()!=shard["sha256"]:raise ValueError("HD shard digest drift")
        raw=gzip.decompress(raw)
        if len(raw)!=shard["uncompressed_bytes"]:raise ValueError("HD shard size drift")
        rawhash.update(raw);n=0
        for line in raw.splitlines():
            x=json.loads(line);a,z=map(g.timestamp,(x["start_utc"],x["end_utc"]))
            if (prev is not None and a!=prev) or z<=a:raise ValueError("HD coverage drift")
            prev=z;n+=1
            f=x["chart_features"];gg=geometry(f);ch=g.source_hd_chart(f)
            key=(ch["type"],ch["profile"],tuple(sorted(ch["defined_centers"])))
            if key not in seen:seen[key]=tuple(b.hd_score(ch,rows,o)["score"] for o in obs)
            if a<=at<z:
                ri=len(geo);hit+=1
                if gg!=rg or any(b.hd_active(ch,r["chart_feature_predicate"])!=b.hd_active(ref,r["chart_feature_predicate"]) for r in rows):
                    raise ValueError("Exact reference structural mismatch")
            geo.append(gg);scores.append(seen[key])
        if n!=shard["state_count"]:raise ValueError("HD shard count drift")
    if len(geo)!=g.HD_N or rawhash.hexdigest()!=g.HD_ROWS or hit!=1:raise ValueError("HD logical checksum drift")
    a=np.asarray(geo,dtype=np.uint64);return a,np.asarray(scores,float),ri,len(seen)

def byte_lut(t):
    n=len(t[0]);lut=np.zeros((2,(n+7)//8,256),np.uint64)
    for k in range(lut.shape[1]):
        for j in range(256):
            for bit in range(8):
                i=k*8+bit
                if i<n and j&(1<<bit):
                    lut[:,k,j]|=(t[0][i],t[1][i])
    return lut

def bitlookup(carrier,lut):
    out=np.zeros((2,len(carrier)),np.uint64)
    for k in range(lut.shape[1]):
        ix=((carrier>>np.uint64(k*8))&np.uint64(255)).astype(np.intp)
        out|=lut[:,k,ix]
    return out[0],out[1]

def model_bits(geo,groups,keys,mode):
    gate_lut=byte_lut(s.table(groups["gate"],keys,mode))
    ch_lut=byte_lut(s.table(groups["channel"],keys,mode))
    p=s.table(groups["ordered_profile"],keys,mode)
    l=s.table(groups["line"],keys,mode)
    pn=geo[:,4].astype(np.intp)
    ordered=tuple(a[pn] for a in p)
    pairs=np.asarray([[int(x)-1 for x in q.split("/")] for q in PROFILES])
    lines=tuple((a[pairs[:,0]]|a[pairs[:,1]])[pn] for a in l)
    ch=bitlookup(geo[:,3],ch_lut)
    gc=bitlookup(geo[:,2],gate_lut);gd=bitlookup(geo[:,1],gate_lut);ga=bitlookup(geo[:,0],gate_lut)
    pc0=s.union(ordered,ch)
    return dict(zip(FAMILIES,(lines,ordered,ch,gc,gd,ga,pc0,s.union(pc0,gc),s.union(pc0,gd),s.union(pc0,ga)),strict=True))

def weights(a,WM,AM,H,rivals):
    total=np.zeros(g.HD_N,np.int64);rw=total.copy();processed=0;unknown=0;seen=0
    rr=np.asarray(rivals,np.int64)
    for wi,ai,hi in zip(WM["chunks"],AM["shards"],H["shards"],strict=True):
        n=wi["count"]
        if not(wi["first_index"]==ai["first_index"]==hi["index_first"]==processed and hi["count"]==n):raise ValueError("Grid alignment drift")
        for path,meta,size in zip((a.west/"chunks"/wi["file"],a.angles/"shards"/ai["file"],a.join/"shards"/hi["file"]),(wi,ai,hi),(64,136,4),strict=True):
            if path.stat().st_size!=n*size or b.digest(path)!=meta["sha256"]:raise ValueError("Source shard drift")
        ids=np.memmap(a.join/"shards"/hi["file"],dtype="<i4",mode="r",shape=(n,))
        if np.any(ids<-1) or np.any(ids>=g.HD_N):raise ValueError("HD index drift")
        good=ids>=0;unknown+=int((~good).sum());total+=np.bincount(ids[good],minlength=g.HD_N)
        ix=rr[(rr>=processed)&(rr<processed+n)]-processed
        if np.any(ids[ix]<0):raise ValueError("Old rival boundary unknown")
        rw+=np.bincount(ids[ix],minlength=g.HD_N);seen+=len(ix);processed+=n
    if processed!=g.N or unknown!=125 or total.sum()!=g.N-125 or seen!=len(rr):raise ValueError("Grid weight accounting drift")
    return total,rw

def ranks(score,ref,w,mask=None):
    if mask is None:mask=np.ones(len(w),bool)
    return dict(higher=int(w[mask&(score>ref+g.EPS)].sum()),tied=int(w[mask&(np.abs(score-ref)<=g.EPS)].sum()),lower=int(w[mask&(score<ref-g.EPS)].sum()))

def bound_ranks(lo,hi,tl,th,w):
    return dict(certainly_higher=int(w[lo>th+g.EPS].sum()),could_equal_or_exceed=int(w[hi>=tl-g.EPS].sum()),certainly_lower=int(w[hi<tl-g.EPS].sum()))

def compare(geo,base,ri,groups,shared,observations,w,rw):
    # profile order: broad, narrow, contextual broad; same shared character
    # evidence for broad and contextual broad, only old structural score differs.
    results=[{} for _ in observations];matrix=np.empty((len(observations),len(SCORES),len(geo)),np.float64)
    keys=tuple(k for d in pc.DOMAINS for k in shared["domains"][d])
    for mode in MAPS:
        bits=model_bits(geo,groups,keys,mode)
        for family,bb in bits.items():
            tag=family+"|"+mode
            for i,obs in enumerate(observations):
                _,om=s.obs_masks(shared,obs);z=s.score(bb,om);point=z["score"];h=base[:,i]
                record={"mapped_items":int(z["known_items"][ri]),"conflicting_items":int(z["conflicting_items"][ri]),
                        "mapped_rows":int(w[z["known_items"]>0].sum()),"reference":{},"ranks":{}}
                for kind,sc,lo,hi in (("archetypes",point,z["lo"],z["hi"]),("blend",(h+point)/2,(h+z["lo"])/2,(h+z["hi"])/2)):
                    k=tag+"|"+kind;matrix[i,SCORES.index(k)]=sc-sc[ri]
                    record["reference"][kind]=float(sc[ri])
                    record["ranks"][kind]={"full_grid":ranks(sc,sc[ri],w),
                       "prior_rivals":ranks(sc,sc[ri],rw),
                       "matched_items":ranks(sc,sc[ri],w,z["known_items"]==z["known_items"][ri]),
                       "bounds":bound_ranks(lo,hi,lo[ri],hi[ri],w)}
                results[i][tag]=record
    return results,matrix

def load_inputs(a):
    W,WM,A,AM,H,proof=g.verify_inputs(a);x,groups,shared=load_map()
    prior=json.loads(a.overlap.read_text());cross=json.loads(a.cross_coding.read_text());context=json.loads(a.context.read_text())
    if prior["runner_sha256"]!=b.digest(ctx.cc.m.__file__) or cross["runner_sha256"]!=b.digest(ctx.cc.__file__) or cross["full_overlap_sha256"]!=b.digest(a.overlap):
        raise ValueError("Earlier cross comparison drift")
    if context["runner_sha256"]!=b.digest(ctx.__file__) or context["prior_overlap_sha256"]!=b.digest(a.overlap) or context["prior_cross_coding_sha256"]!=b.digest(a.cross_coding) or context["adjudication_sha256"]!=b.digest(a.adjudication):
        raise ValueError("Contextual receipt drift")
    inv=json.loads(a.inventory.read_text());ref=next(u["chart_midpoint"] for u in inv["comparison_units"] if u["private_id"]=="REFERENCE")
    at=g.timestamp(ref["utc"]);rows=b.load_mapping(a.mapping_library);old=[];observations=[]
    for i,(hp,ep) in enumerate(zip(a.hd_evidence,a.evidence,strict=True)):
        he=json.loads(hp.read_text());e=json.loads(ep.read_text())
        if he["inventory_sha256"]!=b.digest(a.inventory) or e["map_sha256"]!=pc.MAP_SHA or e["hd_evidence_sha256"]!=b.digest(hp) or prior["profiles"][i]["HD_evidence_sha256"]!=b.digest(hp) or prior["profiles"][i]["evidence_sha256"]!=b.digest(ep):raise ValueError("Frozen evidence drift")
        old.append(he["hd"]);observations.append(e["observations"])
    adj=json.loads(a.adjudication.read_text());extra={k:v["observation"] for k,v in ctx.s.coder.code(rows,adj["admission_policy"]["new_contextual_tokens"]).items() if v["observation"] is not None}
    if set(extra)&{k for o in old for k,v in o.items() if v is not None}:raise ValueError("Original observation overwrite")
    obs=[*old,{**old[0],**extra}];observations.append(observations[0])
    return W,WM,A,AM,H,proof,groups,shared,ref,at,rows,obs,observations,prior,cross,context

def run(a):
    paths=[a.west,a.angles,a.hd_cache,a.join,a.mapping_library,a.inventory,a.overlap,a.cross_coding,a.context,a.adjudication,a.output,a.state_output,*a.hd_evidence,*a.evidence]
    if any(p.resolve().is_relative_to(b.ROOT) for p in paths) or a.output.exists() or a.state_output.exists():raise ValueError("External immutable private inputs/outputs required")
    if len(a.hd_evidence)!=2 or len(a.evidence)!=2:raise ValueError("Two frozen evidence versions")
    W,WM,A,AM,H,proof,groups,shared,ref,at,rows,obs,observations,prior,cross,context=load_inputs(a)
    geo,base,ri,nstruct=load_states(a.hd_cache,rows,obs,ref["HD"],at)
    w,rw=weights(a,WM,AM,H,cross["strict_survivor_indices"][ctx.s.CORE])
    for i,k in enumerate(("old_ranks","old_ranks","new_ranks")):
        j=0 if i==2 else i
        if ranks(base[:,i],base[ri,i],w)!=context["profiles"][j][k] or base[ri,i]!=b.hd_score(ref["HD"],rows,obs[i])["score"]:raise ValueError("Prior HD score replay failed")
    print("Complete structural cache and earlier HD ranks verified.",flush=True)
    result,matrix=compare(geo,base,ri,groups,shared,observations,w,rw)
    same={}
    for i,j,label in ((0,1,"original_pair"),(2,1,"context_pair")):
        same[label]={}
        for k,tag in enumerate(SCORES):
            x,y=matrix[i,k],matrix[j,k]
            ge=(x>=-g.EPS)&(y>=-g.EPS);gt=(x>g.EPS)&(y>g.EPS)
            same[label][tag]={"full_grid_ge":int(w[ge].sum()),"full_grid_strict":int(w[gt].sum()),
                              "prior_rivals_ge":int(rw[ge].sum()),"prior_rivals_strict":int(rw[gt].sum())}
    # Score deltas are kept privately for exact same-row cross-family use.
    os.umask(0o077)
    with a.state_output.open("xb") as f:np.savez_compressed(f,delta=matrix,base_delta=(base-base[ri]).T,arms=np.asarray(SCORES),map_sha256=MAP_SHA,runner_sha256=b.digest(__file__))
    out={"status":"EXECUTED_COMPLETE_HD_ARCHETYPE_CATALOGUE_FINITE_GRID_NOT_VALIDATION","grid_rows":g.N,"ranked_rows":int(w.sum()),
         "map_sha256":MAP_SHA,"arms_per_coding":len(ARMS),"point_scores_per_coding":len(SCORES),"prior_structure_keys":nstruct,
         "profiles":result,"same_coding_pair":same,"runner_sha256":b.digest(__file__),"state_output_sha256":b.digest(a.state_output),
         "prior_overlap_sha256":b.digest(a.overlap),"prior_cross_coding_sha256":b.digest(a.cross_coding),"prior_context_sha256":b.digest(a.context),
         "evidence_sha256":[b.digest(p) for p in a.evidence],"HD_evidence_sha256":[b.digest(p) for p in a.hd_evidence],"grid_proof":proof}
    with a.output.open("x") as f:json.dump(out,f,indent=2,sort_keys=True);f.write("\n")
    print("Complete HD catalogue score comparison finished; private score deltas retained.",flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("west","angles","hd-cache","join","mapping-library","inventory","overlap","cross-coding","context","adjudication","output","state-output"):
        p.add_argument("--"+k,type=Path,required=True)
    for k in ("evidence","hd-evidence"):p.add_argument("--"+k,type=Path,action="append",required=True)
    run(p.parse_args())
if __name__=="__main__":main()
