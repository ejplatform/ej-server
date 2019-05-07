from boogie.router import Router

from ej_notifications.models import Channel

app_name = "ej_notifications"
urlpatterns = Router(
    login=True,
    template=["ej_notifications/{name}.jinja2", "generic.jinja2"],
    models={"channel": Channel},
    lookup_field={"channel": "slug"},
    lookup_type="slug",
)
notification_url = f"<model:channel>/"
