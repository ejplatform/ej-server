from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from rest_framework.documentation import include_docs_urls

from boogie.rest import rest_api
from ej.fixes import unregister_admin

unregister_admin.unregister_apps()

urlpatterns = [
    # Basic authentication and authorization
    path('', include('ej.routes')),
    path('', include('ej_users.routes', namespace='auth')),

    # EJ Routes
    path('', include('ej_conversations.routes', namespace='conversations')),
    path('profile/', include(('ej_profiles.routes', 'ej_profiles'), namespace='profiles')),
    path('config/', include(('ej_configurations.routes', 'ej_configurations'), namespace='configurations')),

    path('dataviz/', include(('ej_dataviz.routes', 'ej_dataviz'), namespace='dataviz')),

    # Rocket
    path('talks/', include(('ej_rocketchat.routes', 'ej_rocketchat'), namespace='rocketchat')),

    # Admin
    path(settings.ADMIN_URL.rstrip('^'), admin.site.urls),

    # REST API
    path('api/', include(rest_api.urls)),
    path('api/v1/docs/', include_docs_urls(title='ej API Docs', public=False)),
    # path('api/v1/', include('courier.urls', namespace='courier')),
    # path('api/v1/rocketchat/', include('ej.ej_rocketchat.urls')),

    # User management
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),

    # Static files for the dev server
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]

if settings.DEBUG:
    # Pages for error codes
    urlpatterns.extend([
        path('error/400/', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        path('error/403/', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        path('error/404/', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        path('error/500/', default_views.server_error),
    ])

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns.append(
            path('__debug__/', include(debug_toolbar.urls))
        )
