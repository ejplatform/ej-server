from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from rest_framework.documentation import include_docs_urls

from ej.users.views import FacebookLogin, TwitterLogin


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # url(r'^cities_light/api/', include('cities_light.contrib.restframework3')),

    url(r'^api/v1/docs/', include_docs_urls(title='pushtogether API Docs', public=False)),
    
    # User management
    url(r'^api/v1/profile/', include('ej.users.urls', namespace='v1')),
    url(r'^api/v1/gamification/', include('ej.gamification.urls', namespace='v1')),
    url(r'^api/v1/', include('ej.conversations.urls', namespace='v1')),
    url(r'^api/v1/math/', include('ej.math.urls', namespace='v1')),
    url(r'^api/v1/auth/facebook/$', FacebookLogin.as_view(), name='fb_login'),
    url(r'^api/v1/auth/twitter/$', TwitterLogin.as_view(), name='tw_login'),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^activity/', include('actstream.urls')),
    url(r'^api/v1/', include('courier.urls', namespace='v1')),
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
