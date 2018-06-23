from . import views
from django.urls import path
from django.conf.urls import url

app_name = "ej_missions"
urlpatterns = [
    url(r'/(?P<pk>[0-9]+)/receipts', views.MissionViewSet.as_view({'get': 'receipts'})),
    url(r'/(?P<pk>[0-9]+)/receipt', views.MissionViewSet.as_view({'post': 'receipt'})),
    url(r'/(?P<pk>[0-9]+)', views.MissionViewSet.as_view({'get': 'retrieve'})),
    url(r'/accept', views.MissionViewSet.as_view({'post': 'accept'})),
    url(r'/$', views.MissionViewSet.as_view({'post': 'create', 'get': 'list'}))
]
