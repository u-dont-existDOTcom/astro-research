# Mastro current-source reanalysis, 17 November 2026

> **17 November follow-up:** Three supplied UTC values and source locations required correction. The original tail was one-sided. Read the [source corrections and protocol clarification](source-corrections.md) before interpreting or reusing this first-run report.

All **141 people and 282 current chart outputs** were generated and accepted under the frozen 7.8.5 workflow. The original spreadsheet arithmetic reconciles. The current run retains the hemisphere pattern in the binary endpoint, while individual keyword vectors differ and the magnitude-based BIO reassignment diagnostic is borderline. This is a reanalysis of the known cohort using currently available inputs; historical input equivalence remains unverified.

## Primary result

| Hemisphere | Historical inversion wins | Current inversion wins | Current standard wins | Ties |
| --- | ---: | ---: | ---: | ---: |
| North | 26/73 (35.6%) | 24/73 (32.9%) | 49 | 0 |
| South | 48/68 (70.6%) | 49/68 (72.1%) | 19 | 0 |

The current South-minus-North inversion-win difference is **39.18 percentage points**. The first report used a supplementary two-sided calculation: **z=4.65262, p=0.00000327747**; Fisher's exact two-sided p=0.00000425030. A two-sided recalculation on the supplied counts gives z=4.15518, p=0.0000325028; the author’s original workbook instead uses a one-sided large-df approximation, p=0.0000162648731. All expected cells exceed five. Three people change winning condition: two toward standard in the North and one toward inversion in the South.

These fractions describe which of two keyword comparisons is higher. They are not personality-identification success rates or forecast accuracy. The two-proportion endpoint was specified by the author in advance according to his retained clarification; this report does not characterize it as selected after seeing this rerun.

## Magnitudes and conditional controls

Using inverted minus standard weighted score, the current mean paired difference is −0.011686 North and +0.022530 South. The South-minus-North mean difference is **0.034216 score units**, with a 5,000-resample percentile bootstrap interval [0.007392, 0.059625]. A separate 9,999-draw hemisphere-allocation test gives two-sided p=0.0099. Score units are the literal study normalization, with no established clinical or behavioral meaning. Hemisphere exchangeability is an assumption; this test does not remove demographic or source confounding.

The separately fixed BIO reassignment diagnostic permutes whole BIO lists over intact chart pairs **within each hemisphere**, without replacement, allowing self-assignments. It uses 1,000,000 draws, seed 20261117, exact tie half-credit and an inclusive upper tail:

| Endpoint | Exceedances | Plus-one Monte Carlo p | Interpretation |
| --- | ---: | ---: | --- |
| Difference in inversion-win fractions | 0/1,000,000 | 0.000000999999 | Beyond this simulation's observed binary tail; not p=0 |
| Difference in mean paired score | 53,275/1,000,000 | 0.05327595 | Borderline magnitude result under this conditional null |

The binary Monte Carlo resolution is approximately 0.000001 and the Wilson 95% upper bound for the sampled tail probability is approximately 0.00000384144. Zero sampled exceedances do not mean zero uncertainty. The continuous tail's Wilson interval is [0.052837, 0.053717]. This is a newly fixed diagnostic, not an exact replay of an earlier seed. It supports a narrower binary conclusion than a blanket assertion that every analysis confirms the effect.

## Preserved sensitivities

| Analysis | North inversion wins | South inversion wins | Two-sided proportion-test p |
| --- | ---: | ---: | ---: |
| Primary copied comparison BIO | 24/73 | 49/68 | 0.00000327747 |
| Separate retained BIO workbook | 24/73 | 49/68 | 0.00000327747 |
| Current raw A/AA source ratings | 18/60 | 34/46 | 0.00000738373 |
| Exclude four unresolved supplied-clock conventions | 23/72 | 46/65 | 0.00000566531 |

