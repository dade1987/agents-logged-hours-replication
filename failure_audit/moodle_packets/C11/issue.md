# CORS incorrectly configured for REST API

[user]  raised this in MDL-88472:

{quote}Hey all, I’m a little concerned about the CORS middleware change here. We now only add CORS headers when {{Accept}} explicitly includes {{application/json}}, but normal {{fetch}} requests usually send {{Accept: */*}}.

So now existing {{/api/rest/v2}} routes may have their responses blocked by the browser, even though Moodle has processed the request. This could be especially problematic for writes, which may now succeed while appearing to fail.

I didn’t see any discussion about it in the comments so just wanted to raise it for discussion.{quote}
