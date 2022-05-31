from django.urls import path
from . import views

app_name = "ej_admin"

urlpatterns = [
    path(
        "",
        views.index,
        name="index",
    ),
    path(
        "recent-boards/",
        views.recent_boards,
        name="recent_boards",
    ),
    path(
        "searched-users/",
        views.searched_users,
        name="searched_users",
    ),
    path(
        "searched-boards/",
        views.searched_boards,
        name="searched_boards",
    ),
    path(
        "searched-conversations/",
        views.searched_conversations,
        name="searched_conversations",
    ),
    path(
        "favorite-boards/",
        views.get_favorite_boards,
        name="favorite_boards",
    ),
]
