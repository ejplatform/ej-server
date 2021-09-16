================================
CHANGELOG of EJPlatform releases
================================

Here you can follow all the fixes and new features on every EJPlatform release.


2.12.0 release
====================

* Date: Set 16, 2021
* Features
- Adds new reports menu;
- Minor fixes on header;
- Minor fixes on user navigation;
- Fixes comment count;
- Fixes webchat tool page, when adding a existent domain;
- Adds new ej_tools app;

2.11.0 release
====================

* Date: Ago 31, 2021
* Features
- Adds new navigation menu for boards;
- Adds user profile logo on header;
- Adds limitation for conversation creation, based on user Signature;
- Adds oauth2 authentication between EJ and Mautic;
- Adds UI improvements on Webchat tool;

2.10.0 release
====================

* Date: Ago 16, 2021
* Features
- Moves menu to the left side;
- Creates default board to new users;
- Adds channel field on Vote model;
- Improves Opinion Component tool page;

2.9.0 release
====================

* Date: Ago 5, 2021
* Features
- Creates profile for user on /rest-auth/registration;
- Improve rasa Webchat tools page;
- Improves mailing tools page;
- Improves /docs;
- WIP: Adds Mautic tools page;

2.8.0 release
====================

* Date: Jul 5, 2021
* Features
- New model ConversationAnalysis, to store data for airflow integration;
- Changes analytics authentication method;
- Adds conversation ID on /api/v1/conversations/<id>;

2.7.0 release
====================

* Date: Jun 29, 2021
* Features
- Adds integration between EJ and Airflow API;
- Adds integration between EJ and Mongodb instance;
- Improves integration between EJ and Analytics API;
- Refactoring TemplateGenerator class;
- Fixes template generation on mailing tool page, when no template is selected;
- Adds pagination on votes api;

2.6.0 release
====================

* Date: Jun 8, 2021
* Features
- Fixes template color on mailing tool page;
- Adds button to remove a webchat domain, on rasa tool page;
- Fixes rasa webchat documentation;
- Fixes opinion component snippets;

2.5.0 release
====================

* Date: May 11, 2021
* Features
- Adds new conversation analysis page;
- Adds custom fields on mailing template tool;
- Minor improvements on tools list;
- Minor improvements on opinion component tool page;
- Minor improvements on mailing template tool page;
- Minor improvements on rasa webchat tool page;

2.4.1 release
====================

* Date: April 26, 2021
* Features
- Improves dev and user documentation;

2.4.0 release
====================

* Date: April 8, 2021
* Features
- Adds tool mautic template;

2.3.0 release
====================

* Date: March 30, 2021
* Features
- Fixes /docs route;
- Adds documentation page for opinion component tool;
- Adds tool opinion component;
- Adds documentation page for ejBot tool;
- Adds new page for  ejBot configuration;
- Adds new API endpoint api/v1/rasa-conversations/integrations?domain=URL
- Fixes board route
- Adds poetry as default package manager 

2.2.0 release
====================

* Date: March 15, 2021
* Features
- Adds new page for  EJ opinion component configuration;
- Adds new page for  ejBot configuration;

2.1.0 release
====================

* Date: February 15, 2021
* Features
- New conversation tools page
- Improves API to exports EJ data. This data is consumed by conversation component
- Generates mailing template for marketing campaigns (/conversation/tools/mailing)
- Initial instructions to conversation component integration (/conversation/tools/component)

ADA LOVELACE release
====================

* Date: October 11, 2018
* Features
- Participate on conversations with votes and comments
- Add conversation to favorites
- Track your comments on conversations viewing how they perform with other users
- Create new conversations and organize them on boards
- Accept or reject comments with reasoning
- Define stereotypes on conversations to read reports of opinion groups
- Fill your profile information with a personalized picture
- Read basic documentation about how to use EJPlatform
