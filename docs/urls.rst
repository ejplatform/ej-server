URL structure
=============

This document register the default URLs used in the platform and where to find
them in their corresponding apps.


Users/login
-----------

Public views controlling authentication and creation of new users.
Both login and register views accept a ?next=<url> tag that controls the
redirect page.

login/ (auth:login):
    Login page.
logout/ (auth:logout):
    End user session.
register/ (auth:register):
    Register a new user.
profile/recover-password/ (auth:recover-password):
    Recover user password.
profile/reset-password/ (auth:reset-password):
    Allow user to change its password.
profile/remove/ (auth:remove-account):
    Remove user account. This is an non-reversible operation that the user
    must confirm in order to actually remove the account.

All views are included in the ej_accounts app.



Profile views
-------------

Users cannot see each other's profiles since EJ is not meant to be a traditional
social network. There is no concept of "friends", "followers",
"private conversations" etc.

profile/ (profile:index):
    Show user profile.
profile/edit/ (profile:edit):
    Edit profile.
profile/comments/ (profile:comments):
    Show statistics about all approved comments created by a user.

Those URLs require login and are implemented in the ej_profiles app.


Gamification
............

Show gamification information for the user profile.

profile/badges/ (gamification:badges)
    List of badges for the user.
profile/leaderboard/ (gamification:leaderboard)
    Show the user position in the leaderboard.
profile/powers/ (gamification:powers)
    See all unused powers.
profile/quests/ (gamification:quests)
    See all open quests.

Those views are implemented in the ej_gamification app.


Global powers
.............

Interface that users can use to manage global powers and resources in the
platform.



Notifications
-------------

Notifications are displayed using alerts (push notifications) for most users.
However, some users may not have support for this technology on their browsers
and even the users who have, might want to keep a record of the later
notifications in the system.

notifications/ (notifications:index):
    List all unread notifications.
notifications/history/ (notifications:history):
    List all notifications.

All notifications are managed by the ej_notifications app.



Conversations
-------------

Public views for displaying information about conversations.

conversations/ (conversations:list):
    List all available conversations
conversations/<category>/ (conversations:category):
    List all conversations in the given category
conversations/<category>/<conversation>/ (conversations:conversation-detail):
    Detail page for an specific conversation.
conversations/<category>/<conversation>/comments/  (conversations:comment-list):
    Show all comments the user already voted in the given conversation.
conversations/<category>/<conversation>/my-comments/  (conversations:user-comments):
    Show information about all comments a user posted in a conversation.
conversations/<category>/<conversation>/comments/<id>/ (conversations:comment-detail):
    Show a specific comment + associated statistics.
conversations/<category>/<conversation>/info/ (conversations:info):
    Advanced information about conversation (statistics, graphs, etc)
conversations/<category>/<conversation>/leaderboard/ (conversations:leaderboard):
    Leaderboard: show a list of users sorted by rank.

Those URLs are implemented in the ej_conversations app. Notice that this app
lives in a separate repository at http://github.com/ejplatform/ej-conversations.


CRUD
....

All those URLS are only available for users with permission to edit
conversations. This can be applied to staff members or to the owner of the
conversation.

conversations/create/ (conversations:create-conversation):
    Add a new conversation.
conversations/<category>/<conversation>/edit/ (conversations:edit-conversation):
    Edit conversation.
conversations/<category>/<conversation>/moderate/ (conversations:moderate-comments):
    Can classify all non-moderated comments.

Those tree urls are implemented in the ej_conversations app.


Stereotype management
.....................

Only staff members and the conversation owner have access to those pages.

conversations/<category>/<conversation>/stereotypes/ (clusters:stereotype-list):
    List of all stereotypes showing information about the assigned cluster and
    statistics.
conversations/<category>/<conversation>/stereotypes/<id>/ (clusters:stereotype-vote):
    Allow the given stereotype to vote in conversation.

Stereotypes are implemented in ej_clusters.


Reports
.......

Only staff members and the conversation owner have access to those pages.

conversations/<category>/<conversation>/reports/ (reports:index):
    Aggregate reports for the given conversation.
conversations/<category>/<conversation>/reports/clusters/ (reports:clusters):
    Show information for each cluster.
conversations/<category>/<conversation>/reports/radar/ (reports:radar):
    Display comments in a 2D layout to show the distribution of opinions and
    comments.
conversations/<category>/<conversation>/reports/divergence/ (reports:divergence):
    Hierarchical view for the degree of divergence and concordance of each
    comment.

Reports have its own app at ej_reports.


Clusters
........

Display the clusters associated with a conversation. All those urls require
authentication, but are visible to all users.

conversations/<category>/<conversation>/clusters/ (clusters:index):
    See cluster information in conversation. Display in which cluster the user
    was classified. The user must have cast a minimum number of votes if it
    wants to be classified into clusters.
conversations/<category>/<conversation>/clusters/<index>/ (clusters:detail):
    Show information about a specific cluster.

Urls are implemented into the ej_clusters app.



Help
----

Urls with the intention of explaining how to use the platform. Most of those
urls are implemented as flat pages and are stored as HTML or markdown under
either local/pages or lib/pages/.

/start/ (help:start):
    Landing-page broadly explaining what is EJ and how to use the platform.
/rules/ (help:rules):
    Explain the rules of how the "EJ game" works.
/faq/ (help:faq):
    Frequently asked questions.
/about/ (help:about):
    About EJ or the organization deploying an instance.
/usage/ (help:usage):
    Usage terms for the platform.
/social/ (help:social):
    Links to EJ social networks.

All urls are implemented in the ej_help app.



Talks
-----

Rocketchat integration.

/talks/ (rocket:index)
    Display Rocketchat inside a <iframe>.
/talks/intro (rocket:intro):
    Initial page displayed by the Rocketchat instance.
/talks/channels (rocket:channels):
    List of Rocketchat channels available for the user.

All urls are implemented in the ej_rocketchat app.



Administrative tasks
--------------------

All views in this section require staff permissions.

admin/:
    Django admin.
debug/styles/ (config:styles):
    Exhibit the main design elements like colors and typography applied in the
    current theme.
debug/info/ (config:info):
    Show basic debug information about the server
debug/logs/ (config:logs):
    Platform logs.
debug/data/ (config:data):
    Importable resources like reports, backups, etc.
    * User list
    * Logs
