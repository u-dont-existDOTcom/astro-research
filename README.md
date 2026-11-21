# astro-research


## Active public home for all astrology and Human Design research

**Canonical repository: `u-dont-existDOTcom/astro-research`.** The older private
`humandesign` repository has been superseded and must not receive new work.
The generic, source-safe AstroHD comparison methods, audit code, tests and
migration inventory are now under [AstroHD research recovery](docs/astrohd/README.md).
Its separate [Gemini onboarding](docs/astrohd/GEMINI_ONBOARDING.md) tells
connected assistants to read this repository, not stale private branches.

Before committing any AstroHD work, run
`python3 scripts/verify_active_astrology_repository.py --root .`. This rejects
the old repository as an active destination, even if a historical handoff
still points to it. Original personal source records are **not public**.


The public side of an astrology research project: calculation code, method notes and source audits that contain no personal data.

## Status, 17 November 2026

The [completed Mastro current-source reanalysis](docs/mastro/reanalysis-results.md)
contains all 141 paired people and 282 current chart outputs. Inversion wins are
24/73 North and 49/68 South; historical arithmetic gives 26/73 and 48/68.
The binary hemisphere pattern persists, while historical chart inputs and exact
keyword-vector equality remain unresolved. The magnitude-based BIO reassignment
diagnostic is borderline, and no new behavioral accuracy study was run.

- [Source corrections and original-protocol clarification](docs/mastro/source-corrections.md)
- [When and how to test inversion](docs/mastro/inversion-use-policy.md)
- [Mastro operating guide](docs/mastro/operating-guide.md)
- [Usefulness for our research](docs/mastro/research-value.md)
- [Aggregate results](docs/mastro/reanalysis-aggregate.json)
- [Analysis code and reproducibility](tools/mastro/README.md)
- [Current research state](state/CURRENT-STATE.md)

A first test of the forecasting side is also complete, on one person with 41 dated events:

- [Forecast curves: the published method and a first test](docs/mastro/forecast-curves.md). By the published rule, 2 events of 41 fell near a peak of their theme where chance expects 3.2.
- [Timing tests](docs/timing-tests/README.md): ninety techniques from seven traditions against the same dates, with four controls. All at chance; a system fitted to half of the dates did worse than chance on the other half.
- [Calculation engine](engine) and the [test code](tools/timing_tests).

## What belongs here

- Calculation engines and their tests, built on the Swiss Ephemeris: Western, Hellenistic, Jyotish, Human Design, BaZi, numerology and the Maya day-count.
- Method documents: how a reading is built, how agreement between systems is counted, how predictions are sealed and scored.
- Audits of public-domain sources.
- Test designs and results that identify nobody.

## What does not

- Anyone's birth details, interview answers, readings or correspondence.
- Extracts from books that are still in copyright.
- Keyword databases or other licensed content of commercial programs.

## Rules

- No personal data, ever. Test fixtures use public figures whose birth data is published, or invented data.
- Results are reported as they came out, including the ones at chance.
