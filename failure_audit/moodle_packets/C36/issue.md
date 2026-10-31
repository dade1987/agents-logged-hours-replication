# Forgot password tokens should be invalidated when account email address changes or a new token is requested

We should only be accepting tokens sent to an account's current email address, so when a user's email account is updated, we should invalidate tokens used in password reset (forgotten password) links sent to the old address. (It would be worth also having a look for  any other similar tokens that may need similar treatment.)

We should also be removing existing tokens if a new one is generated (ie another forgot password request for the account is received).

Given the (default) short life of such tokens and the fact that they are single use, these are fairly edge case, but is a valid fix to comply with security best practice. Taking that into account along with the low risk of being an exploitable issue, I've marked this as a security benefit, and not assigned a security level.

For consistency, we should also invalidate forgot password tokens if the password is changed, regardless of method..

 

_Written up by_ [user]{_}, based on reports by{_} [user], [user] and others.
