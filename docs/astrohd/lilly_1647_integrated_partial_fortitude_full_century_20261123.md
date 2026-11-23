# Original Lilly 1647: integrated but partial planetary fortitude across the full fixed UTC century

**23 November 2026.** An actually executed source-hash-verified, same-instant century calculation. **Scope: partial natal-body planetary strength only, not a completed Lilly CVII manners significator, Ptolemy III.13 governor, or human personality predictor.**

## Why integration is different from the earlier studies

The earlier research calculated original-source subcomponents **independently**:

- [Original 1647 essential debilities, possible reception and peregrine](lilly_1647_p112_reception_peregrine_full_century_20261122.md) for each natal body's own zodiac position;
- [Original p.115 twelve-house accidental fortitude](lilly_1647_original_house_accidental_strength_century_20261122.md) under Regiomontanus and Placidus independently;
- [Original p.115 direct/retrograde motion](lilly_1647_source_motion_direct_retrograde_century_20261122.md) with precise Mercury source speed, reproducible finite speed for the other four nonluminary classic planets, and explicit station abstentions.

**This pass actually combines those three families at the same UTC instant for all seven traditional planets.** It preserves exactly the source points from Lilly's original p.104, p.112 and p.115, as interpreted in the earlier separately reviewed source reports, without making up a new weighting for them.

However, **a sum of three legitimate historical components is not the original source's complete total**. Lilly's original fortitude table contains *many more* conditions: appropriate planets acting as the matter's significators, reception by other dignities, orientality, swift/slow speed, Sun beams, partile benefic/malefic aspects, nodes, fixed stars and other testimonies. Some of these are partially computable but historically ambiguous; some require additional pinned data. This computation does **not** resolve them, or supersede Lilly CVII's previously source-sensitive **ordered eligibility stages**. It also does not replace the different final CVII rule of having dignities at **the places of Mercury and Moon**.

## Exactly what was computed

At every timestamp, the model computes the **partial natal-body score** as:

**Natal essential dignities and debilities + natal house-position points + direct/retrograde-motion points.**

Independent source/operational variants are always kept separate:

| Component | Declared variants |
|---|---|
| Original historic printed terms | 1647 Lilly first print; 1940 Loeb Ptolemaic; 1940 Loeb Egyptian: **3** |
| Original essential reception and debility conventions | Five positive intrinsic points only; add detriment/fall/peregrine; potential mutual domicile/exaltation reception clearing peregrine; same reception preserving intrinsic peregrine: **4** |
| House division | Regiomontanus versus original source-cached Placidus: **2** |
| Direct/retrograde near-station uncertainty | 0.01 / 0.02 / 0.05 degrees per day, **engineering thresholds, not Lilly-authored**: **3** |

**Total 3 × 4 × 2 × 3 = 72 separate scenarios.** These are source-labeled mechanical sensitivities; the original sources do **not** prescribe one overall final selection among all 72.

Unknown motion near stations is **not** treated as a value of zero or an imputed direct/retrograde planet. Instead, the possible motion score is bounded by **−5 to +4**. A planet is declared the *strictly unique highest partial score* under an individual scenario only when its **minimum total partial score exceeds every competitor's maximum**. Near day/night solar-horizon ambiguity, no planet is selected. An all-scenario agreement exists only when **all 72** separate policies select the **same strictly unique body**.

The source-specific numerical weights remain distinct from a trait model. There are no participant labels, personal natal times, questionnaires, or outcomes in any input.

## Actual 3,506,400-timestamp century computation

The [reproducible full-century engine](../../tools/astrohd/scripts/lilly_1647_integrated_partial_fortitude_full_century_v01.py) was executed against the original **1926-11-19 (inclusive) to 2026-11-19 (exclusive) quarter-hour UTC grid** at the one predeclared fixed research location. It individually verified the original **36 planetary +36 site-angle +36 HD lookup binary shard SHA-256 manifests** and checked the independent **288,908 HD structural intervals**. Original **125 HD transition-margin samples** were left unassigned, as were **5,049** near-day/night-sector records for strict comparative leaders.

