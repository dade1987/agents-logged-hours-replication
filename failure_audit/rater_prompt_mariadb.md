You are an independent rater in a software-engineering study. For each case listed below, an AI coding agent tried to fix a real MariaDB Server issue (C/C++) (strict condition: it saw only the issue text and the source code, and could not run code). Its patch FAILED the developers' hidden tests. Your job is to decide WHY it failed.

Read ONLY the files inside the case folders listed below (issue.md, agent.diff, human_code.diff, human_tests.diff, test_summary.txt). You may also read the MariaDB source at the parent commit if you need context: use `git -C /home/user/mariadb show <C>:<path>` where <C> is the content of parent_commit.txt in the case folder, read-only. Do not look at later commits. Do NOT open any other file or folder under /mnt/project-files, do not edit anything, do not run tests, do not use the web.
Note on mtr: a test passes only if its output matches the .result file exactly; the test_summary shows the diff between the expected result (---) and the actual output (+++), or build errors. A BUILD_FAIL or a crash/assertion caused by the agent change is W. EMPTY means no code change was made (W).

Categories (pick exactly one per case):
- W (wrong): the agent's change does not produce the behaviour the issue asks for, or produces it only partly in a way a maintainer would reject (missing case, wrong place, breaks something else), or it does not compile / has a fatal error.
- M (right but mismatched with the tests): the behaviour the issue asks for is plausibly produced, but the hidden tests fail because they rely on implementation choices the issue text does not specify: a new function/method/class/file name or signature, a specific error string, a data structure, a new setting name, a UI string, or exact mtr .result output (e.g. an error code, warning text or row order) that the issue does not specify.
- A (ambiguous issue): the issue allows more than one reasonable behaviour, the agent chose a different one from the developers, and the tests check the developers' choice.
- U (cannot tell): not enough information to decide.
Decision rule: if the agent patch has any defect that would make it wrong regardless of the tests, code W, even if there is also a mismatch.

How to work: for each case, read the issue, then the hidden tests (what exactly do they call and assert?), then the agent diff, then the human code diff. Ask: would the agent's code satisfy what the tests check if the tests had been written against the agent's own API/names? Is the agent's behaviour what the issue asks for?

Output: append one JSON object per case, one per line, to the output file given below, with keys: case, code (W/M/A/U), confidence (0-100), reason (2-4 sentences, concrete: name the test assertion or API that fails and why). Use a shell heredoc or python to append; write nothing else to that file. Finish by replying with the list of case codes.
