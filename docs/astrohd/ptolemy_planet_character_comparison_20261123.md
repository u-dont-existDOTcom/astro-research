# Ptolemy III.13 — source-wide planetary character experiment

23 November 2026. Continues the [full finite-grid comparison](full_grid_behavior_comparison_20261123.md)
with a planet-identity alternative to the previous sign-modality rubric.
The owner goal remains a fair source-grounded full-universe multi-system
comparison and independently tested human behavior, not an improved rank
for any pre-exposed recorded chart.

## Original text and source scope

I read the complete III.13 character inquiry, paragraphs 23–64 of the
digitized [Robbins Loeb translation (1940), pp. 333–363](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3D%2A.html).
This is direct English-witness reading, not new original Greek manuscript
collation. It builds on the [previous source register](../../tools/astrohd/reference/research/ptolemy_iii13_natal_character_claims_v1.json)
and [PR35 separate-place uncertainty calculation](ptolemy_iii13_five_mode_aspect_and_sect_20261123.md).

A material distinction, explicitly explained by Robbins's note 151:
the chapter describes five solitary planetary characters (Mercury, Venus,
Mars, Jupiter and Saturn) and all ten two-planet alliances. The luminaries
make additional contributions. Thus seven astronomical candidate bodies
do not supply seven distinct solitary character lists in this chapter.
If a source alternative selects Sun or Moon, retain that result but
abstain on its absent character list. Do not silently select a runner-up.
The section on diseases of the soul (III.14) is not a source for the
behavioral score.

The character descriptions distinguish more effective/honorable planetary
conditions from opposing ones; they are not two lists of morally good and
bad traits. A strong malefic can have source-ascribed undesirable traits.
The source also changes descriptions under mixtures and contrary testimony.
A single ruler of both places receives particular emphasis, but is not an
exclusive admission rule for the character inquiry. No complete historical
numerical condition or alliance adjudicator has been established.

## Source-to-observable mapping

The [versioned operational map](../../tools/astrohd/reference/research/ptolemy_iii13_planet_character_operational_v01.json)
contains all 15 configurations and both source position clauses for each:
37 modern observable constructs and 155 explicitly mapped signed directions.
36 constructs have at least one mapped direction; aspiration is defined but
not given a direction because the historical achievement/status distinction
is unresolved. If observed, it remains a zero-credit denominator item in
this frozen version, uniformly for every candidate.
Each configuration has source passage locators, a rational/sensory split
by construct, and distinct condition alternatives. Examples of selected
non-verbatim operationalizations:

| Source configuration | Sample dignified-position hypothesis | Sample opposing-position hypothesis |
|---|---|---|
| Saturn | sustained effort, stable purpose | solitude, sustained effort |
| Jupiter | intellectual discussion, giving to others | lavish spending |
| Mars | directing others, rapid anger | rapid anger, rash decisions |
| Venus | aesthetic interests, social warmth | fault criticism, fearful hesitation |
| Mercury | inquiry, innovation | hasty decisions, changes of mind |
| Jupiter–Mercury | study, effective communication | verbosity, boasting |
| Saturn–Venus | contemplative practice, self-restraint | criticism, deception |
| Mars–Mercury | invention, detailed work | changeable decisions, deception |

These examples are not exhaustive lists or validated psychometric
constructs. Some semantic conversions, such as sustained reflection
from philosophical interests, remain proxies rather than identical
measurements. The selected vocabulary is bounded to behavior that
can in principle be assessed using general patterns, context and
counterexamples. It intentionally does not translate historical
pathologizing, sexuality, identity, social-status prejudices, criminal
labels, health or supernatural claims into chart-based assertions.
Source descriptors omitted from this limited map are unknown/unscored,
not negative predictions.

All map directions are fixed independently of candidate scores. The
generic source file is hash-bound to the previous registry and contains
no participant-specific weights, observations, identity or chart inputs.
The retrospective participant coding remains post-exposure. Therefore
this is a uniform common-rule development experiment, not a prospectively
preregistered or blinded non-bespoke empirical validation. Do not
select a favorable branch or alter a source direction after seeing
its rank.

## Scoring alternatives

The [runner](../../tools/astrohd/scripts/compare_planet_character_century_v01.py)
reuses the PR35 interval-governor routines and PR37 verified grid and
HD state scorer. It calculates two distinct exploratory source models:

* **Separate places:** use the solitary character table of Mercury-place
  candidate for rational testimony and that of Moon-place candidate for
  sensory/affective testimony. This extends the source's solitary
  descriptions to a place-specific proxy; it does not claim a separate
  planet alone rules the entire soul. Four condition arms retain each
  place's dignified/opposite alternatives independently.
* **Assumed alliance:** if both strict candidate bodies belong to the
  five character planets, read the pair character table (or diagonal
  solitary table for identical bodies), scoring its rational and
  sensory/affective parts separately. Two condition arms use a common
  dignified or opposite clause. Two selected bodies do **not** prove
  Ptolemy's historical alliance; this is expressly hypothetical.
  An unknown candidate or luminary gives no alliance credit.

For a source-mapped behavior with a signed observation, contribution =
mapped direction times observation (+1 or -1). Missing observations or
source-unmentioned constructs contribute zero evidence, not negative
evidence. The denominator within each faculty is the fixed number of
known observations in its entire vocabulary, identical for every
planet/configuration. Each source construct contributes at most once per
faculty; the approach retains coverage rather than normalizing only
successful matches. Source clauses with different numbers of operationalized
traits can still differ in score opportunity, so the result is not a
calibrated measure of likelihood or comparable personality probabilities.

