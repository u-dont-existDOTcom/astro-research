# Working instructions

Read `README.md`, `docs/INDEX.md` and `state/CURRENT-STATE.md` before work.
For Mastro work, read both documents under `docs/mastro/` before changing
settings, exporting keywords or describing what has been reproduced.

This repository is public. Follow the data rules in the README. Keep source
recordings, databases, correspondence, birth records, interview responses,
readings and proprietary keyword corpora in their authorized private stores.
Public method notes must be newly written explanations, not copied transcripts.

For substantive changes, use a task branch and pull request. Preserve unrelated
work. Update the index and current state when the workflow or evidence changes.

Research tools are under `tools/mastro/`; self-contained invented-data tests are
under `tests/`. Bootstrap with Python 3.12 using
`python3 scripts/bootstrap_mastro.py`, then activate `.venv`. Run both gates:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_codex_github.py --root . --fail-on error
```

Also run `git diff --check`, verify relative links, review the complete diff
against the source evidence, and check the exact publication payload for birth
data, correspondence, secrets and copied source text. Record what was checked.
Do not upload private analysis outputs or Mastro captures to hosted CI.

Preserve literal matching, duplicate BIO occurrences, first ASTRO matches and
all returned ASTRO rows, including displayed zeros, in the baseline denominator.
Keep source-BIO, source-quality and clock-convention sensitivities separate.
The analysis tools refuse cohort inference until all 141 expected pairs pass
their source/build/policy, hash, capture and rotation checks. A current-source
reconstruction never silently becomes a verified historical input.

Review correctness, evidence integrity, regressions and test adequacy before
style. The repository profile distinguishes hosted controls from local checks.
Retain unresolved warnings and lesson limits in the current-state checkpoint.
Do not claim that chart generation, automation or statistical re-analysis has
run when only documentation or a plan has been prepared.
