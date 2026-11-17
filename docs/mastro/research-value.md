# How Mastro Expert can help this project

Updated: 17 November 2026. The current research run freezes Mastro Expert 7.8.5.
Its strongest demonstrated value is as an auditable model for reproduction and
exploration. Personality and forecast accuracy remain untested by this project.

## Main value

Mastro turns an astrological chart into explicit keyword lists with numerical
scores and, optionally, the factors supporting each keyword. That gives the
project a model whose outputs can be frozen, compared and challenged. A
language model can then be used for separate tasks such as explaining a list;
the exported Mastro scores remain available for direct analysis.

The retained workbooks' literal weighted comparison has been independently
reconciled: 41,940 comparison cells, 282 global scores and 141 classifications.
The current run can extract complete scored one-level trees from the ordinary
7.8.5 interface, preserving labels, weights, duplicate rows and displayed zeros.
That supports direct comparisons with the retained vectors. Exact historical
vector parity has not been achieved or claimed.

This makes Mastro useful for exposing and testing a defined set of rules. It
currently adds no demonstrated predictive weight to a combined reading or a
consilience claim. Agreement with another astrological model still needs
independent outcome evidence and controls for shared inputs and rules.

## Uses and evidence status

| Use | Value for the project | Evidence status and next check |
| --- | --- | --- |
| Reproduce the 141-person zodiac-inversion study | Immediate priority. Current output can be compared directly with the retained historical vectors. | The frozen 7.8.5 run uses the full 141-person input manifest. All 141 pairs passed guarded capture acceptance and the full analysis ran; see the current-source results. Historical arithmetic is verified, while historical vector and birth-input equivalence remain unresolved. |
| Compare personality questionnaires with candidate charts | Promising baseline for blinded matching: export each candidate's keyword vector, freeze a scoring rule and compare against independent responses. | Proposed application. Questionnaire-to-keyword mapping, candidate generation, leakage controls and held-out accuracy have not been validated. |
| Test individual astrological ingredients | Controlled comparisons can examine midpoints, included points, aspect orbs and zodiac choice while holding other inputs fixed. | Relevant controls were demonstrated. Each ablation needs verified settings and fresh exports. |
| Explain why a score appeared | Optional factor signatures and the documented factor/keyword query tools can help trace an output to its astrological ingredients. | These features support auditing. A complete independent audit of the rule corpus and scoring implementation has not been completed. |
| Test forecasts prospectively | Event keywords and forecast curves could support predictions sealed before feedback, with fixed time windows and outcome definitions. | Officially documented capability; predictive accuracy has not been established by this project. |
| Compare multiple astrological systems | Useful as one defined model in a benchmark against other engines or systems. | Shared planetary inputs and overlapping rules create dependence. Multiple views of the same model must not be counted as independent confirmations. |

## Costs and limits

The ordinary 7.8.5 interface processes people one at a time. This project has
successfully operated four isolated private Wine sessions with independent
queues, complete-tree extraction, source-clock and planetary checks, rotation
checks and hash-bound completion records. The controller stops acceptance when
checks fail and supports guarded restarts. This establishes a practical
project-specific GUI extraction route. A native batch facility, public API or
generally reliable unattended service has not been verified.

The selected input policy uses the numbered tutorial records for all 73
Northern subjects, available supplied records for 23 Southern subjects, and
45 explicitly marked Southern reconstructions from published Astro-Databank
sources. Four supplied records retain unresolved application-clock conventions:
the independently checked positions support the application's actually observed
UTC, but simple civil-offset arithmetic does not explain it. Both the captured
inputs and review flags are preserved. The analysis includes a separately
labeled sensitivity excluding those flags; numerical consistency does not
certify the true or historical birth clock.

The input records and configuration matter. Different birth-time sources,
ayanamsa reference years, filters, languages, scoring settings and export
history can change results. Current keyword weights differ from the older
reference lists, including differences beyond a single displayed rounding step.
The cause has not been isolated. Reconstructed inputs, build/corpus equivalence
and output agreement remain separate questions.

An internal probabilistic keyword score is not automatically a calibrated
probability that a person has a trait or that an event will occur. The
questionnaire and forecast experiments need their own external outcome tests.
The built-in chatbot portrait is a generated presentation of selected inputs;
its apparent specificity is not an independent validation of those inputs.

## Next research decisions

1. Resolve the remaining historical-input and build/corpus questions with the
   author. The completed 282-output comparison preserves vector, score and
   winner differences, including negative findings.
2. Use the completed primary comparison-input BIO analysis and separately labeled
   source-BIO, source-quality and clock-convention sensitivities. Keep the
   optional within-hemisphere BIO/person reassignment diagnostic separate from
   the primary endpoint. All cohort inference requires complete validated input.
3. Use controlled ablations to investigate output differences and individual
   ingredients. Freeze settings before each comparison; changed filters,
   duplicate rules or normalizations define alternative analyses.
4. Use a separate, preregistered dataset to test questionnaire matching or
   forecasts. Seal the rules before outcomes are examined and retain
   wrong-person controls, negative results and subgroup results.

The [current-source results](reanalysis-results.md) report the completed run;
the [research state](../../state/CURRENT-STATE.md) retains unresolved questions. Successful extraction and spreadsheet reconciliation
provide engineering and arithmetic evidence; external outcome tests are needed
before assigning Mastro predictive weight.

## Sources

- [Official features](https://mastroapp.com/en/features), checked 16 November 2026.
- [Official explanation of the expert system](https://mastroapp.com/en/about),
  checked 16 November 2026.
- [Official user manual](https://mastroapp.com/files/documentation_en.pdf),
  a general reference whose build may differ from 7.8.5.
- The owner-provided 16 November 2026 technical demonstration. Procedural
  timestamps are recorded in the [operating guide](operating-guide.md).
