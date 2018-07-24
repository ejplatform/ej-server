from . import views
from django.urls import path
from django.conf.urls import url

app_name = "ej_channels"
urlpatterns = [
    url(r'add-to-channel', views.ChannelViewSet.as_view({'put': 'add_to_channel'})),
    url(r'remove-from-channel', views.ChannelViewSet.as_view({'put': 'remove_from_channel'})),
    url(r'$', views.ChannelViewSet.as_view({'post': 'create', 'get': 'index'})),
]