#!/usr/bin/env python3
"""Audit post-exposure contrastive answers before changing a natal-model score.

The interviewer's source citations are exact substrings of the raw response,
not unreviewed paraphrases. Multi-mechanism answers retain coexisting or
conditional evidence. A scorer cannot claim a score delta without a NEW,
explicitly reviewed chart-to-observable rule-model version.

User responses and source adjudications are supplied via PRIVATE files, never
hardcoded or committed. The previous HD interval-ranking receipt and all
frozen historical mappings remain byte-for-byte unchanged.

This tool compiles a *semantic evidence reconciliation*, NOT an astrology
personality prediction. The output contains only count/source IDs/hashes and
cannot itself change old scores.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path

RAW_SCHEMA="astrohd_contrastive_user_raw_answers_v1"
ADJ_SCHEMA="astrohd_interview_source_triage_v1"
QUESTION_SCHEMA="astrohd_two_system_contrast_question_bank_v0.2"
ALLOWED_STATUS={
    "both_mechanisms_contextual",
    "nonexclusive_context_dependent",
    "specific_behavior_reported_without_opposite",
    "direct_single_mechanism",
    "unknown_or_unanswered",
}
NO_SCORE="NO_AUTOMATIC_SCORE_CHANGE"
NO_NEW_MODEL="NOT_FROZEN"
SOURCE_MODEL_SHA="f16565094a1a8eede720dd369dfdd4c0d4700a213520b535de28f8f88dd40afd"
OVERLAY_SHA="03d25392f9639fb985f806d4814743bbb1cf466bc803c42b6bf6ca8588337735"
PREVIOUS_RANK_SHA="b930e87a366a7d06d0efe40c9ec83044be62116935ec1a986b06c3868fcf9bce"
PROFILE_V37_SHA="6f3f64143f83757636c34b7265d3980b85bb8643cc2ce975de26636431281295"

def sha_file(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def triage(raw:dict,annotation:dict,question_bank:dict)->dict:
    if raw.get("schema")!=RAW_SCHEMA:
        raise ValueError("Incorrect raw interview source schema")
    if annotation.get("schema")!=ADJ_SCHEMA:
        raise ValueError("Unknown semantic reannotation schema")
    if question_bank.get("schema")!=QUESTION_SCHEMA:
        raise ValueError("Unexpected frozen questionnaire")
    if annotation.get("previous_frozen_rank_sha256")!=PREVIOUS_RANK_SHA:
        raise RuntimeError("Frozen HD ranking reference changed")
    if annotation.get("target_profile_version")!="V3.7+interview-dev-20261120-001":
        raise RuntimeError("New interview must have separate development version")
    if annotation.get("prior_target_profile_sha256")!=PROFILE_V37_SHA:
        raise RuntimeError("Incorrect prior V3.7 source")
    if annotation.get("new_scoring_mapping_status")!=NO_NEW_MODEL:
        raise RuntimeError("New chart-to-behavior mapping cannot be declared frozen implicitly")
    question_ids={q["id"] for q in question_bank["questions"]}
    qmap={q["id"]:q for q in question_bank["questions"]}
    raw_ids=set(raw.get("responses",{}))
    coded_ids=set(annotation.get("decisions",{}))
    if not raw_ids or raw_ids!=coded_ids:
        raise ValueError("Every answered question must have exactly one adjudication")
    if not raw_ids.issubset(question_ids):
        raise ValueError("Unknown questionnaire answer")
    observed=[]
    counts={}
    for qid in sorted(raw_ids):
        text=raw["responses"][qid]
        if not isinstance(text,str) or not text.strip():
            raise ValueError("Raw answer must be verbatim nonempty text")
        code=annotation["decisions"][qid]
        if code.get("evidence_status") not in ALLOWED_STATUS:
            raise ValueError("Unsupported evidence status for "+qid)
        if code.get("score_delta_policy")!=NO_SCORE:
            raise RuntimeError("Observed response has an unauthorized automatic scoring delta")
        if code.get("numerical_score_delta") not in (None,0,0.0):
            raise RuntimeError("Implicit positive or negative points forbidden")
        anchors=code.get("exact_user_excerpt_anchors")
        if not isinstance(anchors,list) or not anchors:
            raise ValueError("Each answer requires source-excerpt anchors")
        if any(not isinstance(a,str) or len(a)<9 or a not in text for a in anchors):
            raise ValueError("Unverified quotation or paraphrase presented as exact answer")
        source_ids=set(qmap[qid]["source_ids"])
        affected=code.get("scoring_mapping_ids")
        if not isinstance(affected,list) or not set(affected).issubset(source_ids):
            raise ValueError("Unapproved mapping outside question's frozen source predicates")
        if not isinstance(code.get("observed_propositions"),list) or not code["observed_propositions"]:
            raise ValueError("No encoded behavioral proposition")
        if not isinstance(code.get("not_established"),list) or not code["not_established"]:
            raise ValueError("Missing limitations on inference")
        observed.append({"question_id":qid,"evidence_status":code["evidence_status"],
                         "mapping_ids_examined":affected,
                         "exact_anchors_verified":len(anchors),
                         "new_behavioral_claims":len(code["observed_propositions"]),
                         "unsupported_inferences_rejected":len(code["not_established"]),
                         "score_delta":0})
        status=code["evidence_status"]
        counts[status]=counts.get(status,0)+1
    return {
       "schema":"astrohd_interview_source_triage_compiled_v1",
       "status":"PASS_SOURCE_ANCHORED_INTERVIEW_RECONCILIATION_NO_SCORE_CHANGE",
       "prior_profile_V37_sha256":PROFILE_V37_SHA,
       "profile_version":annotation["target_profile_version"],
       "previous_HD_rank_sha256":PREVIOUS_RANK_SHA,
       "all_old_HD_rankings_and_maps_unchanged":True,
       "responses_reviewed":len(raw_ids),
       "categorical_observation_counts":counts,
       "items":observed,
       "score_change_authorized":False,
       "new_chart_to_personality_model_frozen":False,
       "current_full_century_provisional_HD_rank_remains_source_version_specific":True,
       "rules":"Unknown, mixed and current-time preference cannot be rewritten into exclusive cause, inborn capacity, absence of rival competence or scored contradiction.",
       "extra_systems":"still deferred until Western+HD comparison completes",
    }

def run(args):
    if args.output.exists():
        raise FileExistsError("Never overwrite raw-response adjudication")
    if sha_file(args.question_bank)!=args.question_sha256:
        raise RuntimeError("Frozen source question bank digest changed")
    if sha_file(args.raw)!=args.raw_sha256:
        raise RuntimeError("Verbatim response record digest changed")
    if sha_file(args.previous_ranking)!=PREVIOUS_RANK_SHA:
        raise RuntimeError("Frozen century provisional rank has been overwritten")
    root=args.repo_root
    if sha_file(root/"reference/core/profile_v3_6_v43_mapping_frozen_2026_08_22.json")!=SOURCE_MODEL_SHA:
        raise RuntimeError("Original historic score mapping mutated")
    if sha_file(root/"reference/core/profile_v3_6_v43_mapping_overlay_v2_2026_08_22.json")!=OVERLAY_SHA:
        raise RuntimeError("Original overlay source mutated")
    raw=json.loads(args.raw.read_bytes())
    codings=json.loads(args.annotation.read_bytes())
    if codings.get("raw_answers_sha256")!=args.raw_sha256:
        raise RuntimeError("Adjudication is for a different verbatim respondent answer")
    if codings.get("question_bank_sha256")!=args.question_sha256:
        raise RuntimeError("Question source version and answering source version differ")
    bank=json.loads(args.question_bank.read_bytes())
    compiled=triage(raw,codings,bank)
    compiled["raw_answers_sha256"]=args.raw_sha256
    compiled["annotation_sha256"]=sha_file(args.annotation)
    compiled["question_bank_sha256"]=args.question_sha256
    data=(json.dumps(compiled,indent=2,sort_keys=True)+"\n").encode()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("xb") as out:
        out.write(data)
    print(json.dumps({"status":compiled["status"],"n":compiled["responses_reviewed"],
       "score_change_authorized":False,"output_sha256":sha256(data).hexdigest()},sort_keys=True))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--question-bank",type=Path,required=True)
    p.add_argument("--question-sha256",required=True)
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--raw-sha256",required=True)
    p.add_argument("--annotation",type=Path,required=True)
    p.add_argument("--previous-ranking",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    run(p.parse_args())

if __name__=="__main__":
    main()
