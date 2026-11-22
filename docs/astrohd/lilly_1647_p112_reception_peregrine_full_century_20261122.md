# Lilly 1647: mutual reception, peregrine and natal essential debilities across the full sampled century

**22 November 2026. Original-first-edition source verification plus an actual 3,506,400-timestamp source-bound calculation. Historical comparison only, not psychological validation.**

## Original source examined

The original **1647 first printing** of William Lilly, *Christian Astrology*, printed **page 112** (PDF page 146), was visually inspected as the primary evidence. Direct source-page SHA-256: **37455e68b9eedcbd46f5819b42a9282eac70b570b351f1bf304b81c94546cda1**. The original printed p.115 fortitudes/debilities table (PDF 149), direct page SHA-256 **fe75468d8eaf129a1f643d6d652455e81eb95b0aedd3016091e3ce7c204e4aab**, was checked again. Both come from the preserved original scanned-book SHA-256 **2cb53e20e122ffc6e47917ba10241f6c49687cd7a4696f3b5db655a2a1aab28b**, [Wellcome source catalogue](https://wellcomecollection.org/works/s7z7c46y). Original scanned pages stay in the private archive.

**Lilly defines reception in p.112** between two planets that are **significators of a question or matter** and occupy one another's dignities. His original example is the Sun in Aries and Mars in Leo for mutual reception by house. The page also discusses reception through other essential dignities. This distinction matters: zodiacal longitudes may establish a **geometrically potential** reciprocal condition, but **do not themselves prove both planets qualify as significators of the subject**.

The same original p.112 defines a planet as **peregrine when it has no essential dignity in the degrees it occupies**. Lilly's example distinguishes Saturn at 10° Aries (peregrine) from Saturn at 27° or 28° Aries (dignified by its own term). The first-print p.115 assigns **+5** for domicile **or** mutual reception by house; **+4** for exaltation **or** reception by exaltation; detriment **−5**, fall **−4**, peregrine **−5**. The program does not grant a double domicile or exaltation bonus just because reciprocal reception is also geometrically present.

### Four explicitly different policies, crossed with three printed terms witnesses

The new source-neutral program calculates each classical planet's essential position at **its own natal zodiacal longitude**. This is **not the same** as the earlier Lilly CVII last-fallback calculation of which planet has most dignity **at Mercury and Moon's locations**. It retains:

1. Five intrinsic positive essential components only: domicile, exaltation, day/night triplicity, term and face.
2. The positives plus detriment, fall and **intrinsic** peregrine penalties; no reception awarded.
3. The above with **potential strict mutual domicile/exaltation reception**, which is provisionally permitted to clear the peregrine penalty.
4. The same possible reception, but peregrine is assessed using **intrinsic essential dignity alone**, so the penalty can remain.

These are four **researcher-declared conditional interpretations**, not four original Lilly algorithms. Mixed-kind reception and reception through term/face/triplicity, and the requirement that the bodies be valid *significators for the matter*, remain unimplemented. All four policies are run under **three independent printed term tables**: original Lilly 1647 p.104, Robbins 1940 Loeb Ptolemaic, and Robbins 1940 Loeb Egyptian. **A strict unique highest-score body is only a partial-source numerical candidate**, not an actual Lilly manners ruler or validated trait.

## Full source-bound century calculation

The reproducible [engine](../../tools/astrohd/scripts/lilly_1647_reception_peregrine_essential_body_century_v01.py) was executed on the original **3,506,400 fifteen-minute UTC timestamps** (1926-11-19 inclusive to 2026-11-19 exclusive), at **one fixed research location**. Every one of the original **36 planet + 36 site/angle + 36 HD-index binary shards** was checked by SHA-256. The original independently certified **288,908 HD structural intervals** and **125 near-transition unknown HD timestamps** were preserved. An additional **5,049 samples** abstain from all unique rulership claims because solar altitude was in the defined ±0.1° day/night sect uncertainty zone.

Under the **Lilly 1647 original printed terms**, the candidate counts are:

| Mathematical natal-body source policy | Unique highest-scoring candidate timestamps |
|---|---:|
| Five positive essential dignities alone | **2,939,689** |
| Positive dignities plus detriment, fall and peregrine, no reception | **2,996,946** |
| Plus geometric mutual house/exaltation reception, presumed to clear peregrine | **2,902,984** |
| Same geometric reception, but intrinsic peregrine retained | **3,018,047** |

Among sampled instants where **both compared methods produce a single candidate**, adding the three original negative debilities changes that candidate at **59,222 of 2,916,441** timestamps (about **2.0%**). Adding the potential reciprocal-reception rule to the penalty model changes the candidate at **396,693 of 2,767,742** (about **14.3%**). This is **historical-method sensitivity**, not evidence of any actual psychological effect.

| Printed terms source | Positive-only to penalized: candidate changes | Penalized to potential-reception candidate changes |
|---|---:|---:|
| Lilly 1647 | **59,222** | **396,693** |
| Loeb Ptolemaic 1940 | 56,990 | 395,418 |
| Loeb Egyptian 1940 | 55,585 | 390,302 |

Across **all 12 model/source combinations**, **1,998,041** sampled instants have the **same strictly unique candidate**, spanning **170,375 HD structural intervals**. Of the previously verified **4,553 conditional Ptolemaic Mercury/Moon four-mode shared-leader** instants, **3,711** have one same candidate in all 12 natal essential variants; **2,986** of those agree with the conditional Ptolemaic body and **725** disagree. The methods use many of the same celestial coordinates, so this **is not independent validation**.

The full [source-neutral aggregate](../../tools/astrohd/reference/research/lilly_1647_mutual_reception_peregrine_body_source_century_public_v01.json) also gives each planet's detriment/fall/peregrine counts and possible geometrical reciprocal receptions, with no individual natal time record. For example, Saturn is intrinsically peregrine at **1,748,192** sample times under the original 1647 terms. Allowing reception to clear the status reduces that flag to **1,417,605**. The p.112 original Saturn examples were encoded as regression tests.

## Remaining source and predictive boundaries

The [exact first-print source/variant register](../../tools/astrohd/reference/research/lilly_1647_p112_reception_peregrine_source_register_v01.json) records the direct page hashes, historical quotations, source-conditioned assumptions and unresolved reception/sect decisions. Other verified computations of Lily's last Mercury/Moon dignity fallback, house-only accidental fortitude, direct/retrograde motion, and conditional Ptolemy four-mode aspects **remain independent**; they are not silently summed into a total ruler.

**Not yet done:** identifying the historically qualified *significators of the matter* before assigning reception, integrating mixed-significator/sect/original fortitude and all accidental dimensions with tie handling, completing Ptolemy III.13's phase/aspect and contrary testimony, or preregistering and validating a human behavioral mapping over the candidate universe. The original owner's research objective stays **OPEN**, and no unique natal #1 or predictive accuracy was established.

All original source PDFs, source execution receipts, case histories, birth times and participant interviews remain in the separate authorized **private** store. Only independently reproducible methods, invented-data tests, and aggregate anonymous astronomical counts are in the public research repository.
