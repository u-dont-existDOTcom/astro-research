# Working instructions


## Canonical astrology repository routing — mandatory preflight

`ASTRO_RESEARCH_CANONICAL=u-dont-existDOTcom/astro-research`

**Do not use the older private `humandesign` repository for new public research,
code, issues, PRs, handoffs or source-of-truth updates.** That repository was
superseded; older chats, assistant/project instructions and historical handoffs
can be stale. All new public work belongs to this `astro-research` repository,
including Human Design, Western, Hellenistic, Vedic, Chinese and Gene Keys
research methods. Private natal inputs and interview responses belong only in
the existing authorized private evidence store, never here.

Before writing, run `python3 scripts/verify_active_astrology_repository.py --root .`;
it must refuse a checkout whose GitHub origin is not `astro-research`.
Read `docs/astrohd/README.md`, the privacy/portability manifest and the latest
`state/CURRENT-STATE.md` before resuming AstroHD work. Treat references to old
HD research branches as **archival evidence**, not current writing destinations.
If instructions conflict, verify the current owner routing and canonical
GitHub repository metadata rather than continuing a superseded prompt.

The 21 November 2026 recovery ledger inventories 123 changed historical
branch files: 86 publicly ported and 37 exact private-recovery-only. No public
file may disclose private chart records, user/third-party biographical reports,
correspondence or exact birth data. The original private source remains
available only through separately authorized private access.


Read `README.md`, `docs/INDEX.md` and `state/CURRENT-STATE.md` before work.
For Mastro work, read the operating guide, research assessment and completed
reanalysis under `docs/mastro/` before changing
settings, exporting keywords or describing what has been reproduced. For
method selection or combining systems, also read
`docs/mastro/inversion-use-policy.md`; keep its evidence scope and conditional
adoption rule attached to reuse. Read `docs/mastro/source-corrections.md` before
using the first-run counts or describing source verification. Application
positions matching its displayed UTC establish calculation consistency; verify
the birth-source UTC/date/location separately before calling inputs source-verified.
Distinguish reused outputs, new generation and evidence rebinding explicitly.

When authoring any reader-facing astrology, meditation, journaling or therapeutic-style guidance, read `docs/astrohd/reflective-practice/USING_ASTROLOGY_WISELY.md` first. A chart interpretation is an optional question, never a life decision directive, diagnosis or verified personality fact. Keep the private live-page sources in their authorized separate private repository, and do not transfer personal case evidence here.

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
their recorded-input/build/policy, hash, capture and rotation checks. These
gates alone do not certify every supplied birth source. A current-source
reconstruction never silently becomes a verified historical input.

Review correctness, evidence integrity, regressions and test adequacy before
style. The repository profile distinguishes hosted controls from local checks.
Retain unresolved warnings and lesson limits in the current-state checkpoint.
Do not claim that chart generation, automation or statistical re-analysis has
run when only documentation or a plan has been prepared.
