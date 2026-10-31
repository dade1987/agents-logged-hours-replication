# Run ASAP requests can be clobbered

h2. Background

The ability to run tasks ASAP was added in [https://moodle.atlassian.net/browse/MDL-85548|https://moodle.atlassian.net/browse/MDL-85548|smart-link] but if a scheduled task is already executing, the scheduled tasks page still shows “Run ASAP”.

Running it ASAP while the existing task is running reports success and sets *nextruntime* in the past.  However, when the existing task completes, {{scheduled_task_complete}} recalculates *nextruntime* and overwrites the time from the ASAP request before releasing the task lock.

h2. Expected behaviour

We should either reject Run ASAP while the task is running or preserve the request for a subsequent execution. It shouldn’t report success and silently discard the request.

h2. Replication

A minimal PHPUnit test is attached. Run it with {{vendor/bin/phpunit run_asap_race_test.php}}
