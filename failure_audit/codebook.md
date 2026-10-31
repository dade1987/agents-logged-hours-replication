# Failure audit: codebook and sampling plan (written 28 October 2026, before any failed patch was inspected for this purpose)

Status: exploratory, not preregistered. It answers a reviewer-style question raised by the author: do agents fail on long issues because their fix is wrong, or because the hidden tests expect details of the human implementation?

## Sample
- Moodle: strict condition, run 1 (primary analysis rows). Unit = one failed patch.
- Strata by logged human hours: S (<= 4 h) and L (> 4 h). For each stratum, draw 20 issues at random among issues with at least one failed run-1 patch (seed 20261028), then one failed patch per issue at random (same seed). If a stratum has fewer than 20 such issues, take all of them.
- MariaDB: same rule after evaluation ends (strata <= 2 h and > 2 h, because MariaDB hours are shorter; seed 20261029).

## What the rater sees (blind to hours, stratum, model)
Issue title and description; the agent's diff; the human fix diff split into code and tests; the summary of the hidden test run (before fix, after fix, agent patch).

## Categories (one per patch)
- **W (wrong):** the agent's change does not produce the behaviour the issue asks for, or produces it only partly in a way that a maintainer would reject (missing case, wrong place, breaks something else), or it does not compile / has a fatal error.
- **M (right but mismatched with the tests):** the behaviour the issue asks for is plausibly produced, but the hidden tests fail because they rely on implementation choices the issue text does not specify: a new function/method/class/file name or signature, a specific error string, a data structure, a new setting name, a UI string, or a fixture/generator the human added.
- **A (ambiguous issue):** the issue allows more than one reasonable behaviour, the agent chose a different one from the developers, and the tests check the developers' choice.
- **U (cannot tell):** not enough information to decide.

Decision rule: if the agent patch has any defect that would make it wrong regardless of the tests, code W, even if there is also a mismatch.

## Raters
Two independent AI raters (Claude Opus and Claude Fable subagents, each blind to the other's codes, to hours and to the model that wrote the patch). Disagreements are resolved by a third pass (Claude, main session) that sees both rationales. This is AI-assisted classification and will be declared as such; optional human check by the author on a subset.

## Analysis
1. Share of M (and M+A) per stratum, with Wilson 95% CIs; Fisher exact test S vs L.
2. Agreement: Cohen's kappa and Gwet's AC1 between the two raters.
3. Sensitivity bound: re-run the primary GEE (solved ~ log2h + model) counting M (then M+A) audited patches as solved; for unaudited failed patches, impute M by the stratum's M share (expected-value weighting) and report the log2h odds ratio.
4. Supporting evidence already available: the interface condition (20 issues) and the tests condition.
