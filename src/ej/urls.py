from boogie.rest import rest_api
from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.static import serve
from ej_boards.api import BoardViewSet
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from ej_profiles.api import ProfileViewSet
from ej_tools.api import RasaConversationViewSet
from ej_conversations.api import ConversationViewSet, CommentViewSet, VoteViewSet
from ej_clusters.api import ClusterizationViewSet
from ej_users.api import UsersViewSet
from ej import services
from ej.fixes import unregister_admin

unregister_admin.unregister_apps()

api_router = DefaultRouter()
api_router.register(r"rasa-conversations", RasaConversationViewSet, basename="v1-rasa-conversations")
api_router.register(r"conversations", ConversationViewSet, basename="v1-conversations")
api_router.register(r"comments", CommentViewSet, basename="v1-comments")
api_router.register(r"votes", VoteViewSet, basename="v1-votes")
api_router.register(r"clusterizations", ClusterizationViewSet, basename="v1-clusterizations")
api_router.register(r"profiles", ProfileViewSet, basename="v1-profiles")
api_router.register(r"boards", BoardViewSet, basename="v1-boards")
api_router.register(r"users", UsersViewSet, basename="v1-users")


#
# Optional urls
#
def get_urlpatterns():
    fixes()

    patterns = [
        #
        # Basic authentication and authorization
        path("", include("ej.routes")),
        *with_app("ej_users", "", namespace="auth"),
        *with_app("ej_users", "account/", "routes_account", namespace="account"),
        #
        #  Conversations and other EJ-specific routes
        path("conversations/", include("ej_conversations.public_urls", namespace="conversation")),
        path("comments/", include("ej_conversations.routes_comments", namespace="comments")),
        #
        #  Profile URLS
        *with_app("ej_profiles", "profile/", namespace="profile"),
        #
        #  Data visualization
        path("conversations/", include("ej_dataviz.urls", namespace="dataviz")),
        #
        # Administration Routes
        path("administration/", include("ej_admin.urls", namespace="administration")),
        #
        #  Global stereotype and cluster management
        path("conversations/", include("ej_clusters.urls", namespace="cluster")),
        *with_app("ej_clusters", "stereotypes/", routes="routes_stereotypes", namespace="stereotypes"),
        #
        #  Allauth
        path("accounts/", include("allauth.urls")),
        #
        #  Admin
        *(
            [path(fix_url(settings.ADMIN_URL.lstrip("/")), admin.site.urls)]
            if apps.is_installed("django.contrib.admin")
            else ()
        ),
        #
        #  REST API
        path("api/v1/", include(api_router.urls)),
        path("api/", include(rest_api.urls)),
        path("api/v1/docs/", include_docs_urls(title="ej API Docs", public=False)),
        #
        #  REST API for user management
        path("rest-auth/", include("dj_rest_auth.urls")),
        path("rest-auth/registration/", include("dj_rest_auth.registration.urls")),
        # Static files for the dev server
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
        #
        #  Documentation in development mode
        re_path(r"^docs/$", serve, {"document_root": "build/docs", "path": "index.html"}),
        re_path(r"^docs/(?P<path>.*)$", serve, {"document_root": "build/docs/"}),
        #
        #  Boards
        *with_app("ej_boards", "", namespace="boards"),
    ]

    if settings.DEBUG:
        # Pages for error codes
        patterns.extend(
            [
                path(
                    "error/400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}
                ),
                path(
                    "error/403/",
                    default_views.permission_denied,
                    kwargs={"exception": Exception("Permission Denied")},
                ),
                path(
                    "error/404/",
                    default_views.page_not_found,
                    kwargs={"exception": Exception("Page not Found")},
                ),
                path("error/500/", default_views.server_error),
                path("roles/", include("ej.roles.routes")),
            ]
        )

        if "debug_toolbar" in settings.INSTALLED_APPS:
            import debug_toolbar

            patterns.append(path("__debug__/", include(debug_toolbar.urls)))
    return patterns


def fix_url(url):
    return url.strip("/") + "/"


def fixes():
    if not apps.is_installed("ej_users"):
        user = get_user_model()
        try:
            rest_api.get_resource_info(user)
        except ImproperlyConfigured:
            rest_api(["username"])(user)


def with_app(app, url, routes="routes", namespace=None):
    if apps.is_installed(app):
        return [path(url, include(f"{app}.{routes}", namespace=namespace))]
    else:
        return []


services.start_services(settings)
urlpatterns = get_urlpatterns()
