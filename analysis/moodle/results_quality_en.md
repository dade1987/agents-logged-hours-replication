# Study A+H: exploratory results on the tests condition and patch quality (26 October 2026)

None of the analyses in this file were preregistered. The author chose them on 26/10 (quality option "A + C": SonarQube debt compared with the human fix, plus analysis by task size and model). All p-values are unadjusted and come from about 15 exploratory tests, so they should be read as descriptive.

## 1. Tests condition (Fable and Opus could run Moodle's PHPUnit tests)

| Model | Strict (no tests) | Tests | Only solved with tests | Only solved in strict | McNemar p |
|---|---|---|---|---|---|
| Fable | 34/80 | 38/80 | 4 | 0 | 0.125 |
| Opus | 37/80 | 38/80 | 2 | 1 | 1.0 |

- Being able to run the existing tests gives a small gain that is not significant.
- Two Opus runs (MDL-89893, MDL-89913) hit a model fallback in run 1 and were redone. The primary analysis uses the redo. Using run 1 instead gives identical totals.

## 2. Technical debt added by each patch (SonarQube Community 26.9, sqale_index)

Method (analysis/quality_scan.py):
- For each issue, U = production PHP/JS files touched by the human fix or by any agent patch.
- One SonarQube project per issue holds one copy of U per variant (before the fix, human fix, each agent patch).
- Δdebt = debt of the variant minus debt before, on the same files, in minutes.
- Totals come from the per-folder measures.
- All 80 issues were scanned, with 0 apply errors and 0 scan errors.

Human fixes: median Δdebt 0 min, mean 10.0 min; 48.7% of human fixes add some debt.

Strict condition, run 1, all 80 patches per model:

| Model | Solved | Mean Δdebt agent (min) | Mean Δdebt human (min) | Patches with more / same / less debt than human | Wilcoxon p | Median lines added (human 18) |
|---|---|---|---|---|---|---|
| Haiku | 36 | 4.7 | 10.0 | 8 / 42 / 30 | 0.0003 | 8 |
| Sonnet | 35 | 5.3 | 10.0 | 9 / 41 / 30 | 0.0002 | 8.5 |
| Opus | 37 | 10.1 | 10.0 | 22 / 38 / 20 | 0.73 | 12.5 |
| Fable | 34 | 9.3 | 10.0 | 20 / 38 / 22 | 0.93 | 16.5 |

- The smaller models add less debt mainly because they write smaller patches, many of which do not solve the issue.

Patches that pass the hidden tests (strict, run 1):

| Model | Solved | More debt than human | Extra debt over human (min, sum) | Wilcoxon p |
|---|---|---|---|---|
| Haiku | 36 | 5 | 40 | 0.34 |
| Sonnet | 35 | 5 | 23 | 0.87 |
| Opus | 37 | 10 | 70 | 0.0499 |
| Fable | 34 | 8 | 90 | 0.33 |

- No model adds new SonarQube bugs or vulnerabilities in a meaningful number: 0–1 in total per model.

## 3. "Clean success": passes the hidden tests and adds no more debt than the human fix

| Model | Strict solved | Strict clean | Tests solved | Tests clean |
|---|---|---|---|---|
| Haiku | 36 | 31 | – | – |
| Sonnet | 35 | 30 | – | – |
| Opus | 37 | 27 | 38 | 32 |
| Fable | 34 | 26 | 38 | 30 |

By task size (human hours), clean/solved/n, strict:

| Band | Haiku | Sonnet | Opus | Fable |
|---|---|---|---|---|
| ≤1 h (n=10) | 6/7 | 6/7 | 4/6 | 5/6 |
| 1–4 h (n=19) | 10/10 | 8/10 | 9/13 | 9/10 |
| >4 h (n=51) | 15/19 | 16/18 | 14/18 | 12/18 |

- On the clean-success measure, the larger models lose their small lead in raw success: Opus and Fable more often pass the tests while adding more debt than the human fix.
- Nothing suggests that Fable does better on large tasks. On >4 h issues it has the fewest clean successes.
- The size × model interaction for raw success was also null (Wald χ²=1.81, df=3, p=0.61; see results.json).

## 4. Similarity to the human fix (normalised Levenshtein similarity of the changed lines)

- Median similarity is about 0.30 for every model.
- Patches that pass the hidden tests are more similar to the human fix than patches that fail: median 0.40 vs 0.27, Mann-Whitney p<0.001, strict, all models pooled.
- Debt added grows with task size: Spearman ρ=0.33 between human hours and agent Δdebt, p<0.001.

## 5. Limitations specific to these analyses

- SonarQube's debt model, used with default rules, is the measure we criticise in the SQALE article. Here it is used only as a relative comparison against the human fix on the same files, not as an estimate of hours.
- Exploratory and unadjusted: the only nominally significant results for solved patches (Opus, p=0.0499) would not survive any multiple-comparison correction.
- Duplication detection was disabled, because the variant folders are copies of each other, so duplicated code added by a patch is not counted.
- Agents in the strict condition could not run tests. The tests condition covers only Fable and Opus.

Files:
- analysis/quality.jsonl and analysis/quality_rows.csv: one row per patch.
- analysis/quality_results.json
- analysis/results.json, which holds tests_vs_strict and tests_vs_strict_sens_run1.
- studio/deviazioni.txt
