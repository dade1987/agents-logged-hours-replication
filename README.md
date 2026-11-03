# Replication package: AI coding agents vs maintainers' logged hours

This repository holds the data, scripts and agent transcripts for the article

> *Where Do Claude Coding Agents Stop? Logged Hours, Fix Size and Test Coupling on Real Moodle and MariaDB Issues*

Four Claude models (Haiku 5.5, Sonnet 5.5, Opus 5.5, Fable 5.1) re-solved real issues that were fixed after their training cut-off. Each agent saw only the issue text and the source code at the parent of the fix commit. The developers' own tests from the fix commit then judged its patch. Success is related to the hours the developers logged on the issue in Jira.

- **Study 1 (exploratory):** 80 Moodle issues (PHP, PHPUnit).
- **Study 2 (preregistered replication):** 68 MariaDB Server issues (C/C++, mtr), with three runs per model and issue. The preregistration is on OSF: [osf.io/de6g3](https://osf.io/de6g3/overview?view_only=6e04827760794cf08af92d0e1a976a78) (anonymized view-only link; the registration is under embargo). A copy is in `mariadb/preregistration_mariadb_v1.md`.

## Layout

| Folder | Content |
|---|---|
| `moodle/` | Issue list and hours (`issues.txt`, `issues.jsonl`), fix commits (`commits.txt`), agent prompts, agent patches, evaluation logs, outcomes (`results.csv`), run metadata (`runs.jsonl`), deviations log, scripts |
| `mariadb/` | Frozen sample (`frozen_sample.json`, `excluded.json`), preregistration, prompts, patches, evaluation logs, outcomes (`results.jsonl`), run metadata (`runs.tsv`), blind clarity ratings, deviations log, scripts, oracle check of the candidates (`pilot/`) |
| `analysis/moodle/` | Moodle analysis, transcript audit, leak check, patch-quality scan (SonarQube) and their outputs |
| `analysis/mariadb/` | Preregistered MariaDB analysis (H1–H3, sensitivity analyses a–e), transcript audit and outputs |
| `analysis/robustness/` | Exploratory robustness analyses added in revision: human fix size, issue creation dates, worklog roles, power, spline, contamination, small-sample errors, all-runs H2 (`robustness.json`, `robustness2.json`, `figure_hours_curve.png`) |
| `failure_audit/` | Codebook, rater prompts, case packets, AI rater outputs, final codes and analysis of the failed-patch audit (exploratory) |
| `transcripts/` | Sanitized transcripts of all 1,538 agent runs (`<agent_id>.jsonl.gz`) |
| `tools/` | Script used to sanitize the transcripts |

## Re-running the analyses

The statistical analyses need only Python and the files in this repository. Tested with Python 3.13, pandas 3.0, numpy 2.5, scipy 1.18 and statsmodels 0.15.

```
pip install -r requirements.txt
python3 analysis/moodle/audit_transcripts_moodle.py   # -> analysis/moodle/audit_runs.csv
python3 analysis/moodle/leak_check.py                 # -> analysis/moodle/leak_check.csv
python3 analysis/moodle/analysis_moodle.py            # -> analysis/moodle/results.json
python3 analysis/moodle/quality_analysis.py           # -> analysis/moodle/quality_results.json
python3 analysis/mariadb/audit_transcripts_mariadb.py # -> analysis/mariadb/audit_runs.csv
python3 analysis/mariadb/analysis_mariadb.py          # -> analysis/mariadb/results_mdb.json
python3 failure_audit/analyze_moodle.py               # -> failure_audit/moodle_results.json
python3 failure_audit/analyze_mariadb.py              # -> failure_audit/mariadb_results.json
python3 analysis/robustness/robustness.py          # -> analysis/robustness/robustness.json, figure_hours_curve.png (slow: power simulation)
python3 analysis/robustness/robustness2.py         # -> analysis/robustness/robustness2.json
python3 moodle/scripts/score.py                       # rebuilds moodle/results.csv from moodle/eval_logs/
```

`analysis/robustness/fix_size.py`, `fetch_created.py`, `fetch_worklog_roles.py` and `analysis/mariadb/similarity_mariadb.py` (needs `rapidfuzz`) built their CSV inputs from the Git clones and the public Jira APIs (read on 2 November 2026); their outputs are committed, so the analyses above need neither.

Re-running these scripts from a clean clone reproduces every committed output file byte for byte (checked on 31 October 2026).

Generating new agent runs or re-evaluating patches needs much more: a Moodle or MariaDB Server clone, PHP 8 with PostgreSQL 17 (Moodle) or a MariaDB debug build (MariaDB), and Claude Code. The scripts in `moodle/scripts/` and `mariadb/scripts/` are the ones used in the study. They expect the clone in `MOODLE` (default `/home/user/moodle`) or at `/home/user/mariadb`, and workspaces under `/home/user/ws` or `/home/user/ws_mdb`.

## Where each result in the article comes from

| Article | File and key |
|---|---|
| §4.1 Moodle solve rates, GEE odds ratio, h50, labour share, calibration, Sonnet reliability | `analysis/moodle/results.json` (`descriptive_primary`, `gee_primary`, `horizon_primary`, `labour_share_primary`, `confidence_primary`, `reliability_sonnet`, `sensitivity`) |
| §4.1 interfaces and tests conditions, cost | `analysis/moodle/results.json` (`iface_vs_strict`, `tests_vs_strict`, `agent_cost`) |
| §4.2 MariaDB solve rates, H1–H3, Holm, labour share, reliability, Brier | `analysis/mariadb/results_mdb.json` (`descriptive_primary`, `primary`, `H3`, `holm_adjusted_p`, `labour_share_primary`, `reliability`, `calibration_primary`) |
| §4.2 sensitivity analyses a–e | `analysis/mariadb/results_mdb.json` (`sensitivity`) |
| §4.2 transcript audit | `analysis/mariadb/audit_runs.csv` |
| §4.3 failure audit (both projects, including rater agreement) | `failure_audit/moodle_results.json`, `failure_audit/mariadb_results.json` |
| §4.3 objective re-check with test-support files | `failure_audit/moodle_fixture_recheck.json`, `moodle/eval_logs_fixture_recheck/` |
| §3.2 worklog roles | `analysis/robustness/worklog_roles.csv`, `robustness2.json` (`developer_hours`) |
| §3.3 fix sizes | `analysis/robustness/fix_size.csv` |
| §4.1 Moodle model Wald test | `analysis/robustness/robustness2.json` (`moodle_models_wald`) |
| §4.2 H2 on all runs, clear-only, bias-reduced errors | `analysis/robustness/robustness2.json` (`mariadb_all_runs`, `b_extended_clear_only`, `bias_reduced_se`) |
| §4.3 M/W share differences, fixture cases | `analysis/robustness/robustness2.json` (`failure_audit`) |
| §4.3 corrected-oracle OR, M-share bootstrap | `analysis/robustness/robustness.json` (`moodle_with_fixtures`, `pooled_with_moodle_fixtures`, `moodle_M_as_solved_bootstrap`) |
| §4.4 patch quality | `analysis/moodle/quality_results.json`, `analysis/moodle/results_quality_en.md` |
| §4.4 MariaDB similarity | `analysis/mariadb/similarity_mariadb.json` |
| §4.5 Table 6, Figure 1, power, spline, influence, contamination | `analysis/robustness/robustness.json`, `robustness2.json`, `figure_hours_curve.png` |

## Notes on the data

- **Evaluation logs.** The Moodle evaluation logs use Italian block markers, kept as written: `PRIMA:` means before the fix (the oracle check), `DOPO:` means with the human fix, and `AGENTE <model>_<condition>_<run>:` marks an agent patch. MariaDB outcomes are in `mariadb/results.jsonl`, with build and mtr logs in `mariadb/eval_logs/`.
- **Clarity ratings.** `mariadb/clarity/ratings.json` holds the blind clarity ratings used for sensitivity analysis (b). The values are Italian: `chiara` = clear, `in_parte` = partly clear, `poco_chiara` = unclear. The ratings were made by an independent rater, not by the author as preregistered, and before any MariaDB result was seen (see `mariadb/deviations.txt`).
- **Failure audit.** Two AI raters (Claude Opus and Claude Fable) made the classification, not humans. Disagreements were resolved with the codebook decision rule. The rater prompts are kept exactly as used, including the paths of the original environment.
- **Transcripts.** Each transcript keeps the agent's messages, its tool calls and the full tool outputs. Removed for privacy: the session context injected by the environment, the model's hidden reasoning blocks, the outputs of project/environment tools (a few Haiku runs called them by mistake), e-mail addresses and session links. The first line of each file gives the issue, model, condition and run.
- **Issue texts.** Prompts contain the issue title and description as written in Jira, with user names replaced by `[user]`. The original issues are public at `https://moodle.atlassian.net/browse/<KEY>` and `https://jira.mariadb.org/browse/<KEY>`.

## Licence

Code (`*.py`, `*.sh`): MIT licence (`LICENSE`). Data, transcripts and documentation: CC BY 4.0. The agent patches and the human fix diffs in `failure_audit/*_packets/` modify Moodle (GPL-3.0-or-later) and MariaDB Server (GPL-2.0), and remain under those projects' licences.
