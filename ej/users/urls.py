from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'users'

urlpatterns = [
    # Overrides allauth endpoints
    path('login/', views.SignupView.as_view(), name='account_login'),
    path('close/', TemplateView.as_view(template_name='django/users/../templates/close.html')),
    path('redirect/', views.UserRedirectView.as_view(), name='redirect'),
    path('update/', views.UserUpdateView.as_view(), name='update'),
    path('key/', views.get_api_key, name='api-key'),
    path('reset/', views.clean_cookies, name='clean-cookies'),
]
