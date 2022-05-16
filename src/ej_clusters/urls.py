from django.urls import path
from . import views

app_name = "ej_clusters"
conversation_url = f"<int:conversation_id>/<slug:slug>/"

urlpatterns = [
    path(
        conversation_url + "clusters/",
        views.index,
        name="index",
    ),
    path(
        conversation_url + "clusters/edit/",
        views.edit,
        name="edit",
    ),
    path(
        conversation_url + "stereotypes/",
        views.stereotype_votes,
        name="stereotype_votes",
    ),
    path(
        conversation_url + "stereotypes/stereotype-votes-ordenation",
        views.stereotype_votes_ordenation,
        name="stereotype_votes_ordenation",
    ),
    path(
        conversation_url + "stereotypes/stereotype-votes/create",
        views.stereotype_votes_create,
        name="stereotype_votes_create",
    ),
    path(
        conversation_url + "clusters/ctrl/",
        views.ctrl,
        name="ctrl",
    ),
]
