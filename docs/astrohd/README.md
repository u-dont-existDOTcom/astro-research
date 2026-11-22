# AstroHD public research recovery — 21 November 2026

**Canonical active public repository:** `u-dont-existDOTcom/astro-research`.

The prior private Human Design research repository was superseded. This repository now owns **all new public astrology methods, source audits, and independently reproducible tests**, including HD + Western chart-comparison research. Public research must not be redirected into the old repository because an older conversation, handoff, branch, Project label or prompt mentions it.

## What has been recovered

The historical post-migration development branch in the private predecessor contained **123 changed files**. Every file is accounted for in [the public migration inventory](MIGRATION_INVENTORY_20261121.json), with SHA-256 source hash and disposition. An owner-private compressed recovery archive retains every original file, independently read back and SHA-256 verified. **86 public-safe files** were ported (a mixture of executable methods, data/schema registers, tests and source-only legacy methods). **37 original files remain exclusively private**. Their generic scientific methodology and evidence limitations are summarized below; their identifiable interview/chart content was not published.

The public transfer adds under [`tools/astrohd/`](../../tools/astrohd/README.md):

- Versioned public predictor-admission policies, with unvalidated perfect-safety claims excluded from numerical matching. Belief in an intuitive signal remains a distinct subjective, uncalibrated construct.
- Separate traditional Western source-condition registers (including Ptolemy III.13), contextual behavioral observation contracts and a bounded completion-roadmap checker.
- Source-audited forum disagreement screening across HD, Western, Jyotish, BaZi, Gene Keys, Zi Wei and Maya-related material.
- Exact reproducible source-census, Western feature-grid and HD interval methods where inputs are public-safe; several legacy programs still require *external* private manifests or missing original HD modules and are **not certified as working public pipelines**.
- Self-contained, invented-data tests. No public test asserts human natal prediction accuracy.

**22 November follow-up:** [the newly authorized fourth community-source wave plus two real full-century structural calculations](forum_wave4_lilly_and_structural_century_results_20261122.md) has been completed and stored with source-only caveats. See the fourth-wave evidence register and the first-source-rung Lily CVII mechanical census. This extends the original three-wave forum source coverage; it does not change its original closed sample or turn anecdotes into population rates.

## Forum investigation outcome

A bounded three-pass, complaint-enriched source search examined **22 proposed predictor claims** and **59 public-source observation units**, normalized to **49 distinct discussions/pages**. Only eight observation units were based on fully opened pages; others used explicitly labeled search excerpts. None supplies a representative cohort denominator or independently verified prospective birth-chart prediction.

The result is an *investigative source-qualification audit*, not a ranking of which astrology claims are most frequently false. Issues include ambiguous HD Authority signals, opportunity/invitation reframing, unqualified planetary dignity or rising-sign stereotypes, after-the-event chart-convention selection, Vedic marriage/timing reinterpretation, and the difference between contemplative Gene Keys and empirical predictions. Use the machine-readable source registers under `tools/astrohd/reference/research/`. The source code and tests enforce absent denominators and unverified predictions as **unknown, not zeros or hits**.

See [the cross-system comparison peer-review reconciliation](cross_system_peer_review_reconciliation_20261122.md) for source-qualified handling of time resolution, traditional dignity, HD prenatal feature diversity and human predictive-validation limits. This document does not claim the complete new century-wide behavioral scorer has run.

## Separate research tracks and finish lines

The source-level forum audit is **complete with evidence gaps**. A high-level profile-development protocol and the Gemini reasoning comparison have bounded reports. Completing a **full source-qualified Western + HD behavioral predictor and complete candidate search** remains a distinct, unfinished goal. Another optional future study would test actual prediction in blinded human cohorts. Neither synthetic-test success nor attractive symbolic readings demonstrate accuracy in people.

Earlier source-qualified personal-chart matches, dates, original survey answers, natal locations, prior model-specific individual ranks, correspondence, and proprietary material are retained in the owner's private archive and must not enter this public repository or public CI.

## Canonical work admission

Before any consequential AstroHD write or generated report:

1. Read the current `AGENTS.md`, `README.md`, `docs/INDEX.md` and `state/CURRENT-STATE.md` **from this repository**.
2. Run `python3 scripts/verify_active_astrology_repository.py --root .` in the candidate checkout; it refuses the old private repository even when called from a stale handoff.
3. Use a task branch and PR; preserve the active public engine under `engine/` and its existing tests.
4. Privately quarantine source charts/interviews; publish only de-identified public research methods or aggregate results.
5. Run applicable tests and canonical repository audit before merge; verify the new GitHub head and permissions.

Do not resurrect or merge old private working branches into this public repository wholesale: the exact raw archive contains material disallowed by the README privacy contract.

## Public reproducibility

```bash
python3 scripts/verify_active_astrology_repository.py --root .
python3 -m unittest discover -s tools/astrohd/tests/unit -p 'test_*.py' -v
python3 tools/astrohd/tests/test_century_grid_query_and_interview.py -q
python3 tools/astrohd/tests/test_western_utc_grid_cache_pilot.py -q
python3 -m unittest discover -s tests -v
python3 scripts/audit_codex_github.py --root . --fail-on error
```

`ASTRO_EPHE` and `ASTRO_WESTERN_GRID` are optional local external fixture paths for tests that explicitly skip without source assets. Additional source-only tests in `tools/astrohd/legacy_tests/` are not part of the public passing-test claim and may require private mapping libraries, a prior HD runtime or NumPy. See the [tool status](../../tools/astrohd/README.md).

## Change provenance

Full source recovery snapshot hash: `260080ce386b144aaf66c17b7f4cbd7f146f11759d0201cb466cbbc20aa32e22` (owner-private archive). Public original file hashes and port status are in the migration inventory; four test files were adapted to use portable environment paths and their new hashes are recorded separately. No private user biography was included in the publication.
