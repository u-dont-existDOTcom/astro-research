# Mastro research tools

These tools audit retained workbooks and analyze complete current-engine
outputs. They do not generate charts or include the licensed Mastro program,
database contents, keyword corpora or personal input records.

Use Python 3.12 and the pinned environment:

```bash
python3 scripts/bootstrap_mastro.py
source .venv/bin/activate
python3 -m unittest discover -s tests -v
python3 scripts/audit_codex_github.py --root . --fail-on error
```

Keep private inputs and outputs outside tracked paths. The examples use ignored
`private/` and `local-results/` directories. Original filenames and formatting
must be preserved. The workbook audit is specific to the retained study's
73 North / 68 South structure and original comparison rules.

```bash
python3 tools/mastro/audit_references.py --sources private/sources --output private/reference-audit
python3 tools/mastro/cohort_analysis.py --manifest private/reference-audit/person_manifest.json --results private/cohort-results --out-prefix local-results/current-cohort
python3 tools/mastro/audit_latitude.py --workbook private/sources/Latitude_Correlation.xlsx --manifest private/reference-audit/person_manifest.json --output private/latitude-audit
python3 tools/mastro/current_latitude_cli.py --manifest private/reference-audit/person_manifest.json --results-dir private/cohort-results --historical-audit private/latitude-audit/audit-private.json --historical-workbook private/sources/Latitude_Correlation.xlsx --out-prefix local-results/current-latitude
python3 tools/mastro/reassignment_null.py --help
```

The reference audit emits a private manifest containing the historical vectors
and the two BIO variants. Treat that manifest and person-level result files as
private inputs. Partial current runs produce descriptive checks only. Full
inference requires all expected pairs to pass identity, build/policy, hash,
capture and rotation checks.

Each current person folder contains `input.json`, the raw standard/inverted
one-level trees and planetary positions, visible birth-field evidence,
inversion settings, a passing `capture-validation.json` and a hash-bound
`complete.json`. The source-clock CLI accepts explicit local-versus-UTC
interpretations and a tightly bound, supplied-record-only observed-app-UTC
exception. It never searches times to improve scores.

Preserve displayed zero rows, duplicates, whitespace and first-match behavior.
The optional reassignment diagnostic uses a separately fixed protocol and must
not be substituted for the primary hemisphere contrast. Test fixtures are
invented; successful unit tests do not certify an actual chart run or human
predictive accuracy.