Western score = mean of rational Mercury and sensory Moon scores; joint
score = mean of Western and the unchanged generic HD score. Fixed equal
weights are an experimental convention, not an ancient prescription.
This is a planet-character **alternative**, not an additive score atop the
PR37 sign/illumination rubric: preserve the old outputs unchanged and
avoid double-crediting correlated source testimony. A future integrated
model should cap dependence and explicitly retain lunar/Solar modifying
conditions.

For every one of the 64 historical candidate scenarios, evaluate all six
fixed condition arms and separate conservative score intervals for the
two models. Bounds allow any possible body, either source condition,
and independent abstention of each faculty. The possible-candidate
Cartesian product and separate faculty extrema are outer relaxations;
jointly attainable values may be narrower. No calculation treats a
dignified/contrary witness as definitive honorability. The condition
envelope is a bound on this rubric, not on complete historical doctrine.
Strict unresolved candidates contribute zero evidence rather than a
fabricated planet. An HD boundary-unknown row is kept in coverage but
not ranked, as in PR37.

## Reproduction

Supply the existing verified fixed-site century source caches, exact
generic mapping and original private chart inventory. The runner
requires one immutable private observational file per unchanged HD
observation version. The file records the public map SHA, paired
HD evidence SHA, domain observations (+1/-1/null), and separate
private semantic coding rationale. Freeze coding before calculation;
unknowns remain explicit. All private inputs and outputs must be
outside the public checkout.

```bash
python tools/astrohd/scripts/compare_planet_character_century_v01.py \
 --west /private/west-grid --angles /private/site-grid \
 --hd-cache /private/hd-cache --join /private/hd-join \
 --mapping-library /private/frozen-hd-mapping.json \
 --inventory /private/frozen-panel.json \
 --hd-evidence /private/previous-hd-coding.json \
 --evidence /private/planet-observations.json \
 --output /private/new-immutable-result.json
```

Repeat both evidence arguments to include a second frozen coding.
The runner verifies source grid digests, source row continuity,
exact same-site reference and all admitted HD predicates, 108
aligned planetary/site/HD binary shards and all HD structural
shards. Each exact comparison counts higher, equal and lower grid
timestamps. Each interval comparison counts certainly-higher and
could-equal-or-exceed cases. An exact-time reference need not be
on the sampled grid. The units are timestamps at one fixed site,
not independent people. All 64 x 6 fixed arms and uncertainty
envelopes are retained privately; never report the best arm alone
as a historical or empirical result.

## Additional source-condition pilot (selected panel only)

The [partial-condition runner](../../tools/astrohd/scripts/compare_planet_character_condition_pilot_v01.py)
applies existing own-domicile, fixed-sect and opposite-fixed-sect
preceding-square witnesses uniformly to every chart in the frozen 15-unit
development panel. Two declared policy sensitivities retain different
uncertainty boundaries: familiarity-only uses a dignified-clause proxy
only when own domicile or fixed-sect agreement is present and the
contrary-square witness absent; fixed-sect contrast additionally uses
the opposing clause when fixed sect is opposite and own domicile absent.
Contrary-square witnesses cause abstention under both, rather than
being converted to a decisive adverse judgment. Missing governor,
variable sect without familiarity, and luminary character-list
absence are preserved as abstentions. These are intentionally incomplete
operational proxies, not Ptolemy's final rule of planetary condition.

The actual 15-unit private pilot ran all 64 historical scenarios under
both condition policies (128 comparisons). Its ranks are a separate,
selection-limited development result, never substituted for full-grid
results or used to choose the preferred condition rule. Both source
condition proxies should be tested across the same full grid if
retained, with further independently sourced planetary familiarity
and overcoming criteria as needed. Individual ranks remain private.

## Executed outcome

The corrected runner completed the entire 3,506,400-row source grid with 125 HD boundary abstentions and all 64 historical alternatives, six fixed condition arms (384 per coding), and two conservative envelopes. Both frozen retrospective evidence versions were evaluated; exact and bounded rank counts reconciled for every arm. Private results were read back with their runner SHA and restrictive file permissions verified. The source-specific identity expansion has mixed discrimination effects relative to the previous sign model. There is no uniform improvement or unique robust first place; the unresolved-condition envelopes can remove the incremental Western discrimination. This is a substantive development outcome, not a justification for selecting the best-fitting branch. Individual scores and ranks are not public. The source-conditioned 15-unit pilot was also executed; it is not a full-grid condition-adjudicated result.

## Tests and decision boundary

Synthetic tests enforce five solitary/ten mixed source profiles and
both clauses, signed directions, rejection of unregistered observations,
fixed denominators, luminary and near-horizon abstentions, separate
faculty computations, conditional pair lookup, and exhaustive containment
of possible-body and condition combinations within the envelopes.

The first full-grid computation reached all timestamps, but its final accounting rejected the receipt: a substring filter for score-envelope metric names also matched the historical phase_envelope scenario tag. The corrected version parses the final arm and metric fields instead, validates both exact and bounded counts, and adds a regression requiring both historical tags. No score, source mapping, observation coding or candidate-selection policy was changed by the repair.

The appropriate comparison is discrimination against the previous
frozen sign-only developmental baseline and the uncertainty sensitivity,
not choosing whichever branch puts the reference first. Independent
held-out people with frozen observations and a nonastrological or
whole-person reassignment null remain necessary for accuracy claims.
No person-specific evidence, scores, private file locations or
birth metadata are permitted in the public repository.
