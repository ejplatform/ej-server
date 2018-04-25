URL structure
=============

This document register the default URLs used in the platform:


Users/login
-----------

Public views controlling authentication and creation of new users.
Both views accept a ?next=<url> tag that controls the redirect.

/login/:
    Login page.
/register/:
    Register a new user.


Profile views
-------------

Users cannot see each other's profiles. Those URLs require a successful login.

/profile/:
    Show user profile.
/profile/edit/:
    Edit profile.


Conversations
-------------

Public views for displayng information about conversations.

/conversations/:
    List all available conversations
/conversations/<category>/:
    List all conversations in a category




Administrative tasks
--------------------

All views in this section require staff permissions.

/admin/:
    Django admin.
/debug/styles/:
    Exhibit the main design patterns in the current theme.
/debug/info/:
    Show basic debug information about the server #TODO
/debug/import/:
    Importable resources like statistics,
