from django.contrib import admin

from .models import Notification, Channel, Message, NotificationConfig

admin.site.register(Notification)
admin.site.register(Channel)
admin.site.register(Message)
admin.site.register(NotificationConfig)
