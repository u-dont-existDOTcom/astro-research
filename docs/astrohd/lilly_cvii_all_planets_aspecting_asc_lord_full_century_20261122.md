# Lilly CVII p.536: “If no Planet aspect him” and the century-wide alternative-planet gap

**22 November 2026 — original-source sensitivity, not a personality prediction.**

This follows the direct examination of the [1647 first printing's planetary moieties, partile aspects and previous full-century five-stage model](lilly_1647_original_orb_moiety_partile_full_century_20261122.md). The owner’s complete Ptolemy–Lilly–Human Design chart-to-observable-behavior comparison remains **OPEN**; astronomical stage labels do not establish human traits or a superior natal chart.

## Primary text: the missing third situation

I revisited William Lilly, *Christian Astrology*, original **1647 first edition**, Book III, chapter CVII, printed **p.536** (one-based scan PDF **570**). The scan identified by SHA-256 `2cb53e20e122ffc6e47917ba10241f6c49687cd7a4696f3b5db655a2a1aab28b` was visually checked; page rendering SHA-256 `4cdd11d5cf468e20f38fed7889e42f2e6298540e05f7f196c9b916e28bb57b24`. [Original first-printing archive](https://wellcomecollection.org/works/s7z7c46y); [separate typed copy as secondary corroboration](https://cdn.astmd.gr/attachments/2023/11/29/williamlilly500-543.pdf).

Lilly first makes the **Ascendant lord’s dispositor beholding it by an aspect** a condition for the third-stage manners rule. Then he writes **“If no Planet aspect him”** before turning to a planet forcibly and partilely aspecting Moon and Mercury. These two statements leave a source-relevant, previously omitted case:

> A planet other than the Ascendant lord's dispositor aspects the Ascendant lord, but the dispositor itself does not.

This is a *researcher-formulated case description*, not a quotation from Lilly. Under a broad literal reading, it fails the **specific dispositor** requirement, while the next condition, **no planet aspects the lord**, also fails. Lilly does **not** unambiguously nominate a winner for this third situation on p.536. Under the narrower retrospective interpretation, “no Planet” could mean effectively “no eligible dispositing aspect,” allowing the partile fallback. Both remain independently possible historical readings. **We do not promote the broader reading to a certain Lilly doctrine.**

## Algorithm: keep old five stages, add an unassigned source gap

The earlier source-conditioned five-stage calculation is preserved **unaltered**. The new independent source variant partitions the former last two stages as follows:

| New label | Qualification | Rule outcome |
|---|---|---|
| S1 | Planet in initial rising-sign, first-house, or intercepted-sign geometry | Candidate presence; strengths unresolved |
| S2 | With S1 empty, a planet joins Moon or Mercury | Candidate presence; original orb variants |
| S3 | With S1/S2 empty, the **dispositor** aspects Ascendant lord | Ascendant lord is a *candidate* |
| **SX** | With S1/S2 empty, another planet aspects the lord but **dispositor does not** | **Abstain: source does not assign a unique ruler** |
| S4 | With S1/S2 empty, **no other planet** aspects the lord and a planet has a candidate partile aspect to Moon/Mercury | Partile candidate, source “forcibly” still unknown |
| S5 | Same absence conditions, no selected partile | Remaining essential dignity/fixed-star conditions, not implemented |

Neither an Ascendant lord's aspect **to itself** nor an aspect automatically supplied by a different planet is treated as proof that Lilly's disposer qualification has been satisfied.

The new test separately considers **all six other classical planets** by (a) traditional **non-bodily sign or orb rays** and (b) those rays **plus source-moiety-qualified bodily conjunctions**. These are two source-conditioned interpretations, not equivalent rules. Lilly's original 1647 printed planetary orbs and source uncertainties are inherited without change. No Ptolemy I.24 latitude rule is improperly attributed to Lilly.

Across the same original `3 rising/house conditions × 2 smaller/larger printed orb envelopes × 2 joining scopes × 2 dispositor-ray readings × 2 partile conjunction readings × 2 broader all-planet aspect classes`, **96** separate six-way source-conditional partitions were computed. Each partition must cover the exact same finite UTC population, and every original five-stage count is checked against the immutable previous result.

## Actually executed 3,506,400-sample century comparison

The program examined the declared **1926-11-19 through 2026-11-19 (exclusive), quarter-hour UTC** sample grid at the original frozen fixed-location research site. All **36 original planet + 36 original angle + 36 HD-index binary shards** were SHA-256 rechecked along with the HD structural cache. The HD index retains **288,908** structural intervals and **125** root-transition-margin clock samples that cannot be assigned safely.

For a transparent example, hold constant **Ascendant sign**, **four nonluminary externally joined planets**, **dispositor beholds by sign ray**, **numbered-degree partile Moon OR Mercury**, and the **smaller** original printed orb table.

| Condition | Earlier five-stage allocation | New literal rays-only allocation | New literal rays plus bodily allocation |
|---|---:|---:|---:|
| S1 initial occupation | 1,428,060 | 1,428,060 | 1,428,060 |
| S2 Moon/Mercury joining | 891,641 | 891,641 | 891,641 |
| S3 eligible dispositor aspect | 593,535 | 593,535 | 593,535 |
| **SX ambiguous other-planet aspect** | Not recognized | **575,812** | **585,966** |
| S4 partile candidate | 88,670 | **1,769** | **867** |
| S5 final dignity candidate unresolved | 504,494 | **15,583** | **6,331** |
| **Total independent UTC timestamps** | **3,506,400** | **3,506,400** | **3,506,400** |

In the **non-bodily rays-only** interpretation, **86,901** of the earlier partile-branch timestamps and **488,911** of the earlier final-dignity timestamps become *unresolved third-case* records. This is a large consequence of source ambiguity, **not** an increase or decrease in human chart accuracy. With larger original orbs and the same Ascendant-sign/ray-only interpretation, **545,614** timestamps fall into SX; the remaining S4/S5 are **1,685 / 14,301**.

The full source-neutral aggregate, including **all three initial house/sign definitions**, both original orb envelopes, narrower/broader joining and partile readings, both all-planet aspect categories and HD structural interval coverage, is in [the versioned result JSON](../../tools/astrohd/reference/research/lilly_cvii_all_other_planets_full_century_public_v01.json).

## Exact same-UTC Ptolemy and HD cross-check

The source-conditioned four-variant Ptolemy *Mercury/Moon four-mode possible common leader* filter was independently recalculated on the same raw clock records. It matched the frozen **4,553 UTC samples**. That is a **conditional geometric candidate**, *not* Ptolemy's final soul governor.

For the narrower Lilly source example above:

| Lilly category for these same 4,553 Ptolemy-conditional timestamps | Historical previous narrow gate | New rays-only reading | New rays plus bodily reading |
|---|---:|---:|---:|
| S1 | 1,746 | 1,746 | 1,746 |
| S2 | 1,363 | 1,363 | 1,363 |
| S3 | 772 | 772 | 772 |
| **SX ambiguous other-planet aspect** | Not counted | **649** | **664** |
| S4 | 88 | **0** | **0** |
| S5 | 584 | **23** | **8** |
| **All timestamp samples** | **4,553** | **4,553** | **4,553** |

The **649** broad-literal rays-only SX records span **116 distinct certified HD structural intervals**; rays plus bodily produces **664** SX clock records spanning **121 HD intervals**. HD interval counts within each stage are **not mutually exclusive across stages**, unlike the UTC sample partition: a single HD structural state can occur at several differently classified Western timestamps. The earlier **Ptolemy strict 3° latitude-qualified 162-record subset** is a separate experiment and was **not used as an additional truth filter** in this six-stage census.

## Verification and real remaining tasks

Reproducible full-century runner: `tools/astrohd/scripts/lilly_cvii_any_planet_aspecting_asc_lord_century_v01.py`. The source adjudication is separately preserved in `tools/astrohd/reference/research/lilly_cvii_all_planet_aspect_source_adjudication_v03.json`. The runner explicitly checks earlier v02 five-stage counts for all 48 old branches and all 4,553 previous Ptolemy conditional timestamps, then checks six-stage conservation for **all 96 new branches**. All programmatic regression fixtures use **invented generic longitude samples** and a public-source-neutral aggregate; no participant source charts or interview responses are inputs.

The **actual Ascendant lord, manners significator, historical priority weights and the participant's true psychological fit remain UNSCORED**. This study does not settle which reading of “no Planet” Lilly intended, or whether conjunctions count as the relevant aspect, or the complete relative-strength and dignity conditions. The original Ptolemy III.13 qualitative/contrary testimonies, source-bound Wolf commentary and a preregistered independent human behavioral evaluation are still outstanding. If the historical rules are underdetermined, the responsible outcome is a **source-conditioned set of possibilities or abstention**, not a fabricated winning chart.

All original PDF scans, private numerical execution receipts and personal interview/birth evidence remain in the authorized local private archive. Only source methodology, public-source provenance and **anonymous aggregate astronomical results** are published.
