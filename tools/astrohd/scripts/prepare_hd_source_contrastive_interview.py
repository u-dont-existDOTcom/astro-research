#!/usr/bin/env python3
"""Compile HD chart-predicate differences into a neutral, frozen questionnaire.

REUSE:
 - original V3.6/V4.3 44-pathway mapping and match_predicate compiler,
 - verified production ExactChartAdapter, and
 - existing private source replay for UTC reference/candidate selectors.

This is a *post-exposure development contrast*, not an independently blinded
test, a synthetic human validation or a personality-likelihood ranking.

Only participant questions (no chart/date/HD labels) go in participant.json.
The complete provenance, source-predicate directions and UTC input identity
remain in the PRIVATE researcher key. Never commit either private output.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json,os
from pathlib import Path
import sys

from hdmatch.runtime.chart_adapter import ExactChartAdapter

QUESTION_SCHEMAS={"astrohd_two_system_contrast_question_bank_v0.1","astrohd_two_system_contrast_question_bank_v0.2"}
REPLAY_SHA="24fcf067ace194366426ed26e5c10ac59b0afa1734991e7844efd1bbe69074fc"


def digest(p:Path)->str:
    return sha256(p.read_bytes()).hexdigest()
def canon(data)->bytes:
    return (json.dumps(data,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()
def inspect_source_question_bank(bank:dict,model:dict):
    if bank.get("schema") not in QUESTION_SCHEMAS:
        raise ValueError("Incorrect neutral question bank schema")
    byid={m["id"]:m for m in model["mappings"]}
    qids=set()
    for q in bank["questions"]:
        if not q.get("id") or q["id"] in qids:raise ValueError("Duplicate/missing question ID")
        qids.add(q["id"])
        if not q.get("text"):raise ValueError("Question lacks neutral behavioral wording")
        if not q.get("source_ids"):raise ValueError("Question must have source predicates")
        for mid in q["source_ids"]:
            if mid not in byid:
                raise ValueError("Unknown source mapping "+mid)
            if byid[mid].get("post_selection"):
                raise ValueError("Postselected source cannot be promoted to interview discriminator")
    return byid

def make_queue(bank:dict,model:dict,matcher,reference_state,alternate_state,
               *,question_bank_sha:str,prior_receipt_sha:str):
    byid=inspect_source_question_bank(bank,model)
    participant=[]
    secret=[]
    for question in bank["questions"]:
        differences=[]
        matched={}
        for mid in question["source_ids"]:
            predicate=byid[mid]["predicate"]
            ra=bool(matcher(reference_state,predicate))
            rb=bool(matcher(alternate_state,predicate))
            matched[mid]={"reference_predicate":ra,"alternative_predicate":rb,
                          "source_dependency_cluster":byid[mid]["cluster"]}
            if ra!=rb:differences.append(mid)
        if not differences:
            continue
        participant.append({
            "id":question["id"],
            "text":question["text"],
            "prompt":"Please give a specific example and a counterexample, or say if none comes to mind.",
            "options":"Both, neither, depends on context, and unknown are all valid answers.",
        })
        secret.append({
            "id":question["id"],
            "source_mappings":matched,
            "actually_distinguishing_mappings":differences,
            "source_evidence_status":"historical_doctrinal_development_only",
            "behavioral_outcome_not_yet_observed":True,
        })
    return {
        "schema":"hd-contrastive-participant-questions-v1",
        "purpose":"exploratory questionnaire about differences; no promised predictive accuracy",
        "has_candidate_birth_chart_or_direction":False,
        "questions":participant,
    },{
        "schema":"hd-contrastive-researcher-key-v1",
        "status":"private_post_exposure_frozen_source_difference",
        "question_bank_sha256":question_bank_sha,
        "previous_private_replay_sha256":prior_receipt_sha,
        "reference_chart_source":"private_existing_replay_selection_0",
        "alternative_chart_source":"private_existing_replay_selection_2",
        "question_source_differences":secret,
        "predictive_validity":"NOT_ESTABLISHED",
    }

def run(args):
    if args.output_dir.exists():raise FileExistsError("No overwrite for frozen interview bundle")
    if digest(args.prior_replay)!=REPLAY_SHA:
        raise RuntimeError("Unrecognized or changed private HD replay")
    if digest(args.question_bank)!=args.question_sha256:
        raise RuntimeError("Question source hash changed")
    prior=json.loads(args.prior_replay.read_bytes())
    questions=json.loads(args.question_bank.read_bytes())
    if prior["target_version"]!="V3.6" or prior["mapping_count"]!=44:
        raise RuntimeError("Prior source replay not expected 44-rule model")
    if len(prior["reference_comparisons"])<3:
        raise RuntimeError("Missing prior alternative comparison")
    root=args.repo_root.resolve()
    sys.path.insert(0,str(root/"scripts"))
    import v43_profile_netinfo_rerun as runner
    import replay_historical_v36_hd_on_verified_cache as replay
    model=replay.current_model(root)
    adapter=ExactChartAdapter(args.ephemeris)
    targets=[prior["reference_comparisons"][0]["input_utc"], args.alternative_utc or prior["reference_comparisons"][2]["input_utc"]]
    from replay_v37_development_direct_hd_observables import utc,from_engine
    reference=from_engine(adapter.calculate(utc(targets[0])))
    alternative=from_engine(adapter.calculate(utc(targets[1])))
    shown,key=make_queue(questions,model,runner.match_predicate,
                         reference,alternative,question_bank_sha=digest(args.question_bank),
                         prior_receipt_sha=digest(args.prior_replay))
    key["private_source_UTC"]={"reference":targets[0],"alternative":targets[1]}
    key["source_HD_state"]={
       "reference":{"type":reference["type"],"authority":reference["auth"],
                    "profile":reference["profile"],
                    "channels":sorted("-".join(map(str,p)) for p in reference["channels"])},
       "alternative":{"type":alternative["type"],"authority":alternative["auth"],
                      "profile":alternative["profile"],
                      "channels":sorted("-".join(map(str,p)) for p in alternative["channels"])},
    }
    args.output_dir.mkdir(parents=True)
    public=canon(shown);private=canon(key)
    for name,data in (("participant_questions.json",public),("researcher_sealed_key.json",private)):
        dest=args.output_dir/name
        fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,"wb") as stream:
            stream.write(data);stream.flush();os.fsync(stream.fileno())
    print(json.dumps({"status":"POST_EXPOSURE_DIFF_QUESTIONS_FROZEN",
      "neutral_questions_with_actual_source_differences":len(shown["questions"]),
      "participant_file_sha256":sha256(public).hexdigest(),
      "researcher_file_sha256":sha256(private).hexdigest(),
      "no_human_answers_collected":True},sort_keys=True))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--ephemeris",type=Path,required=True)
    p.add_argument("--prior-replay",type=Path,required=True)
    p.add_argument("--question-bank",type=Path,required=True)
    p.add_argument("--question-sha256",required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--alternative-utc",help="optional development alternative exact UTC instant")
    run(p.parse_args())

if __name__=="__main__":main()
