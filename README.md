# astro-research

The public side of an astrology research project: calculation code, method notes and source audits that contain no personal data.

## Status, 17 November 2026

The [completed Mastro current-source reanalysis](docs/mastro/reanalysis-results.md)
contains all 141 paired people and 282 current chart outputs. Inversion wins are
24/73 North and 49/68 South; historical arithmetic gives 26/73 and 48/68.
The binary hemisphere pattern persists, while historical chart inputs and exact
keyword-vector equality remain unresolved. The magnitude-based BIO reassignment
diagnostic is borderline, and no new behavioral accuracy study was run.

- [When and how to test inversion](docs/mastro/inversion-use-policy.md)
- [Mastro operating guide](docs/mastro/operating-guide.md)
- [Usefulness for our research](docs/mastro/research-value.md)
- [Aggregate results](docs/mastro/reanalysis-aggregate.json)
- [Analysis code and reproducibility](tools/mastro/README.md)
- [Current research state](state/CURRENT-STATE.md)

## What belongs here

- Calculation engines and their tests, built on the Swiss Ephemeris: Western, Hellenistic, Jyotish, Human Design, BaZi, numerology and the Maya day-count.
- Method documents: how a reading is built, how agreement between systems is counted, how predictions are sealed and scored.
- Audits of public-domain sources.
- Test designs and results that identify nobody.

## What does not

- Anyone's birth details, interview answers, readings or correspondence.
- Extracts from books that are still in copyright.

## Rules

- No personal data, ever. Test fixtures use public figures whose birth data is published, or invented data.
- Results are reported as they came out, including the ones at chance.
