# When and how to test zodiac inversion

> **Source-check correction:** Consult the [follow-up](source-corrections.md). Positions matching the application’s UTC do not establish that the UTC is the correct birth instant. Three UTC and two source-location issues were addressed in a separate, labeled sensitivity; historical input equivalence remains open.

Recorded: 17 November 2026. Status: available research option, with conditional
adoption after a new comparison. This records the owner's request to retain
the completed results so inversion can be used where it demonstrably helps.

## Evidence behind the option

The [completed current-source reanalysis](reanalysis-results.md) generated all
141 paired people and 282 Mastro Expert 7.8.5 outputs. Inversion won 49/68
Southern comparisons and 24/73 Northern comparisons. The difference was strong
under the original-style binary test. The fixed within-hemisphere BIO
reassignment diagnostic had zero binary exceedances in one million draws, but
its mean-score endpoint gave p=0.05327595. These results support retaining and
testing the option; they do not establish a universal improvement or a
72.1% personality-identification success rate.

Keep the limitations attached to every reuse: 45 Southern inputs were current
reconstructions, 14 retain source cautions, four supplied records have unresolved
clock conventions, historical vector equality remains unresolved, and the known
BIO cohort is not new blinded validation. The latitude analyses detected no
linear association; they establish no rule for tapering inversion near the
equator. The [machine-readable aggregate](reanalysis-aggregate.json) and full
methods remain the numerical reference.

## Where the option applies

| Situation | Current action | Reason |
| --- | --- | --- |
| Southern birth latitude, tropical natal keyword research | Generate both standard and inverted variants under the same frozen configuration | This is the study's candidate use; retain the standard comparator |
| Northern birth latitude | Retain standard tropical as the reference; use inversion as a labeled comparator when specified | The current Northern comparisons favored standard 49/73 |
| Exactly zero or unknown birth latitude | Leave the hemisphere decision unresolved and preserve both variants if testing | There is no validated assignment rule for that case |
| Birth close to the equator | Record the actual latitude and uncertainty; do not invent a cutoff or gradual correction | The study did not validate a boundary model |
| Relocation or current residence | Use the natal birth location for this hypothesis | The retained study concerns birth charts, not a validated relocation rule |
| Sidereal/Jyotish, Human Design, BaZi or another model | Keep that model's existing rules unless a separate protocol tests a transfer | Evidence from this Mastro tropical keyword comparison does not validate changing another system |
| Forecasts or client-facing conclusions | Do not assign a new confidence weight or automatically switch methods from these results alone | Forecast and independent personality accuracy were not tested |

The hemisphere is a test condition, not a reason to select whichever chart
looks more convincing after hearing a person's story. A Southern person can
still score better under standard, as 19/68 did in the current run.

## Reproduce a paired Mastro comparison

1. Follow the [operating guide](operating-guide.md) for build, source provenance,
   language, natal points, aspect/midpoint orbs, automatic scoring, one-level
   tree and zero cutoff. Save all returned rows, including displayed zeros.
2. Freeze one birth record and its time convention. Save an effective-UTC and
   independent-position check. Keep any source or clock-review flags visible.
3. Select ordinary tropical, clear the prior analysis, regenerate a complete
   stable one-level tree, then capture that output and its position table.
4. Apply the demonstrated user ayanamsa of 180 degrees with January 1 of the
   birth year as reference, using real entry/focus changes. Re-enter and check
   each record rather than trusting a reopened text field or checkbox message.
5. Select the inverted condition, clear the prior analysis, regenerate a
   complete stable one-level tree, then capture its output and position table.
   The reproduction checks eleven planet/node
   longitudes for a near-180-degree uniform rotation: absolute residual at most
   0.03 degrees and residual spread at most 0.002 degrees. Preserve the actual
   residuals. Do not claim that this checks every angle, house or factor rule.
6. Store the two complete trees, raw input/settings evidence and hash-bound
   capture/completion records. Clear prior analyses before regeneration.
7. Apply the same BIO input and literal scorer to both variants. The retained
   baseline uses first ASTRO matches, each BIO occurrence and the full ASTRO
   row count as denominator. Preserve the separate source-BIO sensitivity.

The ideal sign reversal is longitude `(tropical_longitude + 180) % 360`.
The demonstrated Mastro ayanamsa/reference-date workflow is only approximately
that rotation; the accepted run's maximum residual was 0.018333 degrees.
An exact mathematical rotation in a different engine is a distinct labeled
implementation, not proof of identical Mastro factors or keyword weights.
Keep the aspect/midpoint configuration fixed and inspect effective outputs.

## Decide whether it helps a future use

Use the existing within-person standard/inverted comparison as an ablation,
with a fresh evaluation set. This is a proposed acceptance process, not a
claim that the new validation has already happened:

- Define the target task first: personality matching, trait scoring or a
  particular forecast endpoint. Success on one task does not validate another.
- Freeze birth-source eligibility, handling of clock uncertainty, settings,
  mapping, endpoint, tie rules, exclusions and stopping/sample-size plan before
  seeing the new outcomes. Do not tune against this 141-person development set.
- Seal both variants before feedback. Use independent outcomes and blinded
  evaluation, with wrong-person controls and hemisphere/source-quality groups.
  Retain failures and both binary wins and score magnitudes.
- Compare both variants on the same people and outcomes. Report paired effect
  size, uncertainty and all prespecified endpoints. A tiny p-value in the old
  cohort or an attractive narrative is not the adoption criterion.
- Specify a minimum useful improvement for that task before analysis. Adopt
  only for the population/task actually supported by held-out results, then
  retain a standard comparison and monitor subsequent outcomes. An inconclusive
  or negative comparison leaves inversion as an experimental option.

The current result provides no defensible numerical forecast confidence or
automatic weight for a combined reading. Standard and inverted outputs share
inputs and many rules: their agreement is not two independent confirmations.
Any future implementation should record which variant was used and why, and
provide a reversible setting rather than overwrite the original natal data.

## Recordkeeping and communication

The full results and code are already recorded in this repository. The results
email was sent to the research collaborator on 17 November 2026, with the
qualifications and a request for exact historical chart inputs, archived
build/corpus/settings and the demonstrated evaluator. Correspondence, mail
identifiers, birth records and proprietary keyword vectors stay private.

Update this policy and the [current state](../../state/CURRENT-STATE.md) when
new independent evidence changes the recommendation. Record the new task,
population, frozen protocol and result rather than silently treating the
current known-cohort finding as broader validation.
