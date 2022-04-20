================================
CHANGELOG of EJPlatform releases
================================

Here you can follow all the fixes and new features on every EJPlatform release.

3.1.0 release
====================
* Date: April 20, 2022
* Features
- Adds new UI for personas management;
- Fixes boards page margin;
- Removes ej_rocketchat, ej_analysis, ej_gamification and ej_experiments apps;
- Adds new API endpoint /api/v1/users;
- Adds new tab on comments moderation for adding new comments;
- Adds new environment management area for admin profile;
- Fixes mobile menus overlay;

3.0.0 release
====================
* Date: April 06, 2022
* Features
- Adds new user menu on mobile;
- Adds new conversation menu on mobile;
- Adds new conversation dashboard to improves analysis and modeling;
- Adds new frontend for email template tool;
- Adds new frontend for personas management;
- Adds new comments report;

2.23.0 release
====================
* Date: Jan 31, 2022
* Features
- Fixes tools pages margin;
- Implements new conversation balloon;
- Implements new conversation side menu;
- Removes django-boogie from ej_conversations routes;
- Fixes opinion-component preview bug;

2.22.0 release
====================
* Date: Jan 31, 2022
* Features
- Fixes tour images;
- Fixes conversation cards responsiveness;
- Adds mobile UI for board statistics;
- Adds modal to quickly access conversation tools after conversation creation; 
- Adds new UI for whatsapp Tool;
- Adds new UI for opinion component Tool;
- Adds new UI for webchat Tool;
- Adds edit option for telegram poll bot;

2.21.0 release
====================
* Date: Jan 31, 2022
* Features
- Fixes social login redirect;
- Fixes tools routes for unauthenticated user;
- Advises user that no personas was created for the conversation;
- Limit API usage based on conversation author signature;
- Removes django-boogie from ej_tools routes;
- Implements new Telegram tool page;
- Adds new user tour;

2.20.0 release
====================
* Date: Jan 19, 2022
* Features
- Fixes preview for opinion component tool;
- Fixes preview for webchat tool;
- Fixes wrong check on conversation owner signature;
- Fixes whatsapp card tool;
- Evolves signature arquitecture to limit tools usage;
- Adds new UI to opinion component tool;
- Removes django-boogie from ej_conversations API;

2.19.0 release
====================
* Date: Dec 21, 2021
* Features
- Fixes responsiveness issues;
- Fixes default board creation for social login;
- Fixes bug on board signature;
- Improves UX of board edit and conversation creation;
- Fixes social login with Google;
- Adds webchat preview on webchat tool page;


2.18.0 release
====================
* Date: Dec 07, 2021
* Features
- Redirects user to conversation report after conversation creation;
- Improves tools cards UI;
- Improves tools pages navigation; 
- Improves documentations;
- Adds an option to preview poll comments on poll bot card;
- Adds board statistics;
- Fixes boca de lobo opinion component theme;
- Removes django-boogie from ej_tools api; 

2.17.0 release
====================
* Date: Nov 23, 2021
* Features
- Refactoring ej_boards routes.py, to loading other apps routes automatically; 
- Fixes participants report export, as json format;
- Adds new Whatsapp tool frontend;
- Improves boards menu UI;
- Adds new Telegram tool frontend;
- Refactoring singnatures arquitecture;
- Adds support for telegram poll bot, on tools area;
- Fixes vote distribuition graph UI;
- Improves participants report UI;

2.16.0 release
====================
* Date: Nov 09, 2021
* Features
- Adds phone_number on participants report;
- Fixes bug on reports menu;
- Fixes bug on opinion component preview;
- Fixes reports tables overflow;
- Fixes bug on opinion component theme selection;
- Redirects user to conversation report after click on "manage";
- Fixes fonts and colors on general reports;
- Adds Whatsapp tool page;
- Adds "Listen to City" Signature;

2.15.0 release
====================
* Date: Oct 27, 2021
* Features
- Adds new profile menu;
- Fixes mailing template preview;
- Fixes export dropdown on reports pages;
- Adds analytics_utm field on Vote model;
- Fixes tables responsiveness;
- Adds telegram support on Chatbot tool;
- Adds voting by date visualization, on general report;
- Adds opinion component preview, on Opinion Component tool page;

2.14.0 release
====================
* Date: Oct 12, 2021
* Features
- Adds new tool page called Chatbot;
- Removes excel export data option;
- Adds new voting visualization on conversation general report. This visualization segments votes by
  channel;
- Includes Signature model on django admin;
- Fixes bug on conversation card;
- Implements new relation between conversation and board;
- Removes django_rest_auth dependency;

2.13.0 release
====================

* Date: Set 27, 2021
* Features
- Adds new page to comments report;
- Adds visual improvements on reports menu;
- Adds modal to export reports data;
- Fixes participants counter, on general report; 
- Fixes profile image on header; 
- Upgrades aplication to django 3;

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
