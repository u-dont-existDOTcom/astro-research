# Forecast curves: the published method and a first test

Vincent Godbout, a former teacher of mathematics and statistics in Quebec, built the expert system inside the astrology program Mastro (written by François Rouleau, begun in 2009). This note collects what he has published about how it works, in our own words, and records how we put its forecasting side to a test. Material from private conversations is not here.

The [operating guide](operating-guide.md) covers the natal settings and keyword exports used for the 141-person reanalysis. This document covers the other half of the program, the forecast curves, which that work left untested.

## 1. How the expert system reads a chart

- **Sources.** Interpretations of 5,148 combined factors (planets in signs and planets in aspect), condensed from 25 modern authors, plus Ebertin's 858 midpoint pictures turned into keywords. Descriptors are nouns, for consistency.
- **Keywords and signatures.** Every keyword carries a "signature": the list of chart factors whose interpretations contain it. A chart's keyword list comes from crossing the meanings of each planet in its sign with each planet in aspect.
- **Scoring by rarity.** A keyword is scored by how improbable it is that so many of its factors turn up in one chart, corrected for how common the keyword is in the whole corpus. He reports that simply counting repetitions does not work. All factors weigh the same and an orb is either inside or outside; there are no hand-set weights.
- **What is left out.** Houses and rulers are not used, because the authors agree too little about them. The Ascendant and Midheaven count only when the birth time is known.
- **Orbs.** For the natal portrait he recommends generous orbs (conjunction and opposition 10°, trine and square 8°, sextile 6°, half-squares 3°; midpoints 1.5° to 2°).

## 2. Tests of the natal portrait that he has published

- **Automated matching with biographies.** Keyword lists from the charts of celebrities are compared with keyword lists drawn from their portraits in a Le Monde directory, by a "semantic proximity" score; every chart is compared with every biography. A first version in 2017 used 42 people. The 2022 version used 73 of the 100 portraits: the right biography came first for 6 people where chance gives 1, and within the first eight for 21 where chance gives 8. The same procedure with the sidereal zodiac gave nothing.
- **Other samples** reported in interviews and news pieces: profiles from Le Senne's characterology, and Gaston Berger's questionnaire on 85 people.
- **Southern hemisphere (2025, with Hubert Brun).** For 68 notable people born in the south and 73 born in the north, the keyword portrait was computed with the usual zodiac and with the zodiac turned by 180°. The turned zodiac matched the published descriptions better for 48 of the 68 southerners and 26 of the 73 northerners.

Points to keep in mind when reading these. The matching studies use a binomial calculation in which every person has the same chance of ranking first; a control that shuffles the charts among the people would show whether long or generic biographies attract matches. The 73 were chosen from 100, and the way the trait lists were drawn from the biographies matters. None of this has been replicated independently yet, which he says himself.

## 3. Forecast curves

This is the part we tested.

- **What a curve is.** For a chosen person and period, the program computes a transit chart at regular steps and, for each of about seventy event themes (love, marriage, separation, work, travel, surgery, mourning and so on), a score from the expert system. Each theme gives one curve over time. He works with two charts a day. A set of curves is limited to 640 steps, so a full year needs steps of 14 hours.
- **Orbs.** 1.32° for aspects and 0.35° for midpoints. These two numbers were found by trying every value from 0° to 2° in steps of a thousandth of a degree and keeping the ones that gave the most "successes" on a few hundred cases. They are therefore fitted values, and any test of the curves needs events that were not part of that search.
- **The rule of thumb.** Events tend to fall from 4 days before a peak to 3 days after it, and only the five highest peaks of a year mean much. He gives the chance rate as roughly one in ten (five windows of seven days in a year).
- **What the Maximums table lists.** The program's table gives, for each theme, the highest points of the curve by rank. Two or three neighbouring steps of the same peak often fill several ranks, so "the five highest" can be two or three separate moments.
- **Other techniques.** He judges progressions and solar arc directions less interesting than plain transits for this purpose.
- **Evidence published so far.** Worked examples: a "mourning" curve for a singer that peaks a few days after two deaths in her family, a "success" curve for a king that peaks two days before his accession. No statistical test of the curves has been published.

## 4. Birth times

- Large collections of birth data contain too many births on the hour and half-hour, which shows that recorded times were rounded. In research he drops rounded times.
- The natal portrait changes slowly with the birth time (ten minutes changes little); forecasting is more sensitive.
- The Mastro team wrote in 2018 that the portraits are precise enough to correct a birth time without using life events, and a technique for finding the birth hour was said to be in development in 2022. No method or test has been published.

## 5. Our test of the curves

The rule in section 3 is precise enough to check on one person, if three things are done.

