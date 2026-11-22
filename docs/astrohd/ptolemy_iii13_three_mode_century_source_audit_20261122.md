# Ptolemy III.13 — First three source-qualification modes computed across the century

**22 November 2026.** Source-first, public, participant-neutral original-chart research. **No person-level natal prediction, psychological-fit probability or source-complete governor rank is inferred.**

## Why this study was necessary

Ptolemy's *Tetrabiblos*, Book III §13, investigates the condition of the soul by considering Mercury, the Moon, their rulers, aspects, and further planetary conditions. Book III §2 provides five classes of rulership or domination used in that school: **triplicity, domicile, exaltation, term, and phase or aspect**. These are **not** a simplified ranking of how many planetary dignities appear in a whole chart. The earlier source register `ptolemy_iii13_natal_character_claims_v1.json` correctly labeled all 13 character claims **not automatically scoreable**, because actual governors and conflicting planetary testimonies had not been adjudicated.

This continuation calculates a **limited astronomical prerequisite**: whether Mercury and the Moon share at least one *possible* planetary ruler through a subset of Ptolemy's original methods, counted over a fully specified clock-time grid. It implements no psychological trait inference and never equates a source candidate with Ptolemy's final soul governor.

## Exactly which original source rules have been encoded

| Ptolemaic form | Implementation in this pass | Source |
|---|---|---|
| Zodiacal domicile | **Calculated** for both Moon and Mercury | I §§17–19 |
| Planetary exaltation | **Calculated** as distinct candidate set | I §§17–19 |
| Triplicity | **Calculated** by day/night Sun altitude, with **two explicitly separate variants**: principal lord and all source-declared co-rulers | I §18 |
| Terms/bounds | **Unresolved**; no fabricated or silently selected universal table | I §§20–21; manuscript and edition differences |
| Phase/aspect | **Unresolved**; not substituted with an arbitrary modern 3° aspect | III §§2, 13 |

