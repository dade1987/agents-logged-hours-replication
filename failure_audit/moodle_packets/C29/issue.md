# Event user_loggedout does not contain correct realuserid

It has taken some time to understand this issue, however, I think we've got it now.

If you are imitating an account, there is an issue with the fact the buffered writer (tool\log\classes\helper\buffered_writer) tries to retrieve the realuser just after it was destroyed.

Meaning the wrong information is written to the log in the end.

The issue is caused by the fact the $event->trigger() for the require_logout() takes place just after the session manager terminates the current session, meaning it has destroyed the data the buffered_writer wants to write, causing it to revert to null.

Aka, the wrong details eventually end up in the logs.

 

The fix is pretty simple, as it would be enough to just trigger the event before the session is terminated, which should make sure the realuserid is stored correctly while maintaining the rest of the flow.
