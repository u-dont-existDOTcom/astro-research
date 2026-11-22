# Lilly, *Christian Astrology* III. CVII — first-house and joined-planet source audit

**22 November 2026 • Public original-text research with actual full-century Swiss calculations.** This report is NOT a prediction about any person and does not select the native's historical `significator of manners`.

## 1. What Lilly's original rules actually require

The [reproduced text of William Lilly's *Christian Astrology*, Book III, chapter CVII, pp. 535–536](https://cdn.astmd.gr/attachments/2023/11/29/williamlilly500-543.pdf) was examined by original PDF page renders. This scan is a modern reproduction/transcription, **not independently collated to the first printing of 1647**.

Lilly's source procedure has a meaningful **order**:

1. Inspect planets occupying the **Ascendant or an intercepted sign** in its house; consider each one's essential dignities and strength, and its relationship to its dispositor. If several qualify, the strongest tends to have the most lasting influence.
2. Mercury's condition matters: a planet joined to Mercury contributes its nature, qualified by proximity and fortification; other planetary relationships and the luminaries' special fortification modify the result.
3. **If no planet occupies the Ascendant**, ask which planet is *joined to the Moon or Mercury*. A planet joined to both has special consideration, but the source also states that strength and multiple planetary participation can complicate the conclusion.
4. If no planet satisfies the applicable prior conditions, consult the **lord of the Ascendant if the dispositor beholds it by aspect**; then partile aspects to the Moon or Mercury; finally which planet has most essential dignities at their places.
5. Fixed stars and planetary progressions/directions qualify the native's manners. None of this can be replaced with a one-planet rising-sign personality label.

The literal historical roles and missing requirements are registered in `tools/astrohd/reference/research/lilly_cvii_ordered_manners_fallback_source_register_v01.json`.

## 2. Why the earlier rising-sign proxy was misleading

The previous research counted any of the seven traditional planets inside the **same 30-degree zodiac sign as the Ascendant**. That was explicitly labeled a shortcut, but it is *not the first house*, which is bounded by house cusps and may contain parts of more than one zodiac sign.

We checked three separate geometric questions at every source-grid time:

- Planet in the **30° Ascendant zodiac sign** (the old proxy).
- Planet in the **Placidus first house** (a modern counterfactual, already present in the Western source cache).
- Planet in the **Regiomontanus first house**, computed anew at the original fixed location for *every* UTC sample. This house system corresponds more closely to Lilly's historical practice, as independently described in [Astrodienst's Regiomontanus house-system reference](https://www.astro.com/astrowiki/en/Regiomontanus_House_System). Regiomontanus geometry by itself still does not implement every original source condition.

The full **3,506,400 fifteen-minute UTC samples**, from 1926-11-19 inclusive to 2026-11-19 exclusive, were examined; all original **36 planetary + 36 house/sect binary shards** were rechecked against their SHA256 manifests. New Regiomontanus cusps were also checked against the original Swiss Placidus first-house and Ascendant data at **14,176 source-reference longitude comparisons**, with a maximum discrepancy of **0.00000000000765°**. That verifies the source time and ecliptic geometry alignment, not astrological predictive correctness.

| First-condition geometric classification | Samples where a classical planet is present | Percent of UTC timestamps |
| --- | ---: | ---: |
| Rising zodiac sign shortcut | **1,428,060** | **40.73%** |
| Placidus first house | **1,407,259** | **40.13%** |
| Regiomontanus first house | **1,409,411** | **40.20%** |

**Similar overall rates conceal substantial reassignment of particular charts.**

| Comparing two first-condition methods | Instants on which the methods disagree | Percent of timestamps |
| --- | ---: | ---: |
| Rising sign versus **Regiomontanus first house** | **835,699** | **23.83%** |
| Rising sign versus Placidus first house | **844,727** | **24.09%** |
| Placidus versus Regiomontanus first house | **84,004** | **2.40%** |

Regiomontanus places a planet in the first house at **408,525** times when the rising sign contains none; at another **427,174** times, a planet is in the rising sign but **outside** the Regiomontanus first house. This two-way disagreement shows that the former sign-only proxy could distort comparisons even when its global frequency looked nearly correct.

Source-neutral reproduction code:
`tools/astrohd/scripts/lilly_cvii_regiomontanus_house_century_v01.py` and the separate Placidus counterfactual `lilly_cvii_house_vs_asc_sign_placidus_diagnostic_v01.py`. The raw original Swiss/source-bound numerical receipts remain in the private authorized evidence store; only neutral aggregate values enter the public repository.

## 3. Second source branch: only after the first-house test

At **2,096,989 Regiomontanus first-house-empty sampled instants**, the first geometric stage finds no traditional planet. We then check whether at least one non-Mercury, nonluminary planet (Venus, Mars, Jupiter, Saturn) is **close in tropical longitude** to either the Moon or Mercury.

Lilly's phrase *joined* has not yet been assigned one historically authenticated numeric orb in our current source pass. The following angular distances are therefore **engineering sensitivity variants, not validated historical joining rules**.

| Maximum distance to Moon or Mercury | Joined external planet when **Regiomontanus first house is empty** | Percent of those Regiomontanus-empty instants |
| --- | ---: | ---: |
| 1° | **137,535** | **6.56%** |
| 3° | **379,725** | **18.11%** |
| 5° | **597,721** | **28.50%** |
| 10° | **1,029,627** | **49.10%** |

For transparent source-qualification sensitivity, a parallel calculation adds the Sun as a potential joining candidate, then allows a mutual Moon–Mercury joining relationship, **without automatically deciding that those broader variants have historical priority**. These variant counts and the remaining unmatched groups appear in the [source-neutral aggregate](../../tools/astrohd/reference/research/lilly_cvii_regio_house_and_joined_fallback_public_aggregate_v01.json).

A 3° candidate conjunction is not automatically historically acceptable. A planet's actual condition, strength and relationship to the two luminaries still matters. The source's later Ascendant lord/dispositor, partile-aspect and fixed-star fallbacks have **not** been implemented.

## 4. What this means for the unfinished personal-chart comparison

This is a material methodological repair, not a new winner. The owner-authorized historically filtered comparison was checked privately against the new Regiomontanus geometry. Results for specific birth times and natal charts remain private and do **not** enter this public report or create unbiased all-century standings.

A complete qualified comparison still needs to distinguish these independent original questions: (1) planet physically in the Regiomontanus first house, (2) intercepted sign and dignity, (3) multiple-planet fortification and disposition, (4) Moon/Mercury *historically joined* planets, (5) Ascendant lord and its dispositor, (6) partile Moon/Mercury aspects, (7) fixed stars and directions. The absence of source-first priority/strength means **there is no source-complete Lilly manners significator yet**.

Likewise, the concurrent Ptolemaic four-mode and double Mercury/Moon configuration calculations are distinct historical schools; their frequent candidate overlaps must not be naively multiplied into a probability of personal truth.

## 5. Reproducible and honest stopping claim

**Completed:** Original source-ordered first/second branch interpretation register; 3.5-million-source-row ascending-sign, Placidus and actual Regiomontanus first-house censuses; two engineering conjunction sensitivities tied to those different first-stage conditions; original binary source SHA256 readback; synthetic tests; source-neutral public aggregate.

**Not completed:** Original Lilly significator selection from strength, terms, dignities and intercepted houses; historically qualified joining/partile distances; fixed stars; any unique natal personality rank or controlled human predictive validation.

The arithmetic is about celestial geometry only. It should not be used as a factual psychological label or advice directing life choices; the [public guide to reflective use](reflective-practice/USING_ASTROLOGY_WISELY.md) explains how to turn symbolism into questions while retaining real-world judgment and personal autonomy.
