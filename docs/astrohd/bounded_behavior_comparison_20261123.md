# Bounded HD + Ptolemy III.13 behavior comparison v01 (23 November 2026)

**Status:** actual bounded retrospective comparison executed; not preregistered,
blinded, calibrated, independently validated, source-complete, or century-wide.
The source rules are applied uniformly to every chart, not adjusted to improve
one chart's ranking. The observation coding is nevertheless post-exposure and
must not be represented as a genuinely untouched non-bespoke validation.
No personal input, candidate row, private observation, individual score,
individual rank, or personal data digest is published here.

## Scope and existing sources

- Reuse the exact 27 frozen predicates from generic HD V4/V3.2-symbolic-v1
  (mapping SHA256 3424672432f7f071ec90ef9ddce52a67ff6794911e92b1a1e04f079262ea6200,
  already pinned by the existing identifiability audit). The mapping is an
  externally supplied local dependency, not copied from a private repository.
  The existing forward admission policy excludes authority predictions:
  exclude the entire AUTHORITY_DECISION dependency cluster and any authority
  predicate, including the emotional-wave proxy, leaving 21 generic predicates.
- Reuse [the PR35 historical source alternatives](ptolemy_iii13_five_mode_aspect_and_sect_20261123.md)
  for each place independently, including ties, possible fifth geometric claim,
  unknown phase envelope and near-horizon abstention. Keep the previous
  [Ptolemy source register](../../tools/astrohd/reference/research/ptolemy_iii13_natal_character_claims_v1.json)
  unchanged; its original source completeness and automatic scoring gates
  remain unpassed. This is a separate experimental conditional scoring mode.
- The existing private frozen comparison panel is a reference and fourteen
  previously HD-selected competing chart intervals at their recorded midpoints.
  It is not the full universe, not random, not a representative cohort, not
  independent people and not continuous-time coverage. All 15 were scored
  under each of 64 source/uncertainty scenarios, with an additional direct
  sign branch, twice (broader and narrower observation coding).
- No claim is made that Lilly, Vedic, Chinese, Gene Keys or the unimplemented
  Ptolemaic planetary mixture/strength rules have been scored. No common
  Mercury/Moon governor prerequisite is imposed.

## Generic observation codebook (source-limited hypotheses)

Ptolemy III.13, Robbins 1940, pp. 333–335 (faculties and sign qualities),
361–363 (lunar illumination), as recorded in the source register. The
following are narrow modern observable operationalizations, not verbatim
translations, exclusive personality types or equivalent modern psychometrics.

| Key | Candidate testimony | What would constitute a relevant observable |
|---|---|---|
| mercury_solstitial | Cancer/Capricorn sign | Recurrent inquiry, exploration of explanations or invention in reasoning |
| mercury_fixed | Taurus/Leo/Scorpio/Aquarius | Sustains reasoned conclusions or intellectual commitments over time |
| mercury_bicorporeal | Gemini/Virgo/Sagittarius/Pisces | Changes reasoning approaches in response to changing circumstances |
| moon_solstitial | Cancer/Capricorn sign | Recurrent outward interpersonal initiative in sensory/affective circumstances |
| moon_fixed | Taurus/Leo/Scorpio/Aquarius | Sustained affective commitments or steadiness in response to setbacks |
| moon_bicorporeal | Gemini/Virgo/Sagittarius/Pisces | Changes affective expectations or responses with experiences/circumstances |
| moon_waxing_frankness | Increasing illumination | Recurrently expresses feelings/intentions openly |
| moon_waning_caution | Decreasing illumination | Recurrently deliberates or exercises caution in affective circumstances |

Aries/Libra are equinoctial: abstain on the above sign mapping, rather than
relabel them solstitial. At new/full phase boundaries abstain on phase.
The three sign-mode observations are not assumed mutually exclusive. The
model admits only confirmed, contextual evidence for the named behavior (+1),
explicit relevant counterevidence (-1), or unknown (null). An absent chart
carrier, an unasked question or a mixed/unconfirmed behavior is not a negative
human observation. HD source statements retain the original frozen mapping
IDs; retrospective semantic compatibility is not exact survey-token equivalence.
The code accepts an explicit signed evidence mapping, not free-text inferences
or unconfirmed assistant descriptions. Private evidence codings and rationale
are kept separately and fixed before calculation; a narrower sensitivity
omits contestable proxies. Never select whichever coding maximizes reference rank.

