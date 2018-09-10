from django.contrib import admin

from .models import Notification, Channel, Message

admin.site.register(Notification)
admin.site.register(Channel)
admin.site.register(Message)
