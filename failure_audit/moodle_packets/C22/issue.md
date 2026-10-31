# New Web Service for setting a forum post read state when manual mark as read is enabled

Currently is not possible to control the “post read” state via Web Services when the global option to allow users to manually mark as read post “forum_usermarksread“ is enabled.

The existing web services are already returning if the user can control the read status (capabilities → controlreadstatus); however, we do not have and enpoint to change the status to read or unread.

We’d need the following WS (nomenclature is consistent with similar ones to set the pin/lock/favourite state):

{{mod_forum_set_read_state}}

Parameters:

* postid (The post id)
* targetstate (Bool, true to set is read, false to unread)

The related code and capabilities control is already here:

[https://github.com/moodle/moodle/blob/MOODLE_501_STABLE/public/mod/forum/discuss.php#L282|https://github.com/moodle/moodle/blob/MOODLE_501_STABLE/public/mod/forum/discuss.php#L282|smart-link] 
