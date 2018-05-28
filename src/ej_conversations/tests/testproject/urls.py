import debug_toolbar
from django.contrib import admin
from rest_framework.routers import DefaultRouter
try:
    from django.urls import include, re_path as url
except ImportError:
    from django.conf.urls import include, url

from ej_conversations.api import register_routes

router = register_routes(DefaultRouter(), register_user=True)

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^__debug__/', include(debug_toolbar.urls)),
]
