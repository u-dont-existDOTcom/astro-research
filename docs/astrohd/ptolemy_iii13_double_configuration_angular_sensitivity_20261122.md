# Ptolemy III.13: a ruler must also be configured, not merely shared

**22 November 2026 — source-first research, not human prediction.** This is an explicit follow-up to the [four-mode census](ptolemy_1940_terms_four_mode_census_20261122.md). The original question remains a historically faithful chart-to-behavior comparison; a low or high astronomical frequency is **not** a match to anyone's personality.

## What the primary source actually says, and what we previously omitted

The original [*Tetrabiblos* III.13, Loeb Robbins edition, pp.333–339](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3D%2A.html) gives Mercury's condition for the rational/intellectual soul and the Moon, together with planets in the Moon's *applications and separations*, for its sensory counterpart. Later it gives special emphasis to a planet qualifying both places: its relation to **Mercury by an aspect** and to **the Moon by separation or application**, with the planet's own dignity, sect, angularity and contrary testimonies also affecting the original interpretation.

**Correction to any overreading of the earlier census:** The previous four-mode code was mathematically valid as a census of *possible common planetary rulership*, but it deliberately did **not** establish a completed Ptolemaic governor. Merely finding the same planet among the lords of Mercury's and the Moon's signs is inadequate to infer that the more specific III.13 configuration is active. The source says this configuration is especially significant; it does not make the new screen a necessary condition for all Ptolemaic character readings.

[Book I §24](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/1B%2A.html) describes applications/separations as bodily conjunctions or traditional rays, qualified by proximity and, for bodily encounters, the two bodies' ecliptic-latitude sides. The original passage says the interval must be small, but does not supply a definitive numeric boundary. The editor's note **129** reports that an anonymous commentator, as printed by Wolf, mentioned **15°** as a maximum and that the later Ashmand translation invoked distinct planetary orbs. These are **distinct commentators**, NOT numeric instructions directly authored by Ptolemy. The new scan therefore treats **1°, 3°, 5°, 10°, and 15° as separate research thresholds**, with none accepted as the authentic original threshold.

Full exact source conditions and editorial separation are in the [versioned source register](../../tools/astrohd/reference/research/ptolemy_iii13_dual_relation_source_contract_v01.json).

## New complete century-wide astronomical computation

The source-neutral program `tools/astrohd/scripts/ptolemy_iii13_mercury_lunar_dual_aspect_century_v01.py` applies the following separately specified *geometric subset* across **3,506,400 quarter-hour UTC samples** (1926-11-19 inclusive to 2026-11-19 exclusive):

- Begin with the frozen four-mode source candidates (domicile, exaltation, day/night triplicity **including co-rulers**, and the source-edition-specific Ptolemaic or Egyptian terms).
- Identify a **single external nonluminary planet** among Venus, Mars, Jupiter or Saturn that is a common candidate and geometrically close to **a traditional Mercury aspect and a traditional Moon aspect at the same sampled instant**. The exclusion of Mercury's self-relation is explicit and leaves some source interpretations unevaluated; it is **not** evidence against them.
- Look at both lunar *approaching* and *receding* geometry by comparing adjacent original quarter-hour ephemeris longitudes. This is only an approximation to the source's application/separation classification, not a substitute for historic exact event timing and angular qualification.
- Count **non-conjunction aspect witnesses separately** from a wider possible set that includes unverified bodily conjunctions. The original century cache retains longitudes but not the latitude information required to accept every bodily contact.
- Abstain for 5,049 source-grid near-horizon sect-uncertain instants (±0.1° solar altitude) and the 72 first/last shard points lacking symmetric 15-minute motion differences. Source-neutrally screened interior instants: **3,501,279**.
- Count any qualifying external candidate **once per time instant** for each threshold, not one extra point per planet. Several candidates can be present simultaneously.

All **36 original Western planetary shards and 36 original fixed-location solar-altitude shards** were rehashed, size checked and aligned by original sample index. The raw source-bound census is preserved privately; the [public aggregate](../../tools/astrohd/reference/research/ptolemy_iii13_dual_configuration_angular_sensitivity_public_v01.json) contains no identifiable birth input.

## What changes under different proximity choices?

