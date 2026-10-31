# Preregistration (draft v1, 27 October 2026): Can AI coding agents re-solve real MariaDB issues, and does success fall with the hours maintainers logged? A replication of the Moodle study

Status: FINAL v1 (27 October 2026). The author submits it on OSF (project osf.io/u5jah) before any agent runs on MariaDB. No agent has run on the issues in the frozen sample. The only exceptions are the two pilot issues (MDEV-23086, MDEV-28922), which are excluded.

## 1. Background
- In the Moodle study (80 issues fixed since July 2026, four Claude models), the probability that an agent's patch passes the developers' hidden tests fell with the logged human hours: GEE odds ratio per doubling of hours 0.75, 95% CI 0.58–0.98.
- Model size made no clear difference.
- This study repeats the same design on MariaDB Server (C/C++), a project with a different language, build system and test framework (mtr).

## 2. Hypotheses (confirmatory)
- **H1.** The probability that a patch passes the hidden tests decreases with log2 of the human hours logged on the issue (odds ratio per doubling < 1).
  - Test: one-sided, α = 0.05, on the GEE coefficient of log2h.
- **H2.** Success differs between models.
  - Test: two-sided Wald test of the three model terms, α = 0.05.
  - We expect no large difference, as in Moodle, and report the size of the effect whatever the p-value.
- **H3 (replication of H1 across projects).** In a pooled GEE (Moodle + MariaDB, model + project terms), the log2h × project interaction is not significant (two-sided, α = 0.05), and the pooled log2h OR is < 1.
- Holm correction over H1–H3.

## 3. Sample (rule fixed before agents run)
1. MariaDB Jira issues fixed since 1 July 2026 with logged human hours. The data were extracted on 25 October 2026 (176 issues).
2. Exactly one fix commit, which changes both code and mtr tests, with at most 5 non-test files and at most 8 logged hours (98 issues).
3. Exclude bugs that can only be seen with a sanitizer or Valgrind: the title or the first 3,000 characters of the description mention ASAN, UBSAN, MSAN, TSAN, Valgrind, AddressSanitizer, "runtime error:", heap-use-after-free or use-of-uninitialized (82 left).
4. Oracle check on a debug build (MYSQL_MAINTAINER_MODE=OFF; CONNECT, Galera/WSREP, ColumnStore, RocksDB, Mroonga, Spider, S3 and DuckDB engines not built), with mtr run as a non-root user. The fix's tests must fail on the parent commit with the fix's test files copied in, and pass on the fix commit. Issues whose tests already pass before the fix (6) or are skipped in this build (5: CONNECT, Galera, --ps-protocol) are excluded. Script: mariadb_pilota/oracle_check.sh; results: mariadb_pilota/oracle_full.jsonl.
5. The two pilot issues are excluded, and so are issues whose Jira page is not public (MDEV-41667), because the agent must receive the public issue text.
6. If more than 80 issues remain, take a simple random sample of 80 (seed 20261027). Otherwise use all of them.

**Frozen sample: 68 issues** (fewer than 80, so all are used). File mariadb_study/frozen_sample.json (key, fix commit, logged hours, fix date, tests), SHA-256 2852ff7ba5920df0b5f9282e0d7c6a6779e35113ebc0f53b85d81bf5e1ce6e86. Exclusions with reasons: mariadb_study/excluded.json (30: 16 sanitizer-only, 11 oracle, 2 pilot, 1 non-public). Both files will be published in the replication package. Logged hours in the sample: median 2.0 h (range 0.5–8.0); 19 issues ≤1 h, 33 in 1–4 h, 16 >4 h.

## 4. Procedure (same as Moodle)
- **Agents:** Claude Haiku, Sonnet, Opus and Fable, run as Claude Code subagents from the subscription. The exact model id is logged for each run, and any run where the model falls back to another model is redone.
- **Workspace:** each agent gets a copy of the source at the parent commit, without Git history, together with the issue title and description as written in Jira. Usernames are replaced by [user].
- **Rules:** the agent may read and change only its workspace, has no internet, git or web tools, and cannot build or run tests (strict condition). The prompt is in prompt/ (template: ../mariadb_pilota/prompt/).
- **Runs:** 3 independent runs per model and issue. **Run 1 is the primary analysis.** Runs 2–3 are used for reliability and for a sensitivity analysis (majority vote).
- **Evaluation:** the agent's diff is applied without its own mtr changes, the fix's test files are added, and the build is run. The patch is a success when all of the fix's tests pass. A build failure counts as a failure.
- **Isolation** is by instruction only. A transcript audit (same script as Moodle) flags reads outside the workspace, and those runs are excluded in a sensitivity analysis.

## 5. Analysis
- **Primary:** GEE logistic, `solved ~ log2h + model`, clustered by issue, exchangeable correlation, run 1. This is the same code as `analysis/analysis.py`.
- **Time horizon:** h50 per model from `logit(solved) ~ log2h`, with bootstrap CIs (2,000 resamples by issue).
- **Labour share:** human hours on issues solved by at least one model.
- **Reliability:** Fleiss' kappa over the 3 runs, per model.
- **Sensitivity analyses:**
  - (a) majority vote of the 3 runs;
  - (b) excluding issues the author rates "unclear" in a blind rating made before seeing any agent result (scale: clear / partly clear / unclear: does the text say what the correct behaviour is?);
  - (c) excluding runs flagged by the audit;
  - (d) hours in bands (≤1, 1–4, >4 h) instead of log2h, because MariaDB hours are often rounded to 30 minutes; (e) excluding issues whose text already contains a proposed code fix or patch (flagged by the author of the protocol from the issue text alone, before agents run; list in clarity/solution_in_text.json).
