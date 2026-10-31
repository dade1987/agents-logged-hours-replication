# Moodle study: deviations log

English translation of the log kept during the study (original in Italian, entries in the order they were written). Agent ids refer to `moodle/agents_launched.tsv` and `transcripts/moodle/`. The transcript audit (`analysis/moodle/audit_transcripts_moodle.py`) was run on all transcripts afterwards; the primary analysis excludes every run flagged `moodle_seen` or `other_ws_seen`.

## Strict and iface conditions

- 2026-10-24, MDL-88878 opus strict 1: the agent reported that it ran a grep outside its workspace by mistake (it saw files of the evaluation checkout, LLM provider classes); it says it did not use them. Excluded in the sensitivity analysis.
- 2026-10-24, MDL-89008 sonnet strict 1: the first grep ran from the home directory (failed `cd`) and showed results from the evaluation checkout; the agent says it did not use them. Excluded in the sensitivity analysis.
- Note written on 2026-10-24: before the analysis, audit ALL agent transcripts for access to the evaluation checkout and run a sensitivity analysis without contaminated runs (done: audit_transcripts_moodle.py, leak_check.py).
- 2026-10-24, MDL-89289 opus strict 1: ran `git status` (forbidden). The workspace has no `.git` and the home directory is not a repository, so no history was visible. Minor deviation.
- 2026-10-24T15:26Z, MDL-89756 haiku (a3918f2e3ff9ee156): the agent reported running `git -C . status` (read-only) in its workspace, forbidden by the rules.
- 2026-10-24T15:32Z, MDL-89768 sonnet (ad19bf539b1c806fd): failed `cd`; a grep from the home directory read the evaluation checkout and the workspace MDL-89768_fable_strict_1 (the agent says it did not use the results). Isolation deviation; excluded.
- 2026-10-24T15:33Z, MDL-89768 opus (a641f24294e2f9c52): wrong `cd`; a grep from the home directory showed lines of the evaluation checkout and of the workspace MDL-89768_fable_strict_1 (pre-fix code, according to the agent). Isolation deviation; excluded.
- 2026-10-24T15:42Z, MDL-89913 opus (a8b4dd553f5c0e1d7): the agent reported one `git status` (no output, no change), forbidden by the rules.
- 2026-10-24T16:01Z, MDL-61427 haiku iface (aa4f51319fafe7c7b): the agent called a project messaging tool by mistake; no effect on the code.
- a15145cbe0241fe17, MDL-89870 fable iface 1: ran `git status` once in the workspace (not a git repository, no output). No access to the evaluation checkout.
- 2026-10-25 21:08 UTC: PostgreSQL was down after a container restart; 40 evaluations of Sonnet runs 2–3 (issues 1–20) were database connection errors, not outcomes. They were deleted and re-run.
- a4640dd09058a10ca, MDL-88624 sonnet strict 3: left a background process open when it finished (to check whether it tried to run tests).
- ad6b13ddf679091dd, MDL-88867 sonnet strict 2: finished with the text "placeholder", without a report or confidence.
- a12eb9f705217d354: a grep read file names in the home directory outside the workspace by mistake (failed `cd`); no change.
- a3ceaf7e53bbbbf5b: `grep -rn` ran from the home directory (failed `cd`) and showed lines of the evaluation checkout (possible contamination); the agent says it did not use them. Excluded in the sensitivity analysis.
- aa5c1b738628be922: failed `cd`; a grep from the home directory read files of another workspace (a similar fix, probably MDL-89711 run 2). The agent itself declared the run contaminated. Excluded in the sensitivity analysis.
- aa01bfbe50440d3fb: failed `cd`; a grep from the home directory showed lines of another workspace (MDL-89494_sonnet_strict_3); the agent says it did not use them. Excluded in the sensitivity analysis.
- 2026-10-25: fixed a missing line break before `AGENTE` in the cleaned logs (issues 1–20), which hid the outcomes of run 2 from the scoring script.

## Tests condition

- 2026-10-26 ~05:15 UTC: disk full while preparing the "tests" workspaces; the evaluations of MDL-89295 sonnet runs 2/3 that ended with a PHP fatal error were removed and re-run.
- 2026-10-26T05:31Z: the composer vendor cache was limited to 2 trees (least recently used evicted) because of the disk allowance; no effect on the agent environment.
- 2026-10-26T05:58Z, MDL-85977 opus: the agent reported one forbidden `git diff --stat` (read-only, no effect).
- 2026-10-26T06:29Z, MDL-87887 fable: the patch bumps mod/forum/version.php; checked that the evaluation is not broken by the PHPUnit re-initialisation requirement.
- 2026-10-26T07:14Z, MDL-88534 opus: the agent reported one grep run from the home directory (failed `cd`); audit flags apply. (The audit flags this run `moodle_seen`; the patch failed in both the strict and the tests condition, so it does not affect any result.)
- 2026-10-26T11:03Z: container restart at ~11:01 UTC, PostgreSQL restarted at 11:03; the MDL-88624 fable tests agent launched at ~11:01 may have hit the database while it was down for a moment.
- 2026-10-26T11:10Z, MDL-88652 opus: the agent saw a project timeline message (pause request) as background; unrelated to the task.
- MDL-89200 opus tests: the agent saw the same pause/resume message (it checked the clock before starting); no effect on the patch.
- MDL-89209 opus tests: the agent ran `git diff --stat` (forbidden by the "no git" rule); it printed nothing.
- MDL-89267 opus tests: the agent ran `git diff --stat` (nothing printed) and kept a temporary backup copy of a source file in its scratch area to check that the tests fail without its fix (copy deleted).
- MDL-89528 fable tests: the agent ran `git stash -q` by mistake (the workspace is not a git repository; no-op).
- MDL-89893 opus tests: the harness reported that the agent switched to an older Opus model (fallback) because the requested model was unavailable.
- MDL-89913 opus tests: the same model fallback.
- MDL-89921 opus tests: the agent copied core_renderer.php to its scratch area (outside the workspace) to check that the test fails without the fix; restored.
- Redo: MDL-89893 and MDL-89913 opus tests were re-run as run 2 (run 1 hit the model fallback). The primary analysis uses run 2 for these two issues; run 1 is kept for sensitivity (identical totals).
- Transcript audit (added when the package was built, 2026-10-31): two tests-condition runs are flagged by the audit, a7c7421dd0a3e9091 (MDL-87581 fable, `other_ws_seen`) and ab8df60e0a2e997ac (MDL-88534 opus, `moodle_seen`). Neither changes the tests-condition comparison: MDL-87581 fable was already solved in the strict condition, and MDL-88534 opus failed in both conditions.
