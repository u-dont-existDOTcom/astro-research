# Mastro Expert operating guide

Reviewed: 17 November 2026. Observed application: Mastro Expert 7.8.5 running
under Windows/Wine. The source is an owner-provided technical demonstration
recorded on 16 November 2026, with elapsed timestamps below. These are newly written
operating notes. The recording, database contents, correspondence and individual
records are held privately.

Use this guide with the [research assessment](research-value.md) and
[current state](../../state/CURRENT-STATE.md). Reviewing the demonstration and
documenting its method does not complete the chart regeneration. Exact output
equivalence between 7.8.5 and the historical study build remains to be tested.

## 1. Files, version and safe setup

The demonstrated 7.8.5 executable is an update placed in the installed Mastro
program directory, alongside the earlier 7.8.0 installation. Treat it as an
updated executable within that installation. Preserve the previous executable
and record the hash of the actual build used for research.

| Item | Role and handling |
| --- | --- |
| Installed program directory | Usually `C:\Program Files (x86)\Mastro`; a 32-bit Wine installation may use `C:\Program Files\Mastro`. Launch the intended executable from that directory. |
| Application data directory | `C:\ProgramData\Mastro Software\Mastro`. Keep database files separate from the program directory. |
| `CurrentBiography.sdf` | Supplementary biography database. In the demonstrated ordinary build, use a **copy** through the recognized `ClientDatabase.sdf` filename after backing up the existing client database. |
| `TutorialDatabase.sdf` | Supplementary tutorial database. Back up the existing tutorial file, then install a working copy in its recognized slot. |
| Original reference materials | Protocol, 141-person list, BIO-generation prompts, BIO keywords, ASTRO keywords/weights, comparisons, test results and latitude analysis. Preserve the originals. |

Close Mastro before replacing database files. Keep the received files unchanged
and back up every destination being replaced. Do not overwrite unrelated public
or personal databases. The database-slot demonstration is at 02:00:13–02:02:22.

In Wine, the data path is
`<WINEPREFIX>/drive_c/ProgramData/Mastro Software/Mastro`. Use the existing
configured prefix. For an already established 32-bit prefix, a generic launch
pattern is:

```bash
cd '<existing-prefix>/drive_c/Program Files/Mastro'
WINEPREFIX='<existing-prefix>' WINEARCH=win32 wine './<7.8.5-executable>.exe'
```

Replace the placeholders with inspected paths. This is a launch pattern, not a
new installation procedure. Confirm the version in the application window.

There is no dedicated database containing all 141 study subjects in the
demonstrated delivery, and no native automatic run across the entire list was
demonstrated (00:09:23–00:10:17). Search the Public database first, followed by
the supplementary databases. Tutorial entries can have numerical prefixes and
multiple alphabetical blocks. An unsuccessful alphabetical scan is not proof
that a record is absent.

If a record must be recreated from an external birth-data source, record its
provenance and source-quality rating. A present-day reconstruction is not a
confirmed copy of the original study input. The missing-record lookup example
is at 02:18:44–02:24:48. The subsequent inventory found supplied-database
candidates for 96 people and recovered published records for the remaining 45.
The numbered tutorial set covers all 73 Northern subjects. The current-run
selection policy uses that numbered set, the supplied Southern candidates and
explicitly marked reconstructions. Historical input equivalence remains open.

## 2. Freeze the research configuration

The natal and transit controls are separate. Apply the following settings to
the **natal** chart and analysis. A change to the middle/transit wheel does not
establish the natal configuration.

