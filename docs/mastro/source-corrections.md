# Source corrections and original-protocol clarification

17 November 2026. This follow-up addresses source-input and reporting issues in
the [first current-source run](reanalysis-results.md). The original spreadsheet
arithmetic remains reproduced. The first run is preserved; it must not be
called a source-verified exact replication of the historical charts.

## Result using the original directional endpoint

| Dataset | North inversion wins | South inversion wins | One-sided p using the workbook convention |
| --- | ---: | ---: | ---: |
| Author supplied keyword vectors and comparison BIO | 26/73 | 48/68 | 1.62648730933e-05 |
| First current-source Mastro run | 24/73 | 49/68 | 1.64083114795e-06 |
| Published-source follow-up sensitivity | 24/73 | 49/68 | 1.64083114795e-06 |

There are no ties. None of the four regenerated pairs changes winning
condition relative to the first run, although three pairs' scores change.
The unchanged-input control reproduces both keyword/weight multisets exactly.
Three winner differences versus the author's original vectors remain.

Both original result sheets use `1-T.DIST(z,100000,TRUE)`. The alternative is
greater inversion-win probability in the South than in the North. The table
reproduces that large-degrees-of-freedom approximation. The conventional
one-sided normal-z probability for the follow-up is
1.63873598954e-06; it is slightly different numerically.
The previous two-sided probability was a conservative additional calculation,
not the tail used in the original workbook. To reproduce the workbook tail
from the recorded pooled z, use `scipy.stats.t.sf(z, df=100000)`.

These fractions select the higher of two keyword comparisons. They are not
personality-identification success rates or forecast accuracy.

## What was corrected and what was retained

The four source records were frozen before new keyword outcomes. Three
application UTC values were replaced with the instants implied by pinned
official Astro-Databank main entries. Two cases also needed substantive
location corrections; another has only small coordinate precision changes.
The fourth case has unchanged effective UTC and coordinates and serves as a
control. Entry used explicit UTC with zero offset, followed by independent
position and coordinate checks; the observed-app-UTC exception was unavailable.

One source main entry conflicts with its written source note. The official
rendered chart confirms the main entry's effective UTC, but the documentary
conflict and historical-input uncertainty remain visible. These are explicit
published-main-entry sensitivities, not a claim that the historical sources
have been definitively recovered.

Four pairs were freshly generated in a separate private Wine session; 137
unchanged pairs were reused. Every reused tree is byte-identical to its first
run. Exact parent inputs, completion receipts and hashes are retained, with
original generation timestamps separate from new collection-binding times.
The four original retrospectively bound pilots remain four pilots; reuse
does not relabel the other retained captures as pilots. The analysis reader
keeps strict Boolean reuse/pilot flags and all previous identity, hash,
chronology, capture and rotation gates.

## Scope of the earlier warnings

The earlier 96/45 split meant 96 supplied Mastro inputs plus 45 entries
reconstructed from ADB. It did not mean only 45 subjects exist in ADB. An
expanded, bounded alias check found no additional identity in the three
captured inventories, but a missing name in these copies does not prove
absence from another database version, folder or filter. The installed Public
database and the two separately delivered databases need to be reconciled
with one exact folder/display-name example before claiming complete original
record coverage. A single consolidated 141-chart file is not presumed to exist.

The fourteen source-note cautions describe conflicts, approximate or
ascendant-derived times, date interpretation and source changes. They are
conservative review labels, not fourteen demonstrated mismatches against the
author's historical records and not official ADB error classifications.
Published AA/A/B ratings were preserved; B is allowed by the original protocol.

The separately supplied BIO workbook and copied comparison BIO differ for two
people. One person's copied BIO contains seven extra duplicate occurrences,
changing scores but not the winning condition; the other extra occurrence
matches zero and changes no score. The separate BIO sensitivity retains all
occurrences. No replacement BIO was generated.

An Excel comparison workbook was delivered and its arithmetic was verified.
The separate reusable raw-ASTRO/BIO lookup template demonstrated during the
call has not been identified in the bounded inventory. Different sheet names
alone do not establish absence. Resolve the exact filename/link and intended
workflow rather than claim that no evaluator was provided.

## Additional diagnostics remain separate

The author's chosen endpoint is binary. Our continuous-score and BIO
reassignment checks are supplementary. On this follow-up, the fixed million
within-hemisphere reassignments give 0 binary exceedances, with plus-one
p=9.99999e-07 and resolution about 0.000001;
zero sampled exceedances are not zero uncertainty. The Wilson 95% upper bound
is 3.84144406e-06.
The continuous endpoint gives p=0.053043947.
It is not a result published as part of the original study and does not change
the calculation of its directional binary endpoint.

The full 68 current latitude comparison remains near zero:
r=-0.0388625831, two-sided p=0.753030055.
All four defined latitude comparisons are in the
[aggregate](source-corrections-aggregate.json). This does not establish a rule
for a boundary at the equator or exclude nonlinear effects.

## Correct interpretation and next step

The application gate checked a coherent calculation at its reported UTC. It
did not verify the truth of every supplied birth record. The previous headline
of complete numerical capture must not be reused as full birth-source
validation. The three corrected UTC cases, source locations and unchanged
control now have explicit pinned-source readbacks; all other historical input
equivalence remains unverified.

The binary hemisphere pattern persists in this sensitivity. Exact historical
vector equality still has not been achieved: the follow-up retains
9,477 changed shared-row weights,
424 added rows and
259 removed rows versus the supplied vectors.
Do not attribute all differences to a software build before reconciling inputs,
database copies and settings. Keep inversion under the
[conditional use policy](inversion-use-policy.md); this correction is not a
new blinded validation or calibrated confidence weight for another system.

Raw birth data, source-specific case tables, keyword vectors and correspondence
remain private. The [original report](reanalysis-results.md) and its frozen
numbers remain available with this correction attached.
