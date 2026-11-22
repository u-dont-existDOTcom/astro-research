# Joint Human Design and Western astrology comparisons: peer-critique reconciliation

**Status:** public, source-neutral methodological correction, 22 November 2026. This is neither a new personality scorer nor an empirical validation result. A second AI's user-supplied critique prompted this review. The original private reply and personal chart/behavior evidence remain outside this public repository.

**Active repository:** `u-dont-existDOTcom/astro-research`. Work only on the active branch after running `python3 scripts/verify_active_astrology_repository.py --root .`.

## Source evidence actually checked

- Human Design's official glossary defines two sets of planetary calculations, one at birth and the other at the Sun's position **88 degrees of solar arc earlier**, rather than exactly 88 days: [Jovian Archive dictionary](https://jovianarchive.com/pages/human-design-dictionary). The BodyGraph calculates Gates, Channels, defined Centers and Type from both sets: [Jovian Archive chart method](https://jovianarchive.com/pages/get-your-human-design-chart).
- Ptolemy's *Tetrabiblos* III.13 describes soul/character judgments using Mercury, Moon, sign and planetary rulers, Moon's applications/separations, the Sun, angles and condition. It is expressly not a one-planet or dignity-count rule: [LacusCurtius reproduction, Book III.13](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/3D%2A.html).
- William Lilly's *Christian Astrology* Book III, Ch. CVII distinguishes first-house bodies, Mercury-related conjunctions, the Ascendant ruler, dispositors, aspects and dignity fallbacks when selecting a manners significator. The Ascendant ruler is not necessarily the selected significator: [Lilly text reproduced at PDFCoffee](https://pdfcoffee.com/william-lilly-christian-astrology-volume-3-pdf-free.html), Chapter CVII, pp. 534–539. The primary historical content still needs final source-collation and the rule is not numerically scored.
- Project source-reconstruction register: `tools/astrohd/reference/research/ptolemy_iii13_natal_character_claims_v1.json`, labeled `SOURCE_ADJUDICATION_INCOMPLETE_NO_WESTERN_PROFILE_SCORING` and all `automatically_scored=false`.
- Actual previously declared century `1926-11-19T00:00:00Z` to `2026-11-19T00:00:00Z` (end exclusive), according to `tools/astrohd/reference/research/whole_chart_feature_coverage_registry_dev_20261119.json`. A peer description of another window, such as 1900–2000, is **not** this completed cache.

## Four peer-review issues and dispositions

### 1. A structural HD interval is not one Western natal chart

**Agreed correction.** An old HD-only rank may identify an interval of time for which HD Type, Profile and Channels remain the same. During that interval the Ascendant, houses, angularity and sometimes sect can change. A convenient middle instant is **not** a uniquely authoritative natal chart for that interval.

The fair candidate unit is the declared time instant, scored under the exact same source conditions and time resolution used for all other instants; then aggregate over a stable interval if useful with **declared temporal weighting**. Any exact natal reference may be compared to the corresponding instant for an alternative, but a flexible interval must never receive a deliberately chosen best-case Western reading. The old HD-only shortlist is not a certified complete candidate set for a new multi-school model.

Report: per-time scores, sample lattice, full-universe coverage, boundary uncertainty and how out-of-lattice exact instants are handled. The project's fifteen-minute grid is **finite sampled coverage**, not continuous perfect coverage.

### 2. Dignity strength is not directly a character-fit score

**Agreed criticism, with an additional correction.** Essential dignity is a planetary-condition input within a particular classical system. Simply counting dignified planets does not establish that an individual has a stronger personality match, a better life, more leadership, or greater credibility.

A rival peer interpretation that then maps a domiciled Sun to an automatically status-seeking character, or a debilitated Sun to automatically anti-institutional autonomy, **reintroduces the same unsupported shortcut**. Neither claim is valid before the complete Ptolemaic ruler/condition set or Lilly manners-significator priority is resolved. The correct treatment of an uncomputed governor is `ABSTAIN/SOURCE_INCOMPLETE`, not a negative, not a positive, and not a weighted trait shortcut.

### 3. Distinct astronomy does not prove independent predictive evidence

**Qualified correction to our earlier wording.** Human Design includes a prenatal solar-arc offset and a Channel/Center graph. Traditional Western houses and angles depend on the natal horizon and local sidereal time. This creates **partly nonidentical astronomical features**, which may be informative in a structural uniqueness study. A categorical claim that the maps contain no additional astronomical information would be false.

However, the maps still share the same time, natal planetary positions and astronomical constraints. Their empirical dependence is not settled by noting the prenatal offset or by simply stating that both use planets. Measure feature redundancy/association across the **same declared time-weighted candidate distribution** and reveal the empirical outcome. An informative joint intersection of rare labels is **not** automatically an independently calibrated chance probability, let alone proof that either label predicts people. No arbitrary product-of-probabilities calculation.

A useful optional diagnostic is the conditional frequency of Western conditions within each full HD state, or a predeclared information/redundancy statistic over the actual time distribution. It is diagnostic astronomy, not human validation.

### 4. A newly frozen source model remains exposed to past target information

**Agreed, but not a new completion blocker.** Once designers have seen the reference profile and actual chart, later source adjudication and weight selection remain potentially contaminated even if their revised scores are frozen before the next rerun. Track the knowledge exposure and preserve the original versioned results.

The project's bounded deliverable may still finish with a correctly labeled **descriptive development comparison**, **rank conditional on an explicit source rubric**, or **no defensible score**. The separate claim of predictive advantage over chart-free baselines requires independent untouched participants, chart-blind response capture, and a frozen model before seeing those participants' outcomes. This does **not** mean a descriptive report should be blocked indefinitely pending cohort recruitment.

## Ranking/publication claim ladder

| Proposed statement | Required evidence and permitted label |
|---|---|
| The source describes a symbolism / trait | Exact source rule + school + qualifying conditions + dissent; `SOURCE_CLAIM` |
| The chart seems to match a known person | Context-labeled self-report or observation; `POST_EXPOSURE_DESCRIPTIVE` |
| A chart ranks first under an arbitrary frozen source rubric | Completed declared candidate universe + precise rule implementation + ties/bounds + exposure disclosure; `DEVELOPMENT_MODEL_RANK` |
| The charts have rare combined astronomical geometry | Explicit denominator/time weighting + full (or bounded) feature coverage + selection caveat; `STRUCTURAL_RARITY_ONLY` |
| Two systems contribute independent evidence for personality | New untouched human outcomes, incremental advantage over the same baseline and a correctly modeled dependency; `PROSPECTIVE_INCREMENTAL_VALIDITY` only once verified |
| Astrology predicts people better than chance | Preregistered chart-blind holdout, confidence intervals, appropriate null and nonastrological baselines; `EMPIRICALLY_VALIDATED` only after evaluation |

## Next executable work, without scope inflation

1. Complete/resolve original source priority rules for Ptolemy and Lilly, or explicitly report missing/unscorable conditions.
2. Evaluate complete HD and Western source features at identical instants. Split or sample each old HD interval consistently; do not choose the most favorable rising sign after seeing answers.
3. Measure structural redundancy and prevalence over the same time-weighted candidate frame **if the astronomy can actually be reproduced**. Do not estimate from a selected shortlist.
4. Preserve uncertainty and post-exposure contamination. Report the source-conditioned comparative result even if no winner can be justified; reserve claims about real predictive validity for a separate untouched cohort.

**Negative results and unsupported source claims are acceptable stopping outcomes.** This is an interpretation and reproducibility clarification; it adds no new mandatory empirical-validation hurdle to the currently authorized descriptive comparison.