| Control | Research setting | Demonstration evidence |
| --- | --- | --- |
| Included natal bodies/points | Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, mean node, Ascendant and Midheaven | 00:13:07–00:14:00 |
| Additional objects | Lilith, Vertex, Chiron and asteroids are outside the demonstrated expert keyword set | Natal-point explanation |
| Aspect method | Natal; aspects and orbs by angle | 00:11:17–00:12:36 |
| Positions | Apparent, geocentric/Earth-centred, ecliptic | Calculation and House/Zodiac screens, approximately 01:18–01:20 |
| Houses | Koch; keep fixed even where the analysis makes little use of houses | House/Zodiac screen |
| Scoring | Automatic/default | Correction at 01:12:22–01:14:10 |
| Force analysis by word count | Unchecked | Options screen at 00:42:00 |
| Research synthesis | One-level keyword tree | 01:08:53–01:09:14 |
| Natal primary-keyword filter | Include scores **above zero** | Later correction at 01:36:17–01:37:28 |
| Language and keyword corpus | Freeze the language matching the original reference lists; those workbooks use French keywords | Walkthrough and retained comparison audit |

Enabled natal aspect orbs:

| Aspect angle | Orb |
| --- | --- |
| 0° | 10° |
| 45° | 3° |
| 60° | 6° |
| 90° | 8° |
| 120° | 8° |
| 135° | 3° |
| 180° | 10° |

The 150° quincunx and the other unselected aspect angles are disabled. The
aspect screen is visible at 00:12:00.

Natal midpoint orbs, visible at 00:12:50:

| Midpoint aspect family | Orb |
| --- | --- |
| 0° / 180° | 2° |
| 90° | 2° |
| 45° / 135° | 1.5° |
| 22.5° family | 0° |

Two corrections are especially important. The presenter initially had a private
experimental manual scoring option active, then restored automatic/default
scoring and regenerated the list. That Admin control is not an ordinary-user
requirement. Also, the cutoff of 1 shown earlier in the call was superseded by
the research-specific above-zero instruction. Removing low-scoring keywords
changes both the available matches and the evaluator's denominator.

Set the application's research cutoff to zero and preserve **every returned
row**, including a displayed score of `0.0`. Such rows occur in the historical
workbooks and the current UI. Removing them after extraction changes the
denominator. The displayed precision does not establish the hidden unrounded
value or the exact filter comparison operator.

Translate prose separately if needed. Translating keyword labels before the
reproduction changes the literal matching problem.

## 3. Generate a standard/inverted pair

Create a private run manifest with a stable subject ID, original record and
database, birth inputs and time convention, source/quality information, program
hash, language, all settings, condition, export filename and run time. Keep
identifying data out of this public repository.

For the standard condition:

1. Open the intended subject and verify the actual birth inputs.
2. Choose Tropical zodiac and check the frozen natal configuration.
3. Clear the previous interpretation/analysis in the Interpretation, Analysis
   and Synthesis panel.
4. Generate the natal aspects and one-level synthesis with the above-zero
   filter. Check that the active subject and list belong together.
5. Export the fresh list and label it `standard` in the manifest.

For the inverted condition, keep the birth inputs, locations, time, included
points, aspects, orbs and scoring settings fixed:

1. Open **Tools > Preferences > Calculation > User Ayanamsa**.
2. Use the Gregorian calendar and an ayanamsa of **180°**. Set the reference
   year for the current subject's birth year; a complete birth-date reference
   is also attempted in the demonstration.
3. Toggle **Use this Ayanamsa** off/on as needed to apply the setting.
4. In **House and Zodiac**, select Sidereal and the User ayanamsa.
5. Inspect the Sun and/or Ascendant: it should move to the opposite sign with
   essentially the same degree. Record any residual arcminute discrepancy.
6. Clear the previous analysis and regenerate the one-level synthesis.
7. Export and label the output `inverted` explicitly.

This workflow is demonstrated at 01:15:48–01:23:04, with a later reference-year
correction at 02:02:46–02:03:35. Recheck the year for **every** subject. A fixed
reference year across several decades introduces precession differences and is
an approximation to a 180° inversion. It should be a separate sensitivity test.
The demonstration sometimes retained roughly an arcminute of residual change;
inspect the actual chart rather than assuming an exact transformation applied.

