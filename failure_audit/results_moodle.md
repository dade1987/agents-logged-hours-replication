# Failure audit, Moodle (28 October 2026, exploratory)

Codebook: codebook.md (sha256 fdefabcd…, written before inspection). Sample: 36 failed strict run-1 patches (16 issues ≤4 h, 20 issues >4 h; seed 20261028). Raters: two independent AI raters (Claude Opus, Claude Fable), blind to hours, stratum and model; static judgement (no test re-runs). Agreement 33/36 (Cohen's kappa 0.86, Gwet's AC1 0.88). Three disagreements adjudicated by the main session with the codebook decision rule (C11→W, C32→W, C33→A). Files: moodle_final_codes.json, moodle_results.json, analyze_moodle.py.

## Results
| Stratum | n | W wrong | M right, test mismatch | A ambiguous issue |
|---|---|---|---|---|
| ≤4 h | 16 | 3 | 9 (56%, CI95 33–77) | 4 |
| >4 h | 20 | 8 | 10 (50%, CI95 30–70) | 2 |

- About half of all failures are "right but mismatched with the tests" (new names/signatures, exact error strings, fixtures). The share is similar for small and large issues (Fisher p = 0.75). Wrong patches are more frequent on large issues (40% vs 19%), not significant (M+A vs W: p = 0.28).
- Three M cases fail only because developer-added fixture files are not copied by the evaluation (C02, C08, C35), and one because the agent edited a shared fixture (C04): these are artefacts of the oracle.
- Sensitivity (GEE, run 1; unaudited failures imputed with the stratum's share, 200 imputations): original OR per doubling of hours 0.75 (0.58–0.98). Counting M as solved: 0.83 (0.66–1.04), one-sided p = 0.051. Counting M+A as solved: 0.72 (0.56–0.92).

## Interpretation
Test-based success underestimates how often agents produce the requested behaviour, by roughly half of the failures. This bias is not concentrated on large issues, so it does not explain the decline with hours; the decline is weaker but still present when mismatches are counted as successes. Limits: AI raters, static judgement, 36 cases.

## Objective re-check with developers' test-support files (29 October 2026)
For the 16 issues whose fix also changed non-test files under tests/ (fixtures, generators), the 84 failed strict patches were re-run copying those files too (valuta_fixtures.sh, run_fixtures.sh; logs in studio/valutazioni_fixtures/). 17 of 84 now pass (3 issues: MDL-88319, MDL-89431, MDL-90009). Run-1 solved: Haiku 39, Sonnet 34, Opus 38, Fable 37 (was 36/32/35/34). GEE OR per doubling of hours: 0.69 (0.52–0.91), was 0.75 (0.58–0.98). Files: moodle_fixture_recheck.json.
