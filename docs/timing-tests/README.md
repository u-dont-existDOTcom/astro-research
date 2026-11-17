# Timing tests: which techniques find a person's important dates?

A person gives a list of dates that mattered in their life. Many traditions claim that such days stand out in the sky or in a calendar cycle. This folder scores ninety techniques from seven traditions against one list of dates, with the same test for all of them, so that they can be ranked honestly.

Nothing personal is stored here. The person's birth data and dates live in a private file that the code reads at run time. The code is in [`tools/timing_tests`](../../tools/timing_tests); `example_person.json` there is an invented person with made-up dates, for trying the code. The calculation engine is in [`engine`](../../engine).

## How to run

```
pip install pyswisseph numpy tzdata
cd tools/timing_tests
export ASTRO_EPHE=/path/to/ephe          # folder with sepl_18.se1 and semo_18.se1 from the Swiss Ephemeris
export ASTRO_PERSON=example_person.json  # or the path of a private file in the same format
python run_all.py results.json           # every technique, the family-wise check, fit-then-test
python decoys.py 300 decoys.json         # the person's chart against 300 other charts
python kinds.py kinds.json               # does a technique point to the kind of event?
```

The format of the person file is described at the top of `base.py`. Only events dated to the day belong in it.

## The four controls

1. **Shifted dates.** For each technique, a daily "activation" is computed for about fifteen years. Its mean on the person's dates is compared with its mean on the same set of dates moved together through the table, 4,000 times. Moving the dates together keeps their clustering (three events in one month stay three events in one month). Independent random dates do not, and make ordinary results look significant.
2. **The best of many.** With ninety techniques, a few will look good by luck. For every shifted set of dates the best technique is found, and the person's best technique is compared with those.
3. **Other people's charts.** The chart-based techniques are computed for 300 other birth moments (same place, born within two years of the person) and scored against the person's real dates. A technique that reads this chart should do better with this chart.
4. **Fit, then test.** The techniques are weighted by how well they matched the earlier half of the dates, and the weighted system is scored on the later half; then the other way round. This is the direct test of the idea that a system fitted to someone's past will find the rest of their life.

`kinds.py` asks a different question: with the dates fixed, does a technique name the right area of life (love, work, home, body and so on)? Its null shuffles the areas among the dates.

## The techniques

All parameters were fixed before any result was seen and none was tuned afterwards. Orbs are given as the width of a bell curve.

| Family | Techniques |
|---|---|
| Transits | Slow planets to all natal points, hard and soft aspects (1°); Saturn to Pluto to the personal points; each slow planet, the Node and Chiron on their own; slow planets to the angles; Mars; the fast planets; Jupiter and Venus "easy" days; Uranus |
| Cycles | Returns and quarter-returns of Jupiter, Saturn, the Node, Mars and Venus (2°) |
| Curves in the manner of Godbout | Counts of transit aspects within 1.32° and of transit contacts to natal midpoints within 0.35°, six variants; also his rule of the year's five highest peaks (`peak_rule` in `base.py`). Geometry only: the keyword side of Mastro is not reproduced here |
| Stations, eclipses, lunations | Stations within 1.5° of a natal point; eclipses within 3°; New and Full Moons on natal points |
| The Moon | Lunar return; the Moon on the Sun, Moon or angles; return of the birth Sun-Moon phase |
| Solar arcs | All directed points to all natal points (0.15°); with half-squares (Ebertin); to natal midpoints; the angles only |
| Secondary progressions | Progressed Moon aspects, sign changes and phase; progressed inner planets; progressed angles |
| Tertiary and minor progressions | Inner planets and Moon to natal points |
| Primary directions | Planets to the four angles by Naibod's and Ptolemy's keys; with zodiacal aspects; direct and converse |
| Profections | Transits of and to the lord of the year; the profected Ascendant and Midheaven at 30° a year |
| Zodiacal releasing | Changes of level-2 and level-3 periods from Spirit and Fortune; "peak" days |
| Firdaria | Changes of sub-period |
| Vimshottari dasha | Changes of second- and third-level periods, with 365.25-day and 360-day years |
| Human Design | Open channels completed by the day's transits; the Sun or Earth in a natal gate |
| BaZi | Officer-star days; days, months and years that clash or combine with the spouse palace; clash days; changes of luck pillar |
| Numerology | Personal day, month and year 1, 5 or 9 |
| Maya day-count | Birth day-sign, birth number, return of the birth day |
| Sky only | Any New or Full Moon; any eclipse; any station; Mercury, Venus and Mars retrograde; waxing Moon |
| Controls | Biorhythm critical days and emotional extremes; the week of the birthday; weekends |

## First run: one person, 41 dated events over fifteen years (17 November 2026)

The person supplied the dates before any of this was computed. Results are reported as they came out.

- **Single techniques.** The best was "any New or Full Moon" (z = 2.30). Among shifted sets of the same dates, 72% have a best technique at least that good. Six techniques pass z = 1.645 where chance gives 5.3. The mean z over all ninety is -0.01.
- **Both halves.** No technique did well in both the earlier and the later half of the dates. The fit of a technique in one half does not predict its fit in the other (correlation -0.13 to -0.16, depending on where the list is cut).
- **Other people's charts.** The person's own chart did not fit the dates better than 300 other charts: mean z -0.07 against +0.03 for the decoys, and 74% of decoys did at least as well. One family of twenty (tertiary and minor progressions) put the person's chart in the top 2% of decoys, which is what one family in twenty does by chance.
- **Fit, then test.** Weights fitted on the earlier dates gave z = +5.4 on those dates and -1.2 on the later ones. Fitted on the later dates: +6.6 on those and -1.4 on the earlier ones. A system that matches a person's known dates very well says nothing about their other dates.
- **Kinds of event.** Fourteen tests (profection houses, natural significators, house rulers, slow planets through the houses, dasha and firdaria lords, the relationship indicators of BaZi, Venus retrograde, Human Design): z between -1.7 and +1.4. None names the area of life better than shuffling.
- **Birth time.** Scanning the day in five-minute steps with the five angle-dependent techniques, the best time of day reaches z = 3.9, but 8% of shifted date sets have a best time at least that good, and the spike comes from one half of the dates only. The dates do not fix a birth time.
- **The invented person.** `example_person.json` (made-up birth, made-up dates) gives the same picture: fitted weights reach about +4.5 on the dates they were fitted to and fall below zero on the others.

## What this does and does not show

It shows that, for this one person, none of these techniques in these simple forms separates the important days from ordinary days, and that fitting a system to the known dates is easy and worthless as evidence.

It does not show what a skilled reader does with the same factors, and one person is one person. The dates are the ones this person chose as important, not a complete record. Days are sampled at local noon. Techniques that depend on the Ascendant or Midheaven were computed for an estimated birth time.

The test of Mastro Expert's own forecast curves, with themes fixed in advance for each event, is in [Forecast curves](../mastro/forecast-curves.md).

## Adding a technique

Write a function that takes a chart (the dictionary built by `chart_of` in `techniques.py`) and returns one number for each day of the table, higher when the technique says the day matters more. Add it to `TECHS` with a name, a family and a flag for birth-time sensitivity. Fix its parameters before running it on anyone's dates.