Always recompute after changing the subject, zodiac or scoring configuration.
A previously displayed keyword list can otherwise remain stale.

## 4. CSV exports and provenance

The export buttons use French initials (01:25:01–01:29:20):

| Button | Meaning | Use |
| --- | --- | --- |
| A | *Avec*: with supporting astrological factors/signatures | Optional factor-level audit |
| S | *Sans*: without those factors | Keyword/score export used for the study |

These two buttons were visible in the demonstration but are absent from the
ordinary installation used for the current run. Check the actual interface.
A complete scored one-level tree can also be read through ordinary Windows
TreeView messages, preserving exact labels, weights, duplicates and node counts.
This reads the application's visible controls; it does not decode its databases.

In the English interface the file is `Trees.csv` on the Windows Desktop.
Successive exports **append** to that file (01:26:40–01:27:45). Move or rename
the existing file before beginning a clean condition or run, and inspect the
resulting record count. Check the actual output filename in other interface
languages rather than guessing a translated name.

Use either separately preserved files for each subject/condition pair or a
fully labeled manifest for a deliberately accumulated file. Another demonstrated
arrangement exports all standard charts, moves that file, then exports all
inverted charts. In every arrangement, preserve condition identity explicitly.
Hemisphere alone does not identify a chart as standard or inverted.

The original paired chart columns are standard first, inverted second in both
cohorts. Highlighting denoted the hypothesized preferred condition: standard
for the North and inverted for the South. The delivered ASTRO workbook's cohort
worksheet titles were acknowledged to be swapped (02:04:49–02:05:31). Identify
cohorts from the retained subject manifest and the 73 North / 68 South counts,
then verify identity at each join.

For reshaping, the demonstration uses Excel **Data > Text to Columns**, with
comma and `|` separators, followed by selecting keyword/score pairs or building
a pivot (02:25:34–02:34:49). The record prefix contains subject/date information;
do not parse names by assuming a fixed number of words. Inspect actual quoting,
numeric formatting and encoding before implementing a parser. Preserve the
raw CSV; perform splitting, metadata removal and reshaping on working copies.
A scripted reshaper is possible but is not implemented by this guide.

## 5. Weighted evaluator and spreadsheet comparison

Use the weighted semantic-proximity **evaluator**, not the older presence-only
**estimator** (02:37:19–02:41:25). The demonstrated workbook uses `Astro`, `BIO`,
`Feuil1`/`Sheet1`, `Analyse` and Results sheets; actual labels can vary.

1. Select the intended person's retained BIO keyword column.
2. Put that column into the working `Feuil1`/`Sheet1` input.
3. Inspect that same person's standard and inverted ASTRO columns in `Analyse`.
4. Check the list lengths, individual matches, weights and resulting global
   scores before interpreting the comparison.

The displayed global calculation is:

```text
global score = sum of matched ASTRO weights
               / number of ASTRO keyword-score records for that chart condition
```

The denominator is the chart's total exported ASTRO record count, including
repeated records as supplied. It is not the BIO list length, the number of
matches or the sum of all ASTRO weights. The denominator is visible at 02:54:00
and discussed at 02:52:42–02:55:16. The earlier spreadsheet audit reproduced
41,940 populated comparison cells, 282 global scores and 141 classifications
using the retained source conventions.

Preserve the original case-insensitive literal matching, source whitespace,
repeated BIO strings and duplicate lookup behaviour for the faithful
reproduction. Inspect the retained formulas for exact lookup/tie handling.
Cleaning, stemming, semantic similarity, new BIO descriptions or a different
denominator each defines a changed analysis; report it separately.

The original workbook's signed differences use different conventions by cohort:

| Quantity | Definition |
| --- | --- |
| Supplied North difference | Standard score minus inverted score |
| Supplied South difference | Inverted score minus standard score |
| Consistent audit delta, either cohort | Inverted score minus standard score |

