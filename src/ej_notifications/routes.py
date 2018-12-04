from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from ej_notifications.models import Notification

app_name = 'ej_notifications'
urlpatterns = Router(
    login=True,
    template=['ej_notifications/{name}.jinja2', 'generic.jinja2'],
    models={'notification': Notification},
)
notification_url = f'<model:notification>/'


@urlpatterns.route()
def index(request):
    user = request.user
    notifications = Notification.objects.filter(receiver__id=user.id, read=False).order_by("-created_at")
    return {
        'content_title': _('List of notifications'),
        'user': user,
        'notifications': notifications,
    }


@urlpatterns.route('history/')
def clusters(request):
    user = request.user
    notifications = Notification.objects.filter(receiver__id=user.id, read=True).order_by("-created_at")
    return {
        'user': user,
        'notifications': notifications,
    }


@urlpatterns.route('read/' + notification_url)
def read_notification(notification):
    notification.read = True
    notification.save()
    return {'message': notification.message}
