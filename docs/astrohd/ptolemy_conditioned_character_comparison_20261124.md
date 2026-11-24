# Full-century partial planetary-condition comparison

24 November 2026. Continuation of the [planetary character experiment](ptolemy_planet_character_comparison_20261123.md).
The root outcome remains a fair, source-grounded multi-system behavioral
comparison and independent human predictive validation. No new qualification
criterion is declared a mandatory historical or empirical gate here.

## Fixed policy transfer and controls

This work takes the two explicitly partial qualification rules already
implemented in the [selected-panel pilot](../../tools/astrohd/scripts/compare_planet_character_condition_pilot_v01.py)
and applies them without rank-dependent modification to the complete
original verified grid. The source witnesses are own domicile, known
fixed planetary sect and a possible preceding square by a body of opposite
fixed sect, as used in the prior [III.13 fifth-mode source study](ptolemy_iii13_five_mode_aspect_and_sect_20261123.md).
They are not equivalent to the entire historical account of familiar
houses/sects, solar orientation, strength and contrary testimony.

| Fixed experimental rule | Dignified-clause proxy | Opposing-clause proxy | Abstention |
|---|---|---|---|
| Familiarity-only | Own domicile or fixed-sect agreement, without the defined contrary-square witness | Never selected | Otherwise |
| Fixed-sect contrast | Same | Opposite fixed sect, not in own domicile, no defined contrary-square witness | Otherwise |

A preceding-square witness inhibits clause admission under both rules;
it does not by itself establish an adverse condition. Unknown governor,
Sun/Moon character-list absence, and other unresolved qualification
remain explicit. Mercury's variable sect is not fabricated; own
domicile can still admit it under either proxy. These policies were
fixed in the previous experiment before the present full-grid scores.

No favorable/opposing branch is chosen from the participant's self-report.
The complete frozen source map, both previously stored observation
codings, and the generic HD mappings remain unchanged. The two versions
are post-exposure developmental semantic codings, not blind
prospective personality predictions.

## Models

For each historical governor scenario use the original solitary
planetary character tables, with rational Mercury and sensory Moon
independently qualified under the same declared policy. The distinction
between the existence of an admitted condition and the number of mapped
observations is retained. A signed contribution can be zero in sum
despite actual supporting and contradicting evidence; it is not
automatically an abstention. Source-unmentioned or unobserved traits
are not treated as negative predictions.

Evaluate:

- The prior strict governor-sign/illumination score, unchanged.
- Character-only Western score: average of the two place-specific
  character scores.
- A fixed 50:50 blend within the Western family of the preceding two
  models. Each Western model has the same total weight; the blend
  does not reward the existence of an extra correlated testimony
  family by increasing the Western weight. It is a transparent
  exploratory family cap, not proof of item-level independence.
- Each Western score alone and combined with the unchanged generic
  HD score using the existing equal-family weighting.

These are parallel experimental arms, not selection of a winning
model after scoring. The assumed-alliance arms from PR38 remain in
their original receipt; the two partial policies were defined for
separate-place solitary profiles, not a historical alliance decision.

For character and blended scores, retain policy-conditional outer
intervals over every possible provisional governor and independent
abstention. The blend intervals also allow suppression of sign and
illumination testimony; independently combined component extrema
may not be jointly attainable. These are bounds on the specified
partial policies, not on every possible historical condition. The
broader prior unconstrained historical-condition envelopes remain
unchanged.

In addition to ranking all comparable timestamps, stratify by the
exact number of character observations mapped at each faculty of
the reference. Report the denominator and comparison counts within
that matched-opportunity subset. Matching counts is not matching the
same observed items and is not an independent validation. It tests
whether a rank change is driven mainly by how much character
testimony was admitted. Report admitted dignified/opposite/unknown
condition counts per place, both admitted, and zero mapped
observations. Do not condition the primary comparison on coverage.

## Reproducibility and verification

Use [the new runner](../../tools/astrohd/scripts/compare_conditioned_character_century_v01.py)
with the same source caches, original chart inventory, and paired
observation files from PR38. Also supply the earlier sign-grid,
planetary-character-grid and condition-pilot receipts. All input
paths and private outputs remain outside the public checkout.

The runner verifies the canonical grid and HD row hashes and exact
same-site reference, binds both observation files to the previous
receipts, and reproduces the previous scalar condition pilot. For
both observation codings it requires exact scalar/vectorized parity
on every selected-panel chart and all 128 historical/condition arms.
It then computes every one of the 64 historical source scenarios
under both condition policies across the full finite grid, preserving
125 near-HD-boundary abstentions. Every strict sign branch must
reproduce its previous complete-grid higher/tied/lower counts under
both policies; all strict, coverage-stratified and interval counts
must reconcile. The output is an immutable private receipt.

```bash
python tools/astrohd/scripts/compare_conditioned_character_century_v01.py \
 --west /private/west-grid --angles /private/site-grid \
 --hd-cache /private/hd-cache --join /private/hd-join \
 --mapping-library /private/frozen-hd-mapping.json \
 --inventory /private/frozen-panel.json \
 --prior-sign /private/sign-receipt.json \
 --prior-planet /private/planet-character-receipt.json \
 --prior-pilot /private/condition-pilot-receipt.json \
 --hd-evidence /private/broad-hd.json --evidence /private/broad-character.json \
 --hd-evidence /private/narrow-hd.json --evidence /private/narrow-character.json \
 --output /private/new-immutable-result.json
```

The six focused synthetic tests verify the condition truth table,
scalar/vectorized agreement for every body, signed cancellation versus
missing observations, conditional bounds, the family weight cap,
matched-opportunity denominators, and the 128-arm accounting including
phase uncertainty. No individual score, chart input, private evidence
or private path belongs in the public repository.

## Executed outcome

The complete private run finished with both frozen evidence codings and all 3,506,400 original timestamps (3,506,275 ranked, 125 HD boundary abstentions). All 128 historical/condition arms per coding were executed, every prior strict sign-score count reproduced, the previous scalar panel replayed, and all exact, matched-opportunity and bounded counts reconciled. Receipt readback confirmed the runner digest and restrictive private permissions. The family-capped blend improves median specificity in some comparisons but loses all strictly top ties in the tested condition arms; neither policy yields a robust unique first place. The conditions leave substantial character testimony unresolved, and equal-count coverage matching materially changes some comparisons. Do not promote one condition rule based on an exposed reference. Individual counts remain private.

A separate [first Lilly CVII/CVIII scored panel](lilly_cviii_character_panel_comparison_20261124.md) is also complete under both evidence codings. The full-grid Lilly extension was not executed in this pass.

## Decision boundary

Rank within a fixed-site 15-minute candidate grid is a developmental
specificity diagnostic, not a calibrated probability, a count of
people or a measure of predictive accuracy. Differences between
models must be interpreted together with coverage, negative evidence,
both frozen evidence codings and historical uncertainty. An appealing
first-place branch cannot establish the ancient interpretation or
justify new score weights. After this bounded transfer, prioritize
other independently sourced traditions and independent held-out human
outcomes rather than repeatedly maximizing the exposed reference's
rank.
