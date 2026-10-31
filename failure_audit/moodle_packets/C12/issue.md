# H5P $manager->count_attempts() returns wrong number if a user is enrolled with multiple methods

I noticed it in one of our tests sites. In the H5P activity initial screen, the teacher saw: View 14 attempts. But there were only 13 attempts for the activity.

The query done in count_attempts returns duplicated rows when a user is enrolled using more than one enrolment method.