Retain both raw scores and label every difference formula. A later apparent
global-score failure was resolved by replacing the wrong active BIO column
(02:58:55–03:01:26). That identity error does not explain the separate earlier
keyword-weight discrepancies.

For this reproduction, use the original BIO keyword lists. The historical
free-ChatGPT build and full generation sessions are not pinned well enough to
assume a fresh generation would reproduce those lists. New questionnaire or
chatbot-derived BIO lists belong to a separately specified experiment.

## 6. Other useful program workflows

These features are useful for exploration and interpretation, but their settings
must not silently replace the one-level research configuration.

### Two-level portrait and conversational-agent interface

The two-level tree groups traits through analogies/semantic relationships.
The portrait example uses a natal primary cutoff of 1 and a secondary minimum
of three factors (approximately 00:41–00:43). Those are portrait-demo settings.

Generate the two-level tree, open the keywords-to-conversational-agent dialog,
choose the Natal context and a response instruction, inspect the selected
keywords, select the intended agent, then use the copy/open workflow to submit
the generated prompt. A returned response can be pasted back for a report
preview. The precise provider interface may change; the call demonstrates a
copy-and-paste interface, not a tested unattended API integration. Representative
screens appear near 00:56 and 01:06.

Keep the exported scores and their settings alongside any generated portrait.
An attractive narrative is a presentation of inputs, not an independent test
of their accuracy. Obtain appropriate authorization before sending personal
chart material to any external service.

### Factors, keywords and future experiments

The optional signatures export can show supporting astrological ingredients.
Official documentation also describes queries from factors to keywords and
keywords to factors. These are useful for understanding why a trait entered
the list and for planning controlled changes to points, midpoints and orbs.

The official feature list includes event keywords, forecast curves and CSV
export for chart animation. The call does not provide a complete tested
forecasting protocol for this project. Pin the actual interface and export
schema before use, then seal time windows, predictions and outcome definitions
in advance. The keyword score reflects the expert system's weighting of its
astrological corpus; it is not established here as a calibrated probability of
a personality trait or future event.

## 7. Known discrepancies and validation gates

| Check | Current status | Action |
| --- | --- | --- |
| Historical build versus 7.8.5 | Equivalence asserted by the author; current pilot vectors differ and the full source-output comparison is in progress | Record both versions where available and compare complete keyword vectors |
| Small weight differences | Differences of 0.1 appeared at approximately 01:23–01:24 and were attributed to rounding | Verify the cause; retain the observed values |
| Larger weight difference | A standard-chart example differed by 1.3 at 01:31:26–01:32:28; an orb explanation was suggested | Compare actual inputs, orbs, signatures and build before attributing the cause |
| Another unresolved weight | A later example remained unexplained at 02:04:49–02:06:37 | Retain as an unresolved reproduction check |
| BIO/ASTRO identity | A wrong active BIO column caused a later mismatch and was corrected | Assert subject identity before comparing scores |
| Complete original inputs | Coverage audited: 96 supplied candidates and 45 marked reconstructions; historical record equivalence remains unverified | Audit every original subject and mark reconstructions |
| Evaluator workbook | All supplied workbooks inspected; none has the demonstrated interactive evaluator sheet set; verified scoring rule is implemented | Inspect retained sheets/formulas or implement the verified rule independently |
| Large-run automation | Diverse pilot verified; four isolated current-build queues are in progress | Pilot a small labeled run with restart and export checks |

Before scaling, reproduce one complete standard/inverted pair: coordinates,
keyword labels, weights, record counts, matched rows and both global scores.
Then use a small sample covering both hemispheres and the known failure modes.
Only after this validation should the full 282-output regeneration and
statistical comparison be described as completed.

Keep the primary analysis distinct from alternative filters, duplicate
policies, inversion approximations and continuous-score tests. Preserve both
positive and negative findings. Future new-subject inclusion rules, birth-source
quality thresholds, questionnaire mapping and wrong-person controls should be
fixed before scoring. The call suggests AA/A/B source quality for future work
(01:42:18–01:42:39); this is a proposal to formalize, not a completed eligibility
audit of the original cohort.

