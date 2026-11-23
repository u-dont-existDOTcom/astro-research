# Full finite-grid HD + Ptolemy development comparison

## Question and scope

Does the frozen [bounded retrospective rubric](bounded_behavior_comparison_20261123.md)
distinguish an exact recorded chart when the previous HD-selected candidate
shortlist is removed? This is an identifiability/development check, not a test
against independently observed people. Use the same score, weights and both
frozen evidence codings as PR36. Do not optimize the weights or select a
historical variant because it gives a preferred reference rank.

The universe is the previously verified [PR35](ptolemy_iii13_five_mode_aspect_and_sect_20261123.md)
finite UTC grid: 3,506,400 quarter-hour instants over the declared century at
one fixed research site. The HD join covers 288,908 exact structural intervals.
125 grid rows are marked unknown near HD boundaries; they are counted and not
ranked. Near-horizon sect uncertainty (5,049 rows) is handled as source
abstention, not chart exclusion. No worldwide or continuous-time rank is
claimed. A reference need not be on the quarter-hour grid; count the grid
rows above, tied with and below its exact-time score. Do not confuse
timestamps, distinct charts, birth frequencies or actual people.

All personal source material, answers, site details, per-reference
results, candidate-specific counts, and file digests of private inputs
remain in private local research storage. This public report supplies
the algorithm, scope and non-personal test evidence only.

## Reproduction method

The [runner](../../tools/astrohd/scripts/compare_full_grid_behavior_v01.py)
reuses the exact PR36 scorer and PR35 governor routines. It:

1. Checks the original three manifest digests against the PR35 public
   receipt, verifies the HD join and all 108 aligned source binary
   shards, and verifies compressed HD source hashes, continuity and the
   canonical uncompressed row digest.
2. Verifies the private evidence, original inventory, mapping and
   scorer digests and replays the prior 15-chart panel exactly under
   both evidence codings. Checks the exact reference time and same-site
   comparison, and checks all admitted HD predicates against the source
   interval containing the exact reference. No birth coordinates or
   timestamp are printed.
3. Evaluates the generic HD rubric once per unique source HD feature
   signature, reuses that value for every applicable grid row, and
   computes the direct-sign Mercury and Moon testimonies and lunar phase
   for every grid row. The two observation codings are unchanged.
4. Applies all 32 PR35 geometrical/term/triplicity/aspect-scope
   variants, each with both the original geometric and broader phase
   uncertainty envelope. At each place retain strictly determined
   governor and possible-governor scores; independent Mercury and Moon
   testimonies remain distinct. Strict, possible and conservative
   branches use the same PR36 arithmetic, including the explicit
   possibility of abstention. A near-horizon unknown does not falsely
   select a governor.
5. Counts exact score comparisons and ties in each branch; for interval
   scores counts candidates whose minimum exceeds the reference's
   maximum and candidates whose maximum reaches its minimum. These
   are outer comparison bounds, not simultaneous attainable rank
   distributions or probability intervals. Separately records
   intersection/union of strict branches where the grid candidate
   outperforms the exact reference. The equality tolerance is 1e-12.
6. Checks exact row accounting for every strict scenario, the direct
   score comparisons and both evidence profiles. Uses immutable private
   output, with source digests and reproducibility provenance.

For the complete run, use the pinned research Python environment,
with all path arguments external to the repository:

```bash
python tools/astrohd/scripts/compare_full_grid_behavior_v01.py \
 --west /private/west-grid --angles /private/site-grid \
 --hd-cache /private/hd-cache --join /private/hd-join \
 --mapping-library /private/frozen-mapping.json \
 --inventory /private/pr36-panel.json \
 --evidence /private/pr36-broad-coding.json \
 --prior-receipt /private/pr36-broad-receipt.json \
 --evidence /private/pr36-narrow-coding.json \
 --prior-receipt /private/pr36-narrow-receipt.json \
 --output /private/new-result.json
```

No global ranking claim follows from exhaustively evaluating this
partial model. It does not implement complete historical planetary
mixture, honorability, Lilly, Vedic, Chinese or Gene Keys rules.
Strict and possible/conservative outcomes are alternate model outputs,
not validated personality probabilities. Missing or unresolved source
testimony is not negative human evidence.

## Improving observations without changing the model to fit a chart

The generic mapping library already has a finite, source-frozen
question/response mapping. Before authoring more astrological traits
or questions, use its admitted 21 predicates; keep the forward-only
authority-decision exclusion intact. Preserve the distinction between
semantic retrospective evidence and exact answer tokens. For example,
valuing appreciation does not alone establish that recognition changes
both effectiveness and willingness; enduring meaningful work for
several days does not establish indefinite energy renewal; experimenting
sometimes does not imply learning primarily by trial and error. Early
recognition of a private ability and later cultivation of that ability
can coexist. None of these partial statements automatically supplies a
specific frozen response or its contradiction.

The [exact token coder](../../tools/astrohd/scripts/code_frozen_hd_observations_v01.py)
reads question IDs and exact tokens, uses the pinned library's own
support and explicit contradiction lists, returns +1/-1/null with a
trace, and never reads a chart or rank. Other/mixed responses or
unanswered items remain neutral/unknown. No free-text similarity,
fabricated tokens, or absence-of-support penalties. Apply it before
private scoring; retain the separate contextual confirmation protocol
when source responses are not exact survey tokens.

Generic next observation priorities: distinguish recognition from
effective collaboration, sustainable energy from interest-dependent
motivation, internal direction from context-dependent choices, and
investigation from learning through failed experiments; seek concrete
counterexamples and context as well as support. Use already answered
observations first. Prefer questions spanning distinct dependency
clusters rather than repeating several facets of the same profile line.
Any new coded evidence is a new version, not an edit to either PR36
receipt. Score a new fixed coding on the same complete universe;
independent blinded participant outcomes and nonastrological controls
remain necessary before claims about predictive validity.

## Executed result and limits

The complete private run finished on 23 November 2026: both frozen
evidence codings, all 64 historical/uncertainty branches, and the direct
comparison across 3,506,400 original source rows (3,506,275 ranked, 125
HD boundary abstentions). Prior panel receipts replayed exactly, all
source and score counts reconciled, and the result was read back in
private storage with its runner digest and mode 0600 verified. The
selection-biased shortlist is no longer the comparison denominator.
The exact person-specific results and source paths are intentionally
not published. The evaluation remains post-exposure, the rubric is
limited, and this milestone is not independent predictive validation.

## Tests and boundaries

Synthetic tests compare the vectorized full-grid implementation against
every scalar PR36 branch and both positive and negative observations,
including an HD-unknown row, a near-horizon row, phase boundaries, ties
and conservative intervals. The exact-token coder is separately tested
for support, explicit contradiction, neutral response, absent response,
free text and invalid ambiguous mappings.
