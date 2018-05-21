from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'users'

urlpatterns = [
    # Overrides allauth endpoints
    path('key/', views.get_api_key, name='api-key'),
    path('reset/', views.clean_cookies, name='clean-cookies'),
]
