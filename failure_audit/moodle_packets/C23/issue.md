# Recently accessed items block produces PHP warnings when stored cmid no longer exists

h2. Analysis

The {{block_recentlyaccesseditems_get_recent_items}} web service assumes that every {{cmid}} stored in
{{block_recentlyaccesseditems}} is present in the current course modinfo. See: [blocks/recentlyaccesseditems/classes/external.php:70|https://github.com/moodle/moodle/blob/5035e19ecf68972d9d678e07f003472c397a786f/public/blocks/recentlyaccesseditems/classes/external.php#L70]

The {{helper::get_recent_items}} method loads rows from {{block_recentlyaccesseditems}}, groups them by course, loads {{get_fast_modinfo($courseid)}}, and then directly accesses {{$modinfo->cms[$item->cmid]}}, see [blocks/recentlyaccesseditems/classes/helper.php:76-83|https://github.com/moodle/moodle/blob/5035e19ecf68972d9d678e07f003472c397a786f/public/blocks/recentlyaccesseditems/classes/helper.php#L76-L83]

If the recent-items table contains an orphaned row where {{cmid}} no longer exists in {{course_modules}}, that {{cmid}}will not be present in {{$modinfo->cms}} resulting in warnings:

{noformat}PHP Warning: Undefined array key 123 in blocks/recentlyaccesseditems/classes/helper.php on line 78
PHP Warning: Attempt to read property "uservisible" on null in blocks/recentlyaccesseditems/classes/helper.php on line 78{noformat}

There is existing cleanup added in [https://moodle.atlassian.net/browse/MDL-65803|https://moodle.atlassian.net/browse/MDL-65803|smart-link] for module and course deletion at [blocks/recentlyaccesseditems/lib.php:32-46|https://github.com/moodle/moodle/blob/5035e19ecf68972d9d678e07f003472c397a786f/public/blocks/recentlyaccesseditems/lib.php#L32-L46]

However, that only reduces the likelihood of stale rows being created. It does not handle existing orphaned rows or cleanup paths which were missed or interrupted.

The current helper test covers deleted courses, but not deleted/missing course modules: [blocks/recentlyaccesseditems/tests/helper_test.php:31-58|https://github.com/moodle/moodle/blob/5035e19ecf68972d9d678e07f003472c397a786f/public/blocks/recentlyaccesseditems/tests/helper_test.php#L31-L58]

h2. Reproduction steps

# Create a user enrolled in a course
# Create an activity in that course
# Trigger a {{course_module_viewed}} event for that user by visiting the activity so a row is created in {{block_recentlyaccesseditems}}
# Create an orphaned recent items row by either:
#* Removing the referenced {{course_modules}} row without removing the {{block_recentlyaccesseditems}} row, or
#* Inserting a {{block_recentlyaccesseditems}} row with an existing {{courseid}}, valid {{userid}}, and non-existent {{cmid}}.
# As that user, load the Dashboard or call {{block_recentlyaccesseditems_get_recent_items}}

h2. Expected result

The stale recent item is ignored and no PHP warnings are emitted. Ideally, the stale {{block_recentlyaccesseditems}} row could also be removed.

h2. Actual result

The helper attempts to read {{$modinfo->cms[$item->cmid]->uservisible}} even though {{$item->cmid}} is absent from {{$modinfo->cms}}, triggering PHP warnings.

h2. Possible fix

An upgrade step could probably be added to clean up existing rows, but looking at the code it seems difficult to guarantee that the issue won’t happen again (for example if a course deletion is interrupted and the row is left orphaned).

To prevent future occurrences emitting warnings, an early return seems to be the most straightforward:

{code:php}if (empty($modinfo->cms[$item->cmid])) {
    continue;
}{code}

We could also delete the stale {{block_recentlyaccesseditems}} row when we hit this as well.
