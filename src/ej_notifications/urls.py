from . import views
from django.conf.urls import url

app_name = "ej_notifications"
urlpatterns = [
    url(r'user/(?P<pk>[0-9]+)/unread', views.NotificationViewSet.as_view({'get': 'unread'})),
    url(r'user/(?P<pk>[0-9]+)', views.NotificationViewSet.as_view({'get': 'user_notifications'})),
    url(r'(?P<pk>[0-9]+)', views.NotificationViewSet.as_view({'get': 'show'})),
    url(r'update-read', views.NotificationViewSet.as_view({'put': 'update_read'})),
    url(r'$', views.NotificationViewSet.as_view({'post': 'create', 'get': 'index'})),
]
