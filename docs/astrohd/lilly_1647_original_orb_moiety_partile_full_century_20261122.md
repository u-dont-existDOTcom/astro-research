# Lilly CVII, original 1647 *partile* and *platick* rules: full same-instant century fallback census

**22 November 2026.** Original-print source collation and a true 3,506,400-UTC-timestamp astronomical calculation. This is **not** a human personality prediction or final historical manners significator. It continues the [first-edition Lilly and Ptolemy I.24 collation](lilly_1647_ptolemy_i24_original_print_latitude_20261122.md) and the [original HD–Western same-UTC comparison](ptolemy_lilly_hd_same_instant_century_source_arbitration_20261122.md), without altering prior results.

## Historical correction: the original Lilly book does give planetary orbs

Previously we accurately reported that chapter CVII pp.535–536 **does not specify one numerical orb for its “joined” fallback**. But a complete direct examination of the **original 1647 printing** reveals that elsewhere Lilly **defines partile and platick aspects and gives concrete planetary orbs with explicit author variants**. This supplies genuinely original-source-informed *candidate geometry* without making the chapter CVII numerical interpretation uniquely settled.

Directly examined 1647 printed original at **p.106 (one-based scanned PDF 140)**, **p.107 (PDF 141)** and **p.110 (PDF 144)**, together with chapter CVII original pp.535–536 (PDF 569–570). Original printed source SHA-256 **2cb53e20e122ffc6e47917ba10241f6c49687cd7a4696f3b5db655a2a1aab28b**; original photographed page render hashes and exact source/read attribution are frozen in the [source-variants register](../../tools/astrohd/reference/research/lilly_cvii_original_moiety_source_variants_v01.json).

- **Partile, p.106:** Lilly characterizes a perfect aspect in matching zodiacal degrees, giving a Venus–Jupiter trine example and a one-degree Sun–Moon example. The program separately tests matching numbered degrees within signs related by the seven traditional non-bodily rays. This is a transparent *operational proxy* for that printed rule; it is **not** a newly authenticated modern arbitrary 1° angular orb, and “forcibly” still requires strength adjudication.
- **Platick, p.107:** Lilly permits aspects inside both planets' moieties, illustrated with Venus and Saturn, and supplies actual alternative planet-specific orbs. **p.110** again explicitly calculates the two half-orbs' sum for separation. The program therefore compares the angular distance to a conjunction/ray with `(orb_A + orb_B) / 2`.
- **CVII pp.535–536:** Planet in ascending sign/intercepted sign; conditional joining Moon or Mercury (especially when joined to both); ASC lord/dispositor aspect; forceful partile aspects to Moon and Mercury; essential dignities and fixed stars. This ordered *source description* does not supply a unique strength formula, an unambiguous sign-vs-quadrant-house rule, or an exclusive list of luminaries that qualify.

### Actual 1647 printed orb choices retained

| Planet | Smaller printed option | Larger printed option |
|---|---:|---:|
| Saturn | 9° | 10° |
| Jupiter | 9° | 12° |
| Mars | 7° | 7°30′ |
| Sun | 15° | 17° |
| Venus | 7° | 8° |
| Mercury | 7° | 7° |
| Moon | 12° | 12°30′ |

The two complete *bundles* are the **lower/upper componentwise envelope** of the numbers in the original book, not a claim that Lilly prescribed either one consistent bundle or that every mixed combination has been individually run. Increased joining distance can strengthen the early fallback path and reduce later-stage counts without increasing any actual astrological accuracy.

## Newly executed century census: original source-based moiety rather than invented 3° joining tolerance

The [reproduction script](../../tools/astrohd/scripts/lilly_cvii_ptolemy_same_instant_ordered_fallback_v02.py) computes all FIVE ordered **geometric/candidate** branches on all **3,506,400 original quarter-hour UTC timestamps** (1926-11-19 inclusive to 2026-11-19 exclusive), revalidating original SHA-256s for **36 planet + 36 site/angle + 36 HD index binary shards** and the previously verified exact HD structural source. All **125 near-HD-transition clock samples abstain** on HD assignments; the original 288,908 HD structural intervals remain unchanged. All three original first conditions and multiple source interpretation branches are kept:

1. A traditional planet occupies the **ascending sign**, **actual Regiomontanus first house**, or **ascending/intercepted sign** (three separate historical readings).
2. After absence at the first stage, a planet is physically **joined to Moon or Mercury** within **half the sum of the original 1647 planetary orbs**, with **external four traditional planets** versus **the broader seven-planet-body sensitivity** including Sun and mutual Moon–Mercury contact.
3. If still vacant, a separate source candidate exists when the **ASC lord's dispositor** sees the ASC lord by **zodiacal sign ray** or a **near-exact ray inside the source-table moiety**. An ASC lord disposing itself is **not** counted as seeing itself.
4. If still vacant, at least one planetary ray is **partile by numbered degree** to the **Moon OR Mercury**, versus a stricter same-planet Moon **AND** Mercury reading. The original source's “forcibly” has **not** been independently qualified.
5. All remaining timestamps fall to **essential-dignity/fixed-star/strength source arbitration, still genuinely UNRESOLVED**. The numbered stage is **not** a completed manners-significator planet assignment.