| Engineering threshold applied to **both** Mercury–planet and Moon–planet aspects | Ptolemaic terms: non-conjunction witnesses | Share of all UTC samples | Egyptian terms: non-conjunction witnesses | Source-choice disagreement on individual eligibility |
|---|---:|---:|---:|---:|
| 1° | **5,294** | **0.151%** | 4,881 | 2,143 |
| 3° | **46,006** | **1.312%** | 45,176 | 17,374 |
| 5° | **123,192** | **3.513%** | 120,306 | 43,254 |
| 10° | **463,182** | **13.210%** | 449,595 | 148,953 |
| 15° | **968,436** | **27.619%** | 943,172 | 292,086 |

**Important:** these rates are not historical Ptolemaic prediction probabilities or scientifically validated personality frequencies. They are the prevalence of a **particular modern geometrical filter** among the same sampled astronomical times. In particular, the 15° row is not a known Ptolemaic cut-off; it happens to coincide numerically with a later commentator's reported maximum, an assertion whose original Greek commentary has not been independently collated in this pass.

To illustrate missing latitude information, at the 3° threshold the **possible** count increases from 46,006 non-conjunction witnesses to **68,998** if conjunctions are allowed *without checking their latitude*. At 15°, it increases from 968,436 to **1,402,899**. The larger counts must not be treated as valid Ptolemaic contacts: the original source specifically demands an ecliptic-side qualification for bodily conjunctions.

The narrower filter does eliminate much of the apparent universality of the prior 'shared ruler' condition (85.75%), but **the astronomical frequency can be made much smaller or larger by selecting the threshold**. Selecting it after seeing a particular person's chart would be an invalid way to establish an independently impressive match.

### Applying versus separating — what can we currently say?

For each non-conjunction source-neutral record, the signed angular difference from the nearest exact traditional aspect is combined with the *sampled relative angular velocity* of the Moon and candidate external planet. If the angular distance is shrinking, the record carries an **approaching** witness; if it is expanding, a **receding** witness. At 3° these occurred at **22,979 and 23,338 sampled instants**, respectively, within the Ptolemaic table screen; they can overlap because different qualifying planets can be approaching and receding at the same time.

This numerical proxy was checked at nine arbitrary nonpersonal century timestamps for four planets (36 comparisons) against a **separately hash-pinned** strict-SWIEPH source: all relative-motion signs agreed and the largest difference was about **0.000075 degrees/day**. The source files are numerically close but their binary ephemeris hashes are NOT identical; original cache and modern control program remain provenance-distinct.

### Why this still cannot rank chart personalities

The source texts additionally require distinguishing between a planet's own strength and accidental participation in an aspect; sect, angles, orientation, bodily latitude, contrary planetary testimony, other natal indicators and source-valid timing. The new screen does not decide which celestial object is the original **actual soul governor**; it counts only a clearly defined *restricted subset of possible dual configurations*. A missing witness under this subset does **not** disprove an alternative interpretation, and a present witness does **not** establish any actual personality claim.

A historically faithful complete scorer needs an original-source-backed policy for all such qualifications, including alternative manuscript/source schools, **before** computing a ranking for any known person. If the original text does not determine one unique procedure, the correct deliverable is a **set of source-conditioned results** or a defended **no uniquely determined chart ranking**, not a bespoke winning interpretation. Meaningful predictive validity would require a separate blind human study and a chart-free comparator; even a completed post-exposure chart ranking is development evidence only.

## Reproducibility and next research step

- Original primary text and note-layer claims: `tools/astrohd/reference/research/ptolemy_iii13_dual_relation_source_contract_v01.json`.
- Numerical source-bound public aggregate: `tools/astrohd/reference/research/ptolemy_iii13_dual_configuration_angular_sensitivity_public_v01.json`.
- Reproduction engine, independent synthetic edge/boundary tests: `tools/astrohd/scripts/ptolemy_iii13_mercury_lunar_dual_aspect_century_v01.py` and `tools/astrohd/tests/unit/test_ptolemy_dual_aspect_century_v01.py`.
- Original records, owner-specific natal comparison and ephemeris binaries: retained solely in the authorized private research store; not part of the published payload.

**Next executable work:** resolve latitude-sensitive conjunction cases against exact Swiss source where worth computing; compare I.24's original Greek/English with the surviving Wolf commentator to establish what the reported 15° means; finish source-licensed governor strength/contrary testimony and Lilly CVII manners-significator priorities in parallel. The owner's desired full century combined HD–Western personality ranking remains **OPEN**.