- **Exploratory, not confirmatory:**
  - debt added by each patch compared with the human fix, if a C/C++ analyser can be run on the variants;
  - similarity to the human patch (normalised Levenshtein distance);
  - confidence calibration (Brier score).

## 6. Deviations
Any change after submission is logged in deviations.txt with its date and reason, and reported in the article.

## 7. Known limitations (declared in advance)
- The hidden tests can reject reasonable patches when the issue is underspecified. In the pilot, MDEV-28922 offered two fixes, the developers chose one, and the agent chose the other. Sensitivity analysis (b) addresses this.
- Isolation is by instruction, not technical.
- Agents cannot build or run tests.
- The issues were fixed after the models' training data ends, but contamination cannot be fully excluded.

## Appendix A. Frozen sample (68 issues: key, fix commit, logged hours)

- MDEV-22848 7cdbbb44a7 3.4166666666666665 h
- MDEV-24245 228e5b506b 6.5 h
- MDEV-29803 eeb8cb8587 1.1666666666666667 h
- MDEV-31225 151631b8cf 1.0 h
- MDEV-31808 367efd5674 0.5833333333333334 h
- MDEV-32331 1dab253482 3.1666666666666665 h
- MDEV-34074 1088d51f66 7.0 h
- MDEV-38755 75c4adf265 1.0 h
- MDEV-39194 46ea84b186 1.6666666666666667 h
- MDEV-39530 f897dc5ca1 1.5 h
- MDEV-39683 2883bccc7d 6.583333333333333 h
- MDEV-39742 36b0c525ef 5.0 h
- MDEV-39743 e8efde578a 0.5 h
- MDEV-39816 3079790e00 1.0 h
- MDEV-39817 59141cbd2c 1.0 h
- MDEV-39818 5acb435228 4.5 h
- MDEV-39911 2ff230f5fa 4.2 h
- MDEV-39914 d703f0ef51 5.7 h
- MDEV-39969 e331450f1b 4.166666666666667 h
- MDEV-39981 d0eb9e167a 2.0 h
- MDEV-40009 d646e24f7f 4.25 h
- MDEV-40041 4a1e64f722 2.75 h
- MDEV-40122 27dad5cc0c 0.8333333333333334 h
- MDEV-40143 deed18f42d 3.5 h
- MDEV-40153 172609526b 3.5 h
- MDEV-40159 736edbe77c 7.25 h
- MDEV-40186 e1dd1dc000 4.0 h
- MDEV-40229 d26f9ab217 1.0 h
- MDEV-40297 45d582be8c 1.6666666666666667 h
- MDEV-40329 5c04ca5524 2.0 h
- MDEV-40336 f59e460200 1.0 h
- MDEV-40340 6552e45061 1.0 h
- MDEV-40404 fed04cb77f 5.5 h
- MDEV-40409 f221495d59 2.0 h
- MDEV-40417 ce6b2906ca 3.75 h
- MDEV-40470 dbd60d0ad8 1.0 h
- MDEV-40480 2c9d60d713 5.0 h
- MDEV-40484 8a642bc810 2.6666666666666665 h
- MDEV-40540 8856f9fe19 1.0 h
- MDEV-40541 67ea07dd34 1.0 h
- MDEV-40544 387e9af846 1.6666666666666667 h
- MDEV-40584 b608e108d8 1.0 h
- MDEV-40621 f969bd80c7 5.75 h
- MDEV-40636 43565b932e 1.0 h
- MDEV-40670 0931994096 1.0 h
- MDEV-40673 ff80bd286e 2.3333333333333335 h
- MDEV-40678 851f52470d 1.0 h
- MDEV-40689 f49e838d36 1.8333333333333333 h
- MDEV-40722 210ab6edf4 4.0 h
- MDEV-40762 dec45ff9f3 4.266666666666667 h
- MDEV-40790 add6399198 2.0 h
- MDEV-40824 ab96574911 8.0 h
- MDEV-40978 bb4a126399 2.1333333333333333 h
- MDEV-40985 888f5d3bcb 2.15 h
- MDEV-40995 8226e48ab5 3.0 h
- MDEV-40996 52289d4555 3.5833333333333335 h
- MDEV-41021 e30f2bd21e 1.25 h
- MDEV-41022 6fd5edbbe2 2.3333333333333335 h
- MDEV-41067 6e62fd0112 5.183333333333334 h
- MDEV-41094 30ee95c7cc 1.0 h
- MDEV-41265 91b30e2cc1 2.0 h
- MDEV-41297 cf542109f3 1.25 h
- MDEV-41343 647a7402f0 1.0 h
- MDEV-41543 101af8ee09 2.75 h
- MDEV-41556 9a1123dc45 2.0 h
- MDEV-41617 438b373b91 1.1666666666666667 h
- MDEV-41657 a0bdd2c4ac 2.25 h
- MDEV-41669 44b576bd49 1.0833333333333333 h
