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
        f"{conversation_url}/comments/new/",
        views.new_comment,
        name="new_comment",
    ),
    path(
        f"{conversation_url}/comments/delete/",
        views.delete_comment,
        name="delete_comment",
    ),
    path(
        f"{conversation_url}/comments/check/",
        views.check_comment,
        name="check_comment",
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
    path(
        f"update-favorite-boards/",
        views.update_favorite_boards,
        name="update-favorite-boards",
    ),
    path(
        f"is-favorite-board/",
        views.is_favorite_board,
        name="is-favorite-board",
    ),
]
