from django.urls import path
from . import views

app_name = "ej_conversations"
conversation_url = "<int:conversation_id>/<slug:slug>"

urlpatterns = [
    path(
        "",
        views.list_view,
        name="list",
    ),
    path(
        f"{conversation_url}/moderate/",
        views.moderate,
        name="moderate",
    ),
    path(
        f"{conversation_url}/edit/",
        views.edit,
        name="edit",
    ),
    path(
        f"{conversation_url}/",
        views.detail,
        name="detail",
    ),
    path(
        "add/",
        views.create,
        name="create",
    ),
]
