from django.urls import path
from . import views

app_name = "ej_signatures"

urlpatterns = [
    path(
        "signatures/",
        views.list_view,
        name="list",
    ),
    path(
        "signatures/upgrade/",
        views.upgrade,
        name="upgrade",
    ),
]
