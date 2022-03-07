from django.urls import path
from . import views

app_name = "ej_conversations"
conversation_url = "<int:conversation_id>/<slug:slug>/"

urlpatterns = [
    path(
        "",
        views.public_list_view,
        name="list",
    ),
]
