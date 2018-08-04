from . import views
from django.urls import path
from django.conf.urls import url

app_name = "ej_messages"
urlpatterns = [
    url(r'$', views.MessageViewSet.as_view({'post': 'create', 'get': 'index'})),
]