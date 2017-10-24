from rest_framework.routers import SimpleRouter
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

router = SimpleRouter()
router.register(r'', views.UserViewSet),

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
]

urlpatterns.extend(router.urls)
