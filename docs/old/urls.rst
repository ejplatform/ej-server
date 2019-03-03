URL structure
=============

This document register the default URLs used in the platform and where to find
them in their corresponding apps.


Users/login
-----------

Public views controlling authentication and creation of new users.
Both login and register views accept a ?next=<url> tag that controls the
redirect page.

**Actions that do not require authentication**
login/ (auth:login):
    Login page.
register/ (auth:register):
    Register a new user.
recover-password/ (auth:recover-password):
    Recover user password.
recover-password/<token> (auth:reset-password-token):
    URL sent by e-mail after user request a password reset.

**Actions that require authentication**
account/ (auth:account):
    Manage basic account actions such as password reset, e-mail reset, etc.
account/logout/ (auth:logout):
    End user session.
account/remove/ (auth:remove-account):
    Remove user account. This is an non-reversible operation that the user
    must confirm in order to actually remove the account.
account/change-email/ (auth:manage-email):
    Allow user to change its e-mail.
account/change-password/ (auth:change-password):
    Allow user to change its password.

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
profile/contributions/ (profile:comments):
    Show statistics and information about all contributions of the user to
    conversations in the platform.

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

profile/notifications/ (notifications:index):
    List all unread notifications.
profile/notifications/history/ (notifications:history):
    List all notifications.

All notifications are managed by the ej_notifications app.



Conversations
-------------

Public views for displaying information about conversations.

conversations/ (conversations:list):
    List all available conversations
conversations/<conversation>/ (conversations:conversation-detail):
    Detail page for an specific conversation.
conversations/<conversation>/comments/  (conversations:comment-list):
    Show all comments the user already voted in the given conversation.
conversations/<conversation>/my-comments/  (conversations:user-comments):
    Show information about all comments a user posted in a conversation.
conversations/<conversation>/comments/<id>/ (conversations:comment-detail):
    Show a specific comment + associated statistics.
conversations/<conversation>/info/ (conversations:info):
    Advanced information about conversation (statistics, graphs, etc)
conversations/<conversation>/leaderboard/ (conversations:leaderboard):
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
conversations/<conversation>/edit/ (conversations:edit-conversation):
    Edit conversation.
conversations/<conversation>/moderate/ (conversations:moderate-comments):
    Can classify all non-moderated comments.

Those tree urls are implemented in the ej_conversations app.


Stereotype management
.....................

Only staff members and the conversation owner have access to those pages.

conversations/<conversation>/stereotypes/ (clusters:stereotype-list):
    List of all stereotypes showing information about the assigned cluster and
    statistics.
conversations/<conversation>/stereotypes/<id>/ (clusters:stereotype-vote):
    Allow the given stereotype to vote in conversation.

Stereotypes are implemented in ej_clusters.


Reports
.......

Only staff members and the conversation owner have access to those pages.

conversations/<conversation>/reports/ (reports:index):
    Aggregate reports for the given conversation.
conversations/<conversation>/reports/clusters/ (reports:clusters):
    Show information for each cluster.
conversations/<conversation>/reports/radar/ (reports:radar):
    Display comments in a 2D layout to show the distribution of opinions and
    comments.
conversations/<conversation>/reports/divergence/ (reports:divergence):
    Hierarchical view for the degree of divergence and concordance of each
    comment.

Reports have its own app at ej_reports.


Clusters
........

Display the clusters associated with a conversation. All those urls require
authentication, but are visible to all users.

conversations/<conversation>/clusters/ (clusters:index):
    See cluster information in conversation. Display in which cluster the user
    was classified. The user must have cast a minimum number of votes if it
    wants to be classified into clusters.
conversations/<conversation>/clusters/<index>/ (clusters:detail):
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
/contacts/ (help:contacts):
    External contacts.

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
