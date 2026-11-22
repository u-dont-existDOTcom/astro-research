# AstroHD public source and methods package

This is the recovered **public-safe subset** of later HD + Western comparative research previously developed outside the active public repository. `astro-research` is the only destination for new public work. The existing integrated cross-tradition calculator stays in [`engine/astro_engine.py`](../../engine/astro_engine.py) and `engine/hdmatch`; do not replace it with an older branch.

**Latest executable additions:** `scripts/lilly_cvii_initial_geom_grid_census_v01.py` counts only the ASC-sign-presence branch of Lilly CVII; `scripts/audit_hd_western_rising_sign_overlap_v01.py` counts distinct sampled rising signs per HD stable interval; `scripts/audit_disputed_predictor_forum_wave4_v01.py` validates the newly authorized community source pass. All require the correct external source manifests/caches to reproduce numerical findings; supplied aggregate results are `reference/research/century_mechanical_lilly_hd_asc_aggregate_v01.json`. None scores human personalities.

**Ptolemaic astronomical continuation (22 November):** `scripts/ptolemy_mercury_moon_two_dignity_modes_century_v01.py` and `scripts/ptolemy_three_modes_triplicity_sect_century_v01.py` reproduce two- and three-mode source-only ruler-candidate frequencies over the full source-neutral UTC planet grid and one fixed-location solar-altitude grid, with original binary SHA256 checks. Sources `reference/research/ptolemy_iii13_five_domination_mode_source_adjudication_v01.json` and public aggregate `reference/research/ptolemy_iii13_three_modes_century_aggregate_v01.json`. **UNFINISHED:** original terms, Moon applying/separating phase/aspect, governor reconciliation, planetary testimony and any human personality scoring. See `../../docs/astrohd/ptolemy_iii13_three_mode_century_source_audit_20261122.md`.

## Contents and guarantee levels

- `reference/research/`: source-qualification contracts, behavioural observation methods, triage policy, Western source registers, completion roadmap and dated forum search source observations. None claims empirical chart-to-person accuracy.
- `scripts/`: public methods; simple bounded audits are runnable with JSON inputs. More elaborate hundred-year grid and structural HD scripts are **source-only historical modules pending explicit dependency reconciliation**.
- `tests/unit/`: self-contained public tests using synthetic inputs. The tests validate data contracts and failure modes, not astrological claims about humans.
- `tests/`: two extra source-neutral grid tests; ephemeris-backed branches skip when the external test assets are unavailable.
- `legacy_tests/`: recovered source-only historical test cases that depend on original private mapping libraries, chart-provenance files, optional packages or older HD runtime symbols. **Not part of validated public CI**.

Run the active portable tests:

```bash
python3 -m unittest discover -s tools/astrohd/tests/unit -p 'test_*.py' -q
python3 tools/astrohd/tests/test_century_grid_query_and_interview.py -q
python3 tools/astrohd/tests/test_western_utc_grid_cache_pilot.py -q
```

Optional numerical tests in `legacy_tests/` may require `numpy`, `pyswisseph`, verified `ASTRO_EPHE` Swiss files, external source grids and the preserved private source mapping libraries. They are not guaranteed executable by simply cloning this public repository. Do not use a missing private input as an observed negative chart feature.

The migrated artifact origins, byte hashes, public/private status and disabled-until-source requirements are documented in [the migration ledger](../../docs/astrohd/MIGRATION_INVENTORY_20261121.json).

The forum evidence is **source discovery**, not a cohort or failure-rate calculation. The original Ptolemy and HD statements are historical doctrines, not independent human validations. The user's original birth details, interview quotations, other people's private information and full case records are not present here.