## Arithmetic and bounds

For each HD dependency cluster, divide signed active observed contributions
by its number of observed mappings, including inactive carriers in that
denominator. Average across observed clusters; do not reward several overlapping
profile observations as several independent clusters. A missing observation or
carrier gives no score credit; the trace distinguishes missing from negative.
If no known observation exists the numerical credit is zero (no evidence),
not a finding of absence. Coverage and active observation counts are retained.

For Western testimony, direct sign and provisional governor sign are
alternative interpretations of III.13 (not a claim that sign alone is the
complete historic method). Each place gets its own signed observed score.
Compute all 32 original PR35 cross-product source variants, each with two
uncertainty regimes: aspect/bodily claim or broader unknown-phase fifth claim.
Possible governor sets use the same conservative interval algebra as PR35;
their members may not be simultaneously realizable. The strict-only branch
abstains on a non-unique governor; the possible-set branch ranges over the
candidate scores. Own domicile, fixed sect, and preceding-square contrary
witnesses are reported without converting them into invented behavior weights.
The conservative branch allows every testimony to abstain because of
unresolved qualifications (including the separate lunar illumination testimony);
it is an envelope for this limited scoring model, **not** a bound on a complete
historical personality score, which could contain other or reversed testimonies.

Experimental equal-weight aggregation: lunar score = (Moon sign + lunar
phase)/2; Western = (Mercury + lunar score)/2; joint = (HD + Western)/2.
Missing testimony earns no positive credit, and the arithmetic weights are
fixed, transparent, neither fitted nor historically asserted. The scores are
not probabilities, calibrated percent fit, or evidence of accuracy; systems
have different observation coverage. HD-only, Western-only, and joint direct
ranks are retained. In every governor scenario, retain the per-place scores,
candidate sets, qualification flags, strict-only joint ranking, and possible
and conservative joint rank envelopes. Rank lower bound = one plus the
number of competitors whose minimum exceeds the chart's maximum. Rank upper
bound = one plus the number of competitors whose maximum equals or exceeds the
chart's minimum (worst tie ordering); intervals may be loose. Direct ranks
use competition rank and explicit tie count. No tie-break by date or duration.

## Execution, safety and next step

Run from the canonical public checkout, with the research Python environment
and local private input paths **outside** the checkout:

```bash
python tools/astrohd/scripts/compare_bounded_behavior_v01.py \
  --inventory /private/frozen-panel.json \
  --mapping-library /private/frozen-generic-mapping.json \
  --evidence /private/frozen-observation-coding.json \
  --output /private/new-immutable-result.json
```

The inventory must contain distinct comparison units, each with a common
chart-midpoint schema (HD structure and seven classical planetary longitudes,
solar altitude). Observation JSON contains inventory_sha256, hd and western
maps of keys to +1/-1/null. The private output records source file digests,
the scorer digest, traces and all scenario ranks. Output is create-only and
mode 0600 under ordinary Unix file creation. No personal result is added to
Git. Synthetic tests cover negative observations, dependency caps, unknown
carriers, authority exclusions, equinoctial/phase boundaries, separate
candidate sets, all 64 branches and rank ties.

The original 15-unit panel was actually scored, not just audited for
astronomical coverage. The narrowed coding is less discriminating; uncertainty
in historical qualification prevents a unique robust rank. This finding does
not establish predictive accuracy. Next prioritize stronger *observable*
coverage (including explicit counterevidence and an independent blinded
holdout), apply the frozen rubric without ranking-driven retuning to a
declared complete candidate universe, and compare with nonastrological/null
controls. Additional source work should be limited to rules whose admission
could improve the comparison. The root objective remains OPEN.
