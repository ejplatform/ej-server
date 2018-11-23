from django.utils.translation import ugettext_lazy as _
from boogie.router import Router

from ej_notifications.models import Notification, Channel, Message, NotificationConfig
from .forms import NotificationConfigForm

app_name = 'ej_notifications'
urlpatterns = Router(
    login=True,
    template=['ej_notifications/{name}.jinja2', 'generic.jinja2'],
    models={
        'notification': Notification,
    },
    lookup_field={
        'notification': 'id',
    },
    object='notification',
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


@urlpatterns.route('inbox/')
def inbox(request):
    user = request.user

    channels = Channel.objects.filter(users=user)
    messages = Message.objects.none()
    notificationConfig = request.user.notifications_options
    print(notificationConfig)
    for item in channels:
        messages = messages | (Message.objects.filter(channel=item))
    print(messages)

    notification_form = NotificationConfigForm(request.POST or None, instance=notificationConfig)
    if request.method == 'POST':
        if notification_form.is_valid():
            notification_form.save()
    
    return {
        'user': user,
        'notifications':[
            {
                "notification": "Você recebeu o poder Ponte de diálogo. Promova um comentário ou crie um comentário promovido",
                "remaining_time": 35,
                "already_seen": True,
            },
            {
                "notification": "Você recebeu o poder Ponte ativista de minoria. Crie um comentário promovido",
                "remaining_time": 35,
                "already_seen": False,
            }
        ],
        'messages': messages,
        'notification_form': notification_form
    }


@urlpatterns.route('read/' + notification_url)
def read_notification(request, notification):
    notification.read = True
    notification.save()
    return {'message': notification.message}
