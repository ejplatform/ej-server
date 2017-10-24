from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from django.views.generic.base import RedirectView
from rest_framework.documentation import include_docs_urls


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    url(r'^api/docs/', include_docs_urls(title='pushtogether API Docs', public=False)),
    # User management
    # url(r'^users/', include('pushtogether.users.urls', namespace='users')),
    url(r'^polis/', include('pushtogether.polis.urls', namespace='polis')),
    url(r'^api/v1/', include('pushtogether.conversations.urls', namespace='v1')),
    url(r'^api/v1/users/', include('pushtogether.users.urls', namespace='v1')),
    url(r'^rest-auth/', include('rest_auth.urls')),
    # TODO: Remove this redirect after october 2017
    url(r'^rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$', RedirectView.as_view(pattern_name='account_confirm_email'), name='account-confirm-email-redirect'),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^accounts/', include('allauth.urls')),

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
