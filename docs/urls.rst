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
/profile/comments/
    Show statistics about all comments created by a user.


Conversations
-------------

Public views for displayng information about conversations.

/conversations/:
    List all available conversations
/conversations/<category>/:
    List all conversations in a category
/conversations/<category>/<conversation>/:
    Detail page for some specific conversation.
/conversations/<category>/<conversation>/info/:
    Advanced information about conversation (statistics, graphs, etc) #DOING
/conversations/<category>/<conversation>/comments/:
    Show comments in the given conversation #TODO
/conversations/<category>/<conversation>/comments/<id>/:
    Show a comment + associated statistics #TODO



Administrative tasks
--------------------

All views in this section require staff permissions.

/admin/:
    Django admin.
/debug/styles/:
    Exhibit the main design patterns in the current theme.
/debug/info/:
    Show basic debug information about the server #TODO
/debug/logs/:
    Platform logs. #TODO?
/debug/data/:
    Importable resources like reports, backups, etc. #TODO?
    * User list
    * Logs
