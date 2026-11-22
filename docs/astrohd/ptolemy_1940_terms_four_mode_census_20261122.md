# Four Ptolemaic rulership modes: verified printed terms and a bounded Moon-aspect pilot

**22 November 2026 • Public source-neutral research report.** Continues the complete-century [three-mode study](ptolemy_iii13_three_mode_century_source_audit_20261122.md). No participant birth data, interviews, natal success or validated personality prediction is published here.

## Finding 1 — the original 1940 printed tables resolve two web transcription failures

The original 490-page scanned *Tetrabiblos* (F. E. Robbins, Loeb Classical Library, 1940) was obtained and its actual pages rendered and examined, **not only HTML/PDF text extraction**.

- **Ptolemaic terms:** printed Greek page 106 and English page 107 both give **Libra's fifth term to Mars for 6°**. The LacusCurtius HTML digitization gives Saturn twice in Libra and is **wrong on that character** relative to the printed edition.
- **Ptolemaic terms:** the same printed tables give **Jupiter 5° for Virgo's third term**. One later reflow PDF has lost that numerical value.
- **Egyptian terms:** printed Greek page 96 and English page 97 are a *different complete scheme*; they must not be conflated with the subsequent Ptolemaic terms. The terms of Libra are not the same in the two systems.
- **Editorial variants remain:** Robbins's Greek footnotes report textual variants in manuscripts and editions (including Vatican gr. 1453, Proclus and Camerarius). Resolving which original ancient manuscript reading would be preferable is **not** the same thing as correctly transcribing the printed 1940 edition. This work freezes the published 1940 edition, **not all historical term systems**.