Source links: [Ptolemy's five forms in Book III §2](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3A%2A.html), [Mercury/Moon qualification in III §13](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3D%2A.html), and [Book I domiciles, triplicities, exaltations and terms](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/1B%2A.html). These are English translations/digital reproductions, not a newly collated Greek critical edition.

For triplicities the seven-planet graph is **fixed before computing the century scan**. Fire signs receive Sun/Jupiter co-rulers; Earth Venus/Moon; Air Saturn/Mercury; Water Mars with Venus by day or Moon by night. In the **principal-only engineering sensitivity** the day ruler and night ruler are treated as one primary candidate (with water Mars in both). This is a *sensitivity bound*, not a declaration that Ptolemy's genuine method always ignores co-rulers. A 0.1° true solar-altitude band around the horizon is *unresolved* in both sect-specific versions, not assigned a false result.

## Two real full-century scans on verified astronomy

Inputs: **3,506,400 UTC quarter-hour samples**, 1926-11-19 00:00 UTC inclusive to 2026-11-19 00:00 UTC exclusive, **one fixed research location** for Sun altitude. All 36 original planetary binary shards were rehashed against their verified source manifests; in the three-mode scan all 36 original place/solar-altitude shards were independently rehashed. No respondent charts or source interview facts enter these public scripts.

| Restricted source condition | Sampled instants | Percent of *all grid timestamps* |
|---|---:|---:|
| Mercury and Moon occupy identical zodiac signs | 288,789 | 8.236% |
| Their zodiacal domicile lords match | 534,191 | 15.235% |
| At least one ruler candidate shared via **domicile and/or exaltation** | **1,026,641** | **29.279%** |
| At least one shared candidate via domicile/exaltation **plus principal triplicity**, only away from ambiguous horizon | **1,844,501** | **52.604%** |
| At least one shared candidate via domicile/exaltation **plus all declared triplicity co-rulers**, only away from ambiguous horizon | **2,142,360** | **61.099%** |

All counts refer to the same 3,506,400 sample instants; different conditions overlap, so they must **not** be summed. The three-mode result leaves **5,049 samples (0.144% of all instants)** unresolved because of the specified near-horizon sect policy. Of these, 1,476 independently have a two-mode shared candidate, but their *triplicity extension* remains unqualified.

**Material source-semantic sensitivity:** At **297,859 instants, 8.495 percentage points of the total**, the principal-only and all-co-ruler three-mode interpretations disagree on whether Mercury and Moon share a ruler. This substantial mechanical difference is why source conventions must be declared *before* looking for favorable personality matches. Adding co-rulers creates more structural intersections; it does not increase evidence of actual psychological predictive accuracy.

The numerical results were calculated and independently read back from immutable source-bound **private** receipts; the code and public neutral aggregate deliberately omit personal natal metadata. Public aggregate: `tools/astrohd/reference/research/ptolemy_iii13_three_modes_century_aggregate_v01.json`. Code: `tools/astrohd/scripts/ptolemy_mercury_moon_two_dignity_modes_century_v01.py`, `tools/astrohd/scripts/ptolemy_three_modes_triplicity_sect_century_v01.py`. Original binary checksums are verified rather than copying copyrighted or private ephemeris files into public Git.

## Historical terms remain a genuine source conflict, not a license to cherry-pick

The digitized English Book I terms table at the LacusCurtius reproduction appears to give Libra's final term a repeated Saturn symbol, while another digitization of the Robbins translation presents that terminal term as Mars. This **does not prove that the original Greek, Robbins printed Loeb, or any scholar's table was erroneous**. An [independent historical study of Ptolemaic bounds](https://library.keplercollege.org/wp-content/uploads/2022/01/Houlding_ptolemy_terms1.pdf) notes documented alternative term sequences, including a Jupiter–Mercury ordering discrepancy in Libra in some preserved traditions. These are different provenance problems: a rendering/glyph disagreement and a historical sequence disagreement. This turn did not complete visual collation of the printed edition and manuscript witnesses. The `TERMS` source mode accordingly remains **UNSCORED and UNIMPLEMENTED**.

Source register: `tools/astrohd/reference/research/ptolemy_iii13_five_domination_mode_source_adjudication_v01.json`, with explicit per-source read modes and open problems. A future source adjudicator must preserve the historical Egyptian, Ptolemaic and other tables as named variants and justify any adopted text rather than use whichever favors a known chart.

## What we can and cannot conclude

**We have demonstrated** reproducible candidate eligibility for three partial rulership modes in a large, fixed, time-sampled astronomical universe, and that their interpretation varies materially with co-ruler policy.

**We have NOT demonstrated** the final character ruler, its strength or kind, Moon applying/separating actual rulers, angular conditions or sect conflicts, a full Ptolemaic personality assignment, a comparison with the owner's reported life, a unique or top-ranked birth time, a probability that astrology is true, or any independently verified prospective human outcome. A common ruler is not evidence of its correct psychological description. The century's uniform UTC samples are not a weighted sample of human birth times, and the original grid is finite at 15-minute resolution rather than continuous.

## Next executable source work (tracks S/R)

1. Resolve the exact original terms table with independently checked printed witnesses. Preserve alternative manuscripts and table schemes rather than overwriting uncertainty.
2. Implement source-valid lunar *applications/separations* and relevant **phase/aspect familiarity**, including exact chronology and comparable planet-strength conditions, before any soul-governor choice.
3. Define the Ptolemaic dominator-selection arbitration, sect, angle and contradictory testimony rules, then either freeze a source-qualified interpretation contract with countercases or formally classify the remaining rule unscorable.
4. In parallel, finish the nonidentical Lilly manners-significator priority and House/ASC/interception rules, the complete HD profile/Channel source logic, and a separately labeled modern Western interpretation.
5. Only then can one run a fair time-specific, complete candidate-universe descriptive development ranking (or produce a reasoned **no defensible unique ranking** closeout). A separate untouched human study is required to claim out-of-sample accuracy over nonastrological baselines.

**Status:** source-level partial astronomy meaningfully advanced; original rulebook completeness and human predictive validity remain OPEN.
