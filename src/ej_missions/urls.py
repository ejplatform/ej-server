from . import views
from django.urls import path
from django.conf.urls import url

app_name = "ej_missions"
urlpatterns = [
    url(r'/$', views.MissionViewSet.as_view({'post': 'create', 'get': 'list'})),
    url(r'/(?P<pk>[0-9]+)', views.MissionViewSet.as_view({'get': 'retrieve'}))
]