Source: [original scanned 1940 Loeb volume](https://commons.wikimedia.org/wiki/File:Loeb_435_-_Ptolemy_-_Tetrabiblos_by_Robbins_(1940).pdf), pages 96–97 and 106–107; [HTML transcription and visible discrepancy](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/1B%2A.html), §21. Source-provenance record (including original scanned file's SHA256, page numbers and independent facsimile hash checks): `tools/astrohd/reference/research/ptolemy_1940_printed_terms_dual_table_provenance_v01.json`.

**Source logic:** Terms/bounds are short consecutive zones within each 30° zodiacal sign, each assigned to one of the five nonluminary classical planets. The newly transcribed Ptolemaic and Egyptian tables each contain **12 rows of five distinct planets, with lengths totaling exactly 30°**. The event at the exact upper degree boundary is assigned to the *next* term; zero is included in the first term. These source and boundary checks have automated positive and negative tests.

## Finding 2 — genuine full-century terms-scheme sensitivity, not human personality accuracy

The newly source-frozen four-mode programs add **terms** to previously evaluated domicile, exaltation and day/night triplicity. They check all original SHA256-reconciled planet and solar-altitude files across **3,506,400 fifteen-minute UTC samples**, 19 November 1926 inclusive to 19 November 2026 exclusive, at one specified calculation location for sect. A 0.1° Sun-altitude margin leaves 5,049 samples uncertain about day/night triplicity; the report never counts those as certain negatives.

| Mercury/Moon source-ruler candidate condition | Count | Share of all UTC grid samples |
|---|---:|---:|
| Prior three modes, with all triplicity co-rulers | 2,142,360 | 61.10% |
| Four modes, original **Ptolemaic printed terms** plus all co-rulers | **3,006,871** | **85.75%** |
| Four modes, **Egyptian printed terms** substituted as explicit historical sensitivity | **2,965,122** | **84.56%** |
| Same printed-table choice **changes the yes/no candidate classification** | **341,721** | **9.75%** |

The change in the total counts (1.19 percentage points) is much smaller than the **9.75 percentage points of individual instants classified differently**. Reporting only the two headline totals would miss this substantial source-choice sensitivity.

When holding the same lunar/solar sample instants fixed, the term ruler itself differs between the printed Ptolemaic and Egyptian schemes for **43.41% of Mercury placements** and **42.52% of Moon placements**. Their independent source tables are not interchangeable.

**Critical interpretation:** With four forms included, a shared *possible* ruler exists at nearly six-sevenths of time-grid samples. This very broad inclusion is not a discriminating chart signature. An observed common term/ruler is not yet Ptolemy's final selected governor, and none of these counts measures human psychological prediction. This is a uniform *UTC time* prior, not the distribution of actual births.

Both full scans preserve original file hashes and immutable private readback receipts; a public anonymous numeric aggregate, scripts and regression tests are published at `tools/astrohd/reference/research/ptolemy_iii13_four_mode_terms_aggregate_v01.json` and `tools/astrohd/scripts/ptolemy_four_modes_source_terms_century_v01.py`. The three-mode baseline remains untouched.

## Finding 3 — limited Moon application/separation event geometry implemented

Book I §24 says applications and separations may be bodily conjunctions or traditional aspects, that the interval must not be great, and that ecliptic latitude matters for bodily encounters. Book III §13 asks that the Moon's separations and applications be considered when investigating character. **Neither passage sets a precise numerical aspect orb for the whole soul-governor selection algorithm.**

The new `tools/astrohd/scripts/ptolemy_moon_app_sep_geometric_event_witness_v01.py` therefore does **not** invent an ancient source orb. It computes exact chronological Moon–planet aspect roots over a clearly labeled **research-only ±3-day window**, for the seven traditional planets with Moon as the moving subject (six other bodies). It records whether the exact event was before or after the reference timestamp and flags whether the Moon and its partner are on the same or different side of the ecliptic for exact conjunctions. No behavioral trait or “authoritative applying signification” is assigned.

An actual Swiss-Ephemeris source-neutral test at **2000-01-01 00:00 UTC** found **8 exact contact roots** in this six-day search span: four before and four after, with all angular residuals under **0.000000064°**. That checks the numerical root computation only. Its arbitrary search window does **not** define historical proximity.

A reproducibility detail matters: Swiss Ephemeris source files currently downloadable from the official project's GitHub **do not have the same planetary-file hash as the old century grid**. They were pinned separately for this pilot; the Moon file hash agrees. Seven preselected UTC source-neutral clock instants from the original century grid were recomputed with the new file: the maximum difference in the seven classical geocentric longitudes was **0.00000186°**, and all source return flags still identified SWIEPH. This is numerical cross-check evidence, **not evidence the binary source files are identical**. Do not silently promote these pilot contact results into the older century-cache source.

The source is [Ptolemy I §24](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/1B%2A.html) and [III §13](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3D%2A.html). All qualifying-orb choices, chronological motion conventions, aspect precedence, governor strength, dignity, sect, mixed testimony and contradictory conditions are **still unscored**.

## Current status: four source modes coded, one partial fifth-mode geometry witness

| Ptolemy's original mode | Current evidence |
| --- | --- |
| 1. Domicile | Source-neutral geometry coded and century counted |
| 2. Exaltation | Source-neutral geometry coded and century counted |
| 3. Triplicity | Day/night alternatives coded with co-ruler sensitivity; near-sunset/sunrise abstention |
| 4. Terms | **1940 printed Ptolemaic and Egyptian tables manually checked, coded as distinct schemes, century counted** |
| 5. Phase/aspect | **Exact astronomical contact chronology pilot**; full historically justified selection/near-enough rule **not yet implemented** |

**The most consequential remaining work:** source-qualified aspect nearness and Moon's applications/separations; how Ptolemy selects and reconciles actual governing planets, sect, angularity, honorable/contrary conditions and qualitative mixtures; complete Lilly manners significator, HD and modern Western interpretation; then a fair, same-instant, full-candidate-universe chart-to-profile comparison under frozen rules. A mathematically very frequent shared candidate is not a substitute for a unique, source-qualified character conclusion. User feedback and forum reflections remain explanatory, not validated forecasts.

**Conclusion:** We resolved two material text digitization defects and made another reproducible century-wide advance. We did not establish any chart's psychological ranking or independent human predictive accuracy.