## 8. Troubleshooting checklist

| Symptom | Check |
| --- | --- |
| Supplementary database not visible | Correct application data folder, recognized database filename, app closed during replacement, working copy rather than original |
| Person apparently missing | Public and supplementary slots, numeric prefixes, multiple alphabetical blocks, spelling and provenance |
| List belongs to previous condition/person | Clear and regenerate the analysis; verify the active subject and zodiac |
| Inversion changes degrees unexpectedly | User ayanamsa, 180° setting, reference year for this subject, applied toggle and displayed chart |
| Too few keywords or a changed global score | Above-zero research filter, automatic scoring, word-count option, language and actual export record count |
| Mixed or repeated CSV outputs | Existing `Trees.csv` and append behaviour; preserved run boundaries and manifest |
| Workbook result belongs to another person | Active BIO column and the identity of both ASTRO columns |
| Residual mismatch after checks | Preserve evidence and isolate input/build/rule differences; do not force agreement by changing the reference |

## Sources and maintenance

The elapsed timestamps refer to the private technical recording dated
16 November 2026. The numerical settings were checked against visible program
screens; the evaluator normalization was also checked against the retained
independent spreadsheet audit. These notes do not distribute the underlying
recording, correspondence or proprietary keyword corpus.

General references, checked 16 November 2026:

- [Official features](https://mastroapp.com/en/features)
- [Official explanation of the expert system](https://mastroapp.com/en/about)
- [Official user manual](https://mastroapp.com/files/documentation_en.pdf)

The manual is a general reference and may describe a different build. A later
verified correction should update this guide and the current state together,
retaining the evidence and distinguishing demonstrated behaviour from proposed
automation or research.

## 9. Verified execution notes from 17 November

Use private working copies for automation. Record replacement, application
startup and build changes can write database files. Keep the delivered files
unchanged and record working-copy provenance separately.

**New-card OK can insert a record into the selected working database.** Later
sorted row indices can therefore move. Select by a unique exact display label,
then inspect the birth fields. Preserve the original inventory row and the
resolved current row. A similar name is insufficient when the exact label is
absent or duplicated.

For the user ayanamsa, setting a text property programmatically did not reliably
update the calculation. Real keyboard input followed by focus change did.
The degree field can reopen with its default value even after a prior applied
inversion. Enter and verify the intended value for each person, then check the
actual planetary rotation. Native checkbox-state messages were also unreliable
for these .NET controls; use visible state and effective output checks.

Menus, database loading and synthesis are asynchronous under Wine. Wait for the
actual dropdown or dialog to exist before acting. Directing Return to the
observed menu-popup window proved more reliable than sending it to the desktop.
Verify that the previous tree clears, regenerate the aspects, and require a
complete stable one-level tree with its declared node count. Preserve raw
captures and bind completed pairs to their input, settings and output hashes.

Independently check the chart's time convention and planetary positions.
A supplied record can contain a displayed offset that does not explain the
application's reported UTC. Preserve and investigate that disagreement. An
engine reproduction may retain the supplied record and verify the **actually
observed application UTC**, with an explicit unresolved-convention flag. This
does not establish the true or historical birth time. A reconstructed record
must still match its documented source-derived UTC and coordinates exactly;
do not search for a time that produces preferred scores.

The planetary table can round seconds to `60` without carrying them in the
display. Normalize that representation arithmetically for the independent
position check while retaining the raw text. Keep source-coordinate validation
strict. Display-format handling does not justify a wider astronomy tolerance.

The retained comparison BIO columns are the primary arithmetic input. The
separate BIO workbook is a labeled sensitivity input: preserve both rather than
silently substituting one. A successful spreadsheet reconciliation, an engine
output comparison and a fresh blinded accuracy study are separate results.