The 48 source-sensitive combinations all partition the exact same 3,506,400 UTC samples without overlapping temporal stage categories. The matrix is reproduced without human profiles in the [aggregate JSON](../../tools/astrohd/reference/research/lilly_cvii_ptolemy_same_instant_ordered_fallback_public_v02.json).

### One clearly declared comparable source branch

This example fixes: *four external nonluminary joined planets, dispositor sees by sign ray, partile Moon OR Mercury*, and varies only Lilly's original printed orbital bundle and the three historically disputed initial conditions.

| Lilly initial rule | 1647 orb bundle | Stage 1: first | Stage 2: joined | Stage 3: dispositor aspect | Stage 4: partile | Stage 5: unresolved later strength |
|---|---|---:|---:|---:|---:|---:|
| Ascendant sign | Smaller | 1,428,060 | 891,641 | 593,535 | 88,670 | 504,494 |
| Ascendant sign | Larger | 1,428,060 | 950,944 | 565,796 | 84,473 | 477,127 |
| Regiomontanus first house | Smaller | 1,409,411 | 899,101 | 568,505 | 94,312 | 535,071 |
| Regiomontanus first house | Larger | 1,409,411 | 958,391 | 542,192 | 89,895 | 506,511 |
| Ascendant or intercepted sign | Smaller | 1,516,373 | 857,574 | 562,074 | 84,961 | 485,418 |
| Ascendant or intercepted sign | Larger | 1,516,373 | 914,579 | 535,581 | 80,902 | 458,965 |

For the same ascending-sign interpretation, choosing the larger original printed moieties moves **59,303 samples** into the second-stage joined-planet candidate branch, with fewer left for the later fallbacks. This is a meaningful *historical-method sensitivity*, not new empirical support for astrology.

### Cross-check against the exact same Ptolemy/HD timestamps

A second **actual full-century computation** independently applied the previously frozen **Ptolemaic four-terms/triplicity variant-consensus, conditional four-mode Mercury/Moon common-leader test** at every sample. Its result was **exactly 4,553 timestamps** with no HD transition abstention, preserving the earlier source receipt (this **is not Ptolemy's established final soul governor**). Their Lilly fallback breakdown is:

| Lilly first rule | 1647 orb bundle | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 |
|---|---|---:|---:|---:|---:|---:|
| Ascendant sign | Smaller | 1,746 | 1,363 | 772 | 88 | 584 |
| Ascendant sign | Larger | 1,746 | 1,393 | 756 | 85 | 573 |
| Regiomontanus first house | Smaller | 1,920 | 1,280 | 617 | 105 | 631 |
| Regiomontanus first house | Larger | 1,920 | 1,316 | 599 | 105 | 613 |
| Ascendant or intercepted | Smaller | 1,865 | 1,302 | 735 | 87 | 564 |
| Ascendant or intercepted | Larger | 1,865 | 1,332 | 719 | 84 | 553 |

The first row's 4,553 Ptolemy-qualified UTC samples span **300 / 198 / 148 / 20 / 107 distinct HD intervals** in their five respective Lilly stages. Those interval counts should **not** be added: a stable HD interval can contain multiple different Western circumstances, and these are separate counts of which HD states had at least one qualifying UTC sample. The *temporal rows* (1,746 + 1,363 + 772 + 88 + 584) do sum to 4,553. This is cross-tradition structural geometry, **not two independent psychological predictions**.

## What is now resolved and what is genuinely still open

**Resolved this pass:** a missing original historical orb source was recovered from directly examined 1647 Lilly pp.106–107, 110; p106 partile versus p107 platick/moiety terminology was implemented as separate source-conditioned geometric questions; stage 1–5 calculations were actually performed over every declared UTC sample and the certified HD same-UTC join; Ptolemy 4,553 earlier source-conditioned candidates were independently re-identified at those same instants. All source-specific alternative rulership interpretations, source counts, and earlier private personal outcome evidence remain preserved.

**OPEN:** whether the CVII “joined” condition uses each exact orb table option in the same way as Lilly's general platick discussion; stage-1 sign/house semantics; meaning and qualifying strength of “forcibly”; partile minute-degree threshold; whether *and* in Moon and Mercury is conjunctive; missing exact essential-dignity and fortification arbitration; all numerically ambiguous Ptolemy fifth-mode and contrary testimonies; and, crucially, **a non-bespoke chart-to-behavior human predictor applied to the whole declared candidate universe with independent outcomes**. No historical *manners significator* or psychologically first-ranked natal chart has been computed, and arbitrary precision cannot repair missing historical rules.

The original scanned pages and original full, source-bound numeric receipts remain in authorized private research storage. This public report includes only source-safe interpretations and aggregate astronomical counts.
