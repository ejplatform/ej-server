from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from rest_framework.documentation import include_docs_urls

from ej.users.views import FacebookLogin, TwitterLogin
from . import views
from .api import router_v1

urlpatterns = [
    path('', views.index_view, name='home'),
    path(settings.ADMIN_URL, admin.site.urls),

    # REST API
    path('api/v1/', include(router_v1.urls)),
    path('api/docs/', include_docs_urls(title='ej API Docs', public=False)),

    # User management
    path('api/auth/facebook/', FacebookLogin.as_view(), name='fb_login'),
    path('api/auth/twitter/', TwitterLogin.as_view(), name='tw_login'),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),

    # Other urls
    path('accounts/', include('ej.users.urls')),
    path('accounts/', include('allauth.urls')),
    path('activity/', include('actstream.urls')),
    path('api/', include('courier.urls', namespace='courier')),

    # Static files for the dev server
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
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