1. **Fix the theme first.** For every dated event, one theme is chosen from the program's list before any curve is looked at, and the list is sealed.
2. **Use the published rule as it stands.** One set of curves per calendar year (1 January to 1 January, 14-hour steps, transits, the person's birth coordinates, midpoints on, orbs at 100%). An event is a hit if it falls from 4 days before to 3 days after one of the five highest points listed for its theme in its year.
3. **Compute chance, do not assume it.** For every event, chance is the share of that year's days lying inside the windows of its theme. Two further controls: shuffle the themes among the same dates (does the *theme* matter?), and count how many of all the themes peak around the dates compared with random days of the same years (do the *dates* matter?).

[`tools/mastro/forecast_rule_test.py`](../../tools/mastro/forecast_rule_test.py) does the counting. It needs two private files: the Maximums tables and the list of events with their themes.

### How the tables were obtained

Mastro Expert 7.8.5 (the build used for the reanalysis) was driven on the isolated virtual display. The program stores its curves in a protected database and has no export for the Maximums table, and no printer was available, so each year's table was photographed in two screens and read by OCR three times at different sizes, keeping the majority reading of every cell. Each table holds 71 themes and seven ranks.

### First run: one person, 41 dated events, 2012 to 2026

The person supplied the dates long before the curves were computed. Themes were sealed first (SHA-256 of the sealed list: `3feef732124867866c34034d2a1b5ee165d2bd741873ca9c95b23b2826070da1`).

- **The published rule.** 2 of the 41 events fell inside a window of one of the five highest points of their theme. Chance, computed from the actual windows, expects 3.2 (a rate of 7.9% per event, a little under the quoted one in ten because neighbouring steps of one peak share ranks). The probability of 2 or more by chance is 0.85.
- **Looser readings of the rule.** Seven highest points: 4 hits where chance expects 4.4. Five separate peaks, with points within three days merged: 4 hits where chance expects 3.9.
- **Any theme of the event's area of life** (every love and partnership theme for a relationship event, and so on): 13 hits where chance expects 17.5. With the alternate areas of each event added: 24 hits where chance expects 24.8.
- **Does the theme matter?** Shuffling the themes among the same dates gives 3.3 hits on average, and 87% of shuffles do at least as well as the real pairing.
- **Do the dates matter?** Over all 71 themes, 262 theme windows fall on the person's dates where random days of the same years give 255; 35% of random sets reach 262.

On this person the curves do not find the events, by the published rule or by its looser readings.

Limits. This is one person. The birth time is an estimate, and the curves use the natal angles and the Moon. The themes were chosen by us, in advance; Vincent might choose differently. The table of one of the fifteen years (three events, all misses) had been seen before the themes were sealed. The Maximums tables were read by OCR; the three readings disagreed on 22 of 7,455 cells and the majority was kept.

## 6. Questions for Vincent

1. In your own tests of the curves, which settings were used (step, place, the list of themes), and does "the five highest peaks" mean five rows of the Maximums table or five separate peaks?
2. The orbs of 1.32° and 0.35° were chosen to maximise successes. Has the rule been checked on events that were not part of that search, with the theme fixed in advance?
3. Is there a way to export a curve as numbers? With the values of every step, a test needs no screenshots and can use the whole curve instead of five points.
4. For the matching studies, would you run the control in which the charts are shuffled among the people?

## Sources

- Vincent Godbout, "Using Expert Systems in Astrological Research", NCGR Research Journal, winter 2018-19, pages 86 to 92: https://ncgrastrology.org/wp-content/uploads/publications/research-journal/NCGR_Research_Journal-2018-19_Winter.pdf
- Vincent Godbout, "Comparison of Astrological Charts with Biographies using Automated Matching", NCGR Research Journal, winter 2022, pages 46 to 53: https://ncgrastrology.org/wp-content/uploads/publications/research-journal/NCGR_Research_Journal-2022-Winter.pdf
- Press release on the 2017 study: https://www.24-7pressrelease.com/press-release/442931/are-astrological-birth-charts-really-revealing
- A presentation of the Mastro expert system hosted by the Dutch society NVWOA (March 2021): https://www.nvwoa.nl/txt/20210320-Mastro.pdf
- Mastro user guide, version 7.8 (July 2026), chapters on forecast curves and on animation.
- Mastro blog, "Utiliser Mastro Expert pour la rectification" (2018): https://mastroapp.com/fr/blog/utiliser-mastro-expert-pour-la-rectification
- Vincent Godbout and Hubert Brun, "Faut-il inverser le zodiaque tropical dans l'hémisphère Sud ?", L'Écho d'Hermès, autumn 2025, pages 24 to 32.
- Interview by Jean-François Gérault (2021): http://jeanfrancoisgerault.blogspot.com/2021/02/interview-du-quebecois-vincent-godbout.html
- List of his articles in Correlation: https://correlationjournal.com/tag/vincent-godbout/
- "Initiation à l'astrologie", a series of fifteen broadcasts (2022) in which he presents the program.
