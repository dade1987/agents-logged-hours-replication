# Harden PAT storage

At the moment we’re generating the PAT secret using {{random_string()}}, which is a Moodle-specific method which generates a random string. This is generating a value using {{random_bytes()}}, which is good, but it’s just not the _right_ solution. We don’t need this value to be human readable, and the simpler solution is {{bin2hex}} wrapping {{random_bytes()}} instead.

This is what we do for oauth2 secrets:

{noformat}$secret = bin2hex(random_bytes(32));{noformat}

[user] and I also discussed other improvements to secrets, including how we can harden the PATs themselves by adding a calculated integrity check value using the list of scopes, and the token expiry. By adding this into the secret before hashing it, we can ensure that the database value has not been modified in any way.

This prevents someone from manually modifying the database to extend the remit of a PAT.
