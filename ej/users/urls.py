from django.conf.urls import url
from django.views.generic import TemplateView

from . import views
app_name = 'users'

urlpatterns = [
    # Overrides allauth endpoint
    url(r'^login/$', views.SignupView.as_view(), name='account_login'),
    url(r'^close/$', TemplateView.as_view(template_name='users/close.html')),
    url(r'^redirect/$', views.UserRedirectView.as_view(), name='redirect'),
    url(r'^update/$', views.UserUpdateView.as_view(), name='update'),
    url(r'^key/$', views.get_api_key, name='api-key'),
    url(r'^reset/$', views.clean_cookies, name='clean-cookies'),
]
