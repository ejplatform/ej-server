============
Social Login
============

Users can login to EJ with Twitter or Facebook, too. In order to do that, you need to prepare the environment and to create the social apps on the respective social networks.

Twitter
=======

First, go to Twitter Developer interface (https://apps.twitter.com) and create an app. The important point is to setup the "Callback URLs" and to mark the checkbox "Allow this application to be used to Sign in with Twitter". Please add two callback URLs: https://your-host/accounts/twitter/login/callback/ and http://your-host/accounts/twitter/login/callback/.

Now, on the Django side, go to the admin interface and create a new social app: http://localhost:8000/admin/socialaccount/socialapp/add/. Choose "Twitter" as the provider, put a name like "EJ Twitter", choose the ejplatform.org.br site and put the consumer key under "Client id" and consumer secret under "Secret key" fields. You can find the consumer key and consumer secret on the Twitter app page, under the "Keys and Access Tokens" tab.

Facebook
========

Important thing to keep in mind: Facebook only allows HTTPS and doesn't allow localhost. So, for local development, we suggest to use a tool like Local Tunnel (http://localtunnel.github.io/www/) or Ngrok (https://ngrok.com/) in order to have a public HTTPS URL that redirects to your local EJ instance. Remember to add that host to DJANGO_ALLOWED_HOSTS.

Once you have the host, go to the Facebook Apps Management page (https://developers.facebook.com/apps) and add a new web app. Go to Configurations > Basic and add the host to "Application domains" and "Site". Add the product "Facebook Login" to your app and, under its settings, add https://your-host/accounts/facebook/login/callback as a valid OAuth URI.

Now, on the Django side, go to the admin interface and create a new social app: http://localhost:8000/admin/socialaccount/socialapp/add/. Choose "Facebook" as the provider, put a name like "EJ Facebook", choose the ejplatform.org.br site and put the app id under "Client id" and secret key under "Secret key" fields. You can find the app id and secret key on the Facebook app page, under Configurations > Basic.

Google
======

In order to have Google login, you need a first-level valid domain that you can confirm the ownership. Go go the developers console (https://console.developers.google.com/) and create a new project. Create a new credential and add https://your-host/accounts/google/login/callback/ as an authorized redirect URI. Remember to also add the domain as a valid domain.

Now, on the Django side, go to the admin interface and create a new social app: http://localhost:8000/admin/socialaccount/socialapp/add/. Choose "Google" as the provider, put a name like "EJ Google", choose the ejplatform.org.br site and put the app id under "Client id" and secret key under "Secret key" fields. You can find the app id and secret key on the Google app page, under Credentials.


Other information
=================

For all cases, for local development you may need to set, at src/ej/settings/__init__.py, ACCOUNT_EMAIL_VERIFICATION = 'none'.

More details at https://django-allauth.readthedocs.io/en/latest/providers.html.
