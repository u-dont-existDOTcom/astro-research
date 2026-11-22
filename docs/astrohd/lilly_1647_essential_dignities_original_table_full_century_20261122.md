# Lilly's original 1647 essential dignities at Mercury and Moon: full-century final-fallback candidate study

**22 November 2026. Source-grounded astronomical computation, not personality validation.**

This continues the [complete six-stage Lilly CVII source-variant and identical-UTC Ptolemy/HD census](lilly_cvii_all_planets_aspecting_asc_lord_full_century_20261122.md). The root research objective remains a defensible source-qualified chart-to-observable-behavior comparison. In particular, a **rare astronomical candidate is not evidence for a unique person's best psychological chart**.

## Primary sources: 1647 original, independently inspected

The directly read **original 1647 first printing** of William Lilly's *Christian Astrology* contains more executable essential-dignity rules than previously implemented. The preserved Wellcome scanned-original file SHA-256 is `2cb53e20e122ffc6e47917ba10241f6c49687cd7a4696f3b5db655a2a1aab28b`. The page images remain in authorized private historical-source storage; reproducibility records their source page mappings and hashes in the [source register](../../tools/astrohd/reference/research/lilly_1647_original_five_dignities_and_terms_source_register_v01.json). The originals are available through [Wellcome's catalogue](https://wellcomecollection.org/works/s7z7c46y).

- **Printed p.101 (one-based source PDF 135), chapter XVII:** gives a planet **five dignity points in its domicile**. This does not mean it is guaranteed fortunate, powerful or the personal significator when other testimonies conflict.
- **Printed p.102 (PDF 136):** gives **four** for exaltation, **three** for sect-appropriate triplicity and **two** for terms. Lilly's text explicitly distinguishes day and night triplicity, with Mars governing the water triplicity both day and night.
- **Printed p.103 (PDF 137):** gives **one** for its decan or face, the smallest essential dignity, and explicitly distinguishes these essential dignities from strength by being direct, swift, angular or receiving certain aspects.
- **Printed p.104 (PDF 138), p.105 (PDF 139):** reproduces Lilly's own 12-sign **terms, faces, domiciles, exaltations and triplicity** table, heading it as according to Ptolemy, then explains how to read the cumulative degree endpoints.
- **Printed pp.531–532 (PDF 565–566), chapter CV:** reports historical disagreement about the general *Lord of the Geniture*. Lilly personally favors combining **essential AND accidental dignities**, angularity and planetary conditions, with near-equal competitors participating. He then reports a *Greek* approach choosing a planet with most dignity claims **in Moon's and Mercury's places**. This reported Greek custom is **not automatically Ptolemy III.13's actual complete algorithm**, and not automatically Lilly's personal preference.
- **Printed p.536 (PDF 570), chapter CVII:** after the initial rising/intercepted, Moon/Mercury joining, Ascendant lord/dispositor and forceful partile steps, the last fallback invokes whoever has **the most essential dignities at Mercury and Moon**. A **candidate** can therefore be scored mechanically, with unresolved interpretation, without retrospectively reordering the original stages.

### Source-defined essential-dignity numbers

| Original Lilly essential dignity | Points | Sect-conditioned? |
|---|---:|---|
| Own domicile | 5 | No |
| Exaltation | 4 | No |
| Triplicity ruler | 3 | **Yes** |
| Term ruler | 2 | No |
| Face (decan) ruler | 1 | No |

These five values are from Lilly's own original text, **not a new model-selected weighting scheme**. The question of *combining Mercury's and Moon's place scores* is separate: the passage does not unambiguously require an additive sum, a maximum, or distinct winners. Accordingly, the program retains both `sum_of_both_places` and `strongest_of_two_places` as **non-authoritative operational policies**, which are crossed with the competing printed term editions.

## A newly recognized major historical source discrepancy

The newly transcribed **1647 Lilly “according to Ptolomy”** term table is **not equivalent** to the two term tables already transcribed from the separate **1940 Greek/English Loeb printing** (the Loeb Ptolemaic and Loeb Egyptian versions). For example, in the first printing's Taurus row **Saturn's term continues to 26° Taurus**, whereas the Loeb Ptolemaic source changes to Mars before that boundary. Lilly's original Leo first term is **Saturn**, while the Loeb Ptolemaic first term is **Jupiter**. All 12 source rows, their cumulative degree ends and original decans are independently saved in [the reproduction code](../../tools/astrohd/scripts/lilly_cvii_original_essential_dignity_final_fallback_century_v01.py).

The new complete 3,506,400-clock-sample study finds:

| The *same* source-place longitude | Lilly original 1647 vs Loeb Ptolemaic 1940 — different term lord | Lilly 1647 vs Loeb Egyptian 1940 — different term lord |
|---|---:|---:|
| Moon's place | **818,854** | **1,705,152** |
| Mercury's place | **832,853** | **1,744,068** |

This is a **historical calculation-source disagreement**, not a comparison of psychological predictions. Each edition's printed table has independent provenance. Identifying textual errors, Greek archetypes, manuscript interpolations or editorial choices requires qualified source criticism; no table is chosen because it seems to match an individual's experiences.

## Actual full-century source computation

The independently reproducible engine checks all **3,506,400** fifteen-minute UTC samples from **1926-11-19 inclusive to 2026-11-19 exclusive**. It rechecks all original 36 planetary + 36 location/angle + 36 HD same-UTC source-index shard SHA-256 values and the original **288,908 HD structural intervals**. The **125 clock positions near HD change roots** remain unassigned, not replaced with a neighboring HD structure. No chart owner's birth record, private interviews or human ratings are used in the public analysis.

At each same-instant timestamp, the source-defined dignity score is evaluated for **each of the seven traditional planets**, **at Mercury's and the Moon's zodiacal longitudes separately**, using the five original essential dignity conditions. The algorithm then calculates **six explicit comparison policies** (three original printed term tables × two ways to combine the two placements). A source-conditioned *unique candidate* needs one planet with strictly more such points than all competitors and at least one positive dignity claim. A tie, absent claims or uncertain day/night sect yields **an abstention**, not a false zero or a winner selected after seeing a person's answers.

The scores are applied **only after the previous 96 source-condition-specific six-stage Lilly fallback procedures reach S5**. They do not award a new winner in a chart where earlier stages or another-planet source ambiguity has not been resolved.

### Example with all preceding assumptions explicitly frozen

Take the original Ascendant-sign first rule, Lilly's smaller printed joining orbs, four nonluminary external joining planets, dispositor seeing by sign ray, Moon **OR** Mercury partile and the broad-literal **non-bodily-ray-only** interpretation of whether any other planet aspects the Ascendant lord.

| Outcome in the **15,583 S5-eligible UTC timestamps** | Count |
|---|---:|
| Unique dignity candidate, original 1647 Lilly term table, **sum** at Moon and Mercury | **13,825** |
| Tied dignity leaders, same terms and sum | **1,744** |
| Sect ambiguous near original-horizon threshold | **14** |
| Unique dignity candidate, original Lilly terms, **max** of Moon/Mercury place scores | **12,894** |
| **Identical unique candidate across all 3 term tables × both place aggregations** | **9,089** |
| Those 9,089 agreement cases spanning distinct HD structural intervals | **1,562** |

These categories are **not mutually additive** across different scoring policies. The single sum-policy partition is **13,825 unique + 1,744 tied + 14 sect-unknown = 15,583**, and the cross-variant 9,089 is a strict subset of the source-dependent candidate pool.

The earlier independently verified **4,553** timestamps with a Ptolemaic four-variant *conditional four-mode Mercury/Moon leader* were also joined at exactly the same UTC position. Only **23** of those reach this Lilly S5 branch; all **23** retain the same unique essential-dignity candidate under all six new candidate policies. This is a **cross-method geometric agreement conditional on many source/interpretation choices**, not a demonstration that both ancient systems predicted the same human characteristic.

### The complete declared alternative universe is not collapsed to this example

The machine-readable [anonymized aggregate](../../tools/astrohd/reference/research/lilly_cvii_original_essential_dignity_final_fallback_public_v01.json) includes all **96 original sign/house, joining, dispositor, partile and other-planet-aspect branches**, each crossed with six separate essential-dignity selection policies. The original S5 size varies **2,754–137,590** timestamps across these historical variants; cases with an unambiguous same-planet six-policy *dignity candidate* range **1,675–77,493**, and conditional Ptolemy overlap varies **0–197**. These variation ranges do **not** indicate predictive accuracy or how many people would match the claims.

A source-grounded numeric point assignment is now available for the **final essential-dignity candidate branch**. **Not computed** are an actual historical global Lilly *manners significator*, the strongest/fortified planet among earlier stages, the ambiguous `SX` other-planet scenario, exact original intended Mercury/Moon combination, fixed-star fortification, original Ptolemy fifth phase/aspect and contrary testimony, nor an independently validated human personality comparison. The 1647 first-print table and the 1940 Loeb variants must remain separate until critical scholarship resolves them.

## Reproduction, privacy and next implementation

Source: [Lilly 1647 first-edition register](../../tools/astrohd/reference/research/lilly_1647_original_five_dignities_and_terms_source_register_v01.json). Reproduction engine: `tools/astrohd/scripts/lilly_cvii_original_essential_dignity_final_fallback_century_v01.py`. Numeric output: `tools/astrohd/reference/research/lilly_cvii_original_essential_dignity_final_fallback_public_v01.json`. The runner fails if the original 108 source shards, HD transition-margin sample counts, earlier 96 historical S5 stage totals, or conditional four-mode Ptolemy 4,553-sample result differ. Its unit tests use invented zodiac positions and explicitly catch 8-bit sign arithmetic overflow.

**No personal evidence or original scans were published**; complete input binaries, source page renders and exact numerical execution receipts remain in authorized private research storage.

**Next:** complete source-licensed accidental strength and dignities, evaluate ties and competing testimony at every earlier source stage, independently adjudicate old Greek term variants and original Wolf speed-relative phase/orb language, then construct the actual source-defined, non-bespoke chart-to-observable-behavior model with full declared comparable century candidates and independent human validation. When the original sources cannot uniquely determine a rule, return a set of possible candidates or abstain instead of inventing certainty.
