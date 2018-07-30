from . import views
from django.urls import path
from django.conf.urls import url

app_name = "ej_channels"
urlpatterns = [
    url(r'(?P<pk>[0-9]+)/add-to-general-channel', views.ChannelViewSet.as_view({'put': 'add_to_general_channel'})),
    url(r'(?P<pk>[0-9]+)/remove-from-general-channel', views.ChannelViewSet.as_view({'put': 'remove_from_general_channel'})),
    url(r'add-to-group-channel', views.ChannelViewSet.as_view({'put': 'add_to_group_channel'})),
    url(r'remove-from-individual-channel', views.ChannelViewSet.as_view({'put': 'remove_from_individual_channel'})),
    url(r'(?P<pk>[0-9]+)', views.ChannelViewSet.as_view({'get': 'show'})),
    url(r'$', views.ChannelViewSet.as_view({'post': 'create', 'get': 'index'})),
]
