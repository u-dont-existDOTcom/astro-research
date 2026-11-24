# Lilly CVII–CVIII: full finite-century behavioral comparison

24 November 2026. Extend the exact [selected-panel character experiment](lilly_cviii_character_panel_comparison_20261124.md) to the original fixed-site, quarter-hour century grid. Preserve the previously frozen source map, both observation codings, all 96 historical stage interpretations, four conditional scoring arms, and unresolved strength/participant bounds. The parent multi-system comparison and independent human validation remain open.

## Method and source continuity

The [previous Lilly map](../../tools/astrohd/reference/research/lilly_cviii_planet_character_operational_v01.json) contains 44 signed directions, five standalone planetary character profiles, and both strong/weak conditions. It is based on the previously recorded CVIII text witness, not a newly claimed first-print collation. No source directions or participant observations are changed. The earlier [original CVII source census](lilly_cvii_1647_full_ordered_stage_coverage_20261123.md) supplies the exact 96 stage paths and 11 status categories.

Use the original [panel scorer](../../tools/astrohd/scripts/compare_lilly_character_panel_v01.py) to generate source-primary and secondary masks and score them. The single-strong and single-weak arms abstain on plural or unresolved primaries. The mean-strong and mean-weak arms average all provisional principal bodies under the same assumed clause. Secondary possible dignity participants, both conditions and abstention remain in the outer convex-mixture envelope, as before. Unresolved primary paths allow all seven body scores plus abstention in the outer relaxation. No condition is selected by observed fit; the source's actual fortitude and mixture conditions remain incomplete. A luminary contributes no standalone character-list credit, not another planet's profile. The four score arms are deliberately conditional, not claims that all planets really have one condition.

Each reference and grid row uses the same frozen HD observation model. Joint score is the existing equal-weight mean of HD and the chosen Western score, not an extra weight for using another related Western tradition. Report Western alone and the combined score separately. Preserve the sign, character and condition-policy Ptolemy experiments as separate comparisons; different model-specific high-rank counts do not identify the same candidate timestamps and cannot be multiplied as independent probabilities.

## Complete-grid computation

The [runner](../../tools/astrohd/scripts/compare_lilly_character_century_v01.py) verifies the original same-site UTC source manifests, 108 aligned planetary/site/HD-index shards, and HD state continuity. It verifies both previous private panel receipts, including their scorer and evidence digests, and exactly replays all panel scores and ranks. Recompute Regiomontanus cusps on every original clock sample with the frozen Swiss Ephemeris version and verify the existing ascendant longitude. The prior reference is evaluated at its exact recorded UTC, which need not fall on the grid.

For each historical path the same panel functions return a seven-bit primary mask and a seven-bit outer possible participant mask. Each unique frozen HD score receives a discrete code. A histogram of (HD score code, body mask) is sufficient to reconstruct every score in the frozen rubric without selecting, pruning or approximating candidates. Separate primary and outer-mask histograms provide exact scores and interval endpoints respectively; both are counted on every ranked source timestamp. The two synthetic regressions compare histogram and literal rowwise results, including negative scores, ties, missing HD rows, matched-count denominators, and full 96-stage accounting across multiple chunks.

Reconcile every one of the 96 x 11 historical stage counts against the earlier source-only public census. Count ranked single, multiple and unresolved primaries, certain/possible S1 secondary participants, higher/equal/lower score counts, and interval comparisons. Also report the conditional rank among timestamps with the same number of provisional primaries as the reference. This is a coverage sensitivity, not a score tuned to the reference or a test with independent humans. Matching counts does not establish matched characteristics or participants.

The run accepts external paths only:

```bash
python tools/astrohd/scripts/compare_lilly_character_century_v01.py \
 --west /private/west-grid --angles /private/site-grid \
 --hd-cache /private/hd-cache --join /private/hd-join \
 --mapping-library /private/frozen-hd-mapping.json \
 --inventory /private/frozen-panel.json \
 --hd-evidence /private/broad-hd.json --evidence /private/broad-character.json \
 --prior-panel /private/broad-lilly-panel.json \
 --hd-evidence /private/narrow-hd.json --evidence /private/narrow-character.json \
 --prior-panel /private/narrow-lilly-panel.json \
 --output /private/new-immutable-result.json
```

The model is retrospective, uses a pre-exposed reference, and is limited to the declared fixed-site finite grid. The number of timestamps is not a count of independently assessed people; a rank improvement would be development evidence, not independent predictive validity. No private chart input, observation, individual rank, receipt path or identifier is published.

## Executed outcome

The full scan completed all 3,506,400 original samples, with 3,506,275 ranked and 125 HD-boundary abstentions. Both immutable evidence versions and all 96 historical paths were scored. All 1,056 prior historical stage totals, prior scalar panel scores and ranks, and every exact, coverage-matched and interval count reconciled. The private result was read back against its runner digest and restrictive file permissions. The selected-panel favorable ranking under the mean-strong arm does not survive full-grid comparison; the weak-condition arms can produce very large top ties because of sparse or nonpositive character testimony, and no arm provides a unique first place. The previous Ptolemy condition-blend is more discriminating toward the exposed reference in the median comparison, but that is not independent evidence of accuracy or a reason to adopt a preferred historical interpretation. Conservative Lilly bounds yield no guaranteed incremental discrimination beyond the frozen HD score in this experiment. No individual scores or ranks are published.

## Further traditions: source reuse, not invented replacement models

The prior October five-book Jyotish survey contains 432 accepted documentary annotations (not verified human predictions). The Sārāvalī XV–XVI conjunction catalogues provide 21 pairs and 35 triples with recorded original printed-source locators. Their actual modern conjunction geometry, priority for overlapping combinations and qualitative modifiers remain source-sensitive. In particular XV.23's Sanskrit qualitative class term is not equivalent to a numerically defined good/bad divisional strength modifier. A next bounded developmental comparison should independently admit observable directions across the entire relevant source family, retain named source alternatives and explicit abstentions, and apply the same finite source grid with declared sidereal conventions. Do not treat absence of a recorded rule as negative evidence, or double-count correlated clauses. Earlier local Chinese work has two-witness BaZi mechanics and an independently checked partial Zi Wei chart engine; those are calculation foundations, not behavioral scores. Existing authorized archives are read-only historical evidence. New source-safe public research belongs in this active repository; private source scans and research evidence remain private.

No new Vedic or Chinese behavioral rank is claimed by this Lilly experiment. No new participant data collection or prospective experiment is authorized merely by this source-method continuation.
