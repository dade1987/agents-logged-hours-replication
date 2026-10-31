# Implement OAuth 2 Server client manager class

To support an internal OAuth2 authorisation server within Moodle, we need a centralised management class to handle CRUD operations for OAuth2 clients, their associated secrets, and redirect URIs.

Scope:

* The class should implement methods that allow
** Fetching clients
*** by ID
*** by client identifier
** Updating a client (restricted to modifying administrative metadata: name, description)
** Revoking a client
** Reactivating a revoked client
** Permanent deletion of a client
** Generation of client secrets (including a logic to enforce a maximum active secret limit per user to 2)
** Fetching client secrets
** Revoking client secrets
** Fetching redirect URIs
** Creation of redirect URIs
** Removal of redirect URIs
** Validation of redirect URIs
* Unit test coverage

h2. Clarifications

* *Secret limit scope*: the maximum of 2 active secrets is enforced *per client*, not per user (a user may own multiple clients, each with its own limit of 2 active secrets).
* *Client revocation cascade*: revoking a client immediately revokes all of that client's active tokens and secrets (integrates with the revocation logic in MDL-88473), fully cutting off access rather than just blocking new token issuance.
* *Reactivation semantics*: reactivating a revoked client only restores the client record itself. Previously-revoked secrets and tokens remain revoked; the client must generate new secrets and go through authorization again to obtain new tokens.
* *Deletion precondition*: permanent deletion is only allowed once a client is already in a revoked state. This acts as a safety guard against accidentally destroying a live integration.
* *Redirect URI validation*: URIs must match exactly (no prefix/wildcard matching) and must use HTTPS, except for {{localhost}}/loopback addresses (to support native app development). No cap on the number of redirect URIs per client.
* *Class design*: all methods must be instance methods (not static), and the class is expected to be loaded via dependency injection (Moodle's {{\core\di}} container), not instantiated directly or accessed via static/singleton patterns.

h2. Acceptance criteria

# All CRUD/lifecycle methods listed above are implemented with the rules described in Clarifications.
# Secret generation enforces the per-client limit of 2 active secrets.
# Revoking a client cascades to revoke its active tokens and secrets.
# Reactivating a client does not restore previously-revoked secrets/tokens.
# Permanent deletion is rejected unless the client is already revoked.
# Redirect URI validation rejects non-exact matches and non-HTTPS URIs (except localhost/loopback).
# The class exposes only instance methods and is resolvable via dependency injection.
# PHPUnit test coverage for all of the above, including edge cases (secret limit exceeded, delete-before-revoke rejection, invalid redirect URI schemes, reactivation not restoring secrets).

----

_Fleshed out via a grill-me session during the more-detail-needed/hqteam_tt grooming pass._
