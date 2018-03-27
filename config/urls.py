from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from django.views.generic.base import RedirectView
from rest_framework.documentation import include_docs_urls

from ej.users.views import FacebookLogin, TwitterLogin


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # url(r'^cities_light/api/', include('cities_light.contrib.restframework3')),

    url(r'^api/docs/', include_docs_urls(title='pushtogether API Docs', public=False)),
    # User management
    url(r'^api/profile/', include('ej.users.urls', namespace='users')),
    url(r'^api/gamification/', include('ej.gamification.urls', namespace='gamification')),
    url(r'^api/', include('ej.conversations.urls', namespace='v1')),
    url(r'^api/math/', include('ej.math.urls', namespace='math')),
    url(r'^api/auth/facebook/$', FacebookLogin.as_view(), name='fb_login'),
    url(r'^api/auth/twitter/$', TwitterLogin.as_view(), name='tw_login'),
    url(r'^rest-auth/', include('rest_auth.urls')),
    # TODO: Remove this redirect after october 2017
    url(r'^rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$', RedirectView.as_view(pattern_name='account_confirm_email'), name='account-confirm-email-redirect'),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^activity/', include('actstream.urls')),
    url(r'^api/', include('courier.urls', namespace='courier')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
