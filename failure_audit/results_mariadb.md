# Failure audit, MariaDB (29 October 2026, exploratory)

Same codebook and procedure as Moodle (codebook.md). Sample: 27 failed run-1 patches (12 issues ≤2 h, 15 issues >2 h; seed 20261029; all eligible issues). Raters: Claude Opus and Claude Fable, blind; agreement 24/27 (kappa 0.77, AC1 0.86). Adjudicated: D09→W, D15→A, D19→W. Files: mariadb_final_codes.json, mariadb_results.json, analyze_mariadb.py.

| Stratum | n | W wrong | M right, test mismatch | A ambiguous issue |
|---|---|---|---|---|
| ≤2 h | 12 | 9 | 3 (25%) | 0 |
| >2 h | 15 | 10 | 3 (20%) | 2 |

- Most MariaDB failures are genuinely wrong (70%): crashes left in a related path, incomplete fixes, build failures, no change. Test mismatches are rarer than in Moodle (22% vs 53%), plausibly because mtr tests check SQL-level behaviour rather than PHP API names.
- No difference between strata (Fisher p = 1.0 for M; 0.70 for M+A).
- Sensitivity GEE (run 1): original OR per doubling 0.81 (0.52–1.25); M as solved 0.79 (0.51–1.23); M+A as solved 0.87 (0.57–1.33).
