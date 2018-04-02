from rest_framework.routers import SimpleRouter
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

router = SimpleRouter()
router.register(r'', views.UserViewSet),
router.register(r'^me/$', views.UserViewSet.as_view({'get': 'retrieve'}), base_name='me'),
app_name = 'users'

urlpatterns = [
    url(
        regex=r'^signin/$',
        view=views.LoginSignupView.as_view(),
        name='signin'
    ),
    url(r'^close/$', TemplateView.as_view(template_name='users/close.html')),
    url(
        regex=r'^~redirect/$',
        view=views.UserRedirectView.as_view(),
        name='redirect'
    ),
    url(
        regex=r'^~update/$',
        view=views.UserUpdateView.as_view(),
        name='update'
    ),
    url(
        regex=r'^key/$',
        view=views.get_api_key,
        name='api-key'
    ),
    url(
        regex=r'^reset/$',
        view=views.clean_cookies,
        name='clean-cookies'
    ),
]

urlpatterns.extend(router.urls)
