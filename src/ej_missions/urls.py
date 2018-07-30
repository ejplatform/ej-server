from . import views
from django.urls import path
from django.conf.urls import url

app_name = "ej_missions"
urlpatterns = [
    url(r'inbox/(?P<pk>[0-9]+)$', views.MissionViewSet.as_view({'get': 'inbox'})),
    url(r'accepted/(?P<pk>[0-9]+)$', views.MissionViewSet.as_view({'get': 'accepted_missions'})),
    url(r'(?P<pk>[0-9]+)/receipts', views.MissionViewSet.as_view({'get': 'receipts'})),
    url(r'(?P<mid>[0-9]+)/user-status/(?P<uid>[0-9]+)', views.MissionViewSet.as_view({'get': 'user_status'})),
    url(r'(?P<pk>[0-9]+)/statistics', views.MissionViewSet.as_view({'get': 'statistics'})),
    url(r'(?P<pk>[0-9]+)/receipt', views.MissionViewSet.as_view({'post': 'receipt'})),
    url(r'receipt/(?P<pk>[0-9]+)', views.MissionViewSet.as_view({'post': 'update_receipt'})),
    url(r'(?P<mid>[0-9]+)/conversations/(?P<cid>[0-9]+)/comments', views.MissionViewSet.as_view({'get': 'conversation_comments'})),
    url(r'(?P<mid>[0-9]+)/conversations/user/(?P<uid>[0-9]+)', views.MissionViewSet.as_view({'get': 'next_conversation'})),
    url(r'(?P<mid>[0-9]+)/conversations/(?P<cid>[0-9]+)/vote', views.MissionViewSet.as_view({'get': 'conversation_comments'})),
    url(r'(?P<pk>[0-9]+)/comments$', views.MissionViewSet.as_view({'get': 'comments'})),
    url(r'(?P<pk>[0-9]+)/comment', views.MissionViewSet.as_view({'post': 'add_comment'})),
    url(r'(?P<pk>[0-9]+)', views.MissionViewSet.as_view({'get': 'retrieve'})),
    url(r'accept', views.MissionViewSet.as_view({'post': 'accept'})),
    url(r'$', views.MissionViewSet.as_view({'post': 'create', 'get': 'list'})),
]
