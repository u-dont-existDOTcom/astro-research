# AstroHD human behavioral evaluation: frozen source-readiness and scoring-admission audit

**23 November 2026. Reused the existing source coverage logic through a versioned, provenance-safe successor. The original migrated code remains byte-identical. No new prediction score or human personality validation was performed.**

## Why this audit was necessary

The owner’s full objective is a historically grounded, non-bespoke comparison of Western astrology, Human Design and other systems against **independently observable real human behavior**. The recent [original Lilly CVII ordered stage census](lilly_cvii_1647_full_ordered_stage_coverage_20261123.md) and [1647 p535 secondary manners participation correction](lilly_cvii_1647_p535_secondary_dignified_participants_century_20261123.md) verified astronomical source conditions. They did **not** measure behavioral prediction.

Before inventing another metric, I checked the active public repository. It already includes a [source-aware Western/HD feature registry](../../tools/astrohd/reference/research/whole_chart_feature_coverage_registry_dev_20261119.json), an [original mechanics checker](../../tools/astrohd/scripts/audit_full_chart_feature_coverage.py) and its [fail-closed v02 source-provenance successor](../../tools/astrohd/scripts/audit_full_chart_feature_coverage_v02.py), an [existing behavioral observation protocol](../../tools/astrohd/reference/research/behavioral_pattern_confirmation_protocol_v01.json), a [source-conditional Western/HD contrast](../../tools/astrohd/scripts/compare_western_hd_behavior_contrast_v01.py), and a [conditional Mastro whole-person reassignment null](../../tools/mastro/reassignment_null.py).

The new work **reuses the exact immutable historical coverage semantics through a v02 fail-closed source-provenance wrapper**, rather than building a second incompatible scoring system. The [development-only input manifest](../../tools/astrohd/reference/research/astrohd_behavioral_source_readiness_profiles_20261123_v01.json) freezes the exact 19 November feature registry by SHA-256 **c3e8acddfb8948eaaf162bc7172e4b4f262aaf20a545fd7b72195f24049af30a**. The [recomputed source-only receipt](../../tools/astrohd/reference/research/astrohd_behavioral_source_readiness_receipt_20261123_v01.json) distinguishes passing mechanics from a blocked historical/behavioral model.

## Three explicitly different readiness questions

| Development-only profile | Mechanically supported | Uncertified | Actual conclusion |
|---|---:|---:|---|
| Minimal six-feature Western+HD source reference | **6/6** | 0 | **Mechanical data presence only** |
| Historical governor + human outcome source prerequisites (10 features) | **7/10** | **3** | **Cannot certify a human prediction model** |
| All 22 Western+HD registry features, an exploratory pressure test | **14/22** | **8** | **Comprehensive feature coverage absent** |

The first pass does not demonstrate that any symbolic traits predict people. The third pressure-test is **not** an adopted requirement that all valid models must use HD color/tone or every optional line; the current registry does not even enumerate Vedic, Chinese and Gene Keys input requirements. The old original century grid is a **finite 15-minute sample at one fixed research location**, not all possible continuous worldwide natal charts.

The **three direct blockers** in the 10-feature historical-governor + observable behavior profile are:

- **PTOL_EMPOWERED_MERCURY_MOON_SOUL_LORDSHIP**: original Ptolemy III.13 phase, aspects, sect, contrary testimony and full historical soul governor remain source-incomplete.
- **FULL_TIME_CONTRADICTION_AWARE_BEHAVIOR_MAP**: no frozen, non-bespoke source-to-human-observable scoring vocabulary, confirmation/contradiction handling, missing-data abstention or independent trait-cluster weights exists.
- **VALID_FINAL_SCORE_UPPER_BOUNDS_ALL_FEATURES**: no proven bound over the full required feature universe, so an apparent top chart in a partial scan cannot be certified globally best.

Under the exploratory 22-feature Western/HD source pressure test, five more source classes are uncertified: **FULL_PLANET_LONGITUDINAL_SPEED**, **PLACIDUS_PLANET_HOUSE_POSITION**, **SEVEN_PLANET_LATITUDES_DECLINATION**, **HD_PERSONALITY_DESIGN_ALL_NON_SUN_LINES**, and **HD_COLOR_TONE_BASE**.

These are **status labels in the pinned 19 November feature registry**, not proof the later 22–23 November source research never derived some of these astronomy values. For example, recent source-bound Lilly studies calculated some planetary speeds and house membership. To promote a feature, its exact source/compiler, resolution, requirements, SHA provenance and coverage must be explicitly registered and retested. Do not silently relabel a partially derived field as a fully certified continuous worldwide feature.

## Actual existing-source security/accuracy defect fixed

The preexisting feature coverage checker rejected a missing source digest **if** a feature already supplied a source ID. It did **not** reject a future developer changing an unsupported feature’s status to **ready** while its source ID remained null. This could incorrectly certify a provenance-free astrological feature as mechanically available.

The original migrated [v01 implementation](../../tools/astrohd/scripts/audit_full_chart_feature_coverage.py) and its [migration-pinned tests](../../tools/astrohd/tests/unit/test_full_chart_feature_coverage_gate.py) remain **byte-identical** to their historical SHA-256 records; editing them caused the migration-inventory regression to fail and was correctly reverted before publication. The new active [v02 fail-closed wrapper](../../tools/astrohd/scripts/audit_full_chart_feature_coverage_v02.py) requires every ready or derivable feature to carry a nonblank, registered source identifier with a nonempty manifest digest. Empty, absent, unregistered or digest-less sources fail closed. This is exercised by [new v02 source-provenance regressions](../../tools/astrohd/tests/unit/test_full_chart_feature_coverage_v02.py) and [independent profile/status regression tests](../../tools/astrohd/tests/unit/test_behavioral_source_readiness_profiles_20261123_v01.py).

**Lesson disposition:** project-specific runtime correction. The universal source-provenance principle already existed, so no new global policy was needed. The affected executable checker and its focused tests were actually changed; the report records the evidence and reason instead of merely claiming to “learn a lesson.”

## Before a genuine human validation

The next analysis must first declare **observable, falsifiable, comprehensible behaviors** and their context, source-derived prediction criteria, independent/dependent symbolic families, contradiction/abstention rules and source-supported qualifying features **before** seeing any held-out human outcomes. Its scoring weights, date/location candidate universe, score bounds, null comparison and private holdout protocol must be frozen and versioned. Only after that can separate, consented, preferably blinded participant observations be scored against appropriate cross-person reassignment and nonastrological baselines, with effect sizes, denominators and uncertainty disclosed.

The existing Mastro reassignment statistic is a precedent for **one particular conditional null**, not automatic authorization to treat that previous cohort as a new unexposed blinded AstroHD validation. Already discussed individuals and earlier exposed questionnaires are development data, not independent prospective performance evidence.

**Verified here:** 6/6 limited mechanical inputs ready, three critical missing human/governor prerequisites, an 8-item entire-registry source coverage deficit, and a repaired fail-open provenance defect. **Not verified:** full original Lilly/Ptolemy rulers, an adopted human trait model, predictive accuracy, or a unique best natal chart. The owner-wide research objective remains OPEN.

No private birth inputs, human interviews, personal chart scores, original facsimile pages or case evidence were loaded or published. All new code, synthetic tests, source profiles and audit receipts remain source-neutral public research.
