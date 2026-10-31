# Forum template changes break overrides without warning or deprecation

This was originally raised in [MDL-88183|https://moodle.atlassian.net/browse/MDL-88183?focusedCommentId=1167753] before it was released, but it wasn’t followed up on.

To reproduce:

# Install the attached *local_forumdemolisher* plugin on Moodle 5.2
# Log in as admin and create a forum in a course with “Subscription mode” set to “Optional subscription”
# Open the forum's subscribers page and note the id parameter in its URL
# Visit */local/forumdemolisher/index.php?id=FORUM_ID*, replacing *FORUM_ID* with the value from 3.
# Select “Manage subscribers” from the dropdown
## Note that it works and opens the subscriber management page
# Repeat 1-5 on main and note that it no longer navigates
