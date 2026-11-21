#!/usr/bin/env python3
"""Generate a sealed, contrastive question queue for two chart signatures.

For the participant: questions are neutral, behavior-first, without chart
directions or candidate rankings. Researcher-only file preserves the opposing
V3.8 symbolic testimony, model hashes, candidate provenance and item order.

This is an exploratory DEVELOPMENT interview. Neither output asserts that
any symbolic mapping is a validated psychological prediction.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

ALLOWED={"SUPPORT_ONLY","QUALIFIER_ONLY","MIXED","ABSTAIN"}
SOURCE_BANK_SHA="a464a09604451275850efd009cbd399f8c1b688a511499bfb1c316f55deb2527"


def sha_file(path:Path)->str:return sha256(path.read_bytes()).hexdigest()


def make_queue(reference:dict,candidate:dict,bank:dict):
    r=reference["survey_statuses"];c=candidate["survey_statuses"]
    known={q["id"] for q in bank["questions"]}
    if set(r)!=set(c) or not set(r).issubset(known):
        raise ValueError("Incompatible signature schema")
    for qid in r:
        if r[qid] not in ALLOWED or c[qid] not in ALLOWED:
            raise ValueError("Unknown signature status")
    order={"symbolic":0,"exploratory_bridge":1,"weak_bridge":2,"abstain":3}
    selected=[]
    for q in bank["questions"]:
        qid=q["id"]
        if qid not in r or r[qid]==c[qid]:continue
        if q["evidence_tier"]=="abstain":continue
        if r[qid]=="ABSTAIN" and c[qid]=="ABSTAIN":continue
        delta=(
            3 if {r[qid],c[qid]}=={"SUPPORT_ONLY","QUALIFIER_ONLY"}
            else 2 if (r[qid]=="SUPPORT_ONLY")^(c[qid]=="SUPPORT_ONLY")
            else 1
        )
        selected.append((order.get(q["evidence_tier"],9),-delta,qid,q))
    selected.sort(key=lambda x:(x[0],x[1],x[2]))
    participant=[];sealed=[]
    for k,(_,neg_delta,qid,q) in enumerate(selected,1):
        participant.append({
          "item_id":qid,"order":k,"text":q["prompt"],
          "answer_options":[
            {"code":"1","label":"Strongly untrue for me"},
            {"code":"2","label":"Usually untrue"},
            {"code":"3","label":"Depends on situation or life period"},
            {"code":"4","label":"Usually true"},
            {"code":"5","label":"Strongly true"},
            {"code":"U","label":"Uncertain / not enough examples"}],
          "followup":"Give one specific recent example and one counterexample if available. When did the pattern begin? What circumstances change it?",
          "no_chart_labels_visible":True
        })
        sealed.append({
          "item_id":qid,
          "reference_status":r[qid],
          "alternative_status":c[qid],
          "priority":-neg_delta,
          "evidence_tier":q["evidence_tier"],
          "source_ids":q.get("source_ids",[]),
          "warning":"These are symbolic hypotheses, not known character facts."
        })
    public={"purpose":"exploratory contrastive behavioral interview",
       "version":"chart-signature-diff-v1",
       "not_anastrological_accuracy_measure":True,
       "response_coding":"one answer code per item; do not force certainty",
       "items":participant}
    private={"purpose":"sealed post-exposure chart-signature comparison",
       "version":"chart-signature-diff-v1",
       "reference_signature_status":"developer_visible",
       "candidate_signature_status":"developer_visible",
       "comparisons":sealed}
    return public,private


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--bank",required=True,type=Path)
    ap.add_argument("--comparison-report",required=True,type=Path)
    ap.add_argument("--all-samples-jsonl",required=True,type=Path)
    ap.add_argument("--alternative-utc",required=True)
    ap.add_argument("--output-dir",required=True,type=Path)
    a=ap.parse_args()
    if a.output_dir.exists():raise FileExistsError("Never overwrite frozen interview queue")
    if sha_file(a.bank)!=SOURCE_BANK_SHA:raise ValueError("Questionnaire source hash changed")
    bank=json.loads(a.bank.read_bytes())
    report=json.loads(a.comparison_report.read_bytes())
    if report.get("status")!="POSTHOC_DEVELOPMENT_NOT_VALIDATED":
        raise ValueError("Unexpected comparison report")
    candidate=None
    for line in a.all_samples_jsonl.open():
        row=json.loads(line)
        if row["utc"]==a.alternative_utc:
            candidate=row
            break
    if candidate is None:raise ValueError("Alternative time not present in archived chart samples")
    public,private=make_queue(report["reference"],candidate,bank)
    private.update({
        "question_bank_sha256":sha_file(a.bank),
        "reference_chart_signature_from":"comparison_report.json",
        "candidate_utc":a.alternative_utc,
        "input_report_sha256":sha_file(a.comparison_report),
        "input_chart_samples_sha256":sha_file(a.all_samples_jsonl),
        "no_predictive_claim":True,
    })
    a.output_dir.mkdir(parents=True)
    def content(obj):return (json.dumps(obj,indent=2,sort_keys=True)+"\n").encode()
    b=content(public);c=content(private)
    (a.output_dir/"participant_questions.json").write_bytes(b)
    (a.output_dir/"sealed_researcher_key.json").write_bytes(c)
    print("INTERVIEW_QUEUE_FROZEN",json.dumps({
        "questions":len(public["items"]),
        "participant_sha256":sha256(b).hexdigest(),
        "private_sealed_sha256":sha256(c).hexdigest(),
        "uncalibrated_development":True},sort_keys=True))


if __name__=="__main__":main()
