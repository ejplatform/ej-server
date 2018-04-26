from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^check-login$', views.check_login),
    url(r'^redirect$', views.rc_redirect),
]
