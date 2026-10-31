# Still getting occasional Call to a member function populate_from_record() because of a missing continue

I missed this when I did MDL-79332. Thanks to [user] for spotting the  mistake and letting me know about it:

bq. Hi Tim, for Question bank error "Call to a member function populate_from_record() on null" for some categoires [MDL-79332], I think the issue is probably we missed a continue statement in the following if condition. [MDL-79332 Question stats: make loading robust to bad data -  timhunt/moodle@a047d2f (github.com)|https://github.com/timhunt/moodle/commit/a047d2f8b467b5b9c01cbf984a8fa7b473f0d37e#diff-d3a701d3d209fbdfcb7eb63d99d5f73567bd3ea319a71fdc89378bc1d5961aeaR221].

(The fix for MDL-79332 was not working for all questoin banks on our system, once we deployed the previous fix.)
