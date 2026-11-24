# Sārāvalī XV–XVI: first finite-grid combination behavior comparison

24 November 2026. A bounded development comparison from the existing five-book Jyotiṣa source research, not a complete Vedic astrology model. The parent goal of fair multi-tradition comparison and independent predictive validation remains open. Neither prior Western score nor generic HD score is changed.

## Source continuity and operational mapping

The previously inspected 1928 edited Sanskrit source (Nirṇaya Sāgar Press, printed pp.41–45, JainQQ catalogue 009887) supplies all 21 named two-planet combinations in XV.2–22 and 35 named three-planet combinations in XVI.1–35. The earlier B178 and B180 source registers explicitly enumerate the bodies and printed verse/page locators. The new [operational register](../../tools/astrohd/reference/research/saravali_xv_xvi_shared_observable_v01.json) binds both archive-file SHA-256 digests and reproduces their full 56-combination enumeration. In this pass, the complete English chapter witness was read at [AstroNeemo, chapters XV and XVI](https://www.astroneemo.net/articles/sraval-kalyana-varma-4.html?showall=1); the [electronic Sanskrit and machine translation](https://indike.org/pramana/in.astro.hora.yavana.saravali.16) are a secondary aid, not a newly collated physical Sanskrit witness. The old photograph-based Sanskrit source decisions remain distinguishable from the new English-based behavioral hypotheses.

The earlier source-qualified five-book survey contained 432 documentary annotations, not 432 validated predictions. This new map includes all 56 named configurations, but only 36 have a selected direction in the existing 37-construct vocabulary. The 64 directions split into 17 relatively direct operational mappings and 47 semantic proxies. For example, a source description of skill in speaking is closer to the existing eloquence construct than a historical leadership title is to a person's habitual preference for taking command. Scholar/learning, harshness/ordinary conflict, and other such conversions are labeled proxies where appropriate. The direct/proxy label reflects a narrow semantic judgment, not psychometric validation. Reuse the frozen behavioral observations rather than choose new questions because the reference has a particular conjunction.

No sensitive identity, disease, criminal label, inherited social status, reproductive or partner outcome is turned into a modern behavior assertion. Twenty catalogue entries have no admitted shared direction; all remain in the mechanical coverage denominator. No missing clause is a negative prediction. Earlier documented source disagreements are preserved: XV.6 bondage versus wealth, XV.23 qualitative class versus translator's varga interpretation, and XVI.27 inherited status wording and omitted enthusiasm are not turned into additional scored claims. The 1928 register does not specify a numerical conjunction orb, a universal nested-combination priority, or a quantitative strength multiplier. The later parental and benefic/malefic clauses and chapters XVII onward require separate source models. No claim of exhaustive reading of the entire five-book corpus follows.

## Fixed experimental alternatives

Use the original verified century source clock (3,506,400 UTC quarter-hour instants at one fixed research site), immutable generic HD map, and both unchanged planet-character observation files. The model evaluates 4 geometry conventions x 4 overlap treatments x 2 vocabulary interpretations = 32 arms per frozen observation profile.

Geometry:

- Lahiri same sidereal sign and Raman same sidereal sign. Same-sign grouping is equivalent to occupying the same whole-sign house; no claim that either ayanāṃśa or this house convention is the original unique textual rule.
- Circular pairwise distance no greater than 3 or 10 degrees, independent of zodiac origin. For a triple all three mutual distances must qualify, not merely a transitive chain. These thresholds are researcher-defined sensitivity alternatives.

Overlap treatments: inclusive pairs, inclusive triples, both inclusive, and isolated exact groups. The isolated arm requires that no conjunction edge links a group to any outside body. It therefore excludes larger groups and incomplete linked clusters rather than interpreting an arbitrary two- or three-body subset as their definitive character. Inclusive arms retain nested possibilities as a different declared hypothesis. No artificial priority is selected from observed fit.

Mappings: direct only, or direct plus proxy. The earlier shared rational and sensory/affective vocabulary and fixed number of known observations per domain determine the denominator. For each item, repeated concordant active directions count once; conflicting directions cancel to an abstention in the unscaled score. Compare the signed prediction to the observed positive or negative pattern. An absent observation or source-unmentioned construct adds zero evidence, not a contradiction. Average the two domain means and combine with generic HD by the established equal-family mean.

XV.23's qualitative modifier is unresolved. The exact arm is an unscaled conditional score, not a strength-qualified prediction. A separate outer envelope allows every admitted contribution to attenuate to zero and permits either sign of a conflict. It bounds this limited item model only, not all possible historical-strength effects. No percentage or varga multiplier is attributed to the text.

## Reproducible computation

The [runner](../../tools/astrohd/scripts/compare_saravali_combinations_century_v01.py) checks the original ephemeris source files against the original grid manifest, the source grid and join manifests, HD state continuity, and frozen evidence digests against the prior planet-character receipt. It computes the Swiss sidereal corrections at each declared clock under both modes, checking cached tropical minus correction against direct Swiss sidereal calculation for every classical body at the first, middle and last sample of each processed chunk and the exact reference. A 0.00001 degree numerical boundary margin marks rows with an ambiguous sign or angular threshold; those are separately counted, not silently ranked. These sampled numerical checks do not prove arbitrary continuous-time equality or historical correctness. The independent HD boundary abstentions remain in coverage.

A 21-edge bit mask represents the seven-planet conjunction graph; every distinct graph yields the same admitted catalogue entries and fixed score. Compact unique-graph evaluation therefore preserves rowwise scoring exactly. The runner returns Vedic-alone and HD+Vedic higher/equal/lower counts, attenuation interval counts, number with usable mapped observations, conflicting-item coverage, and an equal-number-of-known-items comparison. The latter is a coverage sensitivity, not independent validation. It also counts same timestamps strictly higher or tied under all 32 combined arms on their common usable grid; marginal rank statistics are not cross-tradition intersections.

Use all input and output paths outside the public checkout, with the original frozen ephemeris directory and prior private planet-character receipt:

```bash
python tools/astrohd/scripts/compare_saravali_combinations_century_v01.py \
 --west /private/west-grid --angles /private/site-grid \
 --hd-cache /private/hd-cache --join /private/hd-join \
 --ephemeris /private/original-ephemeris \
 --mapping-library /private/frozen-hd-mapping.json \
 --inventory /private/frozen-panel.json \
 --prior-planet /private/planet-character-receipt.json \
 --hd-evidence /private/broad-hd.json --evidence /private/broad-character.json \
 --hd-evidence /private/narrow-hd.json --evidence /private/narrow-character.json \
 --output /private/new-immutable-result.json
```

The seven synthetic tests verify complete catalogue enumeration, circular geometry and numerical boundaries, pair/triple clique membership, isolation, per-item caps and counterevidence, exact compact-to-rowwise parity, and all 32 score/coverage arms. A first execution stopped on an ephemeris checksum mismatch before evaluating candidates; the actual original two ephemeris files were located and reverified. The initial differing planetary file was not silently substituted.

The reference was already exposed and the evidence is retrospective. All source variants are retained regardless of score outcome. This is an exploratory same-site finite-clock discrimination experiment, not a calibrated prediction or independent assessment of actual people. No individual chart, interview, private file locator, rank or result count is published. No new participant collection is authorized by this comparison.

## Executed outcome and continuation

The corrected private run completed all 3,506,400 original quarter-hour timestamps in both frozen evidence profiles and all 32 declared arms per profile. Original HD-boundary exclusions remained 125; the four geometry-specific numerical boundary margins excluded a further 10–19 rows with known HD (the common usable denominator was 3,506,210). The largest sampled discrepancy between direct Swiss sidereal computation and cached tropical minus the correction was below 0.00000005 degrees in both sidereal modes. All score, coverage, matched-item and interval counts reconciled and both receipt profiles and the scorer digest were verified at readback.

The bounded conjunction family does not provide a stable improvement over the previous Western developmental comparisons. Its direct mappings are sparse, and the larger proxy vocabulary changes discrimination materially; an apparently favorable restricted conjunction reading is not a robust result across the declared alternatives. The attenuation bounds provide no guaranteed incremental separation beyond the original HD score. The two source chapters should be retained as a specific historical family, not promoted to a complete Vedic system or fitted to the exposed reference. All personal scores and rank counts remain private.

Next, broaden actual Jyotiṣa behavioral coverage through a different source family (e.g. the twelve Moon-rāśi descriptions or solar/lunar yogas), using the earlier Sanskrit/source qualifier registers and a fixed observable rubric rather than adding more arbitrary conjunction thresholds. Then continue into Chinese systems with the existing two-witness calculation work. Compare systems on the same timestamp rows and distinguish same-row intersections from marginal rank summaries; do not give related traditions multiple independent votes for the same observed trait. Separate independent held-out validation remains unperformed.
