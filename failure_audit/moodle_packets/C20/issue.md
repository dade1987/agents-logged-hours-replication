# Client and secret last accessed time is not logged during OAuth2 flows

There are currently DB fields and to track the last accessed time for client and client secrets. Also, the UI on the client and secret management pages are designed to show this information. However, currently this information is not being logged during authorization or token exchange.
