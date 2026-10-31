# tag_cron_task Error reading from database (number of parameters must be between 0 and 65535)

This happen as we have {{81535}} (tag instance ids) parameters:

{noformat}Scheduled task failed: Background processing for tags (core\task\tag_cron_task), Error reading from database (number of parameters must be between 0 and 65535)
SELECT ti.*, COALESCE(t.name, 'deleted') AS name, COALESCE(t.rawname, 'deleted') AS rawname
FROM mdl_tag_instance ti
LEFT JOIN mdl_tag t ON t.id = ti.tagid
WHERE ti.id IN (VALUES (...)
...
-- line 208 of /lib/classes/task/tag_cron_task.php: call to pgsql_native_moodle_database->get_records_sql()
-- line 51 of /lib/classes/task/tag_cron_task.php: call to core\task\tag_cron_task->cleanup(){noformat}
