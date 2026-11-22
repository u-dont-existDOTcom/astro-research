# Original Lilly 1647 and Ptolemy I.24: printed-source collation and latitude-qualified century census

**22 November 2026.** Historical source methods, not psychological validation. This continues the [same-instant 1926–2026 Ptolemy/Lilly/HD comparison](ptolemy_lilly_hd_same_instant_century_source_arbitration_20261122.md), without changing its original numerical receipts.

## 1. Lilly, *Christian Astrology* III, chapter CVII: original printed book directly inspected

The initial report relied on a modern typeset reproduction. The exact **1647 first-edition original** was now independently read as page images from [Wellcome's digitized original, b30338724](https://wellcomecollection.org/works/s7z7c46y), rather than inferred from its catalogue. The inspected print is preserved under original scan SHA-256 **2cb53e20e122ffc6e47917ba10241f6c49687cd7a4696f3b5db655a2a1aab28b**. Original printed page 535 corresponds to one-based PDF page **569**; printed 536 to PDF page **570**. The original numbered pages 534 and 537 were also inspected as context. Source pages 535–536 were independently rendered and hashed; hashes and exact read modes are recorded in the [versioned original-edition register](../../tools/astrohd/reference/research/ptolemy_lilly_original_print_and_latitude_source_adjudication_v02.json). No private respondent evidence enters the source record.

### Page 535: the original printed rule really does begin with an ascending *sign*

The original 1647 print uses the exact words **“Sign ascending, or which is intercepted”** to qualify a planet as principal significator of manners. Other planets having dignity at its place participate. This is a material constraint on the earlier claim that the whole Regiomontanus first house alone replaces a simple ascending-sign check.

The same page says that a significator and its dispositor, favorable or hostile planetary aspects, strength and debility must change the judgment. A joined Mercury takes the nature of the closest and most fortified/dignified conjunction partner. Several planets in the horoscope all participate, with the more powerful influence persisting longer. A significant luminary is an additional conditional case. There is **no uniquely specified numerical single-planet dominance function** in the paragraph.

### Page 536: actual fallback order verified from the 1647 printing

The original next page says that, **if no planet is in the ascendant**, a planet joined to the Moon or Mercury is considered. Being joined to **both** receives special weight, but competing planetary strengths and differing duration still matter. If the first two stages fail, the rule turns to the **lord of the ascendant conditional on its dispositor beholding it by aspect**, then a **forceful partile aspect to Moon or Mercury**, then **the greatest essential dignities at their places**. Fixed stars of the first or second magnitude modify the selected significator; the star discussion continues on page 537.

Because the first sentence uses *sign ascending*, while later text uses *ascendant* and *horoscope*, the original printing **confirms** the textual ambiguity instead of resolving sign-only versus whole first-house scope. Preserve all three astronomical cohorts from the previous full scan:

| Source-conditioned first stage | All 3,506,400 quarter-hour timestamps |
|---|---:|
| Planet in ascendant sign | 1,428,060 |
| Planet physically in Regiomontanus first house | 1,409,411 |
| Planet in ascendant sign or fully intercepted first-house sign | 1,516,373 |

This is genuine first-edition source verification, **not a fresh 3.5-million planet-in-house calculation**. The numbers come from the already source-verified [earlier report](ptolemy_lilly_hd_same_instant_century_source_arbitration_20261122.md). The original 1647 text has no unambiguous 3° or 10° joining orb or universal numerical priority for mixed fortification and dignity. Consequently Lilly's **actual manners significator remains a set of unresolved source-dependent candidates**, not an invented winning planet.

## 2. Ptolemy: original Greek/English printing and qualified phase

The existing 1940 Loeb scan was separately inspected directly at original printed **Greek I.24 p.112** (one-based PDF 136), **English I.24 pp.113 and 115** (PDF 137, 139), **Greek III.3 p.236**, **English III.3 p.237**, and **English III.13 pp.333, 335**. Original scanned-book SHA-256 **10b44f40e47409215aa3d6c4ec2863ebc3982b81d33b4d4e5e2a065761ab7fec**. This is an edition-level Greek/English source check, not an independent complete translation of Greek manuscripts. [I.24 translation and editor's notes](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/1B%2A.html); [III.3](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3A%2A.html); [III.13](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3D%2A.html).

Book I.24 describes which body precedes/follows another along the zodiac when the interval is small. Robbins's note glosses the preceding body as more occidental; the text and notes distinguish **bodily encounters** from configurations by **rays**. Crucially, **bodily contacts require both bodies on the same side of the ecliptic**; non-bodily aspect rays do not. The original does not numerically define how near these contacts must be. The frequently repeated 15° maximum is quoted by Robbins from the anonymous commentator published by Wolf, not Ptolemy; Wolf's original commentary has not been newly collated.

Our old source grid cached tropical longitudes but **not planetary ecliptic latitudes**. It therefore gave (a) a conservative non-bodily contact count and (b) a larger conjectural count that allowed *unverified* conjunctions. The new Swiss latitude check tests that missing necessary condition instead of treating every apparent conjunction as historically acceptable.

## 3. Newly executed strict Swiss latitude checks and source comparison

The new reproducible [source-neutral engine](../../tools/astrohd/scripts/ptolemy_iii13_latitude_certified_same_instant_century_v01.py) traversed **every one of the original 3,506,400 fixed-place, 15-minute UTC timestamps** from 1926-11-19 to 2026-11-19 exclusive. It confirmed all **36 planetary + 36 location/angle shards** by original SHA-256, and re-audited all **36 HD join shards** plus the HD structural source. The old **288,908** HD structural intervals and **125 unassigned transition-margin timestamps** remain unchanged. The source-limited Ptolemy prerequisite is still the four historically contested terms/triplicity configurations producing a **4,553-timestamp same-planet consensus**; no retrospective personality feature was applied.

To check bodily configurations, **248 source-matched timestamps** needing new latitude were recalculated with **Swiss Ephemeris 2.10.03**, requiring strict Swiss source flags. Both newly used ephemeris files are separately SHA-256 pinned. The new files are not silently described as the very same binary as the old century archive; at every selectively re-evaluated planet the absolute longitude deviation was checked, with maximum observed difference **1.363×10⁻⁷ degrees**. Their body latitudes permit the same-ecliptic-side test.

| Engineering contact-nearness tolerance | Original non-bodily ray witness | Longitude-only possible (uncertified) | **Latitude-qualified witness** | Cases excluded by missing/opposite latitude | Distinct certified HD intervals |
|---|---:|---:|---:|---:|---:|
| 1° | 15 | 15 | **15** | 0 | 2 |
| 3° | 115 | 165 | **162** | 3 | 19 |
| 5° | 200 | 296 | **270** | 26 | 33 |
| 10° | 575 | 815 | **658** | 157 | 81 |
| 15° | 944 | 1,192 | **1,027** | 165 | 123 |

The 3° latitude check adds **47** valid bodily-involving cases over the prior 115 non-bodily cases, giving **162** distinct quarter-hour timestamps in **19** HD intervals. A count at any tolerance refers to **this specific nonexclusive experimental geometry within the 4,553 four-mode-consensus instants**, not to all possible Ptolemaic soul-governor paths. It is neither a probability of personality nor a first-place birth chart. The same input timestamps can satisfy multiple thresholds; these rows must never be added together.

### Which body is applying or separating?

The newly independent zodiacal-precedence witness was compared at every qualifying record with the old **15-minute relative angular velocity** proxy. In the finite qualified cohorts, their applying-versus-separating signs agreed on **all checked records** (no disagreement). At **3°**, 78 were applying and 84 separating; at **15°**, 637 applying and 390 separating. These paired results arise from lunar motion in the selected samples. It is **not evidence that historical precedence and velocity are mathematically identical at all possible astronomical events**. Exact aspect event roots, the commentator's distance rule, and qualitative power remain separate questions.

### What this does and does not accomplish

**Completed in this pass:** original 1647 Lilly printed pages 535–536 inspected; original Loeb I.24 and III.13 relevant printed Greek/English pages inspected; original-first-branch ambiguity adjudicated as unresolved and transparently versioned; full same-UTC source-hash-verified numerical scan; necessary bodily latitude qualification at every 1/3/5/10/15-degree candidate; source-labelled proxy vs zodiacal direction comparison; HD same-instant index verification; synthetic tests. Old source registers, old counts, and prior personal evidence remain untouched.

**Still unresolved:** fully original-source-defined numeric orb, exact general phase/aspect and relative testimony procedure, Lilly's strength/dispositor/partile/stellar priority including exact historical orbs, ancient manuscript/Wolf commentary variants, and a historically defensible chart-to-behavior mapping for a complete impartial universe-wide ranking. Zero human prospective prediction tests were performed, so human accuracy or a chart's unique natal #1 standing is **not established**.

All source-linked numerical receipts, scan images and archived prior private comparison evidence remain in the existing private research store. The [public aggregate](../../tools/astrohd/reference/research/ptolemy_i24_source_bound_latitude_and_phase_public_v01.json) is exclusively de-identified source-neutral counts and hashes; no person-specific birth records or responses are published.
