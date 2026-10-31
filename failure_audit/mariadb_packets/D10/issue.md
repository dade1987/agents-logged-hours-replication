# 11.4 JSON functions not interuptable

[11.4 json functions|https://mariadb.com/docs/release-notes/community-server/11.4/what-is-mariadb-114#json] need to be killable/timeout.

Functions added in 11.4:
* JSON_ARRAY_INTERSECT
* JSON_OBJECT_FILTER_KEYS
* JSON_OBJECT_TO_ARRAY
* JSON_SCHEMA_VALID

Like MDEV-28404 they need:
* {{je.killed_ptr}} assignment after {{json_scan_start}} where the is a function to {{json_scan_next}} used within the Item
* Remove {{check_killed()}} if present - handled by {{report_json_error}}.
* {{JSON_DO_PAUSE_EXECUTION(thd, 0.0002);}} in {{Item_function::val*}}
* json library functions to end up in {{report_json_error(js, &je, 0);}} immediately after error, and return null.
* add to {{func_json_notembedded.test}} - ensure result file is the timeout error.
