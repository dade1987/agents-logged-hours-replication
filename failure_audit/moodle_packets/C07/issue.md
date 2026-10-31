# Allow obtaining multiple markers feedback via WebServices

In [https://moodle.atlassian.net/browse/MDL-86007|https://moodle.atlassian.net/browse/MDL-86007|smart-link] , the multiple markers feature was modified to let each marker add different feedback via plugins (e.g. each marker has its own feedback comments, or feedback files). And the student can see the feedback of each marker, along with the overall (general) feedback.

Since this change affects students, we would like to support the students part in the Moodle app, so students can also see the feedback for each marker in there. However, the WebServices weren’t modified as part of this issue, so right now there’s no way to obtain that information via WebService.

The WebService that currently returns the feedback is {{mod_assign_get_submission_status}}. In an assign with multiple markers, it’s only returning the overall/generic feedback, but not the feedback for each marker. We should probably modify the WebService to also return the feedback for each marker (when the user calling the WebService is allowed to see this information).