It independently reproduced two earlier declared source controls: **1,088,009 samples where at least one classical planet switches house between Placidus and Regiomontanus**, and the original planet-motion direct/retrograde/near-station counts for all five moving nonluminaries under all three uncertainty thresholds.

## Main finding: source-variant stability

| Outcome across same actual UTC sample population | Count |
|---|---:|
| Every one of the **72 source/operational scenarios** chooses the **same unique partial-strength planet** | **1,677,330** |
| All other sample times have at least one tie, uncertainty, or source-dependent different leader | 1,829,070 |
| HD structural intervals containing at least one all-72-stable timestamp | **200,569** |
| Earlier *conditional* four-mode Ptolemaic possible common Mercury/Moon leader timestamps, whole grid | 4,553 |
| Among those Ptolemy-conditional timestamps, all-72 partial Lilly strength winner stable | **3,057** |
| Of the latter, **same planet** as conditional Ptolemy possible leader | **2,039** |
| Of the latter, **different planet** | **1,018** |

**These are not 1.68 million human subjects.** They are the **sampled astronomical clock instants** in one fixed-location grid. The two traditions share substantial astronomical inputs, so agreement is **not independent predictive validation**, and the Ptolemaic body is not yet the historical complete III.13 soul governor. A stable *partial* source-component maximum remains distinct from complete natal fortitude or Lilly CVII's manners significator.

## How much does house choice still matter after combining partial strength?

At the middle engineering station tolerance (**0.02° per day**), for otherwise identical original printed terms and natal essential rules:

| Terms/essential policy | Both house divisions select a unique partial-strength winner | Same winner | Different winners |
|---|---:|---:|---:|
| Lilly1647 original terms; add detriment/fall/peregrine, **no reception** | **3,013,806** | 2,949,504 | **64,302** |
| Lilly1647 original terms; allow strict *potential* mutual-house/exalt reception clearing peregrine | **2,988,802** | 2,922,237 | **66,565** |

These are **one-component-source-convention sensitivities embedded in a partial aggregate**, not performance scores against people. The second reception policy does **not** establish that the affected planets are actual valid significators of a question or matter: Lilly first requires that qualification at p.112, which cannot simply be deduced from zodiac positions.

## Source and acceptance safeguards

The [source method and historical boundaries register](../../tools/astrohd/reference/research/lilly_1647_integrated_partial_fortitude_source_methods_v01.json) records which original point categories were combined, the original printed references, source-status caveats, 72 declared alternatives and missing conditions. The [public numerical aggregate](../../tools/astrohd/reference/research/lilly_1647_integrated_partial_fortitude_full_century_public_v01.json) is byte-identical to the authorized private full-century execution receipt, but contains only **anonymized astronomical counts and historical metadata**.

The implementation refuses changed input hashes and verifies the **original previous independent house and motion totals before publishing**, in addition to the conditional Ptolemy 4,553 and near-transition HD 125 record baselines. Its tests use invented zodiac examples, numerical score-interval adversarial cases, all 72 complete denominator partitions and explicit prohibitions against treating these as final manners governors. The [eight-lane completion-scope contract](../../state/RESEARCH-COMPLETION-SCOPE.json) remains **OPEN** for Ptolemy III.13 historical fifth-mode and contrary testimonies, Lilly CVII true matter significators and full original strengths, human trait mapping, and independent human validation.

**Most useful next parent-goal step:** source-authorize the actual planetary eligibility for the matter in Lilly CVII, identify which of the remaining original accidental conditions are both historically unambiguous and computable, then evaluate complete **historical** candidate sets through all prior eligibility stages. The unvalidated personality comparison should use preregistered, non-bespoke observable traits and private blinded outcomes, not the rarity of these astronomical combinations.

No personal birth record, questionnaire, interview, participant identity or prior natal-ranking outcome was used in this public work.
