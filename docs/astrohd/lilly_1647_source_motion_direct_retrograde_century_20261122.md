# Lilly 1647 direct/retrograde strength: original 3.5-million-time source-bound motion census

**22 November 2026.** Completed original-source-limited motion component, **not** complete accidental fortitude, a historical manners ruler or human prediction.

## Original historical rule and missing data

William Lilly, *Christian Astrology* first printing (1647), **p.115**, lists **direct planetary motion +4** among accidental fortitudes and **retrogradation −5** among accidental debilities. The printed wording expressly excludes scoring direct motion as a special bonus for **Sun and Moon**, which are normally direct. Original 1647 PDF scan SHA-256 `2cb53e20e122ffc6e47917ba10241f6c49687cd7a4696f3b5db655a2a1aab28b`; actual p.115 image hash `fe75468d8eaf129a1f643d6d652455e81eb95b0aedd3016091e3ce7c204e4aab`. The original Wellcome scan is retained in private research storage; [catalogue](https://wellcomecollection.org/works/s7z7c46y).

The previously verified original celestial longitude cache contained **seven classic geocentric longitudes and an exact Mercury longitude-speed field**. Full five nonluminary speed data were **not** precomputed. The new reproducible script reads Mercury's original exact signed speed and reconstructs the signed longitude derivative of **Venus, Mars, Jupiter and Saturn** from centered **15-minute, 2-tick finite differences**. A wrap-safe circular 360° difference and adjacent shard edge rows preserve the original clock, and the absolute first/last timestamps abstain. Near stations, a numerical bound is needed; **0.01, 0.02 and 0.05 degrees per day are deliberately conservative engineering uncertainties, not source-authored Lilly thresholds**.

Two separately SHA-pinned Swiss Ephemeris 2.10.03 planetary files independently checked speed and original longitude at **1,620 deterministic controls** spread across all 36 input shards. The largest source longitude difference was **1.79 × 10⁻⁶ degrees**. Absolute differences between some finite estimates and source exact/reference speeds reached approximately **0.0116 degrees/day**; no Mercury direct/retrograde sign disagreements occurred when both estimates lay outside the chosen station tolerance. Such numerical discrepancies and station uncertainty are **not** redefined as evidence of astrological effect.

## Actual source-hash-verified full sampled-century result

The computation traversed the **original fixed research-place quarter-hour UTC grid** from 1926-11-19 inclusive to 2026-11-19 exclusive: exactly **3,506,400 timestamps**. Original **36 Western planet +36 site/angle +36 HD join shard** SHA-256 evidence and **288,908 independent HD structural intervals** were audited again; original **125 near-HD-transition sample IDs abstained**. This is a finite sampled grid at one source-neutral research location, **not every worldwide birthplace or continuous time**. No participant chart, private interview, psychological target or outcome rating was used.

At the middle **0.02° per day engineering uncertainty threshold**:

| Planet | Clearly direct samples | Clearly retrograde samples | Near-station or edge abstentions |
|---|---:|---:|---:|
| Mercury (original exact source speed) | **2,822,770** | **662,552** | **21,078** |
| Venus | **3,245,489** | **248,704** | **12,207** |
| Mars | **3,164,298** | **314,680** | **27,422** |
| Jupiter | **2,344,807** | **945,094** | **216,499** |
| Saturn | **2,009,399** | **1,066,348** | **430,653** |

Each row partitions the same 3,506,400 timestamps; retrograde counts **must not be added across planets** as though they refer to disjoint people. The source contains all three engineering-station threshold variants and the count of distinct HD structural intervals containing clear retrograde samples.

The original conditional Ptolemy four-terms/triplicity-mode Mercury/Moon common-candidate witness still totals **4,553** original UTC samples. Under the 0.02°/day classification, the separate intersections with Mercury, Venus, Mars, Jupiter and Saturn retrogradation are respectively **553 / 418 / 214 / 1,048 / 1,169**. Those are overlapping astronomical classifications and do **not** establish Ptolemy's full soul governor or correlate with any actual human behavior.

## Reproducibility, limits and next work

The direct computational method is in `tools/astrohd/scripts/lilly_1647_source_direct_retro_motion_century_v01.py`. The [anonymous aggregate](../../tools/astrohd/reference/research/lilly_1647_direct_retrograde_full_century_public_v01.json) records proof hashes, 1,620 independent controls, per-planet/threshold category partitions, the frozen HD and Ptolemy overlap, and explicit human-validity disclaimers. The reproduction script accepts only original source-neutral astronomical manifests, HD join, separately hash-pinned ephemeris and a versioned output path; it rejects unverified input shards or alternative ephemeris fallback.

**Only source-conditional direct/retrograde motion is now calculated.** “Swift” versus “slow” motion, angularity and whole-planet fortitude, essential reception and debilities, Sun beams, aspects, nodes, fixed stars and competing qualitative testimony remain **OPEN**. A precise direction of motion does not resolve the practical meaning, weight or predictive accuracy of the ancient astrological interpretation. The [completion-claim audit](../../state/COMPLETION-CLAIM-AUDIT-20261122.md) prevents this completed source-limited computation from being mistaken for a finished historical ruler or any empirically validated natal personality rank.

Private original receipt v02, previous exploratory v01 receipt, original ephemeris binaries and all personal natal/interview evidence remain in authorized private storage. The public repository contains only method, tests and source-neutral aggregate counts.
