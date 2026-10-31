# Configurable quiz statistics delay

Currently quiz statistics are calculated using a 1 hour delay.

The first submission to a quiz triggers an adhoc task due in 1 hour. However most of our sites and quiz’s this is just far to often, especially given how heavy of a task this is. There are many sites where this report is almost never viewed, and just have a constant drip-feed of quiz attempts, causing this quiz statistics task to essentially be constantly queued up to run, adding significant server load for something that is not really used.

Our suggestion is 2 parts.

# Make this configurable, so instead of a hard-coded 1 hour it is configurable in the admin.
# Switch it from a delay to a de-bounce.

Making it a de-bounce I think is a large improvement, it allows the heavy statistics calculation to run only when the feed of quiz attempts stops. 

We have already put this change into production and seen an absolute massive reduction in server load. We have it set to a 1 week de-bounce, as this is not view much on this site. However on other sites it could be reduced if the report is viewed frequently.

This report can be set to be triggered imminently from the admin GUI as well, so even with a large de-bounce, it can be re-calculated as needed. We will also be making this immediately recalculation happen via an adhoc task as well. As we have seen this report take up to 7 hours to calculate, making it always run via an adhoc task means there's no timeout issues for any course. 

This change, combined with some other optimisations in the linked tracker we have seen a massive 2000x reduction in server load caused by quiz statistics, see: [https://moodle.atlassian.net/browse/MDL-87180?focusedCommentId=1051572|https://moodle.atlassian.net/browse/MDL-87180?focusedCommentId=1051572|smart-link] 
