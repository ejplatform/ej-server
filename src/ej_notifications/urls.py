from . import views
from django.urls import path
from django.conf.urls import url

app_name = "ej_notifications"
urlpatterns = [
    url(r'user/(?P<pk>[0-9]+)', views.NotificationViewSet.as_view({'get': 'user_notifications'})),
    url(r'(?P<pk>[0-9]+)', views.NotificationViewSet.as_view({'get': 'show'})),
    url(r'$', views.NotificationViewSet.as_view({'post': 'create','get': 'index'})),
]