# How Mastro Expert can help this project

Assessment date: 16 November 2026. The observed workflow uses Mastro Expert
7.8.5. This is an assessment of research usefulness; a proposed experiment is
not a measured success rate.

## Main value

Mastro turns an astrological chart into explicit keyword lists with numerical
scores and, optionally, the factors supporting each keyword. That gives the
project a model whose outputs can be frozen, compared and challenged. A
language model can then be used for separate tasks such as explaining a list;
the exported Mastro scores remain available for direct analysis.

The official feature list includes natal keywords from aspects and midpoints,
one-level and two-level synthesis, event keywords, forecast curves and CSV
export for chart animation. The actual interface, export schema and performance
must still be checked in the pinned research version.

## Uses and evidence status

| Use | Value for the project | Evidence status and next check |
| --- | --- | --- |
| Reproduce the 141-person zodiac-inversion study | Immediate priority. It is the source program that generated the reference keyword vectors. | Chart loading, inversion and CSV exports were demonstrated. The complete 282-output regeneration is pending. |
| Compare personality questionnaires with candidate charts | Promising baseline for blinded matching: export each candidate's keyword vector, freeze a scoring rule and compare against independent responses. | Proposed application. Questionnaire-to-keyword mapping, candidate generation, leakage controls and held-out accuracy have not been validated. |
| Test individual astrological ingredients | Controlled comparisons can examine midpoints, included points, aspect orbs and zodiac choice while holding other inputs fixed. | Relevant controls were demonstrated. Each ablation needs verified settings and fresh exports. |
| Explain why a score appeared | Optional factor signatures and the documented factor/keyword query tools can help trace an output to its astrological ingredients. | These features support auditing. A complete independent audit of the rule corpus and scoring implementation has not been completed. |
| Test forecasts prospectively | Event keywords and forecast curves could support predictions sealed before feedback, with fixed time windows and outcome definitions. | Officially documented capability; predictive accuracy has not been established by this project. |
| Compare multiple astrological systems | Useful as one defined model in a benchmark against other engines or systems. | Shared planetary inputs and overlapping rules create dependence. Multiple views of the same model must not be counted as independent confirmations. |

## Costs and limits

The demonstrated 7.8.5 workflow processes people one at a time. CSV accumulation
is available, but the call did not demonstrate a native automatic batch run
over the whole subject list. UI automation is a possible integration route;
its reliability and throughput still need a small measured pilot. No public
API or unattended large-run capability has been verified here.

The input records and configuration matter. Different birth-time sources,
ayanamsa reference years, filters, languages, scoring settings and export
history can change results. Some keyword scores in the demonstration differed
from the older reference lists. Those differences remain verification items.

An internal probabilistic keyword score is not automatically a calibrated
probability that a person has a trait or that an event will occur. The
questionnaire and forecast experiments need their own external outcome tests.
The built-in chatbot portrait is a generated presentation of selected inputs;
its apparent specificity is not an independent validation of those inputs.

## Recommended order

1. Freeze the program build, input records, language, settings and original BIO
   lists. Resolve one complete standard/inverted reference pair, including
   keyword weights and list lengths.
2. Test extraction on a small selection of cases covering both hemispheres,
   multiple databases and the known discrepancies. Measure elapsed time and
   failure modes before scaling an automation.
3. Regenerate all 282 original chart outputs. Reconstruct the verified evaluator
   calculation and compare complete vectors, scores and winner classifications.
4. Run explicit sensitivity analyses for filters, approximate inversion,
   duplicate keywords, whitespace and alternative normalizations. Preserve the
   original definition as the reproduction baseline.
5. Use a separate, preregistered dataset to test questionnaire matching or
   forecasts. Seal the rules before outcomes are examined and retain
   wrong-person controls, negative results and subgroup results.

This order makes Mastro a useful reference implementation and experimental
model while its accuracy and integration limits are measured.

## Sources

- [Official features](https://mastroapp.com/en/features), checked 16 November 2026.
- [Official explanation of the expert system](https://mastroapp.com/en/about),
  checked 16 November 2026.
- [Official user manual](https://mastroapp.com/files/documentation_en.pdf),
  a general reference whose build may differ from 7.8.5.
- The owner-provided 16 November 2026 technical demonstration. Procedural
  timestamps are recorded in the [operating guide](operating-guide.md).