The BIO word multisets differ for two people. One person's scores change and no winning condition changes. Both variants preserve duplicate occurrences and original whitespace. Ratings come from currently captured/source fields; they do not establish historical source quality or eligibility. The raw current rating counts are AA80, A26, B21, C5, DD3 and XX6. No current rating is silently upgraded.

## Latitude

| Prespecified comparison | n | Pearson r | Two-sided p |
| --- | ---: | ---: | ---: |
| Original workbook latitudes and historical scores | 67 | −0.053937 | 0.664652 |
| Same original latitudes and current scores | 67 | −0.036691 | 0.768165 |
| Current captured latitudes and current scores | 68 | −0.035542 | 0.773545 |
| Original 67 identities, current latitudes and scores | 67 | −0.051673 | 0.677939 |

These results show no detected linear latitude association in this cohort. They do not establish equivalence, rule out nonlinear/boundary effects or resolve behavior near the equator. The original missing latitude stays missing in its historical field; the newly captured coordinate is used only in the labeled current analysis. Degrees of freedom are n−2. Probabilities were cross-checked through t and exact normal-null beta formulations.

## What was reproduced and what changed

The historical audit reconciles all 41,940 comparison cells, 282 global scores and 141 winner labels, with maximum floating-point error 2.22e−16. The scorer uses case-insensitive literal matching, the first matching ASTRO row, each BIO occurrence and division by the complete ASTRO row count. No stemming, synonym expansion, trimming or outcome-driven cleanup is applied. Historical/current displayed zero rows are 23/59 and remain in the denominators.

The current run contains 459 added keyword rows, 304 removed rows and 9,624 changed shared-row weights. No complete person-level standard/inverted vector pair is identical as a multiset. Thus the binary finding persists despite output differences; exact historical vector reproduction has not been achieved. The relative contributions of input records, build/corpus and other unresolved settings have not been isolated.

The frozen source policy uses numbered tutorial records for all 73 Northern people, available supplied records for 23 Southern people, and pinned official Astro-Databank reconstructions for the remaining 45 Southern people. Fourteen reconstructions retain source-review cautions. Four supplied records retain unresolved time conventions: actual observed application UTC agrees with independently calculated positions, but birth-dialog offset arithmetic differs. Their inputs were retained and the exclusion sensitivity is separate. Reconstructed records could not use that exception route. Historical input equivalence is unverified for all 141.

Every accepted pair binds raw birth fields, source metadata, standard/inverted position tables and complete trees, inversion settings and a passing capture receipt by SHA-256. Ten physical-planet longitudes independently agree within 0.01° at the recorded effective UTC. Eleven planet/node rotations are uniformly near 180° within 0.03°, with maximum observed residual 0.018333°. The January 1 birth-year reference follows the demonstrated workflow. This does not independently audit every angle, house or proprietary factor rule. Four initial pilots were independently validated and bound retrospectively with original timestamps retained. Failed/provisional attempts are excluded.

## Interpretation and next step

This completes the requested current-source calculation and arithmetic audit. It preserves a strong binary hemisphere contrast on the existing development cohort, with mixed evidence across magnitude/control definitions. No new human responses or forecasts were collected. The original BIOs were generated with knowledge of named people; this is not an untouched validation set. Tests and sensitivities are unadjusted for multiple comparisons.

Ask the author for the exact historical chart inputs, time conventions and archived build/corpus/settings needed to resolve vector differences. Then specify a genuinely new blinded validation with frozen inclusion, scoring and wrong-person controls. The retained results make Mastro a useful model for this work; they do not establish a calibrated probability that its descriptions are true.

The [machine-readable aggregate](reanalysis-aggregate.json), [operating guide](operating-guide.md), [research assessment](research-value.md) and [analysis tools](../../tools/mastro/README.md) record the reusable public work. Raw source attachments, birth records, keyword vectors and person-level reports remain private. The results reply was sent to the research collaborator on 17 November 2026. The [conditional use policy](inversion-use-policy.md) records where to test inversion and what would justify future adoption.
